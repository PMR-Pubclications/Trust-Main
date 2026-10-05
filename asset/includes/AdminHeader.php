<?php
/**
 * Trust Administrator - Core Layout Header & Side Navigation
 * Path: trust-main/includes/adminHeader.php
 */

$currentPage = basename($_SERVER['PHP_SELF']);
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title><?= $pageTitle ?? 'TRUST ADMIN CONSOLE' ?></title>
    <style>
        :root {
            --term-green: #00ff66;
            --term-green-dim: #009933;
            --term-green-dark: #003311;
            --term-blue: #00ccff;
            --term-red: #ff3333;
            --term-black: #050b05;
            --term-bg-dark: #0a140a;
            --term-glow: rgba(0, 255, 102, 0.2);
            --font-terminal: 'Courier New', Courier, monospace;
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }

        body {
            background-color: var(--term-black);
            color: var(--term-green);
            font-family: var(--font-terminal);
            display: flex;
            min-height: 100vh;
        }

        /* Side Menu Layout */
        .admin-sidebar {
            width: 260px;
            background-color: var(--term-bg-dark);
            border-right: 2px solid var(--term-green-dark);
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            padding: 20px 0;
            flex-shrink: 0;
        }

        .sidebar-brand {
            padding: 0 20px 20px 20px;
            border-bottom: 1px solid var(--term-green-dark);
            margin-bottom: 20px;
        }

        .sidebar-brand h1 {
            font-size: 1.1rem;
            letter-spacing: 1px;
            color: var(--term-green);
        }

        .sidebar-brand span {
            font-size: 0.75rem;
            color: var(--term-green-dim);
            display: block;
            margin-top: 4px;
        }

        .nav-list {
            list-style: none;
            display: flex;
            flex-direction: column;
            gap: 6px;
            padding: 0 10px;
        }

        .nav-item a {
            display: flex;
            align-items: center;
            padding: 10px 14px;
            color: var(--term-green-dim);
            text-decoration: none;
            font-size: 0.88rem;
            border: 1px solid transparent;
            transition: all 0.15s ease-in-out;
        }

        .nav-item a:hover {
            color: var(--term-green);
            background-color: rgba(0, 255, 102, 0.05);
            border-color: var(--term-green-dark);
        }

        .nav-item.active a {
            color: var(--term-black);
            background-color: var(--term-green);
            font-weight: bold;
            border-color: var(--term-green);
            box-shadow: 0 0 8px var(--term-glow);
        }

        .nav-item.active-blue a {
            color: var(--term-black);
            background-color: var(--term-blue);
            font-weight: bold;
            border-color: var(--term-blue);
        }

        .sidebar-footer {
            padding: 15px 20px 0 20px;
            border-top: 1px solid var(--term-green-dark);
            font-size: 0.75rem;
            color: var(--term-green-dim);
        }

        /* Main Content Viewport */
        .admin-main-viewport {
            flex: 1;
            padding: 24px;
            overflow-y: auto;
            background-color: var(--term-black);
        }

        /* Shared UI Cards & Utility CSS */
        .card {
            background-color: var(--term-bg-dark);
            border: 1px solid var(--term-green-dark);
            padding: 16px;
            border-radius: 2px;
        }

        .card-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 14px;
            padding-bottom: 8px;
            border-bottom: 1px solid var(--term-green-dark);
        }

        .card-title {
            font-size: 0.95rem;
            color: var(--term-green);
        }

        .blue-link {
            color: var(--term-blue) !important;
            text-decoration: none;
        }

        .blue-link:hover {
            text-decoration: underline;
        }

        .btn-terminal {
            background-color: var(--term-black);
            border: 1px solid var(--term-green);
            color: var(--term-green);
            font-family: var(--font-terminal);
            cursor: pointer;
        }

        .live-stream-tag {
            color: var(--term-green);
            animation: pulse 1.5s infinite;
        }

        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.3; }
            100% { opacity: 1; }
        }
    </style>
</head>
<body>

<!-- Side Navigation Menu -->
<aside class="admin-sidebar">
    <div>
        <div class="sidebar-brand">
            <h1>&gt; TRUST_ADMIN</h1>
            <span>VERSION 2.6.0 // SECURE</span>
        </div>

        <ul class="nav-list">
            <li class="nav-item <?= $currentPage === 'dashboard.php' || $currentPage === 'index.php' ? 'active' : '' ?>">
                <a href="dashboard.php">&gt; DASHBOARD</a>
            </li>

            <li class="nav-item <?= $currentPage === 'accounts.php' ? 'active' : '' ?>">
                <a href="accounts.php">&gt; ACCOUNTS &amp; YIELD</a>
            </li>

            <!-- Added Audit Logs Item -->
            <li class="nav-item <?= $currentPage === 'audit-logs.php' ? 'active-blue' : '' ?>">
                <a href="audit-logs.php" style="<?= $currentPage === 'audit-logs.php' ? '' : 'color: var(--term-blue);' ?>">
                    &gt; AUDIT &amp; TELEMETRY
                </a>
            </li>

            <li class="nav-item <?= $currentPage === 'cron-settings.php' ? 'active' : '' ?>">
                <a href="cron-settings.php">&gt; CRON ENGINE</a>
            </li>

            <li class="nav-item <?= $currentPage === 'security.php' ? 'active' : '' ?>">
                <a href="security.php">&gt; SYSTEM SECURITY</a>
            </li>
        </ul>
    </div>

    <div class="sidebar-footer">
        <div>USER: <?= htmlspecialchars($_SESSION['user']['username'] ?? 'ADMIN') ?></div>
        <div style="margin-top: 6px;">
            <a href="/responder/logout.php" style="color: var(--term-red); text-decoration: none;">[ LOGOUT ]</a>
        </div>
    </div>
</aside>

<!-- Main Page Viewport Container Starts Here -->
<main class="admin-main-viewport">
