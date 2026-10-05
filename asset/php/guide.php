<?php
declare(strict_types=1);

// 1. Load JSON Feature Manifest
$manifestFile = __DIR__ . '/config/guide_manifest.json';
if (!file_exists($manifestFile)) {
    die("Error: User Guide Manifest not found at {$manifestFile}");
}

$manifest = json_decode(file_get_contents($manifestFile), true);
$appVersion =$manifest['current_version'] ?? '1.0.0';

// 2. Filter Inputs
$activeRole = strtoupper($_GET['role'] ?? $_SESSION['user_role'] ?? 'POLICE');
$searchQuery = strtolower(trim($_GET['q'] ?? ''));
$selectedCategory =$_GET['category'] ?? 'all';

// 3. Helper function to check if feature is new in current version
function isNewFeature(string $addedVersion, string$currentVersion): bool {
    return version_compare($addedVersion,$currentVersion, '>=');
}

// 4. Filter Features based on Role, Category, and Search
$filteredFeatures = array_filter($manifest['features'], function($item) use ($activeRole, $selectedCategory,$searchQuery) {
    // Role filter
    if (!in_array($activeRole,$item['roles'], true)) {
        return false;
    }
    // Category filter
    if ($selectedCategory !== 'all' && $item['category'] !==$selectedCategory) {
        return false;
    }
    // Search query filter
    if (!empty($searchQuery)) {
        $searchableText = strtolower($item['title'] . ' ' . $item['summary'] . ' ' . implode(' ', $item['instructions']));
        if (strpos($searchableText,$searchQuery) === false) {
            return false;
        }
    }
    return true;
});
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title><?= htmlspecialchars($manifest['app_name']) ?> // Dynamic User Guide</title>
    <style>
        :root {
            --bg-dark: #0a0e17;
            --panel-bg: #111827;
            --border: #1f2937;
            --accent: #2563eb;
            --accent-new: #059669;
            --text-main: #f3f4f6;
            --text-muted: #9ca3af;
        }
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, monospace; background: var(--bg-dark); color: var(--text-main); margin: 0; display: flex; min-height: 100vh; }
        .sidebar { width: 300px; background: var(--panel-bg); border-right: 1px solid var(--border); padding: 20px; box-sizing: border-box; }
        .main-content { flex: 1; padding: 30px; overflow-y: auto; }
        .brand { font-size: 1.1rem; font-weight: bold; margin-bottom: 20px; display: flex; justify-content: space-between; align-items: center; }
        .version-tag { background: var(--accent); font-size: 0.75rem; padding: 2px 8px; border-radius: 4px; }
        
        .search-box input { width: 100%; padding: 8px 12px; background: var(--bg-dark); border: 1px solid var(--border); color: #fff; border-radius: 6px; box-sizing: border-box; margin-bottom: 20px; }
        
        .role-picker { display: flex; gap: 6px; margin-bottom: 25px; flex-wrap: wrap; }
        .role-btn { padding: 4px 10px; background: var(--border); color: var(--text-muted); border-radius: 4px; text-decoration: none; font-size: 0.8rem; }
        .role-btn.active { background: var(--accent); color: #fff; }

        .nav-group { margin-bottom: 20px; }
        .nav-group-title { font-size: 0.75rem; text-transform: uppercase; color: var(--text-muted); margin-bottom: 8px; font-weight: bold; }
        .nav-link { display: block; padding: 6px 10px; color: var(--text-muted); text-decoration: none; font-size: 0.85rem; border-radius: 4px; }
        .nav-link:hover { background: var(--border); color: #fff; }

        .feature-card { background: var(--panel-bg); border: 1px solid var(--border); border-radius: 8px; padding: 20px; margin-bottom: 20px; }
        .feature-header { display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid var(--border); padding-bottom: 10px; margin-bottom: 15px; }
        .feature-title { font-size: 1.2rem; margin: 0; }
        
        .badge { font-size: 0.7rem; padding: 2px 6px; border-radius: 4px; text-transform: uppercase; font-weight: bold; }
        .badge-new { background: var(--accent-new); color: #fff; }
        .badge-ver { background: var(--border); color: var(--text-muted); }

        ol { padding-left: 20px; }
        li { margin-bottom: 8px; line-height: 1.5; }
        
        .troubleshoot-box { background: rgba(217, 119, 6, 0.1); border-left: 3px solid #d97706; padding: 10px 15px; border-radius: 4px; margin-top: 15px; font-size: 0.85rem; }
        code { background: rgba(255,255,255,0.08); padding: 2px 5px; border-radius: 3px; color: #60a5fa; }
    </style>
</head>
<body>

    <!-- Sidebar Auto-Built from Manifest Categories -->
    <div class="sidebar">
        <div class="brand">
            <?= htmlspecialchars($manifest['app_name']) ?>
            <span class="version-tag">v<?= htmlspecialchars($appVersion) ?></span>
        </div>

        <form method="GET" class="search-box">
            <input type="hidden" name="role" value="<?= htmlspecialchars($activeRole) ?>">
            <input type="text" name="q" placeholder="Search instructions..." value="<?= htmlspecialchars($searchQuery) ?>">
        </form>

        <div class="nav-group-title">Filter by Category</div>
        <a href="?role=<?= $activeRole ?>&category=all" class="nav-link <?= $selectedCategory === 'all' ? 'active' : '' ?>">All Modules</a>
        <?php foreach ($manifest['categories'] as$cat): ?>
            <a href="?role=<?= $activeRole ?>&category=<?= $cat['id'] ?>" class="nav-link <?= $selectedCategory ===$cat['id'] ? 'active' : '' ?>">
                <?= htmlspecialchars($cat['title']) ?>
            </a>
        <?php endforeach; ?>
    </div>

    <!-- Main Content Panel -->
    <div class="main-content">
        
        <!-- Role Switcher Bar -->
        <div class="role-picker">
            <span style="font-size:0.85rem; color: var(--text-muted); align-self: center;">Role Context:</span>
            <?php foreach (['POLICE', 'FIRE', 'EMS', 'DOT', 'LIFEGUARD'] as $role): ?>
                <a href="?role=<?= $role ?>&category=<?= $selectedCategory ?>" class="role-btn <?= $activeRole ===$role ? 'active' : '' ?>">
                    <?= $role ?>
                </a>
            <?php endforeach; ?>
        </div>

        <h1>Field Operations & Software Guide</h1>
        <p style="color: var(--text-muted); font-size: 0.9rem;">
            Showing instructions for active build <code>v<?= htmlspecialchars($appVersion) ?></code> (Role: <strong><?=$activeRole ?></strong>).
        </p>

        <!-- Feature List Dynamic Rendering -->
        <?php if (empty($filteredFeatures)): ?>
            <div class="feature-card">
                <p style="color: var(--text-muted);">No matching features or instructions found for this query/role combination.</p>
            </div>
        <?php else: ?>
            <?php foreach ($filteredFeatures as$feature): ?>
                <div class="feature-card" id="<?= htmlspecialchars($feature['id']) ?>">
                    <div class="feature-header">
                        <h3 class="feature-title">
                            <?= htmlspecialchars($feature['title']) ?>
                        </h3>
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

    </div>

</body>
</html>
