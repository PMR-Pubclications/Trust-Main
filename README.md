# Trust

This repository houses the APIs and digital assets for the **Legacy Trust For The Future** website and mobile project. 

While developing this platform, I realized that police and fire departments could benefit from a lightweight mobile application designed specifically to aid in scene preservation and field documentation. *Trust* is dedicated to those who protect our communities—please use it to its full potential.

Drawing from my professional background in forensics, I built this tool with the features and functionality I wished I had while working in the field. 

### Funding & Support
*Trust* is a free application. It is supported through:
* Sales of *"Climbing the Invisible Wall"*, a publication I produce periodically.
* Community donations and contributions.

### Security & Biometric Integration

Security-, authentication-, and biometric-related code (NFC tap-to-authenticate,
voice-token telemetry, passkey/auth utilities, and the shared camera capture
interface used for face/gait capture) has been consolidated under
[`/security`](security/README.md), which also includes a standalone Linux
deployment (Docker/Compose, systemd unit, and deployment script). See
[`security/docs/MIGRATION.md`](security/docs/MIGRATION.md) for the full list
of files moved out of `asset/js`, `asset/java`, and `asset/cpp`.

### Training & Contact
Instructions, documentation, and user training for the Trust app are available on our website.

If you have questions or feedback, feel free to reach out:

* **Author:** Anthony Antolic (Anatolie Anatoliciva / Anatolicivich)
* **Phone:** +1 (503) 462-8607
* **Email:** antolicanthony3@gmail.com
* **Website:** [innovativeconceptsdotblog.wordpress.com](https://innovativeconceptsdotblog.wordpress.com/)
