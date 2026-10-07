<?php
/**
 * Role & Credentials Setup
 */
$activeRole = strtolower($activeRole ?? $_SESSION['role'] ?? 'standard');

// Define clearance levels
$isTrustAdmin = in_array($activeRole, ['trust_admin', 'admin', 'sysadmin']);
$isResponder  = in_array($activeRole, ['first_responder', 'first_responder_admin', 'responder']);
$isStandard   = !$isTrustAdmin && !$isResponder;
?>

<!-- Sidebar Navigation (Left Panel) -->
<aside class="sidebar">
    <!-- Live Device System Clock -->
    <div id="os-live-clock" class="os-clock"></div>

    <div class="brand">
        <span><?= htmlspecialchars($manifest['app_name'] ?? 'Trust-Shell') ?></span>
        <span class="version-badge">v<?= htmlspecialchars($appVersion ?? '1.0') ?></span>
    </div>

    <!-- Search box only visible to Admins and Responders -->
    <?php if (!$isStandard): ?>
    <form method="GET" class="search-box" action="<?= htmlspecialchars(basename($_SERVER['PHP_SELF'])) ?>">
        <input type="hidden" name="role" value="<?= htmlspecialchars($activeRole) ?>">
        <input type="text" name="q" placeholder="Search roster or guide..." value="<?= htmlspecialchars($searchQuery ?? '') ?>">
    </form>
    <?php endif; ?>

    <!-- System Navigation based on Credentials -->
    <div>
        <div class="nav-group-title">
            <?= $isTrustAdmin ? 'SYSTEM ADMIN CONSOLE' : ($isResponder ? 'RESPONDER SYSTEM' : 'VOICE INTERFACE') ?>
        </div>
        
        <nav class="nav-links">
            <!-- Duty Roster / Main Screen -->
            <a href="index.php?role=<?= $activeRole ?>" class="nav-link <?= basename($_SERVER['PHP_SELF']) === 'index.php' ? 'active' : '' ?>">
                &#128100; <?= $isStandard ? 'Voice Control Screen' : 'Duty Roster' ?>
            </a>

            <!-- 1. TRUST ADMIN EXCLUSIVE LINKS -->
            <?php if ($isTrustAdmin): ?>
                <a href="app_status.php?role=<?= $activeRole ?>" class="nav-link <?= basename($_SERVER['PHP_SELF']) === 'app_status.php' ? 'active' : '' ?>">
                    &#128187; App Behavior & Health
                </a>
                <a href="payroll.php?role=<?= $activeRole ?>" class="nav-link <?= basename($_SERVER['PHP_SELF']) === 'payroll.php' ? 'active' : '' ?>">
                    &#128178; Payroll Maintenance
                </a>
                <a href="onboarding.php?role=<?= $activeRole ?>" class="nav-link <?= basename($_SERVER['PHP_SELF']) === 'onboarding.php' ? 'active' : '' ?>">
                    &#128221; Admin Onboarding
                </a>

            <!-- 2. FIRST RESPONDER EXCLUSIVE LINKS -->
            <?php elseif ($isResponder): ?>
                <a href="guide.php?role=<?= $activeRole ?>" class="nav-link <?= basename($_SERVER['PHP_SELF']) === 'guide.php' ? 'active' : '' ?>">
                    &#128216; User's Guide
                </a>
                <a href="responder_onboarding.php?role=<?= $activeRole ?>" class="nav-link <?= basename($_SERVER['PHP_SELF']) === 'responder_onboarding.php' ? 'active' : '' ?>">
                    &#128657; Responder Onboarding
                </a>

            <!-- 3. STANDARD USER (VOICE MODE) -->
            <?php else: ?>
                <div class="voice-mode-indicator">
                    <span class="mic-icon">&#127908;</span> Hands-Free Voice Active
                </div>
            <?php endif; ?>

            <!-- External Link (All Users) -->
            <a href="https://www.magcloud.com/user/YOUR_MAGCLOUD_HANDLE_HERE" target="_blank" rel="noopener noreferrer" class="nav-link" style="color: var(--code-text);">
                &#128279; MagCloud Releases &rarr;
            </a>
        </nav>
    </div>

    <!-- Guide Categories (Active for Admins & Responders only) -->
    <?php if (!$isStandard && !empty($manifest['categories'])): ?>
    <div>
        <div class="nav-group-title">Guide Categories</div>
        <nav class="nav-links">
            <a href="guide.php?role=<?= $activeRole ?>&category=all" class="nav-link <?= ($selectedCategory === 'all' && basename($_SERVER['PHP_SELF']) === 'guide.php') ? 'active' : '' ?>">
                All Modules
            </a>
            <?php foreach ($manifest['categories'] as $cat): ?>
                <a href="guide.php?role=<?= $activeRole ?>&category=<?= $cat['id'] ?>" class="nav-link <?= ($selectedCategory === $cat['id'] && basename($_SERVER['PHP_SELF']) === 'guide.php') ? 'active' : '' ?>">
                    <?= htmlspecialchars($cat['title']) ?>
                </a>
            <?php endforeach; ?>
        </nav>
    </div>
    <?php endif; ?>
</aside>

<!-- Styles for Live Clock -->
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

<!-- Script for Device Clock -->
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
