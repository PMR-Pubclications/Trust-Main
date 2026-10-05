<?php
/**
 * Trust Administrator - Dedicated SHA-256 Audit & Telemetry Log Viewer
 * Path: trust-main/audit-logs.php
 * 
 * Clearance Level: SOLE TRUST ADMIN ONLY
 * Features: Live stream inspection, SHA-256 verification hash checks,
 * filtering by log source, real-time client-side keyword search, log clearing,
 * plain text download, and AJAX auto-polling.
 */

if (session_status() === PHP_SESSION_NONE) {
    session_start();
}

// 1. Strict Security Guard (Handled before any output so AJAX returns clean data)
if (!isset($_SESSION['user']) \vert{}\vert{} ($_SESSION['user']['role'] ?? '') !== 'TRUST_ADMIN') {
    if (isset($_GET['ajax'])) {
        http_response_code(403);
        echo 'UNAUTHORIZED_ACCESS';
        exit;
    }
    header('Location: /responder/index.php');
    exit;
}

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

$selectedLog =$_GET['log'] ?? 'sha256';
if (!array_key_exists($selectedLog, $logFiles)) {$selectedLog = 'sha256';
}

$currentLog = $logFiles[$selectedLog];
$logPath    =$currentLog['path'];

/**
 * Helper function to parse and syntax-highlight log entries
 */
function renderFormattedLogEntries($path) {
    if (!file_exists($path)) {
        return '<div style="color: var(--term-green-dim); text-align: center; padding-top: 200px;">'
             . '--- NO TELEMETRY DATA RECORDED IN THIS LOG FILE ---<br>'
             . 'RUN THE ACCOUNTS AUTOMATION ENGINE TO GENERATE SHA-256 AUDIT LOGS.'
             . '</div>';
    }

    $logRaw   = file_get_contents($path);
    $logLines = array_filter(explode("\n", trim($logRaw)));

    if (empty($logLines)) {
        return '<div style="color: var(--term-green-dim); text-align: center; padding-top: 200px;">'
             . '--- LOG FILE IS EMPTY ---'
             . '</div>';
    }

    $html = '';
    foreach ($logLines as$index => $line) {$formattedLine = htmlspecialchars($line);$formattedLine = preg_replace('/(TX_HASH:[a-f0-9\.\.]+)/i', '<span style="color: var(--term-blue); font-weight: bold;">$1</span>', $formattedLine);$formattedLine = preg_replace('/(\[\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\])/', '<span style="color: var(--term-green-dim);">$1</span>', $formattedLine);$formattedLine = preg_replace('/(TYPE:RECEIVABLE)/', '<span style="color: var(--term-green); font-weight: bold;">$1</span>', $formattedLine);$formattedLine = preg_replace('/(TYPE:LIABLE)/', '<span style="color: var(--term-red); font-weight: bold;">$1</span>',$formattedLine);

        $html .= '<div class="log-line" style="margin-bottom: 4px; white-space: pre-wrap; word-break: break-all;">'
              . '<span style="color: var(--term-green-dark); margin-right: 8px;">' . sprintf('%04d', $index + 1) . '|</span>' 
              . $formattedLine 
              . '</div>';
    }

    return $html;
}

// 2. AJAX Intercept Point: Returns updated terminal HTML and metadata without full page reload
if (isset($_GET['ajax']) &&$_GET['ajax'] === '1') {
    header('Content-Type: application/json; charset=utf-8');
    $lineCount = file_exists($logPath) ? count(array_filter(explode("\n", trim(file_get_contents($logPath))))) : 0;
    $fileSize  = file_exists($logPath) ? round(filesize($logPath) / 1024, 2) : 0;

    echo json_encode([
        'status'     => 'success',
        'html'       => renderFormattedLogEntries($logPath),
        'line_count' => $lineCount,
        'file_size'  => $fileSize,
        'timestamp'  => date('H:i:s T')
    ]);
    exit;
}

// 3. Normal HTML Page Flow
$pageTitle = "TRUST ADMIN // REAL-TIME TELEMETRY & AUDIT LOGS";
require_once __DIR__ . '/includes/adminHeader.php';

// Handle File Actions: Clear or Download
$statusMsg = '';
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $action =$_POST['action'] ?? '';

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

$fileSize  = file_exists($logPath) ? round(filesize($logPath) / 1024, 2) : 0;
$lineCount = file_exists($logPath) ? count(array_filter(explode("\n", trim(file_get_contents($logPath))))) : 0;
?>

<!-- Action Status Notification -->
<?php if (!empty($statusMsg)): ?>
    <div style="border: 1px solid var(--term-green); background-color: var(--term-bg-dark); color: var(--term-green); padding: 12px; margin-bottom: 20px; font-weight: bold; text-align: center;">
        &gt; <?= $statusMsg ?>
    </div>
<?php endif; ?>

<!-- Log Control Bar -->
<div class="card" style="margin-bottom: 20px;">
    <div class="card-header">
        <h2 class="card-title">&gt; TELEMETRY SOURCE SELECTION</h2>
        <span class="metric-val" style="color: var(--term-blue);" id="fileSizeBadge">[ FILE SIZE: <?= $fileSize ?> KB ]</span>
    </div>

    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 15px;">
        <!-- Selector Tabs -->
        <div style="display: flex; gap: 10px;">
            <?php foreach ($logFiles as $key =>$info): ?>
                <a href="audit-logs.php?log=<?= $key ?>" class="btn-terminal" style="text-decoration: none; display: inline-block; padding: 8px 14px; margin-top: 0; background-color: <?= $selectedLog ===$key ? 'var(--term-blue)' : 'var(--term-black)' ?>; color: <?= $selectedLog ===$key ? 'var(--term-black)' : 'var(--term-blue)' ?>;">
                    <?= $key === 'sha256' ? '&gt; SHA-256 AUDIT' : '&gt; CRON ENGINE' ?>
                </a>
            <?php endforeach; ?>
        </div>

        <!-- Controls & Metrics -->
        <div style="display: flex; gap: 14px; align-items: center; flex-wrap: wrap;">
            <span style="font-size: 0.85rem; color: var(--term-green-dim);">
                TOTAL ENTRIES: <strong style="color: var(--term-green);" id="lineCountVal"><?= $lineCount ?></strong>
            </span>

            <!-- Auto-Refresh Toggle Button -->
            <button id="pollToggleBtn" class="blue-link" style="background: none; border: 1px solid var(--term-green-dark); padding: 4px 8px; font-size: 0.82rem; cursor: pointer; color: var(--term-green) !important;" onclick="toggleAutoPoll();">
                [ AUTO-POLL: ON (5s) ]
            </button>

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

<!-- Terminal CRT Output Window Container -->
<div class="card" style="background-color: var(--term-black); border: 2px solid var(--term-green); box-shadow: 0 0 12px var(--term-glow);">
    <div class="card-header">
        <h2 class="card-title">&gt; STREAM: <?= $currentLog['name'] ?></h2>
        <span id="pollPulseTag" class="live-stream-tag" style="font-size: 0.75rem;">&#9673; LIVE STREAM ACTIVE</span>
    </div>

    <!-- Live Client-Side Search Bar -->
    <div style="display: flex; gap: 10px; align-items: center; padding: 10px; background-color: var(--term-bg-dark); border-bottom: 1px solid var(--term-green-dark); margin-bottom: 10px;">
        <span style="color: var(--term-green); font-size: 0.85rem; font-weight: bold; white-space: nowrap;">&gt; FILTER STREAM:</span>
        <input type="text" id="logSearchInput" placeholder="Enter keyword (e.g., RECEIVABLE, ACH_SWEEP, TX_HASH, 2026)..." oninput="filterLogLines();" style="flex: 1; background-color: #000; color: var(--term-green); border: 1px solid var(--term-green-dark); padding: 6px 12px; font-family: var(--font-terminal); font-size: 0.85rem; outline: none;">
        <button class="blue-link" onclick="clearLogFilter();" style="background: none; border: 1px solid var(--term-green-dark); padding: 5px 10px; font-size: 0.8rem; cursor: pointer; white-space: nowrap;">[ CLEAR ]</button>
        <span id="matchCountBadge" style="font-size: 0.8rem; color: var(--term-blue); white-space: nowrap;">[ MATCHES: ALL ]</span>
    </div>

    <!-- Terminal Display Container -->
    <div id="terminalWindow" style="background-color: #010801; border: 1px solid var(--term-green-dark); padding: 16px; height: 500px; overflow-y: auto; font-family: var(--font-terminal); font-size: 0.85rem; line-height: 1.6; color: var(--term-green);">
        <?= renderFormattedLogEntries($logPath) ?>
    </div>

    <!-- Terminal Footer Info -->
    <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 12px; font-size: 0.75rem; color: var(--term-green-dim);">
        <div>
            LAST POLL: <span id="lastPollTime" style="color: var(--term-green);"><?= date('H:i:s T') ?></span>
        </div>
        <div>
            <a href="#" class="blue-link" onclick="scrollToBottom(); return false;">[ SCROLL TO BOTTOM ]</a>
        </div>
    </div>
</div>

<!-- AJAX Polling & Live Search Script -->
<script>
    const currentLogKey = "<?= $selectedLog ?>";
    let isPolling = true;
    let pollInterval = null;

    function scrollToBottom() {
        const term = document.getElementById('terminalWindow');
        if (term) term.scrollTop = term.scrollHeight;
    }

    // Client-side real-time filtering engine
    function filterLogLines() {
        const inputElem = document.getElementById('logSearchInput');
        if (!inputElem) return;

        const query = inputElem.value.toLowerCase().trim();
        const lines = document.querySelectorAll('#terminalWindow .log-line');
        const badge = document.getElementById('matchCountBadge');
        let visibleCount = 0;

        lines.forEach(line => {
            const text = (line.textContent || line.innerText).toLowerCase();
            if (query === '' || text.includes(query)) {
                line.style.display = 'block';
                visibleCount++;
            } else {
                line.style.display = 'none';
            }
        });

        if (badge) {
            if (query === '') {
                badge.innerText = `[ MATCHES: ALL (${lines.length}) ]`;
                badge.style.color = 'var(--term-blue)';
            } else {
                badge.innerText = `[ MATCHES: ${visibleCount} / ${lines.length} ]`;
                badge.style.color = visibleCount > 0 ? 'var(--term-green)' : 'var(--term-red)';
            }
        }
    }

    function clearLogFilter() {
        const inputElem = document.getElementById('logSearchInput');
        if (inputElem) {
            inputElem.value = '';
            filterLogLines();
        }
    }

    function toggleAutoPoll() {
        isPolling = !isPolling;
        const toggleBtn = document.getElementById('pollToggleBtn');
        const pulseTag  = document.getElementById('pollPulseTag');

        if (isPolling) {
            toggleBtn.innerText = '[ AUTO-POLL: ON (5s) ]';
            toggleBtn.style.color = 'var(--term-green)';
            if (pulseTag) pulseTag.style.display = 'inline-block';
            startPolling();
        } else {
            toggleBtn.innerText = '[ AUTO-POLL: PAUSED ]';
            toggleBtn.style.color = 'var(--term-red)';
            if (pulseTag) pulseTag.style.display = 'none';
            stopPolling();
        }
    }

    function fetchLatestLogs() {
        if (!isPolling) return;

        const term = document.getElementById('terminalWindow');
        // Detect if user is scrolled near the bottom before update
        const isAtBottom = (term.scrollHeight - term.clientHeight - term.scrollTop) < 60;

        fetch(`audit-logs.php?log=${currentLogKey}&ajax=1`)
            .then(response => {
                if (!response.ok) throw new Error('NETWORK_ERROR');
                return response.json();
            })
            .then(data => {
                if (data.status === 'success') {
                    // Update content
                    term.innerHTML = data.html;

                    // Re-apply active search filter on freshly injected DOM elements
                    filterLogLines();

                    // Update UI status badges
                    document.getElementById('lineCountVal').innerText = data.line_count;
                    document.getElementById('fileSizeBadge').innerText = `[ FILE SIZE: ${data.file_size} KB ]`;
                    document.getElementById('lastPollTime').innerText = data.timestamp;

                    // Keep view pinned to bottom if user was already at bottom
                    if (isAtBottom && document.getElementById('logSearchInput').value.trim() === '') {
                        scrollToBottom();
                    }
                }
            })
            .catch(err => {
                console.warn('Log polling paused due to network anomaly:', err);
            });
    }

    function startPolling() {
        stopPolling();
        pollInterval = setInterval(fetchLatestLogs, 5000);
    }

    function stopPolling() {
        if (pollInterval) clearInterval(pollInterval);
    }

    // Initialize on page load
    window.addEventListener('DOMContentLoaded', () => {
        filterLogLines();
        scrollToBottom();
        startPolling();
    });
</script>

<?php
// Shared Admin Footer
require_once __DIR__ . '/includes/adminFooter.php';
?>
