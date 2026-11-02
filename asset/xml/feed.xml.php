<?php
/**
 * TRUST-MAIN DYNAMIC RSS/ATOM FEED GENERATOR
 * Publishes system updates, whitepaper releases, and open-source deployment 
 * notices for municipal IT aggregators.
 */
$configFile = __DIR__ . '/config/config.yaml';
$config = [];
if (file_exists($configFile) && function_exists('yaml_parse_file')) {
    $config = yaml_parse_file($configFile);
}

$appName    = $config['app_name'] ?? 'Trust-Main';
$appVersion = $config['version'] ?? '1.2';
$labId      = $config['system']['lab_id'] ?? 'MOBILE_LAB_01';
$pubDate    = date(DATE_RSS);

header("Content-Type: application/rss+xml; charset=UTF-8");
echo '<?xml version="1.0" encoding="UTF-8"?>';
?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
    <channel>
        <title><?= htmlspecialchars($appName) ?> Institutional Advisories</title>
        <link>https://patriotsmustrise.org</link>
        <description>Automated release notices, zero-cost deployment windows, and ISO/IEC 17025 compliance updates for first responders and hospitals.</description>
        <language>en-us</language>
        <lastBuildDate><?= $pubDate ?></lastBuildDate>
        <atom:link href="https://patriotsmustrise.org/feed.xml.php" rel="self" type="application/rss+xml" />

        <item>
            <title><?= htmlspecialchars($appName) ?> v<?= htmlspecialchars($appVersion) ?> Released — Zero-Cost Mobile Lab</title>
            <link>https://patriotsmustrise.org/whitepaper.php</link>
            <guid isPermaLink="true">https://patriotsmustrise.org/whitepaper.php?v=<?= htmlspecialchars($appVersion) ?></guid>
            <pubDate><?= $pubDate ?></pubDate>
            <description>
                <?= htmlspecialchars($appName) ?> v<?= htmlspecialchars($appVersion) ?> is now available for zero-cost municipal deployment. Featuring hands-free voice tactical AI, ISO/IEC 17025 evidence logging, and offline PWA field resilience. Lab ID: <?= htmlspecialchars($labId) ?>.
            </description>
        </item>
    </channel>
</rss>
