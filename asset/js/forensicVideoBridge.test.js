'use strict';

const assert = require('node:assert/strict');
const http = require('node:http');
const { once } = require('node:events');
const test = require('node:test');
const WebSocket = require('ws');
const { createForensicVideoBridge } = require('./forensicVideoBridge');

function listen(server) {
  return new Promise((resolve) => {
    server.listen(0, '127.0.0.1', () => resolve(server.address().port));
  });
}

test('accepts authenticated video uploads, forwards them for analysis, and publishes WebSocket events', async (t) => {
  const authorization = ['Bearer', 'test-token'].join(' ');
  let analyzerBody = '';
  const analyzer = http.createServer((request, response) => {
    const chunks = [];
    request.on('data', (chunk) => chunks.push(chunk));
    request.on('end', () => {
      analyzerBody = Buffer.concat(chunks).toString('utf8');
      response.writeHead(200, { 'content-type': 'application/json' });
      response.end(JSON.stringify({ dropletsAnalyzed: 3 }));
    });
  });
  const analyzerPort = await listen(analyzer);
  t.after(() => new Promise((resolve) => analyzer.close(resolve)));

  const bridge = createForensicVideoBridge({
    token: 'test-token',
    analyzerUrl: `http://127.0.0.1:${analyzerPort}/api/forensics/analyze-spatter`,
    maxUploadBytes: 1024
  });
  const bridgePort = await listen(bridge);
  t.after(async () => {
    for (const client of bridge.wss?.clients || []) client.close();
    await new Promise((resolve) => bridge.close(resolve));
  });

  const socket = new WebSocket(`ws://127.0.0.1:${bridgePort}/api/forensics/events`, {
    headers: { authorization }
  });
  const receivedEvents = [];
  socket.on('message', (message) => receivedEvents.push(JSON.parse(message.toString())));
  await once(socket, 'open');

  const video = Buffer.from('sample-video');
  const response = await fetch(
    `http://127.0.0.1:${bridgePort}/api/forensics/videos?caseId=case-42`,
    {
      method: 'POST',
      headers: {
        authorization,
        'content-type': 'video/mp4',
        'content-length': String(video.length),
        'x-file-name': 'scene.mp4'
      },
      body: video
    }
  );

  assert.equal(response.status, 200);
  const responseBody = await response.json();
  assert.equal(responseBody.success, true);
  assert.equal(typeof responseBody.uploadId, 'string');
  assert.deepEqual(responseBody, {
    success: true,
    uploadId: responseBody.uploadId,
    caseId: 'case-42',
    result: { dropletsAnalyzed: 3 }
  });
  assert.match(analyzerBody, /name="caseId"\r\n\r\ncase-42/);
  assert.match(analyzerBody, /name="file"; filename="scene.mp4"/);
  assert.match(analyzerBody, /sample-video\r\n--trust-[a-f0-9]+--\r\n$/);

  await new Promise((resolve, reject) => {
    const deadline = setTimeout(() => reject(new Error('Timed out waiting for analysis event.')), 1000);
    const check = () => {
      if (receivedEvents.some((event) => event.type === 'analysis.completed')) {
        clearTimeout(deadline);
        resolve();
      } else {
        setTimeout(check, 10);
      }
    };
    check();
  });
  assert.ok(receivedEvents.some((event) => event.type === 'connected'));
  assert.ok(receivedEvents.some((event) => event.type === 'analysis.started' && event.caseId === 'case-42'));
  assert.ok(receivedEvents.some((event) => event.type === 'analysis.completed'));
  socket.close();
});

test('rejects unauthenticated requests and invalid case identifiers', async (t) => {
  const bridge = createForensicVideoBridge({ token: 'test-token' });
  const port = await listen(bridge);
  t.after(() => new Promise((resolve) => bridge.close(resolve)));

  const unauthorized = await fetch(`http://127.0.0.1:${port}/api/forensics/videos?caseId=case-1`, {
    method: 'POST'
  });
  assert.equal(unauthorized.status, 401);

  const invalidCase = await fetch(`http://127.0.0.1:${port}/api/forensics/videos?caseId=../private`, {
    method: 'POST',
    headers: {
      authorization: ['Bearer', 'test-token'].join(' '),
      'content-type': 'video/mp4',
      'content-length': '1'
    },
    body: Buffer.from('x')
  });
  assert.equal(invalidCase.status, 400);
});
