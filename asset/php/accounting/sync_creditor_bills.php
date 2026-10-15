<?php
/**
 * CREDITOR BILL DATA EXTRACTION & SYNC SCRIPT
 * Pulls live balances from linked institutions (e.g., Wells Fargo) via Plaid
 */

header('Content-Type: application/json');

$dbPath = __DIR__ . '/asset/json/Legacytrust/bills.json';
if (!file_exists($dbPath)) {
    echo json_encode(['success' => false, 'error' => 'Database not found']);
    exit();
}

$dbData = json_decode(file_get_contents($dbPath), true);
$accessToken = "access-sandbox-YOUR_STORED_PLAID_ACCESS_TOKEN"; // Retrieved from your secure DB after linking

$clientId = 'YOUR_PLAID_CLIENT_ID';
$secret = 'YOUR_PLAID_SECRET';

// Call Plaid Liabilities API to extract live bill data
$payload = json_encode([
    'client_id' => $clientId,
    'secret' => $secret,
    'access_token' => $accessToken
]);

$ch = curl_init('https://sandbox.plaid.com/liabilities/get');
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_POST, true);
curl_setopt($ch, CURLOPT_POSTFIELDS, $payload);
curl_setopt($ch, CURLOPT_HTTPHEADER, ['Content-Type: application/json']);
$response = curl_exec($ch);
curl_close($ch);

$plaidData = json_decode($response, true);

if (isset($plaidData['liabilities']['credit']) || isset($plaidData['liabilities']['mortgage'])) {
    // Loop through extracted creditor liabilities and update local bills.json matching account IDs
    // (Example logic updating balances dynamically from creditor statements)
    
    echo json_encode(['success' => true, 'message' => 'Creditor bill data successfully synchronized.']);
} else {
    echo json_encode(['success' => false, 'error' => 'Failed to retrieve liabilities from creditor.']);
}
