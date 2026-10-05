<?php
/**
 * Shared Admin Footer - Terminal Edition
 * Path: includes/adminFooter.php
 */
?>
    </main> <!-- End Main Wrapper -->

    <!-- Restricted Admin Footer Console -->
    <footer style="margin-top: 40px; border-top: 2px solid var(--term-green); background-color: var(--term-bg-dark); padding: 20px; box-shadow: 0 0 10px var(--term-glow);">
        <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px dashed var(--term-green-dark); padding-bottom: 12px; margin-bottom: 12px;">
            <div>
                <span style="font-weight: bold; color: var(--term-green);">&gt; ADMIN TELEMETRY:</span> 
                <span style="color: var(--term-blue);">RESTRICTED ACCESS LEVEL 0 // ZERO-KNOWLEDGE ENCRYPTED</span>
            </div>
            <div style="font-family: var(--font-terminal); font-size: 0.85rem;">
                SYSTEM TIME: <span id="liveFooterClock" style="color: var(--term-green); font-weight: bold;">--:--:--</span>
            </div>
        </div>

        <div style="display: flex; justify-content: space-between; align-items: center; font-size: 0.8rem; color: var(--term-green-dim);">
            <div>
                &copy; <?= date('Y') ?> TRUST FORENSIC SYSTEM &bull; PMR PUBLICATIONS &bull; TRUSTEE CONFIDENTIAL
            </div>
            <div style="display: flex; gap: 12px;">
                <a href="guide.php" class="blue-link">DOCUMENTATION</a>
                <a href="audit.php" class="blue-link">SYSTEM LOGS</a>
                <a href="#" class="blue-link" onclick="window.scrollTo({top: 0, behavior: 'smooth'}); return false;">[ BACK TO TOP ]</a>
            </div>
        </div>
    </footer>

    <!-- Real-Time Session Timer Script -->
    <script>
        (function() {
            const loginTimeMs = <?= ($loginTimestamp ?? time()) ?> * 1000;

            function updateClocks() {
                const now = new Date();
                
                // Live Footer Clock
                const timeStr = now.toTimeString().split(' ')[0] + ' ' + (Intl.DateTimeFormat().resolvedOptions().timeZone || '');
                const clockElem = document.getElementById('liveFooterClock');
                if (clockElem) clockElem.innerText = timeStr;

                // Session Duration Timer
                const elapsedSeconds = Math.floor((now.getTime() - loginTimeMs) / 1000);
                if (elapsedSeconds >= 0) {
                    const hrs = String(Math.floor(elapsedSeconds / 3600)).padStart(2, '0');
                    const mins = String(Math.floor((elapsedSeconds % 3600) / 60)).padStart(2, '0');
                    const secs = String(elapsedSeconds % 60).padStart(2, '0');
                    
                    const timerHeader = document.getElementById('sessionTimerHeader');
                    if (timerHeader) timerHeader.innerText = `${hrs}:${mins}:${secs}`;
                }
            }

            updateClocks();
            setInterval(updateClocks, 1000);
        })();
    </script>
</body>
</html>
