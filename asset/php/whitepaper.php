<?php
/**
 * TRUST-MAIN DYNAMIC WHITEPAPER GENERATOR
 * Dynamically builds system whitepaper documentation from config/config.yaml
 * and exposes version headers for PWA Service Worker caching.
 */

// 1. Load System Configuration
$configFile = __DIR__ . '/config/config.yaml';
$config = [];
if (file_exists($configFile) && function_exists('yaml_parse_file')) {
    $config = yaml_parse_file($configFile);
}

$appName    = $config['app_name'] ?? 'Trust-Main';
$appVersion = $config['version'] ?? '1.2';
$labId      = $config['system']['lab_id'] ?? 'MOBILE_LAB_01';
$mode       = $config['system']['mode'] ?? 'active_incident';
$agencies   = $config['agencies'] ?? [];
$lastUpdated = date('F j, Y');

// Set custom headers for PWA cache tracking
header("X-Whitepaper-Version: {$appVersion}-" . date('YmdH'));
header("Content-Type: text/html; charset=UTF-8");
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title><?= htmlspecialchars($appName) ?> v<?= htmlspecialchars($appVersion) ?> — Technical White Paper</title>

    <!-- PWA Manifest Link -->
    <link rel="manifest" href="manifest.json">
    <meta name="theme-color" content="#090d16">

    <style>
        :root {
            --bg: #090d16;
            --card-bg: #111827;
            --accent: #38bdf8;
            --text: #f3f4f6;
            --text-muted: #9ca3af;
            --border: rgba(56, 189, 248, 0.2);
            --code-bg: #1f2937;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            background-color: var(--bg);
            color: var(--text);
            line-height: 1.6;
            margin: 0;
            padding: 2rem 1rem;
        }

        .paper-container {
            max-width: 860px;
            margin: 0 auto;
            background: var(--card-bg);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 2.5rem;
            box-shadow: 0 10px 30px rgba(0,0,0,0.5);
        }

        .header-title {
            border-bottom: 2px solid var(--accent);
            padding-bottom: 1rem;
            margin-bottom: 1.5rem;
        }

        h1 {
            color: var(--accent);
            margin: 0 0 0.5rem 0;
            font-size: 2rem;
        }

        .meta-bar {
            display: flex;
            gap: 1.5rem;
            font-size: 0.85rem;
            color: var(--text-muted);
            font-family: monospace;
            flex-wrap: wrap;
        }

        .section {
            margin-top: 2rem;
        }

        h2 {
            color: #ffffff;
            font-size: 1.3rem;
            border-left: 3px solid var(--accent);
            padding-left: 0.75rem;
        }

        .spec-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
            gap: 1rem;
            margin-top: 1rem;
        }

        .spec-card {
            background: var(--code-bg);
            border: 1px solid rgba(255,255,255,0.05);
            border-radius: 6px;
            padding: 1rem;
        }

        .spec-title {
            font-weight: bold;
            color: var(--accent);
            font-size: 0.95rem;
            text-transform: uppercase;
        }

        .spec-val {
            font-family: monospace;
            font-size: 0.85rem;
            color: var(--text-muted);
            word-break: break-all;
        }

        .footer-note {
            margin-top: 3rem;
            border-top: 1px solid var(--border);
            padding-top: 1rem;
            font-size: 0.8rem;
            color: var(--text-muted);
            text-align: center;
        }
    </style>
</head>
<body>

<article class="paper-container">
    <header class="header-title">
        <h1><?= htmlspecialchars($appName) ?> Architecture & Field Specification</h1>
        <div class="meta-bar">
            <span>VERSION: v<?= htmlspecialchars($appVersion) ?></span>
            <span>LAB ID: <?= htmlspecialchars($labId) ?></span>
            <span>MODE: <?= htmlspecialchars(strtoupper($mode)) ?></span>
            <span>PUBLISHED: <?= $lastUpdated ?></span>
        </div>
    </header>

    <section class="section">
        <h2>1. Executive Summary & Deployment Architecture</h2>
        <p>
            <strong><?= htmlspecialchars($appName) ?></strong> is an independent, high-security, blockchain-backed forensic and administrative ecosystem engineered specifically for law enforcement, emergency dispatch, and legal compliance teams. Operating independently of commercial application stores, it deploys directly to department devices via Progressive Web Application (PWA) standards and auditable source repositories.
        </p>
    </section>

    <section class="section">
        <h2>2. Active Agency Dispatches & Compliance Specs</h2>
        <p>The system dynamically coordinates field operations across multiple emergency service domains:</p>
        
        <div class="spec-grid">
            <?php foreach ($agencies as $agencyName => $agencyData): ?>
            <div class="spec-card">
                <div class="spec-title"><?= strtoupper($agencyName) ?> SERVICE</div>
                <div>Format: <strong><?= htmlspecialchars($agencyData['report_format'] ?? 'N/A') ?></strong></div>
                <div class="spec-val"><?= htmlspecialchars($agencyData['endpoint'] ?? '') ?></div>
            </div>
            <?php endforeach; ?>
        </div>
    </section>

    <section class="section">
        <h2>3. Forensic Integrity & ISO Compliance</h2>
        <p>
            All evidence collection and telemetry records created within <?= htmlspecialchars($appName) ?> are bound to an immutable blockchain ledger via the <code>ReportPackagePublisher</code> pipeline. The platform adheres strictly to <strong>ISO/IEC 17025</strong> laboratory standards, providing chain-of-custody verification suitable for judicial presentation.
        </p>
    </section>

    <footer class="footer-note">
        Generated dynamically by <?= htmlspecialchars($appName) ?> Engine | PMR Publications Ecosystem
    </footer>
</article>

<script>
    if ('serviceWorker' in navigator) {
        navigator.serviceWorker.register('/sw.js');
    }
</script>
</body>
</html>
