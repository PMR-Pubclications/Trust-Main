# Accessibility

Target: WCAG 2.1 Level AA for the HTML entry points:
`index.html`, `asset/html/onboarding.html`, `asset/html/firstResponders-admin.html`,
`asset/html/legacy-trust-desktop.html`, `asset/html/First-Responder-Scene-login.html`.

## Implemented
- **Skip link** to `#main-content` as the first focusable element on each page.
- **Landmarks**: `header`, `main`, `aside`, `section` with accessible names.
- **Forms**: every input/select has an associated `<label for>` (or `aria-label`).
- **Keyboard**: all controls are native buttons/links/inputs, or have `role="button"`, `tabindex="0"` and Enter/Space handlers (supervisor drawer, closes with Escape); visible `:focus-visible` outline.
- **Screen readers**: status/log regions use `role="status"`/`role="log"`/`aria-live`; decorative overlays are `aria-hidden`; external links announce "opens in a new tab" and use `rel="noopener noreferrer"`.
- **Images**: descriptive `alt` text.
- **No inline event handlers** in `index.html` and `First-Responder-Scene-login.html`; handlers are attached with `addEventListener`.
- **Headings**: one `h1` per page with `h2` section headings below.

## Color contrast (dark theme)
Text on `#020617`/`#0f172a`/`#1e293b` uses `#f8fafc` or `#94a3b8` (>= 4.5:1).
Button backgrounds with white text: green `#15803d` (5.0:1), blue `#0369a1` (5.9:1),
amber `#b45309` (5.0:1), red `#dc2626` (4.8:1).

## Linting / testing
Run an axe-core audit, for example:

    npx @axe-core/cli index.html asset/html/*.html

or `npx pa11y <url>`. HTML checking: `npx htmlhint "**/*.html"`; `.htmlhintrc` enables
`alt-require`, `attr-lowercase`, `id-unique` and `doctype-first`.

## Known follow-ups
- `asset/html/dispatch-modal.html` and `config.html` still use inline handlers.
- Duplicate GitHub issues #2/#3 should be consolidated on GitHub (not possible from the repository).
