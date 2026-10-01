const fs = require('fs');
const crypto = require('crypto');

// 1. Load the immutable policy whitelist and incoming transaction record
const whitelist = JSON.parse(fs.readFileSync('./authorized-whitelist.json', 'utf8'));
const transaction = JSON.parse(fs.readFileSync('./incoming-transaction.json', 'utf8'));

console.log(`[AUDIT] Evaluating transaction ID: ${transaction.id} for amount: $${transaction.amount}`);

// 2. Rule Check 1: Verify transaction amount limit
if (transaction.amount > whitelist.max_single_transaction_limit) {
  securityViolation(`REJECTED: Transaction amount $${transaction.amount} exceeds maximum allowed limit of $${whitelist.max_single_transaction_limit}.`);
}

// 3. Rule Check 2: Verify destination whitelist status
const destinationMatch = whitelist.approved_destinations.find(
  (dest) => dest.identifier === transaction.destination_identifier
);

if (!destinationMatch) {
  securityViolation(`REJECTED: Unauthorized destination identifier '${transaction.destination_identifier}' not found in whitelist.`);
}

if (!destinationMatch.allow_withdrawals) {
  securityViolation(`REJECTED: Destination '${destinationMatch.name}' is explicitly locked against outgoing withdrawals.`);
}

// 4. Rule Check 3: Cryptographic Signature Verification (Ensuring the payload wasn't forged)
try {
  const publicKeyPem = "-----BEGIN PUBLIC KEY-----\nYOUR_PUBLIC_KEY_HERE\n-----END PUBLIC KEY---------";
  const verified = crypto.verify(
    null,
    Buffer.from(JSON.stringify(transaction.payload)),
    crypto.createPublicKey(publicKeyPem),
    Buffer.from(transaction.signature, 'base64')
  );

  if (!verified) {
    securityViolation("REJECTED: Cryptographic signature verification failed. Possible payload tampering.");
  }
} catch (err) {
  securityViolation(`REJECTED: Cryptographic error during verification: ${err.message}`);
}

// If all checks pass
console.log("[AUDIT] SUCCESS: Transaction complies with all trust boundaries and is cryptographically verified.");
process.exit(0);

// Helper function to handle security violations
function securityViolation(reason) {
  console.error(`[SECURITY ALERT] ${reason}`);
  
  // Create an automated incident log for your GitHub repository record
  const incidentLog = {
    timestamp: new Date().toISOString(),
    transaction_id: transaction.id,
    violation_reason: reason,
    status: "BLOCKED"
  };
  
  fs.writeFileSync(`./security-incident-${Date.now()}.json`, JSON.stringify(incidentLog, null, 2));
  
  // Exit with error code to halt GitHub Actions or server pipeline
  process.exit(1);
}
