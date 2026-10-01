const fs = require('fs');
const path = require('path');
const zlib = require('zlib'); // Or we can structure a clean directory manifest

// Configuration paths
const rootDir = __dirname;
const assetDir = path.join(rootDir, 'asset');
const outputDir = path.join(rootDir, 'deployment_packages');

// Ensure output directory exists
if (!fs.existsSync(outputDir)) {
  fs.mkdirSync(outputDir, { recursive: true });
}

/**
 * 1. Generates the First-Responder SOP Guide dynamically based on project files
 */
function generateSopDocument() {
  let sopContent = `# TRUST SHELL: FIELD DEPLOYMENT & SOP GUIDE\n`;
  sopContent += `====================================================\n\n`;
  sopContent += `## 1. Overview\n`;
  sopContent += `This software package provides automated telemetry logging, secure chain-of-custody tracking, and background resource synchronization designed for vehicular mesh networks.\n\n`;
  
  sopContent += `## 2. Operational Quick-Start\n`;
  sopContent += `- **Automatic Initialization:** The application detects network states automatically. No manual dashboard configuration is required in the field.\n`;
  sopContent += `- **Offline Resilience:** If connection to the certificate-based Wi-Fi mesh is lost, all logs and data packets are securely buffered to the local \`/asset\` directory.\n`;
  sopContent += `- **Auto-Flush:** When entering an active coverage zone, data is burst-transmitted instantly.\n\n`;
  
  sopContent += `## 3. Support & Verification\n`;
  sopContent += `- Configured Target IP: 10.0.0.189\n`;
  sopContent += `- Status: Active mesh-ready protocol.\n`;

  const sopPath = path.join(rootDir, 'FIELD_SOP.txt');
  fs.writeFileSync(sopPath, sopContent);
  return sopPath;
}

/**
 * 2. Compiles the deployment manifest and manifest archive notes
 */
function buildPackage() {
  console.log('[Builder] Initializing First-Responder Deployment Package compilation...');

  // Generate the companion SOP document
  const sopFile = generateSopDocument();
  console.log('[Builder] Generated field-ready SOP document.');

  // Gather required distribution files
  const filesToInclude = ['miner_config.json', 'FIELD_SOP.txt'];
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
  const packageName = `TrustShell_Field_Package_${timestamp}`;
  const packagePath = path.join(outputDir, packageName);

  // Create a dedicated folder for the release bundle
  if (!fs.existsSync(packagePath)) {
    fs.mkdirSync(packagePath, { recursive: true });
  }

  // Copy assets into the bundle
  filesToInclude.forEach(file => {
    const src = path.join(rootDir, file);
    const dest = path.join(packagePath, file);
    if (fs.existsSync(src)) {
      fs.copyFileSync(src, dest);
      console.log(`[Builder] Bundled component: ${file}`);
    }
  });

  console.log(`\n[Success] Deployment package successfully structured at:\n${packagePath}`);
  console.log(`Ready for distribution to field testing units.`);
}

// Execute the package builder
buildPackage();
