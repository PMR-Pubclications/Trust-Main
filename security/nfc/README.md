# security/nfc

## `NFC_Tap-to-Authenticate.js`

This file is a **browser-only front-end snippet** (an object method fragment,
not a standalone module) that uses the [Web NFC API](https://developer.mozilla.org/en-US/docs/Web/API/Web_NFC_API)
(`NDEFReader`) to read a physical NFC badge/fob and feed the decoded payload
into a login form field (`#oper-id`) before calling `this.authenticate()`.

### Why it cannot run on a headless Linux server

* Web NFC requires a browser context (`window`, `navigator.nfc`/`NDEFReader`)
  and is currently only available in Chromium-based browsers on Android.
* It requires physical NFC hardware on the client device performing the tap,
  not on the server.

This is why `security/server.js` explicitly reports `nfc.mounted: false` —
there is nothing to run server-side for this module. It is preserved here,
unmodified in behavior, so it can be embedded into the appropriate
front-end page (see `this.log(...)` / `#oper-id` / `this.authenticate()`
which are expected to be provided by the surrounding page's script).

Moved from `asset/js/operations/NFC_Tap-to-Authenticate.js` without
functional changes (see `../docs/MIGRATION.md`).
