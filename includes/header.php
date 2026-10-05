<?php
/**
 * Global Header Template - Trust-Shell Operations Portal
 * Expects: $manifest, $appVersion, $activeRole, $selectedCategory, $searchQuery
 */
$pageTitle = $pageTitle ?? ($manifest['app_name'] . ' // Operations & Software Guide');
$activeRole = $activeRole ?? 'POLICE';
$searchQuery = $searchQuery ?? '';
$selectedCategory = $selectedCategory ?? 'all';
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title><?= htmlspecialchars($pageTitle) ?></title>
    <style>
        /* Tactical Red, White, and Blue Theme */
        :root {
            --bg-dark: #070a12;          /* Deepest Navy / Charcoal */
            --panel-bg: #0f172a;        /* Slate Navy Card Background */
            --border: #1e293b;          /* Steel Navy Border */
            --border-bright: #334155;   /* High-Contrast Border */
            
            --accent-blue: #2563eb;     /* Primary Operational Blue */
            --accent-blue-hover: #1d4ed8;
            --accent-red: #dc2626;      /* Alert / High-Priority Red */
            --accent-red-hover: #b91c1c;
            --accent-white: #ffffff;    /* Pure White Highlight */
            
            --text-main: #f8fafc;       /* Bright Crisp White Text */
            --text-muted: #94a3b8;      /* Muted Slate Text */
            
            --code-bg: rgba(37, 99, 235, 0.12);
            --code-text: #60a5fa;
            --warn-bg: rgba(220, 38, 38, 0.1);
        }

        * { box-sizing: border-box; }

        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, monospace;
            background-color: var(--bg-dark);
            color: var(--text-main);
            margin: 0;
            display: flex;
            min-height: 100vh;
        }

        .layout-wrapper {
            display: flex;
            width: 100%;
            min-height: 100vh;
        }

        /* Sidebar Styling */
        .sidebar {
            width: 300px;
            background-color: var(--panel-bg);
            border-right: 1px solid var(--border-bright);
            padding: 24px 20px;
            display: flex;
            flex-direction: column;
            gap: 20px;
            flex-shrink: 0;
        }

        .brand {
            font-size: 1.15rem;
            font-weight: 700;
            letter-spacing: 0.5px;
            color: var(--accent-white);
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 2px solid var(--accent-red);
            padding-bottom: 10px;
        }

        .version-badge {
            background-color: var(--accent-blue);
            color: var(--accent-white);
            font-size: 0.75rem;
            padding: 2px 8px;
            border-radius: 4px;
            font-weight: 700;
        }

        /* Search Box Input */
        .search-box input {
            width: 100%;
            padding: 10px 14px;
            background-color: var(--bg-dark);
            border: 1px solid var(--border-bright);
            color: var(--accent-white);
            border-radius: 6px;
            font-size: 0.85rem;
            outline: none;
            transition: border-color 0.2s, box-shadow 0.2s;
        }

        .search-box input:focus {
            border-color: var(--accent-blue);
            box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.25);
        }

        /* Navigation Links */
        .nav-group-title {
            font-size: 0.7rem;
            text-transform: uppercase;
            color: var(--text-muted);
            letter-spacing: 1px;
            font-weight: 700;
            margin-bottom: 8px;
        }

        .nav-links {
            display: flex;
            flex-direction: column;
            gap: 4px;
        }

        .nav-link {
            display: block;
            padding: 8px 12px;
            color: var(--text-muted);
            text-decoration: none;
            font-size: 0.88rem;
            border-radius: 6px;
            border-left: 3px solid transparent;
            transition: all 0.15s ease;
        }

        .nav-link:hover {
            background-color: var(--border);
            color: var(--accent-white);
        }

        .nav-link.active {
            background-color: var(--border);
            color: var(--accent-white);
            border-left-color: var(--accent-blue);
            font-weight: 600;
        }

        /* Main Workspace */
        .main-content {
            flex: 1;
            padding: 35px 40px;
            overflow-y: auto;
            display: flex;
            flex-direction: column;
        }

        .top-bar {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding-bottom: 20px;
            border-bottom: 1px solid var(--border);
            margin-bottom: 25px;
        }

        /* Role Selector Buttons */
        .role-picker {
            display: flex;
            gap: 6px;
            align-items: center;
        }

        .role-btn {
            padding: 5px 12px;
            background-color: var(--border);
            color: var(--text-muted);
            border-radius: 4px;
            text-decoration: none;
            font-size: 0.8rem;
            font-weight: 700;
            border: 1px solid var(--border-bright);
            transition: all 0.15s ease;
        }

        .role-btn:hover {
            color: var(--accent-white);
            border-color: var(--accent-blue);
        }

        .role-btn.active {
            background-color: var(--accent-red);
            color: var(--accent-white);
            border-color: var(--accent-red);
        }

        /* Feature Cards */
        .feature-card {
            background-color: var(--panel-bg);
            border: 1px solid var(--border-bright);
            border-radius: 8px;
            padding: 24px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
        }

        .feature-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid var(--border);
            padding-bottom: 12px;
            margin-bottom: 16px;
        }

        .feature-title {
            font-size: 1.25rem;
            margin: 0;
            font-weight: 700;
            color: var(--accent-white);
        }

        /* Badges */
        .badge {
            font-size: 0.7rem;
            padding: 3px 8px;
            border-radius: 4px;
            text-transform: uppercase;
            font-weight: 700;
            letter-spacing: 0.5px;
        }

        .badge-new { background-color: var(--accent-red); color: var(--accent-white); }
        .badge-ver { background-color: var(--accent-blue); color: var(--accent-white); }

        /* Lists */
        ol { padding-left: 20px; }
        li { margin-bottom: 8px; line-height: 1.6; color: var(--text-main); }

        /* Code & Callouts */
        code {
            background-color: var(--code-bg);
            padding: 2px 6px;
            border-radius: 4px;
            color: var(--code-text);
            font-family: monospace;
            font-size: 0.9em;
            border: 1px solid rgba(96, 165, 250, 0.2);
        }

        .troubleshoot-box {
            background-color: var(--warn-bg);
            border-left: 4px solid var(--accent-red);
            padding: 12px 16px;
            border-radius: 4px;
            margin-top: 18px;
            font-size: 0.88rem;
            color: var(--text-main);
        }

        footer {
            margin-top: auto;
            padding-top: 30px;
            border-top: 1px solid var(--border);
            font-size: 0.8rem;
            color: var(--text-muted);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
    </style>
</head>
<body>

<div class="layout-wrapper">

    <!-- Sidebar Navigation -->
    <aside class="sidebar">
        <div class="brand">
            <span><?= htmlspecialchars($manifest['app_name'] ?? 'Trust-Shell') ?></span>
            <span class="version-badge">v<?= htmlspecialchars($appVersion) ?></span>
        </div>

        <form method="GET" class="search-box">
            <input type="hidden" name="role" value="<?= htmlspecialchars($activeRole) ?>">
            <input type="text" name="q" placeholder="Search instructions..." value="<?= htmlspecialchars($searchQuery) ?>">
        </form>

        <div>
            <div class="nav-group-title">Module Categories</div>
            <nav class="nav-links">
                <a href="?role=<?= $activeRole ?>&category=all" class="nav-link <?= $selectedCategory === 'all' ? 'active' : '' ?>">All Modules</a>
                <?php if (!empty($manifest['categories'])): ?>
                    <?php foreach ($manifest['categories'] as $cat): ?>
                        <a href="?role=<?= $activeRole ?>&category=<?= $cat['id'] ?>" class="nav-link <?= $selectedCategory === $cat['id'] ? 'active' : '' ?>">
                            <?= htmlspecialchars($cat['title']) ?>
                        </a>
                    <?php endforeach; ?>
                <?php endif; ?>
            </nav>
        </div>
    </aside>

    <!-- Main Content Workspace -->
    <main class="main-content">
        
        <!-- Top Toolbar -->
        <div class="top-bar">
            <div style="font-size: 0.85rem; color: var(--text-muted);">
                Active Deployment Build: <code>v<?= htmlspecialchars($appVersion) ?></code>
            </div>

            <div class="role-picker">
                <span style="font-size:0.8rem; color: var(--text-muted); margin-right: 6px;">Role Filter:</span>
                <?php foreach (['POLICE', 'FIRE', 'EMS', 'DOT', 'LIFEGUARD'] as $role): ?>
                    <a href="?role=<?= $role ?>&category=<?= $selectedCategory ?>" class="role-btn <?= $activeRole === $role ? 'active' : '' ?>">
                        <?= $role ?>
                    </a>
                <?php endforeach; ?>
            </div>
        </div>
