<?php
/**
 * TRUST-MAIN AUTOMATED SBOM (SOFTWARE BILL OF MATERIALS) GENERATOR
 * Generates an auditable JSON manifest of all system components and versions.
 */
$configFile = __DIR__ . '/config/config.yaml';
$config = [];
if (file_exists($configFile) && function_exists('yaml_parse_file')) {
    $config = yaml_parse_file($configFile);
}

$appName    = $config['app_name'] ?? 'Trust-Main';
$appVersion = $config['version'] ?? '1.2';

// Scan core project files to build inventory
$components = [];
$iterator = new RecursiveIteratorIterator(new RecursiveDirectoryIterator(__DIR__));
foreach ($iterator as $file) {
    if ($file->isFile()) {
        $filePath = $file->getRealPath();
        $relativePath = str_replace(__DIR__ . DIRECTORY_SEPARATOR, '', $filePath);
        
        // Skip hidden files, logs, and git metadata
        if (strpos($relativePath, '.') === 0 || strpos($relativePath, 'logs') === 0 || strpos($relativePath, 'vendor') === 0) {
            continue;
        }

        $components[] = [
            "name"         => "trust-main/" . str_replace(DIRECTORY_SEPARATOR, '/', $relativePath),
            "version"      => $appVersion,
            "file_hash"    => hash_file('sha256', $filePath),
            "size_bytes"   => filesize($filePath)
        ];
    }
}

$sbom = [
    "bomFormat"   => "CycloneDX",
    "specVersion" => "1.4",
    "serialNumber"=> "urn:uuid:" . vsprintf('%s%s-%s-%s-%s-%s%s%s', str_split(bin2hex(random_bytes(16)), 4)),
    "version"     => 1,
    "metadata"    => [
        "timestamp" => gmdate('Y-m-d\TH:i:s\Z'),
        "tools"     => [
            [
                "vendor"  => "PMR Publications",
                "name"    => $appName . " SBOM Generator",
                "version" => $appVersion
            ]
        ],
        "component" => [
            "type"    => "application",
            "name"    => $appName,
            "version" => $appVersion,
            "purl"    => "pkg:github/PMR-Pubclications/Trust-Main@" . $appVersion
        ]
    ],
    "components" => $components
];

$sbomJson = json_encode($sbom, JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES);
file_put_contents(__DIR__ . '/sbom.json', $sbomJson);

echo "SBOM successfully generated: sbom.json (" . count($components) . " components indexed).\n";
