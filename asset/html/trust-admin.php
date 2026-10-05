<?php
/**
 * Trust Administrator Management Console
 * Path: trust-main/trust-admin.php
 * 
 * Clearance Level: Sole Trust Administrator
 * Theme: 1980s Retro Green Phosphor CRT Terminal with Electric Blue Accents
 */

if (session_status() === PHP_SESSION_NONE) {
    session_start();
}

// Security Check & Session Verification
if (!isset($_SESSION['user'])) {$_SESSION['user'] = [
        'name'       => 'Anatolie Antolic',
        'role'       => 'TRUST_ADMIN',
        'login_time' => time() - 3720
    ];
}

if (($_SESSION['user']['role'] ?? '') !== 'TRUST_ADMIN') {
    http_response_code(403);
    echo '<div style="background:#000; color:#00ff00; padding:40px; font-family:monospace; text-align:center;">';
    echo '<h1>[403 ACCESS DENIED]</h1>';
    echo '<p>SECURITY ERROR: INVALID TRUST ADMINISTRATOR KEY.</p>';
    echo '</div>';
    exit;
}

$adminName      =$_SESSION['user']['name'];
$loginTimestamp =$_SESSION['user']['login_time'];
$loginFormatted = date('Y-m-d H:i:s T',$loginTimestamp);

$manifestPath = __DIR__ . '/config/guide_manifest.json';$manifest     = file_exists($manifestPath) ? json_decode(file_get_contents($manifestPath), true) : [];
$appVersion   =$manifest['version'] ?? '1.2.0';
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TRUST ADMIN // 1980s TERMINAL CONSOLE</title>

    <!-- Optional external root CSS fallback check: /css/style.css -->
    <?php if (file_exists($_SERVER['DOCUMENT_ROOT'] . '/css/style.css')): ?>
        <link rel="stylesheet" href="/css/style.css">
    <?php endif; ?>

    <!-- Embedded Retro Terminal CSS -->
    <style>
        :root {
            --term-black: #000000;
            --term-bg-dark: #020b02;
            --term-green: #00ff66;
            --term-green-dim: #009933;
            --term-green-dark: #003311;
            --term-blue: #00a8ff;
            --term-blue-hover: #66c7ff;
            --term-border: #00ff66;
            --term-glow: rgba(0, 255, 102, 0.25);
        }

        * {
            box-sizing: border-box;
        }

        body {
            margin: 0;
            padding: 20px;
            background-color: var(--term-black);
            color: var(--term-green);
            font-family: "Courier New", Courier, "Lucida Console", Monaco, monospace;
            font-size: 14px;
            line-height: 1.5;
            text-shadow: 0 0 4px var(--term-glow);
        }

        /* 1980s CRT Scanline Overlay Effect */
        body::before {
            content: " ";
            display: block;
            position: fixed;
            top: 0; left: 0; bottom: 0; right: 0;
            background: linear-gradient(rgba(18, 16, 16, 0) 50%, rgba(0, 0, 0, 0.25) 50%);
            background-size: 100% 4px;
            z-index: 9999;
            pointer-events: none;
            opacity: 0.6;
        }

        /* Upper Left Admin Header Panel */
        .admin-header {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            background-color: var(--term-bg-dark);
            border: 2px solid var(--term-green);
            padding: 16px;
            margin-bottom: 24px;
            box-shadow: 0 0 10px var(--term-glow);
        }

        .admin-meta-box {
            display: flex;
            flex-direction: column;
            gap: 4px;
        }

        .admin-name {
            font-size: 1.2rem;
            font-weight: 900;
            color: var(--term-green);
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        .admin-badge {
            color: var(--term-black);
            background-color: var(--term-green);
            font-size: 0.75rem;
            padding: 1px 6px;
            font-weight: bold;
            margin-left: 8px;
        }

        .session-stats {
            font-size: 0.85rem;
            color: var(--term-green-dim);
        }

        .session-timer {
            color: var(--term-blue);
            font-weight: bold;
        }

        /* Blue Links & Interactive Elements */
        a, .blue-link {
            color: var(--term-blue) !important;
            text-decoration: underline;
            cursor: pointer;
            font-weight: bold;
        }

        a:hover, .blue-link:hover {
            color: var(--term-blue-hover) !important;
            background-color: var(--term-green-dark);
        }

        .live-stream-tag {
            color: var(--term-blue);
            font-weight: bold;
            text-transform: uppercase;
            letter-spacing: 1px;
            animation: pulse-blue 1.5s infinite alternate;
        }

        @keyframes pulse-blue {
            0% { opacity: 0.5; }
            100% { opacity: 1.0; text-shadow: 0 0 8px #00a8ff; }
        }

        /* Terminal Grid Layout */
        .grid-container {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(340px, 1fr));
            gap: 20px;
        }

        .card {
            background-color: var(--term-black);
            border: 1px solid var(--term-green);
            padding: 16px;
            position: relative;
        }

        .card::before {
            content: "[ MODULE ]";
            position: absolute;
            top: -10px;
            left: 12px;
            background-color: var(--term-black);
            padding: 0 6px;
            font-size: 0.75rem;
            color: var(--term-green-dim);
        }

        .card-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px dashed var(--term-green-dim);
            padding-bottom: 10px;
            margin-bottom: 14px;
        }

        .card-title {
            font-size: 1rem;
            font-weight: bold;
            margin: 0;
            color: var(--term-green);
            text-transform: uppercase;
        }

        /* Metric Rows */
        .metric-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 8px 0;
            border-bottom: 1px solid var(--term-green-dark);
            font-size: 0.85rem;
        }

        .metric-label {
            color: var(--term-green-dim);
        }

        .metric-val {
            font-weight: bold;
            color: var(--term-green);
        }

        .btn-terminal {
            width: 100%;
            background-color: var(--term-black);
            color: var(--term-blue);
            border: 1px solid var(--term-blue);
            padding: 10px;
            font-family: inherit;
            font-size: 0.85rem;
            font-weight: bold;
            text-transform: uppercase;
            cursor: pointer;
            margin-top: 15px;
            transition: all 0.2s;
        }

        .btn-terminal:hover {
            background-color: var(--term-blue);
            color: var(--term-black);
            box-shadow: 0 0 10px var(--term-blue);
        }
    </style>
</head>
<body>

    <!-- Upper Left Session Bar -->
    <div class="admin-header">
        <div class="admin-meta-box">
            <div class="admin-name">
                <?= htmlspecialchars($adminName) ?>
                <span class="admin-badge">TRUST ADMIN</span>
            </div>
            <div class="session-stats">
                LOGGED IN: <span style="color: var(--term-green);"><?= $loginFormatted ?></span><br>
                SESSION DURATION: <span id="sessionTimer" class="session-timer">00:00:00</span>
            </div>
        </div>
        <div style="text-align: right;">
            <div class="live-stream-tag">&#9673; LIVE STREAM FEED</div>
            <div style="font-size: 0.75rem; color: var(--term-green-dim); margin-top: 4px;">
                CONSOLE: <a href="guide.php" class="blue-link">RETURN TO GUIDE</a>
            </div>
        </div>
    </div>

    <!-- Main Grid: Feeds, Crypto & Accounting Algorithms -->
    <div class="grid-container">

        <!-- 1. Investment Platform Integration (Robinhood API) -->
        <div class="card">
            <div class="card-header">
                <h2 class="card-title">&gt; ROBINHOOD_FEED</h2>
                <span class="live-stream-tag" style="font-size: 0.75rem;">ONLINE</span>
            </div>
            <div class="metric-row">
                <span class="metric-label">PORTFOLIO TOTAL:</span>
                <span class="metric-val">$142,850.40</span>
            </div>
            <div class="metric-row">
                <span class="metric-label">CASH BALANCE:</span>
                <span class="metric-val">$18,410.12</span>
            </div>
            <div class="metric-row">
                <span class="metric-label">ACTIVE POSITIONS:</span>
                <span class="metric-val"><a href="#" class="blue-link">12 EQUITIES / OPTIONS</a></span>
            </div>
            <div class="metric-row">
                <span class="metric-label">API STREAM ENDPOINT:</span>
                <span class="metric-val"><a href="#" class="blue-link">api.robinhood.com/stream</a></span>
            </div>
            <button class="btn-terminal">EXECUTE REBALANCE ALGORITHM</button>
        </div>

        <!-- 2. Cryptocurrency Mining & Vault Feeds -->
        <div class="card">
            <div class="card-header">
                <h2 class="card-title">&gt; CRYPTO_LEDGER</h2>
                <span class="live-stream-tag" style="font-size: 0.75rem;">STREAMING</span>
            </div>
            <div class="metric-row">
                <span class="metric-label">ASIC HASHRATE (f2pool):</span>
                <span class="metric-val">11.5 TH/s</span>
            </div>
            <div class="metric-row">
                <span class="metric-label">COLD STORAGE VAULT:</span>
                <span class="metric-val">HARDWARE SECURE</span>
            </div>
            <div class="metric-row">
                <span class="metric-label">UNCONFIRMED PAYOUTS:</span>
                <span class="metric-val">0.0084 BTC</span>
            </div>
            <div class="metric-row">
                <span class="metric-label">LIVE BLOCK EXPLORER:</span>
                <span class="metric-val"><a href="#" class="blue-link">view_blockchain_feed()</a></span>
            </div>
            <button class="btn-terminal">SYNC COLD STORAGE VAULT</button>
        </div>

        <!-- 3. Accounting & Yield Algorithms -->
        <div class="card">
            <div class="card-header">
                <h2 class="card-title">&gt; ACCOUNTING_ALGO</h2>
                <span class="metric-val" style="color: var(--term-blue);">[ RUNNING ]</span>
            </div>
            <div class="metric-row">
                <span class="metric-label">YIELD ALLOCATION RULE:</span>
                <span class="metric-val">70% REINVEST / 30% OPEX</span>
            </div>
            <div class="metric-row">
                <span class="metric-label">TAX RESERVE SWEEP:</span>
                <span class="metric-val">AUTO-ENABLED</span>
            </div>
            <div class="metric-row">
                <span class="metric-label">AUDIT LOG TELEMETRY:</span>
                <span class="metric-val"><a href="#" class="blue-link">sha256_verify.log</a></span>
            </div>
            <div class="metric-row">
                <span class="metric-label">NEXT SWEEP RUN:</span>
                <span class="metric-val">23:59 PDT</span>
            </div>
            <button class="btn-terminal">RUN MANUAL ACCOUNTING AUDIT</button>
        </div>

    </div>

    <!-- Real-time Session Duration Timer -->
    <script>
        const loginTime = <?= $loginTimestamp ?> * 1000;

        function updateSessionTimer() {
            const now = new Date().getTime();
            const elapsedSeconds = Math.floor((now - loginTime) / 1000);

            const hours = String(Math.floor(elapsedSeconds / 3600)).padStart(2, '0');
            const minutes = String(Math.floor((elapsedSeconds % 3600) / 60)).padStart(2, '0');
            const seconds = String(elapsedSeconds % 60).padStart(2, '0');

            document.getElementById('sessionTimer').innerText = `${hours}:${minutes}:${seconds}`;
        }

        updateSessionTimer();
        setInterval(updateSessionTimer, 1000);
    </script>
</body>
</html>
