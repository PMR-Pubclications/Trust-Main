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
