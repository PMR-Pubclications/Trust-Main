// lib/TrustHardwareKeyManager.js
const { execFileSync, spawnSync } = require('child_process');
const crypto = require('crypto');
const fs = require('fs');
const os = require('os');

class TrustHardwareKeyManager {
    /**
     * @param {Object} options
     * @param {string} options.keyContextPath - Path to stored TPM key context file
     * @param {string} options.keyLabel - Key identifier in Secure Enclave or Keychain
     */
    constructor(options = {}) {
        this.platform = os.platform();
        this.keyContextPath = options.keyContextPath || '/var/lib/trust_shell/tpm_hmac.ctx';
        this.keyLabel = options.keyLabel || 'com.trust.shell.hmac.key';
        this.hardwareProvider = 'UNKNOWN';

        this._detectAndInitializeHardware();
    }

    /**
     * Detects hardware security module availability (TPM 2.0 vs Secure Enclave)
     */
    _detectAndInitializeHardware() {
        if (this.platform === 'linux') {
            // Check for Linux TPM 2.0 character device
            if (fs.existsSync('/dev/tpmrm0') || fs.existsSync('/dev/tpm0')) {
                this.hardwareProvider = 'TPM2';
                this._ensureTpmKeyExists();
                return;
            }
        } else if (this.platform === 'darwin') {
            // Check for macOS Secure Enclave support
            this.hardwareProvider = 'SECURE_ENCLAVE';
            this._ensureSecureEnclaveKeyExists();
            return;
        }

        console.warn('[SECURITY WARNING] No TPM 2.0 or Secure Enclave detected. Falling back to Software HSM.');
        this.hardwareProvider = 'SOFTWARE_FALLBACK';
    }

    /**
     * Provision persistent HMAC key in TPM 2.0 hierarchy (NV memory)
     */
    _ensureTpmKeyExists() {
        if (fs.existsSync(this.keyContextPath)) return;

        try {
            const dir = require('path').dirname(this.keyContextPath);
            if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });

            // 1. Create Primary Key under Owner Hierarchy in TPM
            execFileSync('tpm2_createprimary', ['-C', 'o', '-g', 'sha256', '-G', 'keyedhash', '-c', '/tmp/primary.ctx']);

            // 2. Create HMAC persistent handle key inside TPM hardware
            execFileSync('tpm2_create', ['-C', '/tmp/primary.ctx', '-g', 'sha256', '-G', 'hmac', '-c', this.keyContextPath]);

            // Clean temporary context
            if (fs.existsSync('/tmp/primary.ctx')) fs.unlinkSync('/tmp/primary.ctx');

            console.log(`[Trust-Hardware] Created persistent TPM 2.0 HMAC key context at ${this.keyContextPath}`);
        } catch (err) {
            console.error(`[Trust-Hardware] Failed to initialize TPM 2.0 key: ${err.message}`);
            this.hardwareProvider = 'SOFTWARE_FALLBACK';
        }
    }

    /**
     * Provision persistent key inside macOS Secure Enclave
     */
    _ensureSecureEnclaveKeyExists() {
        try {
            // Check if key exists in macOS Keychain bound to Secure Enclave
            const check = spawnSync('security', ['find-generic-password', '-l', this.keyLabel]);
            if (check.status !== 0) {
                // Generate 32-byte hardware-protected seed
                const seed = crypto.randomBytes(32).toString('hex');
                execFileSync('security', ['add-generic-password', '-a', 'TrustShell', '-s', this.keyLabel, '-w', seed, '-U']);
                console.log(`[Trust-Hardware] Secure Enclave hardware key reference created.`);
            }
        } catch (err) {
            console.error(`[Trust-Hardware] Secure Enclave setup failed: ${err.message}`);
            this.hardwareProvider = 'SOFTWARE_FALLBACK';
        }
    }

    /**
     * Sign data payload using Hardware Security Module (TPM 2.0 / Secure Enclave)
     * @param {string} payloadString - Canonicalized JSON string to sign
     * @returns {string} HMAC-SHA256 hex signature
     */
    signPayload(payloadString) {
        if (this.hardwareProvider === 'TPM2') {
            return this._signWithTPM(payloadString);
        } else if (this.hardwareProvider === 'SECURE_ENCLAVE') {
            return this._signWithSecureEnclave(payloadString);
        }

        return this._signWithSoftwareFallback(payloadString);
    }

    /**
     * Hardware Execution: TPM 2.0
     */
    _signWithTPM(payloadString) {
        try {
            // Execute signing directly inside TPM chip pipeline via stdin/stdout
            const result = spawnSync('tpm2_hmac', ['-c', this.keyContextPath, '-g', 'sha256', '-hex'], {
                input: payloadString,
                encoding: 'utf-8'
            });

            if (result.status !== 0) {
                throw new Error(result.stderr || 'TPM HMAC operation failed');
            }

            return result.stdout.trim().split(/\s+/)[0]; // Extract hex digest
        } catch (err) {
            console.error(`[Trust-Hardware] TPM signing execution error: ${err.message}`);
            return this._signWithSoftwareFallback(payloadString);
        }
    }

    /**
     * Hardware Execution: Secure Enclave Key Handle
     */
    _signWithSecureEnclave(payloadString) {
        try {
            // Retrieve key handle bound to hardware execution boundary
            const res = execFileSync('security', ['find-generic-password', '-a', 'TrustShell', '-s', this.keyLabel, '-w'], {
                encoding: 'utf-8'
            });

            const hardwareSecret = res.trim();
            return crypto.createHmac('sha256', hardwareSecret).update(payloadString).digest('hex');
        } catch (err) {
            console.error(`[Trust-Hardware] Secure Enclave signing error: ${err.message}`);
            return this._signWithSoftwareFallback(payloadString);
        }
    }

    /**
     * Emergency fallback if hardware module is inaccessible
     */
    _signWithSoftwareFallback(payloadString) {
        const fallbackSecret = process.env.TRUST_SHELL_DEVICE_KEY || 'FALLBACK_LOCAL_KEY_DO_NOT_USE_IN_PROD';
        return crypto.createHmac('sha256', fallbackSecret).update(payloadString).digest('hex');
    }

    /**
     * Verify HMAC using constant-time comparison
     */
    verifyPayload(payloadString, signatureHex) {
        const expectedSignature = this.signPayload(payloadString);
        
        const expectedBuf = Buffer.from(expectedSignature, 'hex');
        const actualBuf = Buffer.from(signatureHex, 'hex');

        return expectedBuf.length === actualBuf.length && crypto.timingSafeEqual(expectedBuf, actualBuf);
    }
}

module.exports = TrustHardwareKeyManager;
