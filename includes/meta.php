<?php
/**
 * TRUST-SHELL DYNAMIC SEO & META TAG MODULE
 * Handles dynamic description updating, canonical links, social graphs, 
 * Schema.org structured data, and search engine compliance.
 */

// 1. Resolve Current Page & URL Parameters
$currentPage = basename($_SERVER['PHP_SELF'], '.php');
$protocol    = (!empty($_SERVER['HTTPS']) && $_SERVER['HTTPS'] !== 'off') ? 'https://' : 'http://';
$host        = $_SERVER['HTTP_HOST'] ?? 'localhost';
$requestUri  = strtok($_SERVER['REQUEST_URI'] ?? '', '?'); 

// Canonical URL (prevents duplicate content issues in search engines)
$canonicalUrl = htmlspecialchars($protocol . $host . $requestUri);

// 2. Dynamic Description & Title Map Matrix
$pageMetaMap = [
    'index' => [
        'title'       => 'Trust-Shell Mobile Operational Console & Dispatch',
        'description' => 'Trust-Shell is a secure, privacy-focused mobile shell providing automated duty roster tracking and system telemetry.',
    ],
    'guide' => [
        'title'       => 'Operational Guide & Module Documentation',
        'description' => 'Comprehensive operations guide and field manual for Trust-Shell system capabilities and navigation.',
    ],
    'app_status' => [
        'title'       => 'System Behavior & Diagnostic Telemetry',
        'description' => 'Real-time performance monitoring, error log verification, and shell system health status.',
    ],
    'payroll' => [
        'title'       => 'Compensation & Financial Ledger Maintenance',
        'description' => 'Secure management console for operator compensation, payroll verification, and duty records.',
    ],
    'onboarding' => [
        'title'       => 'Operator Provisioning & Onboarding',
        'description' => 'System access provisioning, multi-stage credential verification, and device onboarding.',
    ]
];

// 3. Dynamic Description Updater Logic
// Priority 1: Custom page override ($pageDescription set before include)
// Priority 2: Dynamic Category/Query context (e.g. guide.php?category=...)
// Priority 3: Pre-mapped page description
// Priority 4: App Manifest fallback
if (!empty($pageDescription)) {
    $metaDescription = $pageDescription;
} elseif ($currentPage === 'guide' && !empty($_GET['category'])) {
    $catName = htmlspecialchars(ucfirst($_GET['category']));
    $metaDescription = "Explore the {$catName} module category documentation and operational specs within Trust-Shell.";
} else {
    $metaDescription = $pageMetaMap[$currentPage]['description'] 
        ?? ($manifest['description'] ?? 'Trust-Shell secure mobile operational platform and documentation portal.');
}

// Dynamic Page Title Resolver
if (!empty($pageTitle)) {
    $metaTitle = $pageTitle;
} else {
    $metaTitle = $pageMetaMap[$currentPage]['title'] 
        ?? ucfirst(str_replace('_', ' ', $currentPage));
}

// 4. Manifest & App Metadata Setup
$appName     = $manifest['app_name'] ?? 'Trust-Shell';
$appVersion  = $manifest['version'] ?? $appVersion ?? '1.0.0';
$appAuthor   = $manifest['author'] ?? 'PMR Publications';
$fullTitle   = htmlspecialchars("{$appName} | {$metaTitle}");
$metaDescEsc = htmlspecialchars(mb_strimwidth($metaDescription, 0, 155, '...')); // Ideal SEO length: ~155 chars

// 5. SEO Indexing Rules
// Public guide pages are set to index/follow; secure consoles are set to noindex for privacy
$isPublicPage = in_array($currentPage, ['guide', 'index']);
$robotsMeta   = $isPublicPage ? 'index, follow' : 'noindex, nofollow';

// 6. Mobile OS Theme Color Setup
$activeRole = strtolower($activeRole ?? $_SESSION['role'] ?? 'standard');
$themeColor = ($activeRole === 'trust_admin') ? '#000000' : (($activeRole === 'first_responder') ? '#dc2626' : '#0284c7');
?>

<!-- Basic & SEO Meta Tags -->
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<meta http-equiv="X-UA-Compatible" content="IE=edge">

<title><?= $fullTitle ?></title>
<meta name="title" content="<?= $fullTitle ?>">
<meta name="description" content="<?= $metaDescEsc ?>">
<meta name="author" content="<?= htmlspecialchars($appAuthor) ?>">
<meta name="robots" content="<?= $robotsMeta ?>">

<!-- Canonical Link for Search Engines -->
<link rel="canonical" href="<?= $canonicalUrl ?>">

<!-- Mobile OS & Status Bar Integration -->
<meta name="theme-color" content="<?= $themeColor ?>">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="<?= htmlspecialchars($appName) ?>">
<meta name="mobile-web-app-capable" content="yes">

<!-- Open Graph / Facebook / LinkedIn Meta Tags -->
<meta property="og:type" content="website">
<meta property="og:site_name" content="<?= htmlspecialchars($appName) ?>">
<meta property="og:url" content="<?= $canonicalUrl ?>">
<meta property="og:title" content="<?= $fullTitle ?>">
<meta property="og:description" content="<?= $metaDescEsc ?>">
<meta property="og:image" content="<?= htmlspecialchars($manifest['og_image'] ?? 'asset/img/trust-og.png') ?>">

<!-- Twitter Card Meta Tags -->
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:url" content="<?= $canonicalUrl ?>">
<meta name="twitter:title" content="<?= $fullTitle ?>">
<meta name="twitter:description" content="<?= $metaDescEsc ?>">
<meta name="twitter:image" content="<?= htmlspecialchars($manifest['og_image'] ?? 'asset/img/trust-og.png') ?>">

<!-- Schema.org JSON-LD Structured Data for Search Engines -->
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "SoftwareApplication",
  "name": "<?= htmlspecialchars($appName) ?>",
  "operatingSystem": "Mobile / Web",
  "applicationCategory": "UtilitiesApplication",
  "author": {
    "@type": "Organization",
    "name": "<?= htmlspecialchars($appAuthor) ?>"
  },
  "description": "<?= $metaDescEsc ?>"
}
</script>
