const express = require('express');
const axios = require('axios');
require('dotenv').config();

const app = express();
app.use(express.json({ limit: '10mb' }));

const PORT = process.env.PORT || 3000;
const LOCAL_SCRAMBLER_TARGET = process.env.LOCAL_SCRAMBLER_TARGET || 'http://127.0.0.1:8000';
const RELAY_AUTH_KEY = process.env.RELAY_AUTH_KEY;

// Middleware: Pass-through authorization check
app.use((req, res, next) => {
    const authHeader = req.headers['x-relay-auth'];
    if (RELAY_AUTH_KEY && authHeader !== RELAY_AUTH_KEY) {
        return res.status(401).json({ error: 'Unauthorized: Invalid relay token' });
    }
    next();
});

// Wildcard router: Catches all routes and forwards to local 20-layer engine
app.all('/scramble/*', async (req, res) => {
    const endpointPath = req.params[0];
    const targetUrl = `${LOCAL_SCRAMBLER_TARGET}/${endpointPath}`;

    try {
        const response = await axios({
            method: req.method,
            url: targetUrl,
            data: req.body,
            params: req.query,
            headers: {
                'Content-Type': req.headers['content-type'] || 'application/json',
                'X-Relayed-By': 'GitHub-Relay-Node',
                'X-Scrambler-Layer-Count': '20'
            },
            timeout: 15000
        });

        return res.status(response.status).json(response.data);
    } catch (error) {
        const status = error.response ? error.response.status : 502;
        const detail = error.response ? error.response.data : error.message;

        return res.status(status).json({
            status: 'Relay Error',
            message: 'Failed to communicate with local scrambler engine',
            detail: detail
        });
    }
});

app.get('/health', (req, res) => {
    res.json({ status: 'Relay Active', target: LOCAL_SCRAMBLER_TARGET });
});

app.listen(PORT, () => {
    console.log(`[Relay] Server running on port ${PORT}`);
    console.log(`[Relay] Forwarding traffic -> ${LOCAL_SCRAMBLER_TARGET}`);
});
