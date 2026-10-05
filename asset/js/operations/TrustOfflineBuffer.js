// lib/TrustOfflineBuffer.js
const Database = require('better-sqlite3');
const crypto = require('crypto');

class TrustOfflineBuffer {
    constructor(dbPath = './trust_shell_queue.db', trustMainEndpoint) {
        this.dbPath = dbPath;
        this.trustMainEndpoint = trustMainEndpoint;
        this.db = new Database(this.dbPath);
        this.syncInterval = null;
        this.isSyncing = false;

        this._initDatabase();
    }

    /**
     * Updated schema containing the local HMAC signature column and TAMPERED status check
     */
    _initDatabase() {
        this.db.pragma('journal_mode = WAL');
        
        this.db.prepare(`
            CREATE TABLE IF NOT EXISTS payload_queue (
                queue_id TEXT PRIMARY KEY,
                master_shift_hash TEXT UNIQUE NOT NULL,
                module_type TEXT NOT NULL,
                badge_id TEXT NOT NULL,
                payload_json TEXT NOT NULL,
                hmac_signature TEXT NOT NULL,
                status TEXT CHECK(status IN ('PENDING', 'SYNCING', 'SYNCED', 'FAILED', 'TAMPERED')) DEFAULT 'PENDING',
                retry_count INTEGER DEFAULT 0,
                created_at TEXT NOT NULL,
                last_attempt_at TEXT,
                error_log TEXT
            )
        `).run();

        this.db.prepare(`
            CREATE INDEX IF NOT EXISTS idx_payload_status ON payload_queue(status, created_at);
        `).run();
    }

    /**
     * Generate an HMAC-SHA256 signature for local payload integrity checks
     */
    _computeHmac(jsonString) {
        const secret = process.env.TRUST_SHELL_DEVICE_KEY || 'LOCAL_HARDWARE_KEY_32BYTES_LONG';
        return crypto.createHmac('sha256', secret).update(jsonString).digest('hex');
    }

    /**
     * Enqueue payload with an HMAC signature computed at write-time
     */
    enqueue(payload) {
        if (!payload || !payload.master_shift_hash) {
            throw new Error("Invalid payload: missing master_shift_hash.");
        }

        const queueId = `BUF_${Date.now()}_${crypto.randomBytes(4).toString('hex')}`;
        const createdAt = new Date().toISOString();
        const payloadJson = JSON.stringify(payload);
        
        // Generate HMAC signature before writing to disk
        const hmacSignature = this._computeHmac(payloadJson);

        const stmt = this.db.prepare(`
            INSERT INTO payload_queue (
                queue_id, master_shift_hash, module_type, badge_id, payload_json, hmac_signature, status, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, 'PENDING', ?)
        `);

        stmt.run(
            queueId,
            payload.master_shift_hash,
            payload.module || 'BASE_FIRST_RESPONDER',
            payload.badge_id || 'UNKNOWN',
            payloadJson,
            hmacSignature,
            createdAt
        );

        return { queueId, masterShiftHash: payload.master_shift_hash, hmacSignature };
    }

    /**
     * VERIFICATION METHOD: Validates local database record against on-disk tampering
     * @param {Object} record - Database row from payload_queue
     * @returns {boolean} - true if signature matches; false if tampered/corrupted
     */
    verifyRecordIntegrity(record) {
        if (!record || !record.payload_json || !record.hmac_signature) {
            return false;
        }

        const expectedHmac = this._computeHmac(record.payload_json);

        // Convert signatures to buffers for timing-safe comparison to prevent timing attacks
        const storedBuf = Buffer.from(record.hmac_signature, 'hex');
        const expectedBuf = Buffer.from(expectedHmac, 'hex');

        const isValid = storedBuf.length === expectedBuf.length && 
                        crypto.timingSafeEqual(storedBuf, expectedBuf);

        if (!isValid) {
            // Quarantine record immediately in SQLite
            const stmt = this.db.prepare(`
                UPDATE payload_queue 
                SET status = 'TAMPERED', 
                    error_log = ?, 
                    last_attempt_at = ? 
                WHERE queue_id = ?
            `);
            stmt.run(
                'INTEGRITY_VIOLATION: Payload signature mismatch. On-disk record modified prior to sync.', 
                new Date().toISOString(), 
                record.queue_id
            );
            return false;
        }

        return true;
    }

    /**
     * Process queue with pre-sync integrity checks
     */
    async processQueue(maxRetries = 5) {
        if (this.isSyncing) return { processed: 0, status: 'ALREADY_RUNNING' };

        const online = await this.isOnline();
        if (!online) {
            return { processed: 0, status: 'OFFLINE' };
        }

        this.isSyncing = true;
        let syncedCount = 0;
        let failedCount = 0;
        let tamperedCount = 0;

        const selectStmt = this.db.prepare(`
            SELECT queue_id, master_shift_hash, payload_json, hmac_signature, retry_count 
            FROM payload_queue 
            WHERE status IN ('PENDING', 'FAILED') AND retry_count < ?
            ORDER BY created_at ASC
            LIMIT 50
        `);

        const records = selectStmt.all(maxRetries);

        for (const record of records) {
            // STEP 1: Verify on-disk integrity before touching network
            if (!this.verifyRecordIntegrity(record)) {
                tamperedCount++;
                console.error(`[SECURITY ALERT] Payload ${record.queue_id} rejected due to local database tampering.`);
                continue; // Skip network transmission
            }

            // STEP 2: Lock record to SYNCING
            this.db.prepare(`UPDATE payload_queue SET status = 'SYNCING', last_attempt_at = ? WHERE queue_id = ?`)
                .run(new Date().toISOString(), record.queue_id);

            // STEP 3: Transmit to Trust-Main
            try {
                const response = await fetch(this.trustMainEndpoint, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-Trust-Shell-HMAC': record.hmac_signature
                    },
                    body: record.payload_json
                });

                if (response.ok) {
                    this.db.prepare(`UPDATE payload_queue SET status = 'SYNCED', error_log = NULL WHERE queue_id = ?`)
                        .run(record.queue_id);
                    syncedCount++;
                } else {
                    const errText = `HTTP ${response.status}: ${await response.text()}`;
                    this._markFailed(record.queue_id, record.retry_count, errText);
                    failedCount++;
                }
            } catch (err) {
                this._markFailed(record.queue_id, record.retry_count, err.message);
                failedCount++;
            }
        }

        this.isSyncing = false;
        return { 
            total: records.length, 
            synced: syncedCount, 
            failed: failedCount, 
            tampered: tamperedCount, 
            status: 'COMPLETE' 
        };
    }

    _markFailed(queueId, currentRetryCount, errorMessage) {
        const stmt = this.db.prepare(`
            UPDATE payload_queue 
            SET status = 'FAILED', retry_count = ?, error_log = ?, last_attempt_at = ? 
            WHERE queue_id = ?
        `);
        stmt.run(currentRetryCount + 1, errorMessage, new Date().toISOString(), queueId);
    }
}

module.exports = TrustOfflineBuffer;


// Inside TrustOfflineBuffer.js
const TrustSecurityOfficer = require('./TrustSecurityOfficer');

class TrustOfflineBuffer {
    constructor(dbPath = './trust_shell_queue.db', trustMainEndpoint) {
        this.dbPath = dbPath;
        this.trustMainEndpoint = trustMainEndpoint;
        this.db = new Database(this.dbPath);
        
        // Initialize security officer module
        this.securityOfficer = new TrustSecurityOfficer(
            'https://trust-main.internal/api/v1/security/alert',
            this.dbPath
        );

        this._initDatabase();
    }

    verifyRecordIntegrity(record) {
        if (!record || !record.payload_json || !record.hmac_signature) {
            return false;
        }

        const expectedHmac = this._computeHmac(record.payload_json);
        const storedBuf = Buffer.from(record.hmac_signature, 'hex');
        const expectedBuf = Buffer.from(expectedHmac, 'hex');

        const isValid = storedBuf.length === expectedBuf.length && 
                        crypto.timingSafeEqual(storedBuf, expectedBuf);

        if (!isValid) {
            // Trigger Beacon + Local Wipe workflow synchronously
            this.securityOfficer.handleTamperingEvent(record, this.db);
            return false;
        }

        return true;
    }
}

// Inside TrustOfflineBuffer.js
const TrustHardwareKeyManager = require('./TrustHardwareKeyManager');

class TrustOfflineBuffer {
    constructor(dbPath = './trust_shell_queue.db', trustMainEndpoint) {
        this.dbPath = dbPath;
        this.trustMainEndpoint = trustMainEndpoint;
        this.db = new Database(this.dbPath);
        
        // Initialize hardware key manager bound to TPM / Secure Enclave
        this.keyManager = new TrustHardwareKeyManager({
            keyContextPath: '/var/lib/trust_shell/tpm_hmac.ctx',
            keyLabel: 'com.trust.shell.hmac.key'
        });

        this._initDatabase();
    }

    /**
     * Delegates HMAC generation to TPM / Secure Enclave hardware
     */
    _computeHmac(jsonString) {
        return this.keyManager.signPayload(jsonString);
    }
}

// Inside TrustOfflineBuffer.js
const TrustDatabaseMaintenance = require('./TrustDatabaseMaintenance');

class TrustOfflineBuffer {
    constructor(dbPath = '/var/lib/trust_shell/trust_shell_queue.db', trustMainEndpoint) {
        this.dbPath = dbPath;
        this.trustMainEndpoint = trustMainEndpoint;
        this.db = new Database(this.dbPath);

        // Attach database storage maintenance
        this.maintenance = new TrustDatabaseMaintenance(this.db, {
            journalSizeLimit: 16 * 1024 * 1024, // 16MB WAL limit
            checkpointIntervalMs: 15 * 60 * 1000 // Run every 15 minutes
        });

        this._initDatabase();
        this.maintenance.startScheduledMaintenance();
    }

    /**
     * Trigger explicit checkpoint after large sync batches to keep disk footprint small
     */
    async processQueue(maxRetries = 5) {
        const result = await super.processQueue(maxRetries);

        // Force WAL truncation after processing queued records
        if (result.synced > 0) {
            this.maintenance.checkpointWal();
        }

        return result;
    }
}


// Inside lib/TrustOfflineBuffer.js

class TrustOfflineBuffer {
    /**
     * Verifies server receipt authenticity before executing local database deletion
     */
    _verifyServerReceipt(record, receipt, serverSignature) {
        if (!receipt || receipt.status !== 'VERIFIED_AND_PERSISTED') {
            console.error(`[DELIVERY ERROR] Server reported processing failure for ${record.queue_id}`);
            return false;
        }

        // 1. Check that the server acknowledged the exact record sent
        if (receipt.queue_id !== record.queue_id || receipt.received_hmac !== record.hmac_signature) {
            console.error(`[DELIVERY ERROR] Server receipt HMAC/ID mismatch for ${record.queue_id}`);
            return false;
        }

        // 2. Validate server's cryptographic response signature
        const expectedServerSig = crypto
            .createHmac('sha256', process.env.TRUST_MAIN_SERVER_SECRET || 'SERVER_HANDSHAKE_KEY')
            .update(`${receipt.queue_id}:${receipt.received_hmac}:${receipt.timestamp}`)
            .digest('hex');

        const validSig = crypto.timingSafeEqual(
            Buffer.from(serverSignature || '', 'hex'),
            Buffer.from(expectedServerSig, 'hex')
        );

        if (!validSig) {
            console.error(`[SECURITY WARNING] Invalid server response signature on ${record.queue_id}. Refusing to purge.`);
            return false;
        }

        return true;
    }

    async processQueue(maxRetries = 5) {
        if (this.isSyncing) return { processed: 0, status: 'ALREADY_RUNNING' };

        const selectStmt = this.db.prepare(`
            SELECT queue_id, master_shift_hash, payload_json, hmac_signature, retry_count 
            FROM payload_queue 
            WHERE status IN ('PENDING', 'FAILED') AND retry_count < ?
            ORDER BY created_at ASC LIMIT 50
        `);

        const records = selectStmt.all(maxRetries);
        let purgedCount = 0;

        for (const record of records) {
            if (!this.verifyRecordIntegrity(record)) continue;

            try {
                const response = await fetch(this.trustMainEndpoint, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-Trust-Shell-HMAC': record.hmac_signature
                    },
                    body: record.payload_json
                });

                if (response.ok) {
                    const receipt = await response.json();
                    const serverSignature = response.headers.get('X-Trust-Main-Signature');

                    // STRICT CHECK: Only execute hard purge if the signed receipt is valid
                    if (this._verifyServerReceipt(record, receipt, serverSignature)) {
                        this.db.prepare(`DELETE FROM payload_queue WHERE queue_id = ?`).run(record.queue_id);
                        purgedCount++;
                        console.log(`[DELIVERY CONFIRMED] Report ${record.queue_id} persisted on Trust-Main. Local copy purged.`);
                    } else {
                        this._markFailed(record.queue_id, record.retry_count, 'SERVER_RECEIPT_VALIDATION_FAILED');
                    }
                } else {
                    this._markFailed(record.queue_id, record.retry_count, `HTTP_${response.status}`);
                }
            } catch (err) {
                this._markFailed(record.queue_id, record.retry_count, err.message);
            }
        }

        if (purgedCount > 0) {
            this._truncateDiskLog();
        }

        return { processed: records.length, purged: purgedCount };
    }
}
