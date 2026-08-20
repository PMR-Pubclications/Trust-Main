/**
 * ----------------------------------------------------------------------------
 * Project: Trust & Automated Governance Framework
 * File: detect-version.js
 * 
 * Author: Anatolie Anatoliciva
 * Title: Forensic Consultant & Engineer
 * Location: Vancouver, Washington
 * Copyright (c) 2026 PMR Publications. All rights reserved.
 * 
 * Description: Automated version detection utility that extracts and reports 
 * the current build or release version for system audit logs.
 * ----------------------------------------------------------------------------
 */

const fs = require('fs');

function getSystemVersion() {
    try {
        // Option: Read from a standard package or version configuration file
        const packageData = JSON.parse(fs.readFileSync('./package.json', 'utf8'));
        console.log(`[VERSION_DETECT] Active System Version: v${packageData.version}`);
        return packageData.version;
    } catch (error) {
        // Fallback default if config is missing
        console.log("[VERSION_DETECT] Version tag not found. Defaulting to v1.0.0");
        return "1.0.0";
    }
}

getSystemVersion();
