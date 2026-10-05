<?php
/**
 * Trust Administrator Management Console
 * Path: trust-main/trust-admin.php
 */

$pageTitle = "TRUST ADMIN // MANAGEMENT CONSOLE";

// Including adminHeader enforces the TRUST_ADMIN security check automatically
require_once __DIR__ . '/includes/adminHeader.php';
?>

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

<?php
require_once __DIR__ . '/includes/adminFooter.php';
?>
