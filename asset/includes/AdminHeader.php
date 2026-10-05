<?php
/**
 * Shared Admin Header - Access Controlled & Expanded Navigation
 * Path: includes/adminHeader.php
 */

if (session_status() === PHP_SESSION_NONE) {
    session_start();
}

// Strict Access Guard: Only TRUST_ADMIN is permitted.
// Non-admin or unauthenticated requests are redirected immediately to the First Responder interface.
$userRole = $_SESSION['user']['role'] ?? null;

if (!isset($_SESSION['user']) || $userRole !== 'TRUST_ADMIN') {
    header('Location: /responder/index.php');
    exit;
}

$adminName      = $_SESSION['user']['name'] ?? 'TRUST ADMINISTRATOR';
$loginTimestamp = $_SESSION['user']['login_time'] ?? time();
$loginFormatted = date('Y-m-d H:i:s T', $loginTimestamp);

// Active tab highlighting helper
$currentScript = basename($_SERVER['PHP_SELF']);
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title><?= htmlspecialchars($pageTitle ?? 'TRUST ADMIN // TERMINAL CONSOLE') ?></title>

    <!-- Shared 1980s Terminal Stylesheet -->
    <link rel="stylesheet" href="/css/style.css">
</head>
<body>

    <!-- Upper Admin Navigation Header -->
    <header class="admin-header">
        <div class="admin-meta-box">
            <div class="admin-name">
                &#9889; TRUST-MAIN <span style="color: var(--term-green-dim);">//</span> ADMIN CONSOLE
                <span class="admin-badge">SOLE TRUST ADMIN</span>
            </div>
            <div class="session-stats">
                ADMIN: <span style="color: var(--term-green);"><?= htmlspecialchars($adminName) ?></span> &bull; 
                LOGGED IN: <span><?= $loginFormatted ?></span> &bull; 
                SESSION DURATION: <span id="sessionTimerHeader" class="session-timer">00:00:00</span>
            </div>
        </div>

        <nav style="display: flex; flex-direction: column; align-items: flex-end; gap: 8px;">
            <div class="live-stream-tag">&#9673; RESTRICTED ADMIN FEED</div>
            
            <!-- Dynamic Navigation Tabs -->
            <div style="font-size: 0.82rem; display: flex; gap: 10px; flex-wrap: wrap; justify-content: flex-end;">
                <a href="trust-admin.php" class="blue-link <?= $currentScript === 'trust-admin.php' ? 'nav-active' : '' ?>">[ CONSOLE ]</a>
                <a href="accounts-manager.php" class="blue-link <?= $currentScript === 'accounts-manager.php' ? 'nav-active' : '' ?>">[ ACCOUNTS ]</a>
                <a href="audit-logs.php" class="blue-link <?= $currentScript === 'audit-logs.php' ? 'nav-active' : '' ?>">[ AUDIT LOGS ]</a>
                <a href="roster.php" class="blue-link <?= $currentScript === 'roster.php' ? 'nav-active' : '' ?>">[ ROSTER ]</a>
                <a href="guide.php" class="blue-link <?= $currentScript === 'guide.php' ? 'nav-active' : '' ?>">[ MANUAL ]</a>
                <a href="logout.php" class="blue-link" style="color: var(--term-red) !important;">[ LOG OUT ]</a>
            </div>
        </nav>
    </header>

    <!-- Voice Activation Banner -->
    <div class="voice-marquee-container">
        <div class="voice-marquee-text">
            &#9888;&#65039; THIS APP IS COMPLETELY VOICE ACTIVATED. PLEASE REFER TO THE USER'S MANUAL. &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; &#9888;&#65039; THIS APP IS COMPLETELY VOICE ACTIVATED. PLEASE REFER TO THE USER'S MANUAL.
        </div>
    </div>

    <!-- Main Content Wrapper -->
    <main class="main-content-wrapper">
