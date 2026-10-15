<?php
/**
 * LIVE ACCOUNTS LIABLE & BILLING GATEWAY
 * Category: TrustAdmin
 * Database Source: asset/json/Legacytrust/bills.json
 */

session_start();

$activeRole = strtolower($_SESSION['role'] ?? $_GET['role'] ?? 'first_responder');
$isAdmin = in_array($activeRole, ['trustadmin', 'admin']);

if (!$isAdmin) {
    header("Location: accounts_liable.php?role=first_responder&redirect=unauthorized");
    exit();
}

$category = "TrustAdmin";
$message = "";
$messageType = "";

// Path to the live JSON database
$dbPath = __DIR__ . '/asset/json/Legacytrust/bills.json';

function loadDatabase($path) {
    if (!file_exists($path)) return null;
    $json = file_get_contents($path);
    return json_decode($json, true);
}

function saveDatabase($path, $data) {
    file_put_contents($path, json_encode($data, JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES));
}

$dbData = loadDatabase($dbPath);
$searchAccount = filter_input(INPUT_GET, 'lookup_account', FILTER_SANITIZE_FULL_SPECIAL_CHARS);
$accountData = null;

if ($searchAccount && $dbData) {
    foreach ($dbData['accounts'] as $acc) {
        if ($acc['account_number'] === $searchAccount) {
            $accountData = $acc;
            break;
        }
    }
    if (!$accountData) {
        $message = "Account '{$searchAccount}' not found in active records.";
        $messageType = "error";
    }
}

// Process Payment & Update JSON Database
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $accountNumber = filter_input(INPUT_POST, 'account_number', FILTER_SANITIZE_FULL_SPECIAL_CHARS);
    $amount        = filter_input(INPUT_POST, 'payment_amount', FILTER_VALIDATE_FLOAT);
    $paymentMethod = filter_input(INPUT_POST, 'payment_method', FILTER_SANITIZE_FULL_SPECIAL_CHARS);

    if ($accountNumber && $amount > 0 && $dbData) {
        $updated = false;
        foreach ($dbData['accounts'] as &$acc) {
            if ($acc['account_number'] === $accountNumber) {
                $acc['balance'] = 0.00;
                $acc['status'] = "PAID_IN_FULL";
                $updated = true;
                break;
            }
        }
        unset($acc); // Clear reference

        if ($updated) {
            saveDatabase($dbPath, $dbData);
            $message = "Account #{$accountNumber} balance of $" . number_format($amount, 2) . " settled successfully. Database updated.";
            $messageType = "success";
            $accountData = null;
        }
    } else {
        $message = "Transaction error. Verification failed.";
        $messageType = "error";
    }
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Live Accounts Liable | TrustAdmin</title>
    <link rel="stylesheet" href="https://raw.githubusercontent.com/PMR-Pubclications/Trust-Main/main/asset/css/style.css">
    <style>
        body { background: #0f172a; color: #f8fafc; font-family: system-ui, sans-serif; padding: 2rem; }
        .container { max-width: 800px; margin: 0 auto; background: #1e293b; border: 1px solid #334155; padding: 2rem; border-radius: 8px; }
        .badge { background: rgba(56, 189, 248, 0.15); color: #38bdf8; padding: 0.2rem 0.6rem; border-radius: 4px; font-size: 0.75rem; font-weight: bold; }
        input, select { width: 100%; padding: 0.75rem; background: #0f172a; border: 1px solid #334155; color: #fff; border-radius: 4px; margin-top: 0.4rem; }
        button { background: #38bdf8; color: #0f172a; font-weight: bold; border: none; padding: 0.75rem; border-radius: 4px; cursor: pointer; width: 100%; margin-top: 1rem; }
        .alert-success { color: #10b981; background: rgba(16, 185, 129, 0.1); padding: 1rem; border-radius: 4px; margin-bottom: 1rem; }
        .alert-error { color: #ef4444; background: rgba(239, 68, 68, 0.1); padding: 1rem; border-radius: 4px; margin-bottom: 1rem; }
    </style>
</head>
<body>
<div class="container">
    <span class="badge">CATEGORY: <?= htmlspecialchars($category) ?></span>
    <h2>Live Accounts Liable Ledger</h2>
    
    <?php if (!empty($message)): ?>
        <div class="alert-<?= $messageType ?>"><?= htmlspecialchars($message) ?></div>
    <?php endif; ?>

    <form method="GET" action="accounts_liable.php" style="margin-bottom: 2rem;">
        <input type="hidden" name="role" value="<?= htmlspecialchars($activeRole) ?>">
        <label>Lookup Account Number</label>
        <div style="display:flex; gap:1rem;">
            <input type="text" name="lookup_account" placeholder="e.g. ACC-2026-8841" value="<?= htmlspecialchars($searchAccount ?? '') ?>" required>
            <button type="submit" style="width: auto; margin-top:0;">Search</button>
        </div>
    </form>

    <?php if ($accountData && $accountData['balance'] > 0): ?>
        <div style="background: rgba(56, 189, 248, 0.05); border: 1px solid #38bdf8; padding: 1rem; border-radius: 6px; margin-bottom: 1.5rem;">
            <p><strong>Entity:</strong> <?= htmlspecialchars($accountData['liable_entity']) ?></p>
            <p><strong>Balance Owed:</strong> <span style="color: #10b981; font-size: 1.2rem;">$<?= number_format($accountData['balance'], 2) ?></span></p>
        </div>

        <form method="POST" action="accounts_liable.php?role=<?= urlencode($activeRole) ?>">
            <input type="hidden" name="account_number" value="<?= htmlspecialchars($accountData['account_number']) ?>">
            <input type="hidden" name="payment_amount" value="<?= htmlspecialchars($accountData['balance']) ?>">
            <label>Payment Method</label>
            <select name="payment_method">
                <option value="PLAID_WELLS_FARGO">Wells Fargo (Via Plaid Link)</option>
                <option value="ACH">ACH Transfer</option>
            </select>
            <button type="submit" style="background: #10b981; color: #fff;">Settle Balance in Full</button>
        </form>
    <?php elseif ($searchAccount): ?>
        <p style="color: #94a3b8;">Account is either fully settled or inactive.</p>
    <?php endif; ?>

    <!-- Plaid Link Integration for Wells Fargo -->
    <hr style="border-color: #334155; margin: 2rem 0;">
    <button id="link-wells-fargo-btn" style="background: #b91c1c; color: white; font-weight: bold; padding: 0.75rem; border:none; border-radius:4px; width:100%;">
        Link Wells Fargo Account (Plaid)
    </button>
</div>

<script src="https://cdn.plaid.com/link/v2/stable/link-initialize.js"></script>
<script>
document.getElementById('link-wells-fargo-btn').addEventListener('click', async function () {
    try {
        const response = await fetch('/create_link_token.php', { method: 'POST' });
        const data = await response.json();

        const handler = Plaid.create({
            token: data.link_token,
            onSuccess: async function (public_token, metadata) {
                const exchangeRes = await fetch('/exchange_public_token.php', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ public_token: public_token, institution: metadata.institution })
                });
                const result = await exchangeRes.json();
                if (result.success) {
                    alert('Wells Fargo successfully linked for automated billing settlement.');
                }
            },
            onExit: function (err, metadata) {
                if (err) console.error("Plaid Link exited with error:", err);
            }
        });
        handler.open();
    } catch (e) {
        console.error("Error initializing Plaid Link:", e);
    }
});
</script>

</body>
</html>
