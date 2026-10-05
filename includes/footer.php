<?php
/**
 * Global Footer Template - Trust-Shell Operations Portal
 */
$executionTime = round((microtime(true) - ($_SERVER["REQUEST_TIME_FLOAT"] ?? microtime(true))) * 1000, 2);
?>
        <!-- Footer Meta -->
        <footer>
            <div>
                <strong><?= htmlspecialchars($manifest['app_name'] ?? 'Trust-Shell') ?></strong> Operations Guide 
                &bull; System Sync: <?= date('Y-m-d H:i:s T') ?>
            </div>
            <div>
                Render Time: <code><?= $executionTime ?>ms</code> &bull; System Status: <span style="color: var(--accent-blue);">ONLINE</span>
            </div>
        </footer>

    </main><!-- /.main-content -->

</div><!-- /.layout-wrapper -->

</body>
</html>
