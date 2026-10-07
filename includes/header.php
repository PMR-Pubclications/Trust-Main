<?php
/**
 * TRUST-SHELL HEADER & OPERATOR HANDSHAKE ENFORCER
 * 
 * Verifies the 4-Stage Operator Auth Handshake:
 *   Stage 1: Identity & Primary Credentials
 *   Stage 2: Device Hardware & Token Verification
 *   Stage 3: Role & Clearance Authorization
 *   Stage 4: Active Cryptographic Session Lock
 */

// 1. Ensure Session is Active
if (session_status() === PHP_SESSION_NONE) {
    session_start();
}

// 2. Enforce Security & Anti-Caching Headers
header("X-Frame-Options: DENY");
header("X-Content-Type-Options: nosniff");
header("Referrer-Policy: same-origin");
header("Cache-Control: no-store, no-cache, must-revalidate, max-age=0");

// 3. Evaluate 4-Stage Operator Handshake Status
$handshakeStage = (int)($_SESSION['operator_handshake_stage'] ?? 0);
$handshakeToken = $_SESSION['operator_handshake_token'] ?? null;

// If handshake is incomplete (Stage < 4) or token is missing, redirect to login stage
if ($handshakeStage < 4 || empty($handshakeToken)) {
    $nextStage = max(1, $handshakeStage + 1);
    header("Location: login.php?stage={$nextStage}&error=handshake_required");
    exit();
}

// 4. Resolve Active Credentials & Role
$activeRole = strtolower($_SESSION['role'] ?? $activeRole ?? 'standard');

// Map Credentials to Theme CSS Classes
switch ($activeRole) {
    case 'trust_admin':
    case 'admin':
    case 'sysadmin':
        $themeClass = 'theme-admin';     // 1980s Phosphor Green Terminal
        $roleLabel  = 'TRUST ADMIN';
        break;

    case 'first_responder':
    case 'first_responder_admin':
    case 'responder':
        $themeClass = 'theme-responder'; // Tactical High-Contrast Dark/Red
        $roleLabel  = 'FIRST RESPONDER';
        break;

    default:
        $themeClass = 'theme-standard';  // Voice Control Single-Screen Mode
        $roleLabel  = 'OPERATOR';
        break;
}

// Store resolved role back to active context
$appVersion = $manifest['version'] ?? $appVersion ?? '1.0.0';
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <title><?= htmlspecialchars($manifest['app_name'] ?? 'Trust-Shell') ?> | <?= $roleLabel ?></title>

    <!-- Main Stylesheet (Includes role-based theme variables & 80s Green CRT theme) -->
    <link rel="stylesheet" href="asset/css/style.css">
</head>

<body class="<?= htmlspecialchars($themeClass) ?>" data-handshake="stage-4-verified">
