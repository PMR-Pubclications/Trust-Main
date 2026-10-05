<?php
/**
 * Trust Administrator - Automated Accounts Sweep & Payment Cron Routine
 * Path: trust-main/cron-process-accounts.php
 * 
 * Clearance Level: SOLE TRUST ADMIN / AUTOMATED SYSTEM CRON
 * Execution: CLI or Authorized Webhook Trigger
 * Schedule: Recommended Daily Cron (e.g., 0 0 * * *)
 */

// 1. Security Check (CLI or Auth Key)
$isCli = (php_sapi_name() === 'cli');
$cronSecret = $_GET['key'] ?? '';
$expectedSecret = 'TRUST_ADMIN_CRON_KEY_2026'; // Custom access token for web triggers

if (!$isCli && $cronSecret !== $expectedSecret) {
    http_response_code(403);
    header('Content-Type: text/plain');
    echo "[CRON ERROR 403] UNAUTHORIZED EXECUTION ATTEMPT.\n";
    exit;
}

if (!$isCli) {
    header('Content-Type: text/plain; charset=utf-8');
}

// 2. Data Paths
$dataDir     = __DIR__ . '/data';
$accountsFile = $dataDir . '/automated_accounts.json';
$auditLogFile = $dataDir . '/sha256_verify.log';

echo "====================================================================\n";
echo " TRUST-MAIN // AUTOMATED PAYMENT & YIELD SWEEP CRON ENGINE         \n";
echo " TIMESTAMP: " . date('Y-m-d H:i:s T') . "\n";
echo "====================================================================\n\n";

if (!file_exists($accountsFile)) {
    echo "[!] NO ACCOUNTS FILE FOUND AT: {$accountsFile}\n";
    echo "[!] ABORTING ROUTINE.\n";
    exit;
}

// 3. Load Ledger
$accountsJson = file_get_contents($accountsFile);
$accounts     = json_decode($accountsJson, true) ?? [];

if (empty($accounts)) {
    echo "[*] AUTOMATED LEDGER IS EMPTY. NO TRANSACTIONS PENDING.\n";
    exit;
}

$today        = date('Y-m-d');
$processed    = 0;
$skipped      = 0;
$totalAmount  = 0.00;
$logEntries   = [];

// 4. Processing Engine Routine
foreach ($accounts as &$acc) {
    $accId       = $acc['id'] ?? 'UNKNOWN';
    $type        = $acc['type'] ?? 'RECEIVABLE';
    $entity      = $acc['entity_name'] ?? 'UNKNOWN';
    $amount      = floatval($acc['amount'] ?? 0);
    $frequency   = $acc['frequency'] ?? 'MONTHLY';
    $nextRun     = $acc['next_run'] ?? $today;
    $status      = $acc['status'] ?? 'AUTOMATED';
    $method      = $acc['execution_type'] ?? 'ACH_SWEEP';

    // Skip inactive or future scheduled items
    if ($status !== 'AUTOMATED' || $nextRun > $today) {
        $skipped++;
        echo "[-] SKIPPED: [{$accId}] {$entity} - Next Due: {$nextRun}\n";
        continue;
    }

    echo "[+] PROCESSING: [{$accId}] ({$type}) {$entity} | \${$amount} via {$method}...\n";

    // Simulate Transaction Hash Generation (SHA-256)
    $txPayload = json_encode([
        'acc_id'    => $accId,
        'type'      => $type,
        'amount'    => $amount,
        'method'    => $method,
        'timestamp' => microtime(true)
    ]);
    $txHash = hash('sha256', $txPayload);

    // Calculate Next Execution Date
    $currentDateObj = new DateTime($nextRun);
    switch ($frequency) {
        case 'DAILY':
            $currentDateObj->modify('+1 day');
            break;
        case 'WEEKLY':
            $currentDateObj->modify('+1 week');
            break;
        case 'BI_WEEKLY':
            $currentDateObj->modify('+2 weeks');
            break;
        case 'MONTHLY':
            $currentDateObj->modify('+1 month');
            break;
        case 'QUARTERLY':
            $currentDateObj->modify('+3 months');
            break;
        case 'AUTO_SWEEP':
            // Immediate re-arm for next daily check
            $currentDateObj->modify('+1 day');
            break;
        default:
            $currentDateObj->modify('+1 month');
            break;
    }

    $newNextRun = $currentDateObj->format('Y-m-d');
    $acc['last_run'] = $today;
    $acc['next_run'] = $newNextRun;

    $processed++;
    $totalAmount += $amount;

    // Log telemetry
    $logLine = sprintf(
        "[%s] TX_HASH:%s | ID:%s | TYPE:%s | ENTITY:%s | AMT:\$%.2f | METHOD:%s | NEXT_DUE:%s\n",
        date('Y-m-d H:i:s'),
        substr($txHash, 0, 16) . '...',
        $accId,
        $type,
        $entity,
        $amount,
        $method,
        $newNextRun
    );

    $logEntries[] = $logLine;
    echo "    --> SUCCESS! TX_HASH: " . substr($txHash, 0, 24) . "...\n";
    echo "    --> NEXT RUN SCHEDULED: {$newNextRun}\n\n";
}

// Unset reference variable
unset($acc);

// 5. Commit Ledger Updates & Audit Logs
if ($processed > 0) {
    file_put_contents($accountsFile, json_encode($accounts, JSON_PRETTY_PRINT));
    
    // Append to sha256_verify.log
    $logData = implode('', $logEntries);
    file_put_contents($auditLogFile, $logData, FILE_APPEND);
}

echo "====================================================================\n";
echo " EXECUTION SUMMARY\n";
echo "--------------------------------------------------------------------\n";
echo " PROCESSED TRANSACTIONS : {$processed}\n";
echo " SKIPPED TRANSACTIONS   : {$skipped}\n";
echo " TOTAL VOLUME MOVED     : \$" . number_format($totalAmount, 2) . "\n";
echo " AUDIT LOG UPDATED      : {$auditLogFile}\n";
echo "====================================================================\n";
