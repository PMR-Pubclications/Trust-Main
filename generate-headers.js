/**
 * ----------------------------------------------------------------------------
 * Project: Trust & Automated Governance Framework
 * File: generate-headers.js
 * 
 * Author: Anatolie Anatoliciva
 * Title: Forensic Consultant & Engineer
 * Location: Vancouver, Washington
 * Copyright (c) 2026 PMR Publications. All rights reserved.
 * 
 * Description: Automated utility script that scans repository source files 
 * and injects the standardized author and copyright header if absent.
 * ----------------------------------------------------------------------------
 */

const fs = require('fs');
const path = require('path');

const HEADER_TEMPLATE = `/**
 * ----------------------------------------------------------------------------
 * Project: Trust & Automated Governance Framework
 * Author: Anatolie Anatoliciva
 * Title: Forensic Consultant & Engineer
 * Location: Vancouver, Washington
 * Copyright (c) 2026 PMR Publications. All rights reserved.
 * ----------------------------------------------------------------------------
 */\n\n`;

const TARGET_EXTENSIONS = ['.js', '.cpp', '.sh', '.py'];
const EXCLUDE_DIRS = ['.github', 'node_modules', '.git'];

function walkDir(currentPath) {
    const files = fs.readdirSync(currentPath);
    for (const file of files) {
        const fullPath = path.join(currentPath, file);
        const stat = fs.statSync(fullPath);

        if (stat.isDirectory()) {
            if (!EXCLUDE_DIRS.includes(file)) {
                walkDir(fullPath);
            }
        } else {
            const ext = path.extname(file);
            if (TARGET_EXTENSIONS.includes(ext)) {
                processFile(fullPath);
            }
        }
    }
}

function processFile(filePath) {
    let content = fs.readFileSync(filePath, 'utf8');
    
    // Check if the file already contains your name to avoid duplicate headers
    if (!content.includes('Anatolie Anatoliciva')) {
        console.log(`[HEADER_GEN] Injecting header into: ${filePath}`);
        fs.writeFileSync(filePath, HEADER_TEMPLATE + content, 'utf8');
    } else {
        console.log(`[HEADER_GEN] Header already present: ${filePath}`);
    }
}

console.log("[HEADER_GEN] Starting repository header scan...");
walkDir('./');
console.log("[HEADER_GEN] Header verification complete.");
