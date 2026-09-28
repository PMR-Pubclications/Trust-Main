const express = require('express');
const crypto = require('crypto');

const app = express();
app.use(express.json());

// In-memory key store for demonstration. 
// In production, store your private key securely in an environment variable or HSM.
let keyPair = null;

// Utility to generate Ed25519 key pair on initialization
function initializeKeys() {
  keyPair = crypto.generateKeyPairSync('ed25519', {
    publicKeyEncoding: { type: 'spki', format: 'pem' },
    privateKeyEncoding: { type: 'pkcs8', format: 'pem' }
  });
  console.log("Cryptographic key pair generated.");
}

// 1. Endpoint: Retrieve Public Key (Open Profile Registry)
app.get('/api/v1/profile/public-key', (req, res) => {
  if (!keyPair) return res.status(500).json({ error: "Keys not initialized." });
  res.json({
    algorithm: "Ed25519",
    publicKey: keyPair.publicKey
  });
});

// 2. Endpoint: Sign Profile Payload / Metadata
app.post('/api/v1/profile/sign', (req, res) => {
  try {
    const { profileData } = req.body;
    
    if (!profileData) {
      return res.status(400).json({ error: "Missing profileData payload." });
    }

    // Standardize input string (canonical JSON) to ensure signature consistency
    const serializedData = JSON.stringify(profileData);
    const dataBuffer = Buffer.from(serializedData);

    // Sign payload using private key
    const signatureBuffer = crypto.sign(null, dataBuffer, keyPair.privateKey);
    const signatureBase64 = signatureBuffer.toString('base64');

    res.json({
      status: "signed",
      algorithm: "Ed25519",
      payload: profileData,
      signature: signatureBase64,
      timestamp: new Date().toISOString()
    });
  } catch (err) {
    res.status(500).json({ error: "Signing process failed", details: err.message });
  }
});

// 3. Endpoint: Verify Digital Signature
app.post('/api/v1/profile/verify', (req, res) => {
  try {
    const { profileData, signature, publicKey } = req.body;

    if (!profileData || !signature) {
      return res.status(400).json({ error: "Missing required fields for verification." });
    }

    // Use provided public key or fall back to local key
    const keyToUse = publicKey || keyPair.publicKey;
    const serializedData = JSON.stringify(profileData);
    const dataBuffer = Buffer.from(serializedData);
    const signatureBuffer = Buffer.from(signature, 'base64');

    // Verify signature against payload and public key
    const isValid = crypto.verify(null, dataBuffer, keyToUse, signatureBuffer);

    res.json({
      verified: isValid,
      message: isValid ? "Signature is valid. Data integrity confirmed." : "Invalid signature or altered data."
    });
  } catch (err) {
    res.status(500).json({ error: "Verification failed", details: err.message });
  }
});

// Start Server
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  initializeKeys();
  console.log(`Open Profile Signature API running on port ${PORT}`);
});
