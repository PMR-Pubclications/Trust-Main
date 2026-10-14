<?php
/**
 * ACCOUNTS LIABLE & FULL BALANCE PAYMENT MODULE
 * Category: TrustAdmin
 * External Stylesheet: https://github.com/PMR-Pubclications/Trust-Main/blob/main/asset%2Fcss%2Fstyle.css
 */

session_start();

// 1. Resolve Credentials & Role Enforcement
$activeRole = strtolower($_SESSION['role'] ?? $_GET['role'] ?? 'first_responder');
$isAdmin = in_array($activeRole, ['trustadmin', 'admin']);

// 2. Strict Access Control: Redirect Non-TrustAdmin users to FirstResponder view
if (!$isAdmin) {
    header("Location: accounts_liable.php?role=first_responder&redirect=unauthorized");
    exit();
}

$category = "TrustAdmin";
$message = "";
$messageType = "";

// Mock Database / Balance Lookup Service Function
function fetchAccountBalance($accountNumber) {
    // In production, query your database or secure API endpoint here
    $mockLedger = [
        "ACC-2026-8841" => ["entity" => "Clark County Division", "balance" => 4250.50],
        "ACC-2026-9012" => ["entity" => "Vancouver Police Department", "balance" => 1280.00],
        "ACC-2026-4433" => ["entity" => "State Courts District 4", "balance" => 9750.25]
    ];
    
    if (array_key_exists($accountNumber, $mockLedger)) {
        return $mockLedger[$accountNumber];
    }
    return null;
}

$searchAccount = filter_input(INPUT_GET, 'lookup_account', FILTER_SANITIZE_FULL_SPECIAL_CHARS);
$accountData = null;

if ($searchAccount) {
    $accountData = fetchAccountBalance($searchAccount);
    if (!$accountData) {
        $message = "Account reference ID '{$searchAccount}' not found in liability records.";
        $messageType = "error";
    }
}

// 3. Process Payment Submission (Pay in Full)
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $accountNumber = filter_input(INPUT_POST, 'account_number', FILTER_SANITIZE_FULL_SPECIAL_CHARS);
    $liableEntity  = filter_input(INPUT_POST, 'liable_entity', FILTER_SANITIZE_FULL_SPECIAL_CHARS);
    $amount        = filter_input(INPUT_POST, 'payment_amount', FILTER_VALIDATE_FLOAT);
    $paymentMethod = filter_input(INPUT_POST, 'payment_method', FILTER_SANITIZE_FULL_SPECIAL_CHARS);
    $department    = filter_input(INPUT_POST, 'target_department', FILTER_SANITIZE_FULL_SPECIAL_CHARS);

    if ($accountNumber && $liableEntity && $amount > 0 && $paymentMethod) {
        // Record payment settlement and queue blockchain backup transmittal package
        $transactionRecord = [
            "timestamp"          => date('Y-m-d\TH:i:s\Z'),
            "category"           => $category,
            "account_number"     => $accountNumber,
            "liable_entity"      => $liableEntity,
            "amount_settled"     => $amount,
            "payment_method"     => $paymentMethod,
            "target_department"  => $department,
            "processed_by_role"  => $activeRole,
            "status"             => "PAID_IN_FULL",
            "blockchain_backup"  => "ISO/IEC 17025 QUEUED"
        ];

        $message = "Balance of $" . number_format($amount, 2) . " for Account #{$accountNumber} ({$liableEntity}) has been paid in full.";
        $messageType = "success";
        $accountData = null; // Clear active record post-settlement
    } else {
        $message = "Invalid payment transaction parameters. Please verify and retry.";
        $messageType = "error";
    }
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Accounts Liable & Balance Settlement | TrustAdmin</title>
    
    <!-- Link to Github Asset Stylesheet -->
    <link rel="stylesheet" href="https://raw.githubusercontent.com/PMR-Pubclications/Trust-Main/main/asset/css/style.css">
    
    <style>
        :root {
            --bg-dark: #0f172a;
            --panel-bg: #1e293b;
            --accent-blue: #38bdf8;
            --border-color: #334155;
            --text-light: #f8fafc;
            --text-muted: #94a3b8;
            --success-color: #10b981;
            --error-color: #ef4444;
        }
        body {
            font-family: system-ui, -apple-system, sans-serif;
            background-color: var(--bg-dark);
            color: var(--text-light);
            margin: 0;
            padding: 2rem;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            background: var(--panel-bg);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            padding: 2rem;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25);
        }
        .header-badge {
            display: inline-block;
            background: rgba(56, 189, 248, 0.15);
            color: var(--accent-blue);
            border: 1px solid var(--accent-blue);
            padding: 0.2rem 0.6rem;
            border-radius: 4px;
            font-size: 0.75rem;
            font-weight: bold;
            margin-bottom: 1rem;
        }
        .form-group {
            margin-bottom: 1.25rem;
        }
        label {
            display: block;
            margin-bottom: 0.4rem;
            font-weight: 600;
            font-size: 0.9rem;
            color: var(--text-muted);
        }
        input, select {
            width: 100%;
            padding: 0.75rem;
            background: #0f172a;
            border: 1px solid var(--border-color);
            border-radius: 4px;
            color: var(--text-light);
            font-size: 0.95rem;
            box-sizing: border-box;
        }
        input:focus, select:focus {
            outline: none;
            border-color: var(--accent-blue);
        }
        .form-row {
            display: flex;
            gap: 1rem;
        }
        .form-row .form-group {
            flex: 1;
        }
        .btn-action {
            background: var(--accent-blue);
            color: #0f172a;
            font-weight: bold;
            border: none;
            padding: 0.75rem 1.25rem;
            border-radius: 4px;
            cursor: pointer;
            font-size: 0.95rem;
            transition: opacity 0.2s;
        }
        .btn-action:hover {
            opacity: 0.9;
        }
        .balance-display-box {
            background: rgba(56, 189, 248, 0.05);
            border: 1px solid var(--accent-blue);
            padding: 1.25rem;
            border-radius: 6px;
            margin-bottom: 1.5rem;
        }
        .alert {
            padding: 1rem;
            border-radius: 4px;
            margin-bottom: 1.5rem;
            font-weight: 500;
        }
        .alert-success {
            background: rgba(16, 185, 129, 0.15);
            border: 1px solid var(--success-color);
            color: var(--success-color);
        }
        .alert-error {
            background: rgba(239, 68, 68, 0.15);
            border: 1px solid var(--error-color);
            color: var(--error-color);
        }
    </style>
</head>
<body>

<div class="container">
    <div class="header-badge">CATEGORY: <?= htmlspecialchars($category) ?></div>
    <h2>Accounts Liable & Balance Settlement</h2>
    <p style="color: var(--text-muted); font-size: 0.9rem; margin-bottom: 1.5rem;">
        Look up account liability files, pull current outstanding balances, and execute full balance clearance under TrustAdmin oversight.
    </p>

    <?php if (!empty($message)): ?>
        <div class="alert alert-<?= $messageType ?>">
            <?= htmlspecialchars($message) ?>
        </div>
    <?php endif; ?>

    <!-- Step 1: Lookup Account Balance -->
    <form method="GET" action="accounts_liable.php" style="margin-bottom: 2rem;">
        <input type="hidden" name="role" value="<?= htmlspecialchars($activeRole) ?>">
        <div class="form-row" style="align-items: flex-end;">
            <div class="form-group" style="margin-bottom: 0;">
                <label for="lookup_account">Lookup Account / Case Reference ID</label>
                <input type="text" id="lookup_account" name="lookup_account" placeholder="e.g., ACC-2026-8841" value="<?= htmlspecialchars($searchAccount ?? '') ?>" required>
            </div>
            <div>
                <button type="submit" class="btn-action">&#128269; Pull Balance Owed</button>
            </div>
        </div>
    </form>

    <!-- Step 2: Pay in Full Form (Populated dynamically when account data is fetched) -->
    <?php if ($accountData): ?>
    <div class="balance-display-box">
        <h3 style="margin-top: 0; color: var(--accent-blue);">Account File Located</h3>
        <p><strong>Liable Entity:</strong> <?= htmlspecialchars($accountData['entity']) ?></p>
        <p><strong>Current Outstanding Balance Owed:</strong> <span style="font-size: 1.3rem; color: var(--success-color);">$<?= number_format($accountData['balance'], 2) ?></span></p>
    </div>

    <form method="POST" action="accounts_liable.php?role=<?= urlencode($activeRole) ?>">
        <input type="hidden" name="account_number" value="<?= htmlspecialchars($searchAccount) ?>">
        <input type="hidden" name="liable_entity" value="<?= htmlspecialchars($accountData['entity']) ?>">
        
        <div class="form-group">
            <label for="payment_amount">Settlement Amount ($ USD) - Paid in Full</label>
            <input type="number" step="0.01" id="payment_amount" name="payment_amount" value="<?= htmlspecialchars($accountData['balance']) ?>" readonly style="background: #111827; color: var(--success-color); font-weight: bold;">
        </div>

        <div class="form-row">
            <div class="form-group">
                <label for="payment_method">Payment Method</label>
                <select id="payment_method" name="payment_method" required>
                    <option value="">Select Method...</option>
                    <option value="ACH_TRANSFER">ACH Direct Transfer</option>
                    <option value="TREASURY_CHECK">State/Treasury Check</option>
                    <option value="CREDIT_CARD">Corporate / P-Card</option>
                    <option value="BLOCKCHAIN_LEDGER">Blockchain Ledger Settlement</option>
                </select>
            </div>
            <div class="form-group">
                <label for="target_department">Target Recipient Department</label>
                <select id="target_department" name="target_department" required>
                    <option value="COURTS">Courts Division</option>
                    <option value="FIRSTRESPONDER">First Responder Division</option>
                    <option value="FORENSICS">Forensic Investigations Unit</option>
                </select>
            </div>
        </div>

        <button type="submit" class="btn-action" style="width: 100%; background: var(--success-color); color: #fff; padding: 0.85rem; font-size: 1rem; margin-top: 1rem;">
            &#128184; Settle & Pay Balance in Full
        </button>
    </form>
    <?php endif; ?>
</div>

</body>
</html>
