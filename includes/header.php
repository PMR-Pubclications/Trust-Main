<?php
// 1. Determine user role (checks $activeRole, or session variable, default to responder)
$userRole = strtolower($activeRole ?? $_SESSION['role'] ?? 'responder');

// 2. Assign the CSS class based on credentials
switch ($userRole) {
    case 'admin':
    case 'administrator':
        $themeClass = 'theme-admin';
        break;

    case 'first_responder':
    case 'responder':
    case 'duty':
    default:
        $themeClass = 'theme-responder';
        break;
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title><?= htmlspecialchars($manifest['app_name'] ?? 'Trust-Shell') ?></title>
    <link rel="stylesheet" href="style.css">
</head>
<body class="<?= htmlspecialchars($themeClass) ?>">
