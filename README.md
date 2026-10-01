# Trust

This repository houses the APIs and digital assets for the **Legacy Trust For The Future** website and mobile project. 

While developing this platform, I realized that police and fire departments could benefit from a lightweight mobile application designed specifically to aid in scene preservation and field documentation. *Trust* is dedicated to those who protect our communities—please use it to its full potential.

Drawing from my professional background in forensics, I built this tool with the features and functionality I wished I had while working in the field. 

### Funding & Support
*Trust* is a free application. It is supported through:
* Sales of *"Climbing the Invisible Wall"*, a publication I produce periodically.
* Community donations and contributions.

### Training & Contact
Instructions, documentation, and user training for the Trust app are available on our website.

If you have questions or feedback, feel free to reach out:

* **Author:** Anthony Antolic (Anatolie Anatoliciva / Anatolicivich)
* **Phone:** +1 (503) 462-8607
* **Email:** antolicanthony3@gmail.com
* **Website:** [innovativeconceptsdotblog.wordpress.com](https://innovativeconceptsdotblog.wordpress.com/)

### Forensic video analysis bridge

The standalone Trust video bridge accepts encoded video uploads from the C++ engine or Trust-Shell over HTTP, forwards each upload as a multipart request to the ballistics analysis service, and returns the analysis result. It also publishes upload lifecycle events to authenticated WebSocket subscribers.

Start the bridge from the repository root after installing its Node.js dependency:

```sh
npm install --prefix asset/js
TRUST_VIDEO_API_TOKEN='replace-with-a-long-random-token' \
BALLISTICS_ANALYSIS_URL='http://127.0.0.1:9091/api/forensics/analyze-spatter' \
npm start --prefix asset/js
```

The bridge listens on `127.0.0.1:3010` by default. Set `TRUST_VIDEO_HOST` and `TRUST_VIDEO_PORT` to change its bind address and port. Configure `TRUST_VIDEO_API_TOKEN` with a secret shared only with trusted clients; use TLS when exposing the service beyond localhost. Uploads are limited to 512 MiB by default; `TRUST_VIDEO_MAX_UPLOAD_BYTES` and `TRUST_VIDEO_ANALYZER_TIMEOUT_MS` can override the limit and analyzer timeout.

Clients upload the raw encoded video bytes. `caseId` is required, and the optional `X-File-Name` header is sanitized before forwarding:

```sh
AUTH_HEADER="$(printf '%s %s' Bearer "$TRUST_VIDEO_API_TOKEN")"
curl --fail-with-body \
  -H "Authorization: $AUTH_HEADER" \
  -H 'Content-Type: video/mp4' \
  -H 'X-File-Name: scene.mp4' \
  --data-binary @scene.mp4 \
  'http://127.0.0.1:3010/api/forensics/videos?caseId=CASE-123'
```

The HTTP response contains `success`, `uploadId`, `caseId`, and the ballistics analyzer's `result`. Uploads use `Content-Length` and accept `video/*` or `application/octet-stream`; the same endpoint can be used by C++ and Trust-Shell clients.

Connect to `ws://127.0.0.1:3010/api/forensics/events` with an `Authorization` header containing `Bearer` followed by the configured token, and receive `connected`, `analysis.started`, `analysis.completed`, and `analysis.failed` JSON events. A JSON `{"type":"ping","id":"..."}` message receives a corresponding `pong`. Event messages include a timestamp and upload ID; `analysis.started` also includes the case ID, sanitized filename, and byte count.

`BALLISTICS_ANALYSIS_URL` must point to a running analyzer endpoint that accepts a multipart `file` field. The bridge keeps uploads in a private temporary file while analysis runs and removes that file when the request completes.
