<?php
/**
 * Sidebar Navigation Panel with Live Device Clock
 */
?>
<!-- Sidebar Navigation (Left Panel) -->
<aside class="sidebar">
    <!-- Live Device System Clock -->
    <div id="os-live-clock" class="os-clock"></div>

    <div class="brand">
        <span><?= htmlspecialchars($manifest['app_name'] ?? 'Trust-Shell') ?></span>
        <span class="version-badge">v<?= htmlspecialchars($appVersion) ?></span>
    </div>

    <form method="GET" class="search-box" action="<?= htmlspecialchars(basename($_SERVER['PHP_SELF'])) ?>">
        <input type="hidden" name="role" value="<?= htmlspecialchars($activeRole) ?>">
        <input type="text" name="q" placeholder="Search roster or guide..." value="<?= htmlspecialchars($searchQuery) ?>">
    </form>

    <!-- System Navigation -->
    <div>
        <div class="nav-group-title">System Navigation</div>
        <nav class="nav-links">
            <a href="index.php?role=<?= $activeRole ?>" class="nav-link <?= basename($_SERVER['PHP_SELF']) === 'index.php' ? 'active' : '' ?>">
                &#128100; Duty Roster
            </a>
            <a href="guide.php?role=<?= $activeRole ?>" class="nav-link <?= basename($_SERVER['PHP_SELF']) === 'guide.php' ? 'active' : '' ?>">
                &#128216; User's Guide
            </a>
            <!-- MagCloud Releases External Link -->
            <a href="https://www.magcloud.com/user/YOUR_MAGCLOUD_HANDLE_HERE" target="_blank" rel="noopener noreferrer" class="nav-link" style="color: var(--code-text);">
                &#128279; MagCloud Releases &rarr;
            </a>
        </nav>
    </div>

    <!-- Module Categories -->
    <div>
        <div class="nav-group-title">Guide Categories</div>
        <nav class="nav-links">
            <a href="guide.php?role=<?= $activeRole ?>&category=all" class="nav-link <?= ($selectedCategory === 'all' && basename($_SERVER['PHP_SELF']) === 'guide.php') ? 'active' : '' ?>">
                All Modules
            </a>
            <?php if (!empty($manifest['categories'])): ?>
                <?php foreach ($manifest['categories'] as $cat): ?>
                    <a href="guide.php?role=<?= $activeRole ?>&category=<?= $cat['id'] ?>" class="nav-link <?= ($selectedCategory === $cat['id'] && basename($_SERVER['PHP_SELF']) === 'guide.php') ? 'active' : '' ?>">
                        <?= htmlspecialchars($cat['title']) ?>
                    </a>
                <?php endforeach; ?>
            <?php endif; ?>
        </nav>
    </div>
</aside>

<style>
    .os-clock {
        font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", "Segoe UI", Roboto, sans-serif;
        font-size: 0.85rem;
        font-weight: 600;
        letter-spacing: -0.2px;
        color: var(--text-muted, #8a8d93);
        margin-bottom: 0.5rem;
        padding-left: 0.2rem;
        user-select: none;
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
