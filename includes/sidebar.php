<?php
/**
 * TRUST-MAIN DYNAMIC SIDEBAR & DISPATCH LOADER
 * Parses config/config.yaml directly for agencies, capabilities, and categories.
 */

// 1. Resolve Active Credentials & Role
$activeRole = strtolower($activeRole ?? $_SESSION['role'] ?? 'first_responder');
$isAdmin = in_array($activeRole, ['trustadmin', 'admin']);
$isStandard = !in_array($activeRole, ['trustadmin', 'admin', 'first_responder', 'responder']);

// Strict Role Enforcement for non-admins
if (!$isAdmin && (strpos($activeRole, 'admin') !== false || (isset($_GET['role']) && $_GET['role'] === 'TrustAdmin'))) {
    $activeRole = 'first_responder';
    $_SESSION['role'] = 'first_responder';
}

// 2. Load Configuration from your exact config/config.yaml path
$configFile = __DIR__ . '/config/config.yaml';
$config = [];
if (file_exists($configFile) && function_exists('yaml_parse_file')) {
    $config = yaml_parse_file($configFile);
} else {
    // Fallback array if YAML extension is missing
    $config = [
        'app_name' => 'Trust-Shell',
        'version' => '1.2',
        'agencies' => [],
        'capabilities' => [],
        'categories' => []
    ];
}

$appName = $config['app_name'] ?? 'Trust-Shell';
$appVersion = $config['version'] ?? '1.2';
$agencies = $config['agencies'] ?? [];
$capabilities = $config['capabilities'] ?? [];
$categories = $config['categories'] ?? [];

// 3. GitHub Directory Content Fetcher for dynamic asset links
function fetchGitHubFolderContents($folderPath) {
    $repoUser = 'PMR-Pubclications';
    $repoName = 'Trust-Main';
    $url = "https://api.github.com/repos/{$repoUser}/{$repoName}/contents/" . urlencode($folderPath);

    $ch = curl_init();
    curl_setopt($ch, CURLOPT_URL, $url);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_USERAGENT, 'Trust-Shell-Sidebar');
    curl_setopt($ch, CURLOPT_TIMEOUT, 4);
    $response = curl_exec($ch);
    curl_close($ch);

    if (!$response) return [];
    $data = json_decode($response, true);
    return is_array($data) ? $data : [];
}

$phpAssets = fetchGitHubFolderContents('asset/php');
$legalAssets = fetchGitHubFolderContents('legal');
$pdfAssets = fetchGitHubFolderContents('asset/pdf');
$lastSyncTimestamp = date('Y-m-d\TH:i:s\Z');

// 4. Filter Capabilities based on Role & TrustAdmin Restrictions
$userCapabilities = array_filter($capabilities, function($item) use ($activeRole, $isAdmin) {
    if (!$isAdmin && (isset($item['parent_title']) && $item['parent_title'] === 'TrustAdmin' || !empty($item['restricted']))) {
        return false;
    }
    if (empty($item['allowed_roles'])) return true;
    return in_array($activeRole, $item['allowed_roles']);
});

$currentPage = basename($_SERVER['PHP_SELF']);
?>

<!-- Sidebar Navigation (Trust-Main Environment) -->
<aside class="sidebar">
    <!-- Live System Clock & Lab ID -->
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.3rem;">
        <div id="os-live-clock" class="os-clock"></div>
        <span style="font-size: 0.7rem; color: var(--accent-color, #38bdf8); font-family: monospace;"><?= htmlspecialchars($config['system']['lab_id'] ?? 'LAB_01') ?></span>
    </div>

    <div class="brand">
        <span><?= htmlspecialchars($appName) ?></span>
        <span class="version-badge">v<?= htmlspecialchars($appVersion) ?></span>
    </div>

    <!-- Sync Timestamp & Blockchain Publisher Ledger Widget -->
    <div class="blockchain-status-badge">
        <div class="timestamp-label">&#9201; Sync: <?= htmlspecialchars($lastSyncTimestamp) ?></div>
        <a href="https://github.com/PMR-Pubclications/Trust-Main/blob/main/asset%2Fjava%2FballisticVideoAnalysis%2Fsrc%2FReportPackageService%26HTTP-Publisher.java" 
           target="_blank" rel="noopener noreferrer" class="blockchain-link">
            &#9939; Blockchain Publisher Ledger &rarr;
        </a>
    </div>

    <!-- Capabilities Section (Accounts Liable & Core Modules from config.yaml) -->
    <div>
        <div class="nav-group-title">
            <?= $isAdmin ? 'TRUST ADMIN CONSOLE' : 'SYSTEM MODULES' ?>
        </div>
        <nav class="nav-links">
            <?php foreach ($userCapabilities as $cap): ?>
                <?php $isActive = ($currentPage === $cap['url']); ?>
                <a href="<?= htmlspecialchars($cap['url']) ?>?role=<?= urlencode($activeRole) ?>" 
                   class="nav-link <?= $isActive ? 'active' : '' ?>">
                    <?= $cap['icon'] ?> <?= htmlspecialchars($cap['title']) ?>
                </a>
            <?php endforeach; ?>

            <!-- Auto-Discovered PHP Assets (asset/php) -->
            <?php foreach ($phpAssets as $file): ?>
                <?php if (isset($file['type']) && $file['type'] === 'file'): ?>
                    <a href="<?= htmlspecialchars($file['html_url']) ?>" target="_blank" rel="noopener noreferrer" class="nav-link">
                        &#9881; <?= htmlspecialchars(pathinfo($file['name'], PATHINFO_FILENAME)) ?> &rarr;
                    </a>
                <?php endif; ?>
            <?php endforeach; ?>
        </nav>
    </div>

    <!-- Agencies Dispatch Section (Parsed directly from config.yaml agencies block) -->
    <?php if (!empty($agencies)): ?>
    <div>
        <div class="nav-group-title">AGENCY DISPATCH ENDPOINTS</div>
        <nav class="nav-links">
            <?php foreach ($agencies as $agencyKey => $agencyData): ?>
                <a href="<?= htmlspecialchars($agencyData['endpoint']) ?>" target="_blank" rel="noopener noreferrer" class="nav-link">
                    &#128225; <?= ucfirst($agencyKey) ?> <span style="font-size:0.65rem; color:var(--text-muted);">(<?= htmlspecialchars($agencyData['report_format']) ?>)</span>
                </a>
            <?php endforeach; ?>
        </nav>
    </div>
    <?php endif; ?>

    <!-- Legal & Regulatory (legal folder) -->
    <div>
        <div class="nav-group-title">LEGAL & REGULATORY</div>
        <nav class="nav-links">
            <?php if (!empty($legalAssets)): ?>
                <?php foreach ($legalAssets as $file): ?>
                    <?php if (isset($file['type']) && $file['type'] === 'file'): ?>
                        <a href="<?= htmlspecialchars($file['html_url']) ?>" target="_blank" rel="noopener noreferrer" class="nav-link">
                            &#9898; <?= htmlspecialchars(pathinfo($file['name'], PATHINFO_FILENAME)) ?> &rarr;
                        </a>
                    <?php endif; ?>
                <?php endforeach; ?>
            <?php else: ?>
                <a href="https://github.com/PMR-Pubclications/Trust-Main/blob/main/legal%2FAIinLawEnforcementCurrentFederalandStateLegalLandscape.html" 
                   target="_blank" rel="noopener noreferrer" class="nav-link">
                    &#9898; AI in Law Enforcement Framework &rarr;
                </a>
            <?php endif; ?>
        </nav>
    </div>

    <!-- Restricted Category: TrustAdmin PDF Assets (asset/pdf) -->
    <?php if ($isAdmin && !empty($pdfAssets)): ?>
    <div>
        <div class="nav-group-title">TRUSTADMIN ASSETS (PDF)</div>
        <nav class="nav-links">
            <?php foreach ($pdfAssets as $file): ?>
                <?php if (isset($file['type']) && $file['type'] === 'file'): ?>
                    <a href="<?= htmlspecialchars($file['html_url']) ?>" target="_blank" rel="noopener noreferrer" class="nav-link">
                        &#128196; <?= htmlspecialchars(pathinfo($file['name'], PATHINFO_FILENAME)) ?> (PDF) &rarr;
                    </a>
                <?php endif; ?>
            <?php endforeach; ?>
        </nav>
    </div>
    <?php endif; ?>
</aside>

<style>
    .os-clock {
        font-family: var(--font-main, -apple-system, sans-serif);
        font-size: 0.85rem;
        font-weight: 600;
        color: var(--text-muted, #8a8d93);
        user-select: none;
    }
    .blockchain-status-badge {
        background: rgba(56, 189, 248, 0.08);
        border: 1px solid rgba(56, 189, 248, 0.25);
        border-radius: 4px;
        padding: 0.4rem 0.6rem;
        margin-bottom: 0.8rem;
        margin-top: 0.5rem;
    }
    .timestamp-label {
        font-size: 0.72rem;
        color: var(--text-muted, #94a3b8);
        font-family: monospace;
    }
    .blockchain-link {
        font-size: 0.75rem;
        color: var(--accent-color, #38bdf8);
        text-decoration: none;
        font-weight: bold;
        display: inline-block;
        margin-top: 0.2rem;
    }
    .blockchain-link:hover {
        text-decoration: underline;
    }
</style>

<script>
    (function syncDeviceClock() {
        const clockEl = document.getElementById('os-live-clock');
        if (!clockEl) return;

        function tick() {
            const now = new Date();
            clockEl.textContent = now.toLocaleTimeString([], {
                hour: 'numeric',
                minute: '2-digit'
            });

            const millisUntilNextSecond = 1000 - now.getMilliseconds();
            setTimeout(tick, millisUntilNextSecond);
        }

        tick();
    })();
</script>
