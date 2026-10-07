<?php
if (session_status() === PHP_SESSION_NONE) {
    session_start();
}

// Allowed roles with clearance for the TrustAdmin directory
$allowed_roles = ['trust_admin', 'first_responder_admin', 'trust_executor'];
$user_role = $_SESSION['user']['role'] ?? '';

// Deny access if user is unauthenticated or lacks the required role
if (!isset($_SESSION['user']) || !in_array($user_role, $allowed_roles, true)) {
    http_response_code(403);
    header("Content-Type: text/html; charset=UTF-8");
    ?>
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>403 - Access Denied</title>
        <style>
            body { background: #0b0f19; color: #f3f4f6; font-family: system-ui, sans-serif; display: flex; align-items: center; justify-content: center; height: 100vh; margin: 0; }
            .denied-card { background: #111827; border: 1px solid #dc2626; padding: 2rem; border-radius: 8px; text-align: center; max-width: 420px; box-shadow: 0 10px 25px rgba(0,0,0,0.5); }
            h1 { color: #dc2626; font-size: 1.5rem; margin-top: 0; }
            p { color: #9ca3af; font-size: 0.9rem; margin-bottom: 1.5rem; }
            a { background: #0284c7; color: white; text-decoration: none; padding: 0.6rem 1.2rem; border-radius: 6px; font-weight: bold; display: inline-block; }
        </style>
    </head>
    <body>
        <div class="denied-card">
            <h1>403 Restricted Folder Access</h1>
            <p>You lack required clearance (TrustAdmin) to enter this directory. Unauthorized attempt logged.</p>
            <a href="../index.php">Return to Governance Portal</a>
        </div>
    </body>
    </html>
    <?php
    exit;
}
