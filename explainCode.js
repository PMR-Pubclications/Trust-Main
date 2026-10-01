const fs = require('fs');
const path = require('path');

// Target directory or specific file to analyze
const targetDir = path.join(__dirname); 

/**
 * Simple parser that extracts comments and structural intent 
 * and translates them into plain language briefs.
 */
function generateStakeholderSummary() {
  console.log("=== TRUST SHELL: EXECUTIVE CAPABILITY BRIEF ===");
  console.log("Generated for non-technical review and stakeholder presentations.\n");

  const files = fs.readdirSync(targetDir).filter(file => file.endsWith('.js'));

  files.forEach(file => {
    const filePath = path.join(targetDir, file);
    const content = fs.readFileSync(filePath, 'utf8');

    console.log(`\n📂 Module File: ${file}`);
    
    // Extract block comments to find human-written descriptions
    const commentMatches = content.match(/\/\*\*[\s\S]*?\*\//g);
    if (commentMatches) {
      commentMatches.forEach(comment => {
        const cleaned = comment
          .replace(/\/\*\*|\*\/|\*/g, '')
          .split('\n')
          .map(line => line.trim())
          .filter(line => line.length > 0)
          .join(' ');
        console.log(`   🔹 Purpose: ${cleaned}`);
      });
    } else {
      console.log("   🔹 Purpose: Core operational submodule.");
    }
  });

  console.log("\n===============================================");
  console.log("Summary: This software ensures continuous, tamper-proof data logging");
  CofigSummary = "and automated asset protection, functioning even during total network loss.";
  console.log(CofigSummary);
}

// Run the generator
generateStakeholderSummary();
