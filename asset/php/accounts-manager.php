<?php
/**
 * Trust Administrator - Automated Accounts & Liabilities Manager
 * Path: trust-main/accounts-manager.php
 * 
 * Clearance: SOLE TRUST ADMIN ONLY
 * Handles registration of Accounts Receivable (Incoming) and Accounts Liable (Outgoing)
 * for automated sweep, yield allocation, and payment loops.
 */

$pageTitle = "TRUST ADMIN // AUTOMATED ACCOUNTS MANAGER";

// Security Check & Header Inclusion (Redirects non-admins to /responder/index.php)
require_once __DIR__ . '/includes/adminHeader.php';

// Data Storage File (JSON Ledger Store)
$dataFile = __DIR__ . '/data/automated_accounts.json';

// Ensure data directory exists
if (!file_exists(__DIR__ . '/data')) {
    mkdir(__DIR__ . '/data', 0755, true);
}

// Load existing accounts
$accounts = file_exists($dataFile) ? json_decode(file_get_contents($dataFile), true) : [];

$statusMsg = '';
$statusType = 'green'; // 'green' or 'red'

// Handle Form Submission
if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['action']) && $_POST['action'] === 'save_account') {
    $accountType   = trim($_POST['account_type'] ?? '');
    $entityName    = trim($_POST['entity_name'] ?? '');
    $accountNum    = trim($_POST['account_number'] ?? '');
    $amount        = floatval($_POST['amount'] ?? 0);
    $frequency     = trim($_POST['frequency'] ?? 'MONTHLY');
    $executionType = trim($_POST['execution_type'] ?? 'ACH_SWEEP');
    $startDate     = trim($_POST['start_date'] ?? date('Y-m-d'));
    $notes         = trim($_POST['notes'] ?? '');

    if (empty($entityName) || $amount <= 0 || !in_array($accountType, ['RECEIVABLE', 'LIABLE'])) {
        $statusMsg = "ERROR: INVALID INPUT. ENTITY NAME, VALID AMOUNT, AND TYPE ARE REQUIRED.";
        $statusType = 'red';
    } else {
        $newAccount = [
            'id'             => 'ACC-' . strtoupper(substr(md5(uniqid()), 0, 8)),
            'type'           => $accountType, // 'RECEIVABLE' or 'LIABLE'
            'entity_name'    => htmlspecialchars($entityName),
            'account_number' => htmlspecialchars($accountNum),
            'amount'         => $amount,
            'frequency'      => $frequency,
            'execution_type' => $executionType,
            'start_date'     => $startDate,
            'next_run'       => $startDate,
            'status'         => 'AUTOMATED',
            'notes'          => htmlspecialchars($notes),
            'created_at'     => date('Y-m-d H:i:s')
        ];

        $accounts[] = $newAccount;
        file_put_contents($dataFile, json_encode($accounts, JSON_PRETTY_PRINT));

        $statusMsg = "SUCCESS: " . $accountType . " ENTRY [" . $newAccount['id'] . "] REGISTERED FOR AUTOMATION.";
        $statusType = 'green';
    }
}
?>

<!-- System Status Notification Bar -->
<?php if (!empty($statusMsg)): ?>
    <div style="border: 1px solid <?= $statusType === 'red' ? 'var(--term-red)' : 'var(--term-green)' ?>; background-color: var(--term-bg-dark); color: <?= $statusType === 'red' ? 'var(--term-red)' : 'var(--term-green)' ?>; padding: 12px; margin-bottom: 20px; font-weight: bold; text-align: center;">
        &gt; <?= $statusMsg ?>
    </div>
<?php endif; ?>

<div class="grid-container" style="grid-template-columns: 1fr 1fr;">

    <!-- Left Column: New Account Registration Form -->
    <div class="card">
        <div class="card-header">
            <h2 class="card-title">&gt; REGISTER AUTOMATED ACCOUNT</h2>
            <span class="live-stream-tag" style="font-size: 0.75rem;">CONFIG_MODE</span>
        </div>

        <form method="POST" action="accounts-manager.php">
            <input type="hidden" name="action" value="save_account">

            <label class="metric-label" style="display:block; margin-bottom: 4px;">ACCOUNT DIRECTION / CATEGORY:</label>
            <select name="account_type" required style="margin-bottom: 15px;">
                <option value="RECEIVABLE">&plus; ACCOUNT RECEIVABLE (INCOMING / YIELD / SWEEP)</option>
                <option value="LIABLE">&minus; ACCOUNT LIABLE (OUTGOING / EXPENSE / DEBT SERVICING)</option>
            </select>

            <label class="metric-label" style="display:block; margin-bottom: 4px;">ENTITY / COUNTERPARTY NAME:</label>
            <input type="text" name="entity_name" placeholder="e.g., Robinhood Sweep, Mining Payout, Vendor LLC" required>

            <label class="metric-label" style="display:block; margin-bottom: 4px;">ACCOUNT / ROUTING / WALLET REF:</label>
            <input type="text" name="account_number" placeholder="e.g., ****4892 / f2pool Wallet / API Ref">

            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
                <div>
                    <label class="metric-label" style="display:block; margin-bottom: 4px;">SCHEDULED AMOUNT ($):</label>
                    <input type="number" step="0.01" name="amount" placeholder="0.00" required>
                </div>
                <div>
                    <label class="metric-label" style="display:block; margin-bottom: 4px;">FREQUENCY:</label>
                    <select name="frequency">
                        <option value="DAILY">DAILY</option>
                        <option value="WEEKLY">WEEKLY</option>
                        <option value="BI_WEEKLY">BI-WEEKLY</option>
                        <option value="MONTHLY" selected>MONTHLY</option>
                        <option value="QUARTERLY">QUARTERLY</option>
                        <option value="AUTO_SWEEP">ON-TRIGGER (AUTO-SWEEP)</option>
                    </select>
                </div>
            </div>

            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
                <div>
                    <label class="metric-label" style="display:block; margin-bottom: 4px;">EXECUTION METHOD:</label>
                    <select name="execution_type">
                        <option value="ACH_SWEEP">ACH AUTO-SWEEP</option>
                        <option value="WIRE_TRANSFER">WIRE TRANSFER</option>
                        <option value="CRYPTO_AUTO">CRYPTO / COLD VAULT SWEEP</option>
                        <option value="API_INTEGRATION">API REBALANCE ROUTINE</option>
                    </select>
                </div>
                <div>
                    <label class="metric-label" style="display:block; margin-bottom: 4px;">FIRST RUN / DUE DATE:</label>
                    <input type="date" name="start_date" value="<?= date('Y-m-d') ?>" required>
                </div>
            </div>

            <label class="metric-label" style="display:block; margin-bottom: 4px;">AUTOMATION RULES / NOTES:</label>
            <textarea name="notes" rows="3" placeholder="Specify liquidity thresholds, sweep rules, or allocation tags..."></textarea>

            <button type="submit" class="btn-terminal">&plus; COMMMIT ACCOUNT TO AUTOMATION ENGINE</button>
        </form>
    </div>

    <!-- Right Column: Automated Ledger Summary -->
    <div class="card">
        <div class="card-header">
            <h2 class="card-title">&gt; ACTIVE AUTOMATION LEDGER</h2>
            <span class="metric-val" style="color: var(--term-blue);">[ <?= count($accounts) ?> ACTIVE ]</span>
        </div>

        <?php if (empty($accounts)): ?>
            <p style="color: var(--term-green-dim); text-align: center; padding: 20px;">
                NO AUTOMATED ACCOUNTS REGISTERED YET. USE THE FORM ON THE LEFT TO ADD RECEIVABLES OR LIABILITIES.
            </p>
        <?php else: ?>
            <div style="max-height: 520px; overflow-y: auto; padding-right: 5px;">
                <?php foreach (array_reverse($accounts) as $acc): ?>
                    <div style="border: 1px solid var(--term-green-dark); background-color: var(--term-black); padding: 12px; margin-bottom: 12px;">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                            <span style="font-weight: bold; color: <?= $acc['type'] === 'RECEIVABLE' ? 'var(--term-green)' : 'var(--term-red)' ?>;">
                                <?= $acc['type'] === 'RECEIVABLE' ? '[&plus; RECEIVABLE]' : '[&minus; LIABLE]' ?>
                            </span>
                            <span style="font-size: 0.75rem; color: var(--term-green-dim);"><?= $acc['id'] ?></span>
                        </div>

                        <div style="font-size: 1rem; font-weight: bold; color: #fff;">
                            <?= $acc['entity_name'] ?>
                        </div>

                        <div class="metric-row" style="border-bottom: none; padding: 4px 0;">
                            <span class="metric-label">AMOUNT & SCHEDULE:</span>
                            <span class="metric-val" style="color: var(--term-blue);">
                                $<?= number_format($acc['amount'], 2) ?> / <?= $acc['frequency'] ?>
                            </span>
                        </div>

                        <div class="metric-row" style="border-bottom: none; padding: 4px 0;">
                            <span class="metric-label">METHOD & NEXT RUN:</span>
                            <span class="metric-val">
                                <?= $acc['execution_type'] ?> &bull; <a href="#" class="blue-link"><?= $acc['next_run'] ?></a>
                            </span>
                        </div>

                        <?php if (!empty($acc['notes'])): ?>
                            <div style="font-size: 0.75rem; color: var(--term-green-dim); margin-top: 6px; border-top: 1px dashed var(--term-green-dark); padding-top: 4px;">
                                RULE: <?= $acc['notes'] ?>
                            </div>
                        <?php endif; ?>
                    </div>
                <?php endforeach; ?>
            </div>
        <?php endif; ?>
    </div>

</div>

<?php
// Shared Admin Footer
require_once __DIR__ . '/includes/adminFooter.php';
?>
