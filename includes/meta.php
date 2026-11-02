<?php
/**
 * TRUST-MAIN DYNAMIC SEO, META TAG & SCHEMA.ORG MODULE
 * 
 * Repository: PMR-Pubclications/Trust-Main
 * Component: Metadata & SEO Indexing Core Engine
 * Compliance: ISO/IEC 17025, NIBRS, NFIRS, HL7 FHIR
 *
 * Handles dynamic description updating, canonical links, social graphs,
 * Schema.org structured data, direct repository auditing links, and
 * search engine compliance for the Trust-Main ecosystem.
 */

// ============================================================================
// 1. ENVIRONMENT & CANONICAL URL RESOLUTION
// ============================================================================
$currentPage = basename($_SERVER['PHP_SELF'], '.php');
$protocol    = (!empty($_SERVER['HTTPS']) && $_SERVER['HTTPS'] !== 'off') ? 'https://' : 'http://';
$host        = $_SERVER['HTTP_HOST'] ?? 'patriotsmustrise.org';
$requestUri  = strtok($_SERVER['REQUEST_URI'] ?? '', '?'); 

// Construct canonical URL to prevent duplicate content flags across search engines
$canonicalUrl = htmlspecialchars($protocol . $host . $requestUri);

// ============================================================================
// 2. DYNAMIC DESCRIPTION & TITLE MAP MATRIX
// ============================================================================
$pageMetaMap = [
    'index' => [
        'title'       => 'Trust-Main Forensic & Administrative Ecosystem',
        'description' => 'Trust-Main is a secure, privacy-focused forensic administrative ecosystem and first-responder dispatch console operating independently of traditional app stores.',
        'keywords'    => 'forensic software, law enforcement dispatch, ISO 17025 evidence, blockchain ledger, first responder ecosystem'
    ],
    'whitepaper' => [
        'title'       => 'Technical White Paper & System Architecture Specs',
        'description' => 'Comprehensive technical white paper detailing ISO/IEC 17025 evidence transmittal compliance, PWA caching strategy, and active agency dispatch endpoints.',
        'keywords'    => 'forensic white paper, NIBRS compliance, NFIRS fire reporting, ePCR EMS specs, MUTCD traffic alerts'
    ],
    'accounts_liable' => [
        'title'       => 'Accounts Liable & Creditor Ledger Console',
        'description' => 'Secure management console for municipal accounts liability, automated billing extraction, and Plaid-authenticated ledger reconciliation.',
        'keywords'    => 'accounts liable, Plaid ledger integration, municipal billing reconciliation, Wells Fargo settlement'
    ],
    'dispatch_pd' => [
        'title'       => 'Police Department (PD) Operational Dispatch Interface',
        'description' => 'Direct dispatch portal and ballistic evidence transmittal module for municipal police department field units.',
        'keywords'    => 'police dispatch, NIBRS reporting, ballistic video analysis, crime scene telemetry'
    ],
    'dispatch_fire' => [
        'title'       => 'Fire & Rescue Services Incident Dispatch',
        'description' => 'NFIRS-compliant emergency fire incident telemetry and tactical resource coordination portal.',
        'keywords'    => 'fire dispatch, NFIRS compliance, incident command system, emergency rescue telemetry'
    ],
    'dispatch_dot' => [
        'title'       => 'Department of Transportation (DOT) Traffic Operations',
        'description' => 'MUTCD-compliant traffic incident alert system, roadway hazard reporting, and DOT field unit dispatch.',
        'keywords'    => 'DOT operations, MUTCD traffic alerts, roadway hazard dispatch, municipal transit safety'
    ],
    'dispatch_lifeguard' => [
        'title'       => 'Water Safety & Lifeguard Tactical Dispatch',
        'description' => 'Coastal and aquatic rescue unit telemetry, water safety monitoring, and emergency lifeguard dispatch interface.',
        'keywords'    => 'lifeguard dispatch, water safety telemetry, aquatic rescue, emergency shore coordination'
    ]
];

// ============================================================================
// 3. DYNAMIC RESOLVER LOGIC & FALLBACKS
// ============================================================================
if (!empty($pageDescription)) {
    $metaDescription = $pageDescription;
} elseif ($currentPage === 'guide' && !empty($_GET['category'])) {
    $catName = htmlspecialchars(ucfirst($_GET['category']));
    $metaDescription = "Explore the {$catName} module category documentation and operational specifications within the Trust-Main platform.";
} else {
    $metaDescription = $pageMetaMap[$currentPage]['description'] 
        ?? ($config['description'] ?? 'Trust-Main secure operational platform, forensic reporting engine, and agency dispatch console.');
}

if (!empty($pageTitle)) {
    $metaTitle = $pageTitle;
} else {
    $metaTitle = $pageMetaMap[$currentPage]['title'] 
        ?? ucfirst(str_replace('_', ' ', $currentPage));
}

$pageKeywords = $pageMetaMap[$currentPage]['keywords'] 
    ?? 'trust-main, forensic science, law enforcement, PWA dispatch, ISO 17025';

// ============================================================================
// 4. MANIFEST & GLOBAL METADATA SETUP
// ============================================================================
$appName     = $config['app_name'] ?? 'Trust-Main';
$appVersion  = $config['version'] ?? '1.2';
$appAuthor   = 'PMR Publications';
$fullTitle   = htmlspecialchars("{$appName} | {$metaTitle}");
$metaDescEsc = htmlspecialchars(mb_strimwidth($metaDescription, 0, 155, '...')); // Optimal length ~155 chars

// ============================================================================
// 5. INDEXING RULES & DIRECTIVES
// ============================================================================
// Public white papers, index, and guides are indexed; sensitive internal dispatch tools receive noindex
$publicPageRegistry = ['index', 'whitepaper', 'guide'];
$isPublicPage       = in_array($currentPage, $publicPageRegistry);
$robotsMeta         = $isPublicPage ? 'index, follow, max-image-preview:large' : 'noindex, nofollow';

// ============================================================================
// 6. ROLE-BASED DYNAMIC MOBILE THEME COLORING
// ============================================================================
$activeRole = strtolower($activeRole ?? $_SESSION['role'] ?? 'first_responder');
switch ($activeRole) {
    case 'trustadmin':
    case 'admin':
        $themeColor = '#000000'; // Sleek dark console for admin
        break;
    case 'first_responder':
    case 'responder':
        $themeColor = '#dc2626'; // High-visibility emergency red
        break;
    default:
        $themeColor = '#0284c7'; // Standard tactical blue
        break;
}
?>

<!-- ============================================================================ -->
<!-- HTML HEAD METADATA ENGINE BLOCK                                             -->
<!-- ============================================================================ -->
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<meta http-equiv="X-UA-Compatible" content="IE=edge">

<!-- Primary SEO Meta Tags -->
<title><?= $fullTitle ?></title>
<meta name="title" content="<?= $fullTitle ?>">
<meta name="description" content="<?= $metaDescEsc ?>">
<meta name="keywords" content="<?= htmlspecialchars($pageKeywords) ?>">
<meta name="author" content="<?= htmlspecialchars($appAuthor) ?>">
<meta name="robots" content="<?= $robotsMeta ?>">
<meta name="generator" content="Trust-Main Framework v<?= htmlspecialchars($appVersion) ?>">

<!-- Canonical Link -->
<link rel="canonical" href="<?= $canonicalUrl ?>">

<!-- PWA Web App Manifest & Mobile OS Integration -->
<link rel="manifest" href="manifest.json">
<meta name="theme-color" content="<?= $themeColor ?>">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="<?= htmlspecialchars($appName) ?>">
<meta name="mobile-web-app-capable" content="yes">
<link rel="apple-touch-icon" sizes="192x192" href="asset/img/icon-192.png">

<!-- Open Graph / Facebook / LinkedIn Social Graph -->
<meta property="og:type" content="website">
<meta property="og:site_name" content="<?= htmlspecialchars($appName) ?>">
<meta property="og:url" content="<?= $canonicalUrl ?>">
<meta property="og:title" content="<?= $fullTitle ?>">
<meta property="og:description" content="<?= $metaDescEsc ?>">
<meta property="og:image" content="<?= htmlspecialchars($config['og_image'] ?? 'asset/img/trust-og.png') ?>">
<meta property="og:locale" content="en_US">

<!-- Twitter Card Meta Tags -->
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:url" content="<?= $canonicalUrl ?>">
<meta name="twitter:title" content="<?= $fullTitle ?>">
<meta name="twitter:description" content="<?= $metaDescEsc ?>">
<meta name="twitter:image" content="<?= htmlspecialchars($config['og_image'] ?? 'asset/img/trust-og.png') ?>">

<!-- Schema.org JSON-LD Structured Data with Direct Repository Auditing Links -->
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "SoftwareApplication",
  "name": "<?= htmlspecialchars($appName) ?>",
  "alternateName": "TrustAdmin Forensic & Administrative Ecosystem",
  "operatingSystem": "Cross-Platform Web, PWA, Mobile, Linux, Android, iOS",
  "applicationCategory": "SecurityApplication",
  "genre": "Forensic Investigation & Law Enforcement Administration",
  "isAccessibleForFree": true,
  "offers": {
    "@type": "Offer",
    "price": "0.00",
    "priceCurrency": "USD",
    "description": "Complimentary open-source deployment for authorized law enforcement and municipal agencies."
  },
  "author": {
    "@type": "Organization",
    "name": "<?= htmlspecialchars($appAuthor) ?>",
    "url": "https://patriotsmustrise.org"
  },
  "publisher": {
    "@type": "Organization",
    "name": "<?= htmlspecialchars($appAuthor) ?>",
    "url": "https://patriotsmustrise.org"
  },
  "description": "<?= $metaDescEsc ?>",
  "softwareVersion": "<?= htmlspecialchars($appVersion) ?>",
  "downloadUrl": "https://github.com/PMR-Pubclications/Trust-Main",
  "codeRepository": "https://github.com/PMR-Pubclications/Trust-Main",
  "programmingLanguage": [
    "PHP",
    "YAML",
    "C++",
    "Java",
    "Python",
    "JavaScript"
  ],
  "featureList": [
    "ISO/IEC 17025 Compliant Evidence Transmittal",
    "Blockchain-Backed Forensic Reporting Engine",
    "Dynamic First Responder Dispatch (Police, Fire, DOT, Water Safety)",
    "Accounts Liable Ledger & Automated Creditor Billing Reconciliation"
  ],
  "releaseNotes": "https://github.com/PMR-Pubclications/Trust-Main/releases",
  "license": "https://github.com/PMR-Pubclications/Trust-Main/blob/main/LICENSE"
}
</script>
