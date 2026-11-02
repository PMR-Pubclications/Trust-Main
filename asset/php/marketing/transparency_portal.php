<?php
/**
 * TRUST-MAIN INSTITUTIONAL TRANSPARENCY & AUDIT PORTAL
 * Allows department IT leads to verify ledger integrity and review open-source code specs.
 */
require_once __DIR__ . '/includes/AuditLedger.php';

$ledger = new AuditLedger();
$isLedgerValid = $ledger->verifyLedger();

$configFile = __DIR__ . '/config/config.yaml';
$config = [];
if (file_exists($configFile) && function_exists('yaml_parse_file')) {
    $config = yaml_parse_file($configFile);
}

$appName    = $config['app_name'] ?? 'Trust-Main';
$appVersion = $config['version'] ?? '1.2';
$labId      = $config['system']['lab_id'] ?? 'MOBILE_LAB_01';
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title><?= htmlspecialchars($appName) ?> — Institutional Transparency & Audit</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #090d16; color: #f3f4f6; margin: 0; padding: 2rem; }
        .container { max-width: 900px; margin: 0 auto; background: #111827; border: 1px solid rgba(56,189,248,0.3); border-radius: 8px; padding: 2.5rem; }
        h1 { color: #38bdf8; border-bottom: 2px solid #38bdf8; padding-bottom: 10px; margin-top: 0; }
        .status-badge { display: inline-block; padding: 8px 16px; border-radius: 4px; font-weight: bold; font-family: monospace; margin: 15px 0; }
        .status-valid { background: rgba(16, 185, 129, 0.2); color: #34d399; border: 1px solid #34d399; }
        .status-invalid { background: rgba(239, 68, 68, 0.2); color: #f87171; border: 1px solid #f87171; }
        .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-top: 20px; }
        .card { background: #1f2937; padding: 20px; border-radius: 6px; border: 1px solid rgba(255,255,255,0.05); }
        .card h3 { color: #38bdf8; margin-top: 0; }
        a { color: #38bdf8; text-decoration: none; }
        a:hover { text-decoration: underline; }
    </style>
</head>
<body>
<div class="container">
    <h1>Institutional Transparency Portal</h1>
    <p>Welcome to the public transparency verification console for <strong><?= htmlspecialchars($appName) ?></strong>. This interface provides municipal IT auditors and agency leads with real-time verification of system integrity, cryptographic ledger status, and source code availability.</p>

    <div>
        <strong>Ledger Cryptographic Status:</strong><br>
        <?php if ($isLedgerValid): ?>
            <div class="status-badge status-valid">SECURE: SHA-256 Audit Chain Intact (Zero Tampering Detected)</div>
        <?php else: ?>
            <div class="status-badge status-invalid">WARNING: Ledger Chain Integrity Violation Detected</div>
        <?php endif; ?>
    </div>

    <div class="grid">
        <div class="card">
            <h3>System Specifications</h3>
            <p><strong>Active Version:</strong> v<?= htmlspecialchars($appVersion) ?></p>
            <p><strong>Assigned Lab ID:</strong> <?= htmlspecialchars($labId) ?></p>
            <p><strong>Compliance Standards:</strong> ISO/IEC 17025, NIBRS, NFIRS, HL7 FHIR</p>
        </div>
        <div class="card">
            <h3>Codebase & Auditing</h3>
            <p>Review the complete, unencrypted source code to verify absence of proprietary trackers:</p>
            <p><a href="https://github.com/PMR-Pubclications/Trust-Main" target="_blank">GitHub Repository ↗</a></p>
            <p><a href="whitepaper.php">Technical White Paper ↗</a></p>
        </div>
    </div>

    <div style="margin-top: 30px; font-size: 0.85rem; color: #9ca3af; text-align: center;">
        PMR Publications Independent Verification Framework | Powered by Trust-Main Core Engine
    </div>
</div>
</body>
</html>
