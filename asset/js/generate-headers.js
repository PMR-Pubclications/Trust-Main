/**
 * Security Headers Generator (UMD)
 * Works in browser and Node.js
 */
(function (root, factory) {
    if (typeof define === 'function' && define.amd) {
        // AMD
        define([], factory);
    } else if (typeof module === 'object' && module.exports) {
        // Node, CommonJS
        module.exports = factory();
    } else {
        // Browser global
        root.generateSecurityHeaders = factory();
    }
}(typeof self !== 'undefined' ? self : this, function () {
    function generateSecurityHeaders() {
        return {
            "Content-Security-Policy": "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'",
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Permissions-Policy": "geolocation=(), microphone=(), camera=()"
        };
    }

    function applySecurityHeaders(res) {
        var headers = generateSecurityHeaders();
        Object.keys(headers).forEach(function (k) {
            if (res && typeof res.setHeader === 'function') res.setHeader(k, headers[k]);
        });
        return headers;
    }

    return {
        generateSecurityHeaders: generateSecurityHeaders,
        applySecurityHeaders: applySecurityHeaders
    };
}));
