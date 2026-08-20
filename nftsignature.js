const express = require('express');
const crypto = require('crypto');

const app = express();
app.use(express.json());

// Pull private key securely from the environment
const PRIVATE_KEY_PEM = process.env.SIGNING_PRIVATE_KEY;

app.post('/api/v1/profile/sign', (req, res) => {
  try {
    const { profileData } = req.body;
    if (!profileData) return res.status(400).json({ error: "Missing payload" });

    // Format key if needed and sign
    const privateKey = crypto.createPrivateKey(PRIVATE_KEY_PEM);
    const dataBuffer = Buffer.from(JSON.stringify(profileData));
    
    const signature = crypto.sign(null, dataBuffer, privateKey).toString('base64');

    res.json({
      status: "signed",
      payload: profileData,
      signature: signature
    });
  } catch (err) {
    res.status(500).json({ error: "Signing failed", details: err.message });
  }
});
