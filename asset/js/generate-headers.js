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

####encryption####
// cryptoUtils.js - ES Module for Web Crypto API (SubtleCrypto)

/**
 * Generate a new AES-GCM symmetric key (256-bit).
 * @param {boolean} extractable - Whether the key can be exported.
 * @returns {Promise<CryptoKey>}
 */
export async function generateAesKey(extractable = true) {
  return await crypto.subtle.generateKey(
    {
      name: "AES-GCM",
      length: 256,
    },
    extractable,
    ["encrypt", "decrypt"]
  );
}

/**
 * Encrypt plain text using AES-GCM.
 * @param {string} text - Plain text string to encrypt.
 * @param {CryptoKey} key - AES-GCM CryptoKey.
 * @returns {Promise<{ cipherText: ArrayBuffer, iv: Uint8Array }>} Encrypted payload and IV.
 */
export async function encryptData(text, key) {
  const encoder = new TextEncoder();
  const data = encoder.encode(text);
  
  // AES-GCM requires a unique initialization vector (IV) for every operation.
  const iv = crypto.getRandomValues(new Uint8Array(12));

  const cipherText = await crypto.subtle.encrypt(
    {
      name: "AES-GCM",
      iv: iv,
    },
    key,
    data
  );

  return { cipherText, iv };
}

/**
 * Decrypt cipher text back to plain text using AES-GCM.
 * @param {ArrayBuffer} cipherText - Encrypted binary buffer.
 * @param {CryptoKey} key - AES-GCM CryptoKey.
 * @param {Uint8Array} iv - Initialization vector used during encryption.
 * @returns {Promise<string>} Decrypted plain text string.
 */
export async function decryptData(cipherText, key, iv) {
  const decryptedBuffer = await crypto.subtle.decrypt(
    {
      name: "AES-GCM",
      iv: iv,
    },
    key,
    cipherText
  );

  const decoder = new TextDecoder();
  return decoder.decode(decryptedBuffer);
}

/**
 * Export a CryptoKey to raw byte ArrayBuffer or JSON Web Key (JWK) format.
 * @param {CryptoKey} key - The key to export.
 * @param {('raw'|'jwk')} format - Export format ('raw' or 'jwk').
 * @returns {Promise<ArrayBuffer|object>}
 */
export async function exportCryptoKey(key, format = 'raw') {
  return await crypto.subtle.exportKey(format, key);
}

/**
 * Import a raw key or JWK object into a usable CryptoKey.
 * @param {ArrayBuffer|object} keyData - Raw byte buffer or JWK object.
 * @param {('raw'|'jwk')} format - Import format ('raw' or 'jwk').
 * @param {boolean} extractable - Whether imported key remains exportable.
 * @returns {Promise<CryptoKey>}
 */
export async function importCryptoKey(keyData, format = 'raw', extractable = true) {
  return await crypto.subtle.importKey(
    format,
    keyData,
    { name: "AES-GCM" },
    extractable,
    ["encrypt", "decrypt"]
  );
}
####/encrtion####
