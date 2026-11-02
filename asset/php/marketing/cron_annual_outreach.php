<?php
/**
 * TRUST-MAIN ANNUAL INSTITUTIONAL OUTREACH & LEDGER AUTOMATION
 * Scheduled Execution: January 2
 * Purpose: Broadcasts free, hands-free mobile forensic lab deployment to 
 *          first responders/hospitals and commits a verifiable audit trail to the ledger.
 */

// ============================================================================
// 1. LOAD SYSTEM CONFIGURATION & METADATA SOURCE OF TRUTH
// ============================================================================
$configFile = __DIR__ . '/config/config.yaml';
$config = [];
if (file_exists($configFile) && function_exists('yaml_parse_file')) {
    $config = yaml_parse_file($configFile);
}

$appName      = $config['app_name'] ?? 'Trust-Main';
$appVersion   = $config['version'] ?? '1.2';
$labId        = $config['system']['lab_id'] ?? 'MOBILE_LAB_01';
$downloadUrl  = "https://github.com/PMR-Pubclications/Trust-Main";
$whitepaperUrl = "https://patriotsmustrise.org/whitepaper.php";

// ============================================================================
// 2. CONNECT TO INSTITUTIONAL CONTACT DATABASE
// ============================================================================
$dbHost = 'localhost';
$dbUser = 'trust_admin';
$dbPass = getenv('DB_PASS') ?: '';
$dbName = 'trust_main_institutions';

$recipients = [];
try {
    $pdo = new PDO("mysql:host=$dbHost;dbname=$dbName;charset=utf8mb4", $dbUser, $dbPass, [
        PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION
    ]);

    // Fetch verified First Responder & Hospital contact records
    $stmt = $pdo->query("SELECT institution_name, contact_name, email, agency_type FROM agency_contacts WHERE status = 'active'");
    $recipients = $stmt->fetchAll(PDO::FETCH_ASSOC);

} catch (Exception $e) {
    error_log("Database connection failed for annual outreach: " . $e->getMessage());
    exit("Outreach halted: Unable to access institutional contact database.");
}

// ============================================================================
// 3. EMAIL DISPATCH LOOP
// ============================================================================
$successCount = 0;
$failCount = 0;

foreach ($recipients as $recipient) {
    $toName     = $recipient['contact_name'] ?? 'Agency Administrator';
    $toEmail    = $recipient['email'];
    $instName   = $recipient['institution_name'] ?? 'Emergency Services';
    $agencyType = strtoupper($recipient['agency_type'] ?? 'FIRST RESPONDER');

    $subject = "[$appName v$appVersion] Complimentary Zero-Cost Deployment: Trust Forensics Mobile Lab ({$agencyType})";

    $emailBody = '
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #090d16; color: #f3f4f6; margin: 0; padding: 20px; }
            .container { max-width: 650px; margin: 0 auto; background: #111827; border: 1px solid rgba(56, 189, 248, 0.3); border-radius: 8px; padding: 30px; }
            h1 { color: #38bdf8; font-size: 22px; margin-top: 0; border-bottom: 2px solid #38bdf8; padding-bottom: 10px; }
            .highlight-box { background: rgba(56, 189, 248, 0.08); border-left: 4px solid #38bdf8; padding: 15px; margin: 20px 0; font-size: 14px; }
            .stat-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin: 20px 0; }
            .stat-card { background: #1f2937; padding: 15px; border-radius: 6px; text-align: center; }
            .stat-num { font-size: 20px; font-weight: bold; color: #38bdf8; }
            .btn { display: inline-block; background: #0284c7; color: #ffffff; padding: 12px 24px; text-decoration: none; border-radius: 4px; font-weight: bold; margin-top: 15px; }
            .footer { margin-top: 30px; border-top: 1px solid rgba(255,255,255,0.1); font-size: 12px; color: #9ca3af; text-align: center; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Official Notice: Trust Forensics Mobile Lab Deployment</h1>
            <p>Dear <strong>' . htmlspecialchars($toName) . '</strong>,</p>
            <p>As municipal agencies enter the new operational year, budgeting constraints and administrative overhead continue to strain emergency services and healthcare networks. For <strong>' . htmlspecialchars($instName) . '</strong>, we are officially announcing the annual open-source deployment window for <strong>' . htmlspecialchars($appName) . ' v' . htmlspecialchars($appVersion) . '</strong>.</p>
            
            <div class="highlight-box">
                <strong>Zero Commercial Cost:</strong> The Trust Forensics ecosystem is provided entirely free of charge for authorized law enforcement, fire, EMS, DOT, and hospital networks, bypassing commercial app stores and licensing fees entirely.
            </div>

            <p>Designed for field-active personnel, the <strong>Trust Forensics Mobile Lab</strong> integrates voice-activated, <strong>completely hands-free</strong> operations tailored for high-stress incident environments—allowing first responders and clinical staff to log evidence, execute NIBRS/NFIRS/HL7 FHIR compliant reports, and coordinate dispatch without touching a screen.</p>

            <div class="stat-grid">
                <div class="stat-card">
                    <div class="stat-num">100% Free</div>
                    <div>Zero Licensing & Store Fees</div>
                </div>
                <div class="stat-card">
                    <div class="stat-num">Hands-Free</div>
                    <div>Voice-Activated Tactical AI</div>
                </div>
            </div>

            <p><strong>Measurable Time & Cost Savings:</strong></p>
            <ul>
                <li><strong>Eliminate Administrative Backlogs:</strong> Automated blockchain-backed chain of custody reduces report compilation time from hours to minutes.</li>
                <li><strong>Offline Field Resilience:</strong> Deploys instantly as a Progressive Web App (PWA) on existing hardware, maintaining secure local databases even in disconnected zones.</li>
                <li><strong>ISO/IEC 17025 Compliance:</strong> Standardized forensic formatting ready for immediate judicial presentation without proprietary software vendor lock-in.</li>
            </ul>

            <center>
                <a href="' . htmlspecialchars($whitepaperUrl) . '" class="btn">Review Technical White Paper</a> &nbsp; 
                <a href="' . htmlspecialchars($downloadUrl) . '" class="btn" style="background: #1f2937; border: 1px solid #38bdf8;">Access Auditable Codebase</a>
            </center>

            <div class="footer">
                <p>Generated automatically by ' . htmlspecialchars($appName) . ' Core Engine (' . htmlspecialchars($labId) . ')<br>PMR Publications Institutional Outreach Initiative</p>
            </div>
        </div>
    </body>
    </html>
    ';

    $headers  = "MIME-Version: 1.0\r\n";
    $headers .= "Content-type: text/html; charset=UTF-8\r\n";
    $headers .= "From: Trust-Main Deployments <dispatch@patriotsmustrise.org>\r\n";
    $headers .= "Reply-To: support@patriotsmustrise.org\r\n";

    if (mail($toEmail, $subject, $emailBody, $headers)) {
        $successCount++;
    } else {
        $failCount++;
    }
}

// ============================================================================
// 4. BLOCKCHAIN AUDIT LEDGER REGISTRATION (TRANSPARENCY HASH)
// ============================================================================
$executionTimestamp = date('Y-m-d\TH:i:s\Z');
$auditPayload = [
    'event'                => 'ANNUAL_INSTITUTIONAL_OUTREACH',
    'timestamp'            => $executionTimestamp,
    'lab_id'               => $labId,
    'system_version'       => $appVersion,
    'recipients_contacted' => $successCount,
    'recipients_failed'    => $failCount,
    'status'               => 'TRANSMITTED_AND_LOGGED'
];

$payloadJson = json_encode($auditPayload, JSON_UNESCAPED_SLASHES);
$auditHash   = hash('sha256', $payloadJson);

// Write ledger entry to local storage / blockchain sync queue
$ledgerLogFile = __DIR__ . '/logs/blockchain_ledger_audit.log';
$ledgerEntry = json_encode([
    'hash' => $auditHash,
    'data' => $auditPayload
]) . PHP_EOL;

if (!is_dir(__DIR__ . '/logs')) {
    mkdir(__DIR__ . '/logs', 0755, true);
}
file_put_contents($ledgerLogFile, $ledgerEntry, FILE_APPEND | LOCK_EX);

// Output execution summary
echo "Annual Outreach Completed. Sent: {$successCount}, Failed: {$failCount}. Audit Hash Registered: {$auditHash}";


require_once __DIR__ . '/includes/AuditLedger.php';
$ledger = new AuditLedger();

// Log the outreach event to the immutable chain
$auditHash = $ledger->logEvent('ANNUAL_OUTREACH_TRANSMISSION', [
    'version' => $appVersion,
    'recipients_notified' => $successCount,
    'status' => 'COMPLETED'
]);
