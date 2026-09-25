const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const crypto = require('crypto');
const cors = require('cors');
const { exec } = require('child_process');
const path = require('path');

const app = express();
const PORT = Number(process.env.PORT || 3000);
const ADMIN_KEY = process.env.TRUST_ADMIN_KEY || 'trust-admin-key';
const sessions = new Map();
const ROLES = ['trust_executor', 'police', 'fire'];

app.use(express.json({ limit: '100kb' }));
app.use(cors({ origin: true }));

const dbPath = path.resolve(__dirname, '..', '..', 'governance.db');
const db = new sqlite3.Database(dbPath, (err) => {
  if (err) {
    console.error('Database connection error:', err.message);
    process.exit(1);
  }
  console.log('Connected to the SQLite governance database:', dbPath);
});

const run = (sql, params = []) => new Promise((resolve, reject) => {
  db.run(sql, params, function (err) {
    if (err) return reject(err);
    resolve(this);
  });
});

const get = (sql, params = []) => new Promise((resolve, reject) => {
  db.get(sql, params, (err, row) => {
    if (err) return reject(err);
    resolve(row);
  });
});

async function initializeDatabase() {
  await run(`CREATE TABLE IF NOT EXISTS onboarding_profiles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    owner_name TEXT NOT NULL,
    repo_name TEXT NOT NULL,
    organization TEXT,
    contact_email TEXT,
    github_private_key TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
  )`);

  await run(`CREATE TABLE IF NOT EXISTS login_badges (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    personnel_id TEXT NOT NULL UNIQUE,
    badge_hash TEXT NOT NULL UNIQUE,
    display_name TEXT NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('trust_executor','police','fire')),
    status TEXT NOT NULL DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
  )`);
}

initializeDatabase().catch((err) => {
  console.error('Database init failed:', err);
  process.exit(1);
});

function hashBadge(value) {
  return crypto.createHash('sha256').update(String(value).trim()).digest('hex');
}

function safeEqual(a, b) {
  const aa = Buffer.from(String(a || ''));
  const bb = Buffer.from(String(b || ''));
  return aa.length === bb.length && crypto.timingSafeEqual(aa, bb);
}

function adminOnly(req, res, next) {
  const adminKey = req.get('x-admin-key') || '';
  if (!ADMIN_KEY || !safeEqual(adminKey, ADMIN_KEY)) {
    return res.status(401).json({ success: false, error: 'Administrator authorization required.' });
  }
  return next();
}

function roleRequired(...allowedRoles) {
  return (req, res, next) => {
    const authHeader = req.get('authorization') || '';
    const token = authHeader.replace(/^Bearer\s+/i, '').trim();
    const session = token && sessions.get(token);

    if (!session || session.expiresAt < Date.now()) {
      return res.status(401).json({ success: false, error: 'Login required.' });
    }

    if (!allowedRoles.includes(session.role)) {
      return res.status(403).json({ success: false, error: 'Insufficient role privileges.' });
    }

    req.session = session;
    return next();
  };
}

app.get('/health', (req, res) => {
  res.json({ ok: true, service: 'trust-governance', timestamp: new Date().toISOString() });
});

app.post('/api/onboard', async (req, res) => {
  const { owner_name, repo_name, organization, contact_email } = req.body || {};

  if (!owner_name || !repo_name) {
    return res.status(400).json({ error: 'Owner name and repository name are required.' });
  }

  try {
    const { privateKey } = crypto.generateKeyPairSync('rsa', {
      modulusLength: 2048,
      publicKeyEncoding: { type: 'spki', format: 'pem' },
      privateKeyEncoding: { type: 'pkcs8', format: 'pem' }
    });

    const result = await run(
      `INSERT INTO onboarding_profiles (owner_name, repo_name, organization, contact_email, github_private_key)
       VALUES (?, ?, ?, ?, ?)`,
      [owner_name, repo_name, organization || 'PMR Publications', contact_email || '', privateKey]
    );

    return res.json({
      success: true,
      message: 'Onboarding profile saved and private key generated successfully.',
      profile_id: result.lastID,
      generated_key_preview: privateKey.split('\n')[1] + '...'
    });
  } catch (err) {
    console.error('Onboarding failed:', err);
    return res.status(500).json({ error: 'Key generation failed: ' + err.message });
  }
});

app.post('/api/badges', adminOnly, async (req, res) => {
  const { personnel_id, badge_number, display_name, role = 'police' } = req.body || {};

  if (!/^[A-Za-z0-9-]{2,32}$/.test(String(personnel_id || '')) || !/^\d{3,20}$/.test(String(badge_number || '')) || !display_name || !ROLES.includes(role)) {
    return res.status(400).json({
      success: false,
      error: 'Valid personnel ID, numeric badge, display name, and role are required.'
    });
  }

  try {
    await run(
      `INSERT INTO login_badges (personnel_id, badge_hash, display_name, role)
       VALUES (?, ?, ?, ?)
       ON CONFLICT(personnel_id) DO UPDATE SET
         badge_hash = excluded.badge_hash,
         display_name = excluded.display_name,
         role = excluded.role,
         status = 'active',
         updated_at = CURRENT_TIMESTAMP`,
      [personnel_id, hashBadge(badge_number), display_name, role]
    );

    return res.status(201).json({ success: true, personnel_id, display_name, role, status: 'active' });
  } catch (err) {
    console.error('Badge assignment failed:', err);
    const conflict = /UNIQUE|constraint/i.test(err.message || '');
    return res.status(conflict ? 409 : 500).json({
      success: false,
      error: conflict ? 'Badge number is already assigned.' : 'Could not save badge assignment.'
    });
  }
});

app.delete('/api/badges/:personnelId', adminOnly, async (req, res) => {
  const { personnelId } = req.params;
  try {
    await run("UPDATE login_badges SET status = 'revoked', updated_at = CURRENT_TIMESTAMP WHERE personnel_id = ?", [personnelId]);
    return res.json({ success: true });
  } catch (err) {
    console.error('Badge removal failed:', err);
    return res.status(500).json({ success: false, error: 'Could not revoke badge assignment.' });
  }
});

app.post('/api/badge-lookup', async (req, res) => {
  const badge = String(req.body?.badge_number || '').trim();
  if (!/^\d{3,20}$/.test(badge)) {
    return res.json({ valid: false, reason: 'invalid_format' });
  }

  try {
    const row = await get(
      "SELECT personnel_id, display_name, role FROM login_badges WHERE badge_hash = ? AND status = 'active'",
      [hashBadge(badge)]
    );

    if (!row) {
      return res.json({ valid: false, reason: 'not_found' });
    }

    return res.json({
      valid: true,
      personnel_id: row.personnel_id,
      display_name: row.display_name,
      role: row.role
    });
  } catch (err) {
    console.error('Badge lookup failed:', err);
    return res.status(500).json({ valid: false, reason: 'lookup_error' });
  }
});

app.post('/api/badge-login', async (req, res) => {
  const badge = String(req.body?.badge_number || '').trim();

  if (!/^\d{3,20}$/.test(badge)) {
    return res.status(401).json({ success: false, error: 'Invalid badge number.' });
  }

  try {
    const row = await get(
      "SELECT personnel_id, display_name, role FROM login_badges WHERE badge_hash = ? AND status = 'active'",
      [hashBadge(badge)]
    );

    if (!row) {
      return res.status(401).json({ success: false, error: 'Invalid badge number.' });
    }

    const token = crypto.randomBytes(32).toString('hex');
    const session = {
      personnel_id: row.personnel_id,
      display_name: row.display_name,
      role: row.role,
      expiresAt: Date.now() + 8 * 60 * 60 * 1000
    };
    sessions.set(token, session);

    return res.json({
      success: true,
      token,
      user: {
        personnel_id: row.personnel_id,
        display_name: row.display_name,
        role: row.role
      },
      expires_in: 28800
    });
  } catch (err) {
    console.error('Badge login failed:', err);
    return res.status(500).json({ success: false, error: 'Authentication failed.' });
  }
});

app.get('/api/me', roleRequired('trust_executor', 'police', 'fire'), (req, res) => {
  return res.json({ success: true, user: req.session });
});

app.post('/api/trigger-trust-sync', roleRequired('trust_executor'), (req, res) => {
  const scriptPath = path.resolve(__dirname, '..', '..', 'asset', 'py', 'secure-googledive-access.py');

  exec(`python3 "${scriptPath}"`, (error, stdout, stderr) => {
    if (error) {
      console.error('Sync script error:', error.message);
      return res.status(500).json({ success: false, error: 'Sync failed.' });
    }

    if (stderr) {
      console.warn('Sync script stderr:', stderr);
    }

    return res.json({
      success: true,
      message: 'Secure trust Google Drive access script executed successfully.',
      output: stdout
    });
  });
});

app.listen(PORT, () => {
  console.log(`Governance onboarding server running on port ${PORT}`);
});


const express = require('express');
const cors = require('cors');
const app = express();
const PORT = process.env.PORT || 3000;

app.use(cors());
app.use(express.json());

// In-Memory State representing the live mining & ledger backend
let miningState = {
    activeWorkers: 4,
    hashrateTH: 4.8,
    dailyYieldECT: 14.2,
    bctReserve: 342.85,
    ledgerBalance: 1482550.00,
    ledgerStatus: "RECONCILED",
    pendingBlocks: 12,
    transactions: [
        { hash: "0x8f4c...3e19", timestamp: new Date().toISOString().replace('T', ' ').substring(0, 16), category: "Trust Distribution", amount: "+$45,000.00", status: "Verified" },
        { hash: "0x3a12...9b04", timestamp: new Date(Date.now() - 3600000 * 8).toISOString().replace('T', ' ').substring(0, 16), category: "Agent Gas Provision", amount: "-$1,250.00", status: "Verified" },
        { hash: "0x7c91...1a82", timestamp: new Date(Date.now() - 3600000 * 14).toISOString().replace('T', ' ').substring(0, 16), category: "Asset Liquidation (LTF)", amount: "+$120,000.00", status: "Verified" }
    ]
};

// Background loop simulating real mining hashrate fluctuations & ledger increments
setInterval(() => {
    // Add slight natural variance to hashrate (+/- 0.2 TH/s)
    const variance = (Math.random() * 0.4 - 0.2);
    miningState.hashrateTH = parseFloat(Math.max(1.0, miningState.hashrateTH + variance).toFixed(2));
    
    // Accumulate minor fractional yield changes
    miningState.bctReserve = parseFloat((miningState.bctReserve + 0.001).toFixed(4));
}, 5000);

// API Endpoint to fetch real-time miner & ledger stats
api_router = express.Router();
api_router.get('/stats', (req, res) => {
    res.json({
        success: true,
        timestamp: new Date().toISOString(),
        node: "Active-Main",
        ...miningState
    });
});

// API Endpoint to force a sync or add a ledger entry
api_router.post('/sync', (req, res) => {
    // Simulate finding a new block / processing settlement
    const randomHash = '0x' + Math.random().toString(16).substring(2, 10) + '...' + Math.random().toString(16).substring(2, 6);
    const newTx = {
        hash: randomHash,
        timestamp: new Date().toISOString().replace('T', ' ').substring(0, 16),
        category: "ECT Mining Reward Payout",
        amount: "+$2,450.00",
        status: "Verified"
    };
    
    miningState.transactions.unshift(newTx);
    if(miningState.transactions.length > 10) miningState.transactions.pop(); // keep last 10
    miningState.ledgerBalance += 2450.00;

    res.json({
        success: true,
        message: "Backend node synchronized successfully.",
        state: miningState
    });
});

app.use('/api', api_router);

app.listen(PORT, () => {
    console.log(`[BACKEND MINER] Legacy Trust daemon online on port ${PORT}`);
});
