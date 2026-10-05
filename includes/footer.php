<?php
/**
 * Global Footer Template - Trust-Shell Operations Portal
 */
$executionTime = round((microtime(true) - ($_SERVER["REQUEST_TIME_FLOAT"] ?? microtime(true))) * 1000, 2);

// Duty / Clock Status Check
// Evaluates $isOnClock variable, $_SESSION['is_on_clock'], or GET parameter ?clocked_in=1
if (!isset($isOnClock)) {
    if (isset($_GET['clocked_in'])) {
        $isOnClock = filter_var($_GET['clocked_in'], FILTER_VALIDATE_BOOLEAN);
    } else {
        $isOnClock = $_SESSION['is_on_clock'] ?? true; // Default to online/on-clock
    }
}

// Color and Text Assignment
$statusText  = $isOnClock ? 'ONLINE' : 'OFFLINE';
$statusColor = $isOnClock ? '#10b981' : '#dc2626'; // Green for Online, Red for Offline
?>
        <!-- Footer Meta -->
        <footer>
            <div>
                <strong><?= htmlspecialchars($manifest['app_name'] ?? 'Trust-Shell') ?></strong> Operations Guide 
                &bull; &copy; 2026 PMR Publications
                &bull; System Sync: <?= date('Y-m-d H:i:s T') ?>
            </div>
            <div>
                Render Time: <code><?= $executionTime ?>ms</code> 
                &bull; Duty Status: <span style="color: <?= $statusColor ?>; font-weight: 700; letter-spacing: 0.5px;"><?= $statusText ?></span>
            </div>
        </footer>

    </main><!-- /.main-content -->

</div><!-- /.layout-wrapper -->

</body>
</html>
