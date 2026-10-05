<?php
/**
 * Operations & Software Guide - Main Dashboard Entry Point
 * Path: trust-main/guide.php
 */

if (session_status() === PHP_SESSION_NONE) {
    session_start();
}

// 1. Load Manifest Data Configuration
$manifestPath = __DIR__ . '/config/guide_manifest.json';
$manifest = [];

if (file_exists($manifestPath)) {
    $jsonContent = file_get_contents($manifestPath);
    $manifest = json_decode($jsonContent, true) ?? [];
}

// 2. State & Request Parameters
$appVersion       = $manifest['version'] ?? '1.0.0';
$activeRole       = strtoupper($_GET['role'] ?? 'POLICE');
$selectedCategory = $_GET['category'] ?? 'all';
$searchQuery      = trim($_GET['q'] ?? '');

// Pass page title context to header template
$pageTitle = ($manifest['app_name'] ?? 'Trust-Shell') . ' // Operations & Software Guide';

// 3. Filter Modules by Role, Category, and Search Query
$allModules = $manifest['modules'] ?? [];
$filteredModules = array_filter($allModules, function ($module) use ($activeRole, $selectedCategory, $searchQuery) {
    // Role Check
    if (!empty($module['roles']) && !in_array('ALL', $module['roles']) && !in_array($activeRole, $module['roles'])) {
        return false;
    }

    // Category Check
    if ($selectedCategory !== 'all' && isset($module['category_id'])) {
        if ($module['category_id'] !== $selectedCategory) {
            return false;
        }
    }

    // Search Query Check
    if (!empty($searchQuery)) {
        $q = mb_strtolower($searchQuery);
        $titleMatch = strpos(mb_strtolower($module['title'] ?? ''), $q) !== false;
        $descMatch  = strpos(mb_strtolower($module['description'] ?? ''), $q) !== false;
        $codeMatch  = strpos(mb_strtolower($module['command_example'] ?? ''), $q) !== false;

        if (!$titleMatch && !$descMatch && !$codeMatch) {
            return false;
        }
    }

    return true;
});

// 4. Render Header Template
require_once __DIR__ . '/includes/header.php';
?>

<!-- Workspace Title Header -->
<div style="margin-bottom: 25px;">
    <h1 style="font-size: 1.5rem; margin: 0 0 6px 0; color: var(--accent-white);">
        <?= htmlspecialchars($manifest['app_name'] ?? 'Trust Operations') ?> Directives
    </h1>
    <div style="font-size: 0.85rem; color: var(--text-muted);">
        Active Duty Filter: <strong style="color: var(--accent-white);"><?= htmlspecialchars($activeRole) ?></strong>
        <?php if ($selectedCategory !== 'all'): ?>
            &bull; Category: <code><?= htmlspecialchars($selectedCategory) ?></code>
        <?php endif; ?>
        <?php if (!empty($searchQuery)): ?>
            &bull; Search: "<code><?= htmlspecialchars($searchQuery) ?></code>"
        <?php endif; ?>
    </div>
</div>

<!-- Render Filtered Module Cards -->
<?php if (empty($filteredModules)): ?>
    <div class="feature-card">
        <div class="feature-title" style="color: var(--accent-red);">No Active Directives Found</div>
        <p style="color: var(--text-muted); margin-top: 10px; font-size: 0.9rem;">
            No matching operational modules match your current filter selection 
            (Role: <code><?= htmlspecialchars($activeRole) ?></code>, Query: "<code><?= htmlspecialchars($searchQuery) ?></code>").
        </p>
        <a href="guide.php?role=<?= htmlspecialchars($activeRole) ?>" class="role-btn" style="display: inline-block; margin-top: 10px;">Reset Filters</a>
    </div>
<?php else: ?>
    <?php foreach ($filteredModules as $module): ?>
        <div class="feature-card">
            <div class="feature-header">
                <h2 class="feature-title"><?= htmlspecialchars($module['title'] ?? 'Module Directive') ?></h2>
                <div style="display: flex; gap: 6px; align-items: center;">
                    <?php if (!empty($module['badge'])): ?>
                        <span class="badge badge-new"><?= htmlspecialchars($module['badge']) ?></span>
                    <?php endif; ?>
                    <span class="badge badge-ver">v<?= htmlspecialchars($module['version'] ?? $appVersion) ?></span>
                </div>
            </div>

            <p style="margin-top: 0; color: var(--text-main); line-height: 1.5; font-size: 0.92rem;">
                <?= htmlspecialchars($module['description'] ?? '') ?>
            </p>

            <?php if (!empty($module['steps']) && is_array($module['steps'])): ?>
                <ol>
                    <?php foreach ($module['steps'] as $step): ?>
                        <li><?= htmlspecialchars($step) ?></li>
                    <?php endforeach; ?>
                </ol>
            <?php endif; ?>

            <?php if (!empty($module['command_example'])): ?>
                <div style="margin-top: 15px;">
                    <span style="font-size: 0.72rem; text-transform: uppercase; color: var(--text-muted); font-weight: 700; display: block; margin-bottom: 4px;">Command / Syntax:</span>
                    <code><?= htmlspecialchars($module['command_example']) ?></code>
                </div>
            <?php endif; ?>

            <?php if (!empty($module['troubleshooting'])): ?>
                <div class="troubleshoot-box">
                    <strong>Notice:</strong> <?= htmlspecialchars($module['troubleshooting']) ?>
                </div>
            <?php endif; ?>
        </div>
    <?php endforeach; ?>
<?php endif; ?>

<?php
// 5. Render Footer Template
require_once __DIR__ . '/includes/footer.php';
?>
