<?php
/**
 * DYNAMIC SIDEBAR NAVIGATION
 */

// 1. Resolve Active Credentials
$activeRole = strtolower($activeRole ?? $_SESSION['role'] ?? 'standard');
$isStandard = !in_array($activeRole, ['trust_admin', 'admin', 'first_responder', 'responder']);

// 2. Load Capabilities Registry (falls back to manifest if file missing)
$capabilities = file_exists(__DIR__ . '/config/modules.php') 
    ? require __DIR__ . '/config/modules.php' 
    : ($manifest['capabilities'] ?? []);

// 3. Filter Capabilities by User Credentials
$userCapabilities = array_filter($capabilities, function($item) use ($activeRole) {
    if (empty($item['allowed_roles'])) return true;
    return in_array($activeRole, $item['allowed_roles']);
});

$currentPage = basename($_SERVER['PHP_SELF']);
?>

<!-- Sidebar Navigation (Left Panel) -->
<aside class="sidebar">
    <!-- Live Device System Clock -->
    <div id="os-live-clock" class="os-clock"></div>

    <div class="brand">
        <span><?= htmlspecialchars($manifest['app_name'] ?? 'Trust-Shell') ?></span>
        <span class="version-badge">v<?= htmlspecialchars($appVersion ?? '1.0') ?></span>
    </div>

    <?php if (!$isStandard): ?>
    <form method="GET" class="search-box" action="<?= htmlspecialchars($currentPage) ?>">
        <input type="hidden" name="role" value="<?= htmlspecialchars($activeRole) ?>">
        <input type="text" name="q" placeholder="Search roster or guide..." value="<?= htmlspecialchars($searchQuery ?? '') ?>">
    </form>
    <?php endif; ?>

    <!-- Dynamically Rendered Capabilities -->
    <div>
        <div class="nav-group-title">
            <?= $activeRole === 'trust_admin' ? 'TRUST ADMIN CONSOLE' : ($isStandard ? 'VOICE INTERFACE' : 'RESPONDER SYSTEM') ?>
        </div>

        <nav class="nav-links">
            <?php foreach ($userCapabilities as $cap): ?>
                <?php $isActive = ($currentPage === $cap['url']); ?>
                <a href="<?= htmlspecialchars($cap['url']) ?>?role=<?= urlencode($activeRole) ?>" 
                   class="nav-link <?= $isActive ? 'active' : '' ?>">
                    <?= $cap['icon'] ?> <?= htmlspecialchars($cap['title']) ?>
                </a>
            <?php endforeach; ?>

            <!-- Voice Control Banner for Standard Mode -->
            <?php if ($isStandard): ?>
                <div class="voice-mode-indicator">
                    <span class="mic-icon">&#127908;</span> Hands-Free Voice Active
                </div>
            <?php endif; ?>

            <!-- External Releases Link -->
            <a href="https://www.magcloud.com/user/YOUR_MAGCLOUD_HANDLE_HERE" target="_blank" rel="noopener noreferrer" class="nav-link" style="color: var(--code-text);">
                &#128279; MagCloud Releases &rarr;
            </a>
        </nav>
    </div>

    <!-- Guide Categories (Dynamic Loop) -->
    <?php if (!$isStandard && !empty($manifest['categories'])): ?>
    <div>
        <div class="nav-group-title">Guide Categories</div>
        <nav class="nav-links">
            <a href="guide.php?role=<?= urlencode($activeRole) ?>&category=all" 
               class="nav-link <?= (($selectedCategory ?? '') === 'all' && $currentPage === 'guide.php') ? 'active' : '' ?>">
                All Modules
            </a>
            <?php foreach ($manifest['categories'] as $cat): ?>
                <a href="guide.php?role=<?= urlencode($activeRole) ?>&category=<?= urlencode($cat['id']) ?>" 
                   class="nav-link <?= (($selectedCategory ?? '') === $cat['id'] && $currentPage === 'guide.php') ? 'active' : '' ?>">
                    <?= htmlspecialchars($cat['title']) ?>
                </a>
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
        margin-bottom: 0.5rem;
        padding-left: 0.2rem;
        user-select: none;
    }
    .voice-mode-indicator {
        padding: 0.5rem;
        font-size: 0.85rem;
        color: var(--accent-color);
        font-weight: bold;
        border: 1px dashed var(--accent-color);
        border-radius: 4px;
        margin: 0.5rem 0;
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
