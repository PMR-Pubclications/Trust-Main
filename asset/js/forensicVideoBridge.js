'use strict';

const crypto = require('crypto');
const fs = require('fs');
const http = require('http');
const https = require('https');
const os = require('os');
const path = require('path');
const { pipeline, Transform, Readable } = require('stream');
const { promisify } = require('util');
const { WebSocketServer, WebSocket } = require('ws');

const pipelineAsync = promisify(pipeline);
const VIDEO_ROUTE = '/api/forensics/videos';
const EVENTS_ROUTE = '/api/forensics/events';
const DEFAULT_ANALYZER_URL = 'http://127.0.0.1:9091/api/forensics/analyze-spatter';
const DEFAULT_MAX_UPLOAD_BYTES = 512 * 1024 * 1024;
const MAX_ANALYZER_RESPONSE_BYTES = 1024 * 1024;

function safeEqual(left, right) {
  const leftBuffer = Buffer.from(String(left));
  const rightBuffer = Buffer.from(String(right));
  return leftBuffer.length === rightBuffer.length && crypto.timingSafeEqual(leftBuffer, rightBuffer);
}

function bearerTokenMatches(request, token) {
  return safeEqual(request.headers.authorization || '', ['Bearer', token].join(' '));
}

function sendJson(response, statusCode, body) {
  response.writeHead(statusCode, { 'content-type': 'application/json; charset=utf-8' });
  response.end(JSON.stringify(body));
}

function validCaseId(value) {
  return typeof value === 'string' && /^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$/.test(value);
}

function safeFileName(value) {
  const baseName = path.basename(String(value || 'video.mp4').replace(/\\/g, '/'));
  const sanitized = baseName.replace(/[^A-Za-z0-9._-]/g, '_').slice(0, 128);
  return sanitized && sanitized !== '.' && sanitized !== '..' ? sanitized : 'video.mp4';
}

function writeUpload(request, filePath, maxBytes) {
  let receivedBytes = 0;
  const limiter = new Transform({
    transform(chunk, encoding, callback) {
      receivedBytes += chunk.length;
      if (receivedBytes > maxBytes) {
        const error = new Error('Video exceeds the configured upload limit.');
        error.statusCode = 413;
        callback(error);
        return;
      }
      callback(null, chunk);
    }
  });

  return pipelineAsync(
    request,
    limiter,
    fs.createWriteStream(filePath, { flags: 'wx', mode: 0o600 })
  ).then(() => receivedBytes);
}

function forwardToAnalyzer({ analyzerUrl, caseId, filePath, fileName, contentType, timeoutMs }) {
  const url = new URL(analyzerUrl);
  if (url.protocol !== 'http:' && url.protocol !== 'https:') {
    return Promise.reject(new Error('Ballistics analyzer URL must use HTTP or HTTPS.'));
  }

  const transport = url.protocol === 'https:' ? https : http;
  const boundary = `trust-${crypto.randomBytes(18).toString('hex')}`;
  const prefix = Buffer.from(
    `--${boundary}\r\n` +
    'Content-Disposition: form-data; name="caseId"\r\n\r\n' +
    `${caseId}\r\n` +
    `--${boundary}\r\n` +
    `Content-Disposition: form-data; name="file"; filename="${fileName}"\r\n` +
    `Content-Type: ${contentType}\r\n\r\n`
  );
  const suffix = Buffer.from(`\r\n--${boundary}--\r\n`);
  const fileSize = fs.statSync(filePath).size;

  return new Promise((resolve, reject) => {
    const analyzerRequest = transport.request(url, {
      method: 'POST',
      headers: {
        'content-type': `multipart/form-data; boundary=${boundary}`,
        'content-length': prefix.length + fileSize + suffix.length
      }
    }, (analyzerResponse) => {
      const chunks = [];
      let responseBytes = 0;

      analyzerResponse.on('data', (chunk) => {
        responseBytes += chunk.length;
        if (responseBytes > MAX_ANALYZER_RESPONSE_BYTES) {
          analyzerResponse.destroy(new Error('Ballistics analyzer response is too large.'));
          return;
        }
        chunks.push(chunk);
      });

      analyzerResponse.on('end', () => {
        const body = Buffer.concat(chunks).toString('utf8');
        if (analyzerResponse.statusCode < 200 || analyzerResponse.statusCode >= 300) {
          reject(new Error(`Ballistics analyzer returned HTTP ${analyzerResponse.statusCode}.`));
          return;
        }

        try {
          resolve(JSON.parse(body));
        } catch {
          reject(new Error('Ballistics analyzer returned invalid JSON.'));
        }
      });

      analyzerResponse.on('error', reject);
    });

    analyzerRequest.setTimeout(timeoutMs, () => {
      analyzerRequest.destroy(new Error('Ballistics analyzer request timed out.'));
    });
    analyzerRequest.on('error', reject);

    const source = Readable.from((async function* () {
      yield prefix;
      for await (const chunk of fs.createReadStream(filePath)) {
        yield chunk;
      }
      yield suffix;
    })());
    source.on('error', (error) => analyzerRequest.destroy(error));
    source.pipe(analyzerRequest);
  });
}

function createForensicVideoBridge(options = {}) {
  const token = options.token || process.env.TRUST_VIDEO_API_TOKEN;
  if (!token) {
    throw new Error('Set TRUST_VIDEO_API_TOKEN before starting the forensic video bridge.');
  }

  const analyzerUrl = options.analyzerUrl || process.env.BALLISTICS_ANALYSIS_URL || DEFAULT_ANALYZER_URL;
  const maxUploadBytes = options.maxUploadBytes ?? Number(
    process.env.TRUST_VIDEO_MAX_UPLOAD_BYTES || DEFAULT_MAX_UPLOAD_BYTES
  );
  const timeoutMs = options.timeoutMs ?? Number(
    process.env.TRUST_VIDEO_ANALYZER_TIMEOUT_MS || 300000
  );
  if (!Number.isSafeInteger(maxUploadBytes) || maxUploadBytes < 1) {
    throw new Error('TRUST_VIDEO_MAX_UPLOAD_BYTES must be a positive safe integer.');
  }
  if (!Number.isSafeInteger(timeoutMs) || timeoutMs < 1) {
    throw new Error('TRUST_VIDEO_ANALYZER_TIMEOUT_MS must be a positive safe integer.');
  }

  const webSocketServer = new WebSocketServer({ noServer: true, maxPayload: 1024 });
  const server = http.createServer(async (request, response) => {
    const url = new URL(request.url, 'http://localhost');

    if (request.method === 'GET' && url.pathname === '/health') {
      sendJson(response, 200, { ok: true, service: 'trust-forensic-video-bridge' });
      return;
    }

    if (url.pathname !== VIDEO_ROUTE || request.method !== 'POST') {
      sendJson(response, 404, { error: 'Not found.' });
      return;
    }

    if (!bearerTokenMatches(request, token)) {
      sendJson(response, 401, { error: 'Authentication required.' });
      return;
    }

    const caseId = url.searchParams.get('caseId');
    if (!validCaseId(caseId)) {
      sendJson(response, 400, { error: 'A valid caseId query parameter is required.' });
      return;
    }

    const contentType = String(request.headers['content-type'] || '')
      .split(';', 1)[0]
      .trim()
      .toLowerCase();
    if (contentType !== 'application/octet-stream' && !/^video\/[a-z0-9][a-z0-9.+-]*$/.test(contentType)) {
      sendJson(response, 415, { error: 'Send a video/* or application/octet-stream request body.' });
      return;
    }

    const contentLength = Number(request.headers['content-length']);
    if (!Number.isSafeInteger(contentLength) || contentLength < 1) {
      sendJson(response, 411, { error: 'A positive Content-Length header is required.' });
      return;
    }
    if (contentLength > maxUploadBytes) {
      sendJson(response, 413, { error: 'Video exceeds the configured upload limit.' });
      request.resume();
      return;
    }

    const fileName = safeFileName(request.headers['x-file-name']);
    const uploadId = crypto.randomUUID();
    let tempDirectory;

    try {
      tempDirectory = await fs.promises.mkdtemp(path.join(os.tmpdir(), 'trust-video-'));
      const filePath = path.join(tempDirectory, `${uploadId}.video`);
      const receivedBytes = await writeUpload(request, filePath, maxUploadBytes);
      if (receivedBytes !== contentLength) {
        sendJson(response, 400, { error: 'Received body length did not match Content-Length.' });
        return;
      }

      const emit = (type, details = {}) => {
        const event = JSON.stringify({
          type,
          uploadId,
          caseId,
          timestamp: new Date().toISOString(),
          ...details
        });
        for (const client of webSocketServer.clients) {
          if (client.readyState === WebSocket.OPEN) {
            client.send(event);
          }
        }
      };

      emit('analysis.started', { fileName, bytes: receivedBytes });
      try {
        const result = await forwardToAnalyzer({
          analyzerUrl,
          caseId,
          filePath,
          fileName,
          contentType,
          timeoutMs
        });
        emit('analysis.completed');
        sendJson(response, 200, { success: true, uploadId, caseId, result });
      } catch (error) {
        emit('analysis.failed', { error: error.message });
        sendJson(response, 502, { success: false, uploadId, caseId, error: error.message });
      }
    } catch (error) {
      if (!response.headersSent) {
        sendJson(response, error.statusCode || 400, {
          error: error.statusCode === 413 ? error.message : 'Video upload failed.'
        });
      }
    } finally {
      if (tempDirectory) {
        await fs.promises.rm(tempDirectory, { recursive: true, force: true }).catch(() => {});
      }
    }
  });

  server.on('upgrade', (request, socket, head) => {
    const url = new URL(request.url, 'http://localhost');
    if (url.pathname !== EVENTS_ROUTE || !bearerTokenMatches(request, token)) {
      socket.write('HTTP/1.1 401 Unauthorized\r\nConnection: close\r\n\r\n');
      socket.destroy();
      return;
    }

    webSocketServer.handleUpgrade(request, socket, head, (webSocket) => {
      webSocketServer.emit('connection', webSocket, request);
    });
  });

  webSocketServer.on('connection', (webSocket) => {
    webSocket.send(JSON.stringify({
      type: 'connected',
      timestamp: new Date().toISOString()
    }));
    webSocket.on('message', (data) => {
      try {
        const message = JSON.parse(data.toString());
        if (message.type === 'ping') {
          webSocket.send(JSON.stringify({ type: 'pong', id: message.id }));
        }
      } catch {
        webSocket.close(1007, 'Messages must be valid JSON.');
      }
    });
  });

  server.on('close', () => webSocketServer.close());
  server.wss = webSocketServer;
  return server;
}

if (require.main === module) {
  const server = createForensicVideoBridge();
  const host = process.env.TRUST_VIDEO_HOST || '127.0.0.1';
  const port = Number(process.env.TRUST_VIDEO_PORT || 3010);
  server.listen(port, host, () => {
    console.log(`Trust forensic video bridge listening on http://${host}:${port}`);
  });
}

module.exports = { createForensicVideoBridge };
