<?php
/**
 * Trust Administrator - Dedicated SHA-256 Audit & Telemetry Log Viewer
 * Path: trust-main/audit-logs.php
 * 
 * Clearance Level: SOLE TRUST ADMIN ONLY
 * Features: Live stream inspection, SHA-256 verification hash checks,
 * filtering by log source, log clearing, and plain text download.
 */

$pageTitle = "TRUST ADMIN // REAL-TIME TELEMETRY & AUDIT LOGS";

// Include Admin Header (Enforces TRUST_ADMIN access control)
require_once __DIR__ . '/includes/adminHeader.php';

$dataDir = __DIR__ . '/data';

// Available Log Sources
$logFiles = [
    'sha256' => [
        'name' => 'SHA-256 AUTOMATED PAYMENTS & YIELD LOG',
        'path' => $dataDir . '/sha256_verify.log'
    ],
    'cron' => [
        'name' => 'BACKGROUND CRON EXECUTION TELEMETRY',
        'path' => $dataDir . '/cron_execution.log'
    ]
];

$selectedLog = $_GET['log'] ?? 'sha256';
if (!array_key_exists($selectedLog, $logFiles)) {
    $selectedLog = 'sha256';
}

$currentLog = $logFiles[$selectedLog];
$logPath    = $currentLog['path'];

// Handle Actions: Clear or Download
$statusMsg  = '';
$statusType = 'green';

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $action = $_POST['action'] ?? '';

    if ($action === 'clear_log') {
        if (file_exists($logPath)) {
            file_put_contents($logPath, '');
            $statusMsg = "SUCCESS: " . strtoupper($selectedLog) . " LOG PURGED AND RESET BY ADMIN.";
        }
    } elseif ($action === 'download_log') {
        if (file_exists($logPath)) {
            header('Content-Type: text/plain');
            header('Content-Disposition: attachment; filename="' . basename($logPath) . '"');
            header('Content-Length: ' . filesize($logPath));
            readfile($logPath);
            exit;
        }
    }
}

// Read Log Data
$logRaw = file_exists($logPath) ? file_get_contents($logPath) : '';
$logLines = array_filter(explode("\n", trim($logRaw)));
$lineCount = count($logLines);
$fileSize = file_exists($logPath) ? round(filesize($logPath) / 1024, 2) : 0;
?>

<!-- Action Status Message -->
<?php if (!empty($statusMsg)): ?>
    <div style="border: 1px solid var(--term-green); background-color: var(--term-bg-dark); color: var(--term-green); padding: 12px; margin-bottom: 20px; font-weight: bold; text-align: center;">
        &gt; <?= $statusMsg ?>
    </div>
<?php endif; ?>

<!-- Log Control Bar -->
<div class="card" style="margin-bottom: 20px;">
    <div class="card-header">
        <h2 class="card-title">&gt; TELEMETRY SOURCE SELECTION</h2>
        <span class="metric-val" style="color: var(--term-blue);">[ FILE SIZE: <?= $fileSize ?> KB ]</span>
    </div>

    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 15px;">
        <!-- Selector Buttons -->
        <div style="display: flex; gap: 10px;">
            <?php foreach ($logFiles as $key => $info): ?>
                <a href="audit-logs.php?log=<?= $key ?>" class="btn-terminal" style="text-decoration: none; display: inline-block; padding: 8px 14px; margin-top: 0; background-color: <?= $selectedLog === $key ? 'var(--term-blue)' : 'var(--term-black)' ?>; color: <?= $selectedLog === $key ? 'var(--term-black)' : 'var(--term-blue)' ?>;">
                    <?= $key === 'sha256' ? '&gt; SHA-256 AUDIT' : '&gt; CRON ENGINE' ?>
                </a>
            <?php endforeach; ?>
        </div>

        <!-- Telemetry Stats & Tools -->
        <div style="display: flex; gap: 12px; align-items: center;">
            <span style="font-size: 0.85rem; color: var(--term-green-dim);">
                TOTAL ENTRIES: <strong style="color: var(--term-green);"><?= $lineCount ?></strong>
            </span>

            <form method="POST" action="audit-logs.php?log=<?= $selectedLog ?>" style="display: inline;">
                <input type="hidden" name="action" value="download_log">
                <button type="submit" class="blue-link" style="background: none; border: none; font-size: 0.85rem; cursor: pointer;">
                    [ DOWNLOAD TXT ]
                </button>
            </form>

            <form method="POST" action="audit-logs.php?log=<?= $selectedLog ?>" style="display: inline;" onsubmit="return confirm('PURGE LOG FILE? THIS ACTION IS IRREVERSIBLE.');">
                <input type="hidden" name="action" value="clear_log">
                <button type="submit" style="background: none; border: none; color: var(--term-red) !important; font-size: 0.85rem; cursor: pointer;" class="blue-link">
                    [ CLEAR LOG ]
                </button>
            </form>
        </div>
    </div>
</div>

<!-- Terminal CRT Output Terminal -->
<div class="card" style="background-color: var(--term-black); border: 2px solid var(--term-green); box-shadow: 0 0 12px var(--term-glow);">
    <div class="card-header">
        <h2 class="card-title">&gt; STREAM: <?= $currentLog['name'] ?></h2>
        <span class="live-stream-tag" style="font-size: 0.75rem;">&#9673; LIVE MONITOR</span>
    </div>

    <!-- Terminal Display Window -->
    <div id="terminalWindow" style="background-color: #010801; border: 1px solid var(--term-green-dark); padding: 16px; height: 500px; overflow-y: auto; font-family: var(--font-terminal); font-size: 0.85rem; line-height: 1.6; color: var(--term-green);">
        <?php if (empty($logLines)): ?>
            <div style="color: var(--term-green-dim); text-align: center; padding-top: 200px;">
                --- NO TELEMETRY DATA RECORDED IN THIS LOG FILE ---<br>
                RUN THE ACCOUNTS AUTOMATION ENGINE TO GENERATE SHA-256 AUDIT LOGS.
            </div>
        <?php else: ?>
            <?php foreach ($logLines as $index => $line): ?>
                <?php
                    // Highlight SHA-256 hashes in blue and timestamps in dark green
                    $formattedLine = htmlspecialchars($line);
                    $formattedLine = preg_replace('/(TX_HASH:[a-f0-9\.\.]+)/i', '<span style="color: var(--term-blue); font-weight: bold;">$1</span>', $formattedLine);
                    $formattedLine = preg_replace('/(\[\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\])/', '<span style="color: var(--term-green-dim);">$1</span>', $formattedLine);
                    $formattedLine = preg_replace('/(TYPE:RECEIVABLE)/', '<span style="color: var(--term-green); font-weight: bold;">$1</span>', $formattedLine);
                    $formattedLine = preg_replace('/(TYPE:LIABLE)/', '<span style="color: var(--term-red); font-weight: bold;">$1</span>', $formattedLine);
                ?>
                <div style="margin-bottom: 4px; white-space: pre-wrap; word-break: break-all;">
                    <span style="color: var(--term-green-dark); margin-right: 8px;"><?= sprintf('%04d', $index + 1) ?>|</span><?= $formattedLine ?>
                </div>
            <?php endforeach; ?>
        <?php endif; ?>
    </div>

    <!-- Terminal Status Footer -->
    <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 12px; font-size: 0.75rem; color: var(--term-green-dim);">
        <div>STATUS: <span style="color: var(--term-green);">SHA-256 VERIFICATION ENGINE ACTIVE</span></div>
        <div>
            <a href="#" class="blue-link" onclick="document.getElementById('terminalWindow').scrollTop = document.getElementById('terminalWindow').scrollHeight; return false;">[ SCROLL TO BOTTOM ]</a>
        </div>
    </div>
</div>

<script>
    // Auto-scroll terminal stream to bottom on load
    window.addEventListener('DOMContentLoaded', () => {
        const term = document.getElementById('terminalWindow');
        if (term) {
            term.scrollTop = term.scrollHeight;
        }
    });
</script>

<?php
// Shared Admin Footer
require_once __DIR__ . '/includes/adminFooter.php';
?>
