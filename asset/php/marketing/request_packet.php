<?php
/**
 * TRUST-MAIN ON-DEMAND AGENCY INVITATION ENDPOINT
 * Allows first responder and hospital IT leads to instantly request a 
 * secure deployment and verification packet.
 */
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $email = filter_var($_POST['agency_email'] ?? '', FILTER_VALIDATE_EMAIL);
    $agencyName = htmlspecialchars($_POST['agency_name'] ?? 'Emergency Services');

    if ($email) {
        $subject = "[Trust-Main] Secure Deployment & Verification Packet";
        $message = "
        <html>
        <body style='font-family:sans-serif; background:#090d16; color:#f3f4f6; padding:20px;'>
            <div style='max-width:600px; background:#111827; padding:25px; border-radius:8px; border:1px solid #38bdf8;'>
                <h2 style='color:#38bdf8;'>Deployment Packet for {$agencyName}</h2>
                <p>Thank you for requesting direct open-source access to <strong>Trust-Main</strong>.</p>
                <p>You can install the field console instantly as a Progressive Web App (PWA) or audit the core repository below:</p>
                <ul>
                    <li><a href='https://patriotsmustrise.org/whitepaper.php' style='color:#38bdf8;'>Technical White Paper & Specifications</a></li>
                    <li><a href='https://github.com/PMR-Pubclications/Trust-Main' style='color:#38bdf8;'>Auditable GitHub Codebase</a></li>
                </ul>
                <p><em>PMR Publications Institutional Support</em></p>
            </div>
        </body>
        </html>
        ";

        $headers  = "MIME-Version: 1.0\r\n";
        $headers .= "Content-type: text/html; charset=UTF-8\r\n";
        $headers .= "From: Trust-Main Dispatch <dispatch@patriotsmustrise.org>\r\n";

        mail($email, $subject, $message, $headers);
        $successMessage = "Deployment packet successfully dispatched to " . htmlspecialchars($email);
    } else {
        $errorMessage = "Please provide a valid institutional email address.";
    }
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Request Trust-Main Deployment Packet</title>
    <style>
        body { font-family: sans-serif; background: #090d16; color: #f3f4f6; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
        .form-box { background: #111827; border: 1px solid rgba(56,189,248,0.3); padding: 30px; border-radius: 8px; width: 100%; max-width: 400px; }
        input { width: 100%; padding: 10px; margin: 10px 0; background: #1f2937; border: 1px solid #374151; color: #fff; border-radius: 4px; box-sizing: border-box; }
        button { width: 100%; background: #0284c7; color: #fff; border: none; padding: 12px; font-weight: bold; border-radius: 4px; cursor: pointer; }
        button:hover { background: #0369a1; }
        .msg { color: #38bdf8; font-size: 0.9rem; margin-bottom: 10px; }
        .err { color: #f87171; font-size: 0.9rem; margin-bottom: 10px; }
    </style>
</head>
<body>
<div class="form-box">
    <h2 style="color:#38bdf8; margin-top:0;">Request Deployment Packet</h2>
    <?php if (!empty($successMessage)): ?><div class="msg"><?= $successMessage ?></div><?php endif; ?>
    <?php if (!empty($errorMessage)): ?><div class="err"><?= $errorMessage ?></div><?php endif; ?>
    <form method="POST">
        <label>Agency / Hospital Name:</label>
        <input type="text" name="agency_name" required placeholder="e.g. Vancouver Police Dept">
        <label>Institutional Email:</label>
        <input type="email" name="agency_email" required placeholder="admin@agency.gov">
        <button type="submit">Send Deployment Packet</button>
    </form>
require_once __DIR__ . '/includes/AuditLedger.php';
$ledger = new AuditLedger();

// Log the outreach event to the immutable chain
$auditHash = $ledger->logEvent('ANNUAL_OUTREACH_TRANSMISSION', [
    'version' => $appVersion,
    'recipients_notified' => $successCount,
    'status' => 'COMPLETED'
]);

</div>
</body>
</html>
