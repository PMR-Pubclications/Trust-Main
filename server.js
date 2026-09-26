const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const fs = require('fs');
const path = require('path');

const app = express();
const PORT = Number(process.env.PORT || 3000);

app.use(express.json({ limit: '1mb' }));

const dataDir = path.join(__dirname, 'data');
const dbPath = path.join(dataDir, 'trust-main.db');

fs.mkdirSync(dataDir, { recursive: true });

const db = new sqlite3.Database(dbPath, (err) => {
  if (err) {
    console.error('Database connection error:', err.message);
    process.exit(1);
  }
  console.log(`SQLite ready at ${dbPath}`);
});

function run(sql, params = []) {
  return new Promise((resolve, reject) => {
    db.run(sql, params, function (err) {
      if (err) return reject(err);
      resolve({ id: this.lastID, changes: this.changes });
    });
  });
}

function all(sql, params = []) {
  return new Promise((resolve, reject) => {
    db.all(sql, params, (err, rows) => {
      if (err) return reject(err);
      resolve(rows);
    });
  });
}

async function initializeDatabase() {
  await run(`
    CREATE TABLE IF NOT EXISTS health_checks (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      status TEXT NOT NULL,
      created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    )
  `);

  await run(`
    CREATE TABLE IF NOT EXISTS properties (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      property_title TEXT,
      valuation REAL,
      created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    )
  `);

  await run(`INSERT OR IGNORE INTO health_checks (status) VALUES (?)`, ['ok']);
}

initializeDatabase().catch((err) => {
  console.error('Failed to initialize database:', err);
  process.exit(1);
});

app.get('/health', async (req, res) => {
  try {
    await run('INSERT INTO health_checks (status) VALUES (?)', ['ok']);
    res.json({ ok: true, service: 'trust-main', timestamp: new Date().toISOString() });
  } catch (err) {
    res.status(500).json({ ok: false, error: err.message });
  }
});

app.get('/api/stats', (req, res) => {
  res.json({
    ok: true,
    service: 'trust-main',
    uptime: process.uptime(),
    memory: process.memoryUsage(),
    node: process.version,
    timestamp: new Date().toISOString()
  });
});

app.get('/api/property/list', async (req, res) => {
  try {
    const rows = await all('SELECT * FROM properties ORDER BY id DESC');
    res.json({ success: true, properties: rows });
  } catch (err) {
    res.status(500).json({ success: false, error: err.message });
  }
});

app.post('/api/property/add', async (req, res) => {
  const { property_title, valuation } = req.body || {};

  if (!property_title) {
    return res.status(400).json({ success: false, error: 'property_title is required.' });
  }

  try {
    const result = await run(
      'INSERT INTO properties (property_title, valuation) VALUES (?, ?)',
      [property_title, Number(valuation || 0)]
    );

    res.json({
      success: true,
      id: result.id,
      message: 'Property created successfully.'
    });
  } catch (err) {
    res.status(500).json({ success: false, error: err.message });
  }
});

app.get('*', (req, res) => {
  res.status(404).json({ ok: false, message: 'Route not found.' });
});

app.listen(PORT, () => {
  console.log(`[TRUST-MAIN] server running on http://localhost:${PORT}`);
});
