/**
 * @file um-lang.js
 * @description Dynamic internationalization (i18n) and telemetry localization library 
 *              for the Trust forensic mobile platform.
 * @repository https://github.com/PMR-Pubclications/Trust-Main/tree/main/lib/LanguageLibrary
 */

const fs = require('fs').promises;
const path = require('path');

class UmLanguageLibrary {
  constructor(defaultLocale = 'en', apiBaseUrl = '') {
    this.defaultLocale = defaultLocale;
    this.currentLocale = defaultLocale;
    this.dictionaries = new Map();
    this.apiBaseUrl = apiBaseUrl;
    this.localeDir = path.join(__dirname, 'locales');
  }

  /**
   * Load or merge a dictionary into memory for a specific locale
   * @param {string} locale - e.g., 'en', 'es', 'fr'
   * @param {Object} data - Key-value translation object
   */
  loadLocale(locale, data) {
    const existing = this.dictionaries.get(locale) || {};
    this.dictionaries.set(locale, { ...existing, ...data });
  }

  /**
   * Switch the active locale at runtime
   * @param {string} locale 
   */
  setLocale(locale) {
    if (this.dictionaries.has(locale)) {
      this.currentLocale = locale;
    } else {
      console.warn(`[UmLang] Locale '${locale}' not loaded in memory. Retaining '${this.currentLocale}'.`);
    }
  }

  /**
   * Translate a nested key with parameter interpolation
   * @param {string} pathStr - Dot-notation key (e.g., 'forensics.chain_of_custody.status')
   * @param {Object} params - Key-value pairs for dynamic string replacement
   * @returns {string} Translated and interpolated string
   */
  t(pathStr, params = {}) {
    const keys = pathStr.split('.');
    
    // 1. Attempt lookup in current active locale
    let translation = this._resolveKey(this.dictionaries.get(this.currentLocale), keys);
    
    // 2. Fall back to default locale if missing
    if (translation === undefined && this.currentLocale !== this.defaultLocale) {
      translation = this._resolveKey(this.dictionaries.get(this.defaultLocale), keys);
    }

    // 3. Ultimate fallback if key is completely missing across lexicons
    if (translation === undefined) {
      return `[missing: ${pathStr}]`;
    }

    return this._interpolate(translation, params);
  }

  /**
   * Synchronize locale packs dynamically from a secure endpoint or local cache
   * @param {string} locale 
   */
  async syncLocale(locale) {
    try {
      if (!this.apiBaseUrl) {
        throw new Error('API base URL not configured for remote synchronization.');
      }

      const response = await fetch(`${this.apiBaseUrl}/api/locales/${locale}`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${this._getAuthToken()}`,
          'X-Client-Platform': 'Trust-Shell-Mobile'
        }
      });

      if (!response.ok) {
        throw new Error(`Remote sync failed with status ${response.status}`);
      }

      const localeData = await response.json();
      this.loadLocale(locale, localeData);
      await this._cacheToDisk(locale, localeData);
      
      console.log(`[UmLang] Successfully synced and cached locale: '${locale}'`);
    } catch (error) {
      console.warn(`[UmLang] Remote sync failed for '${locale}' (${error.message}). Attempting local fallback.`);
      await this.loadLocaleFromDisk(locale);
    }
  }

  /**
   * Load locale JSON directly from the local disk cache
   * @param {string} locale 
   */
  async loadLocaleFromDisk(locale) {
    try {
      const filePath = path.join(this.localeDir, `${locale}.json`);
      const fileData = await fs.readFile(filePath, 'utf8');
      const parsedData = JSON.parse(fileData);
      this.loadLocale(locale, parsedData);
      console.log(`[UmLang] Loaded locale '${locale}' from local storage cache.`);
    } catch (err) {
      console.error(`[UmLang] Critical: Failed to load local cache for '${locale}'.`, err.message);
    }
  }

  async _cacheToDisk(locale, data) {
    try {
      await fs.mkdir(this.localeDir, { recursive: true });
      const filePath = path.join(this.localeDir, `${locale}.json`);
      await fs.writeFile(filePath, JSON.stringify(data, null, 2), 'utf8');
    } catch (err) {
      console.error(`[UmLang] Failed to cache locale '${locale}' to disk:`, err.message);
    }
  }

  _resolveKey(obj, keys) {
    return keys.reduce((acc, key) => (acc && acc[key] !== undefined ? acc[key] : undefined), obj);
  }

  _interpolate(template, params) {
    return template.replace(/\{\s*([a-zA-Z0-9_]+)\s*\}/g, (match, key) => {
      return params[key] !== undefined ? params[key] : match;
    });
  }

  _getAuthToken() {
    // Return secure device cryptographic session token or API credential
    return process.env.TRUST_SHELL_AUTH_TOKEN || 'offline-device-token';
  }
}

module.exports = UmLanguageLibrary;
