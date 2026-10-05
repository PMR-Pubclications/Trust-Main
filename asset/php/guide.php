<?php
declare(strict_types=1);

// Load Manifest Data
$manifestFile = __DIR__ . '/config/guide_manifest.json';
if (!file_exists($manifestFile)) {
    die("Error: Guide Manifest not found at {$manifestFile}");
}

$manifest = json_decode(file_get_contents($manifestFile), true);
$appVersion =$manifest['current_version'] ?? '1.0.0';

// Query Parameters
$activeRole = strtoupper($_GET['role'] ?? $_SESSION['user_role'] ?? 'POLICE');
$searchQuery = strtolower(trim($_GET['q'] ?? ''));
$selectedCategory =$_GET['category'] ?? 'all';

// Filter Logic
$filteredFeatures = array_filter($manifest['features'], function($item) use ($activeRole, $selectedCategory,$searchQuery) {
    if (!in_array($activeRole,$item['roles'], true)) return false;
    if ($selectedCategory !== 'all' && $item['category'] !==$selectedCategory) return false;
    if (!empty($searchQuery)) {
        $searchableText = strtolower($item['title'] . ' ' . $item['summary'] . ' ' . implode(' ', $item['instructions']));
        if (strpos($searchableText,$searchQuery) === false) return false;
    }
    return true;
});

// Helper for "New" Badge
function isNewFeature(string $addedVersion, string$currentVersion): bool {
    return version_compare($addedVersion,$currentVersion, '>=');
}

// 1. INCLUDE HEADER
require_once __DIR__ . '/includes/header.php';
?>

<h1>Field Operations & Software Guide</h1>
<p style="color: var(--text-muted); font-size: 0.9rem; margin-bottom: 25px;">
    Filtered instructions for <strong><?= htmlspecialchars($activeRole) ?></strong> context.
</p>

<?php if (empty($filteredFeatures)): ?>
    <div class="feature-card">
        <p style="color: var(--text-muted); margin: 0;">No matching features or directives found for this search/role combination.</p>
    </div>
<?php else: ?>
    <?php foreach ($filteredFeatures as$feature): ?>
        <div class="feature-card" id="<?= htmlspecialchars($feature['id']) ?>">
            <div class="feature-header">
                <h3 class="feature-title"><?= htmlspecialchars($feature['title']) ?></h3>
                <div>
                    <?php if (isNewFeature($feature['added_in_version'],$appVersion)): ?>
                        <span class="badge badge-new">New in v<?= htmlspecialchars($feature['added_in_version']) ?></span>
                    <?php else: ?>
                        <span class="badge badge-ver">Updated v<?= htmlspecialchars($feature['last_updated_version']) ?></span>
                    <?php endif; ?>
                </div>
            </div>

            <p><strong>Overview:</strong> <?= htmlspecialchars($feature['summary']) ?></p>

            <h4>Standard Operating Procedure:</h4>
            <ol>
                <?php foreach ($feature['instructions'] as$step): ?>
                    <li><?= preg_replace('/`([^`]+)`/', '<code>$1</code>', htmlspecialchars($step)) ?></li>
                <?php endforeach; ?>
            </ol>

            <?php if (!empty($feature['troubleshooting'])): ?>
                <div class="troubleshoot-box">
                    <strong>Diagnostic / Recovery:</strong><br>
                    <?= preg_replace('/`([^`]+)`/', '<code>$1</code>', htmlspecialchars($feature['troubleshooting'])) ?>
                </div>
            <?php endif; ?>
        </div>
    <?php endforeach; ?>
<?php endif; ?>

<?php
// 2. INCLUDE FOOTER
require_once __DIR__ . '/includes/footer.php';
?>
