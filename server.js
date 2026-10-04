const http = require('node:http');

const PORT = Number(process.env.PORT || 3000);

const server = http.createServer((request, response) => {
  const pathname = new URL(request.url, 'http://localhost').pathname;

  if (pathname !== '/health') {
    response.writeHead(404, { 'Content-Type': 'application/json; charset=utf-8' });
    response.end(JSON.stringify({ error: 'Not found' }));
    return;
  }

  if (request.method !== 'GET') {
    response.writeHead(405, {
      Allow: 'GET',
      'Content-Type': 'application/json; charset=utf-8',
    });
    response.end(JSON.stringify({ error: 'Method not allowed' }));
    return;
  }

  response.writeHead(200, { 'Content-Type': 'application/json; charset=utf-8' });
  response.end(JSON.stringify({
    ok: true,
    service: 'trust-governance',
    timestamp: new Date().toISOString(),
  }));
});

server.listen(PORT, () => {
  console.log(`Trust health server listening on port ${PORT}`);
});
