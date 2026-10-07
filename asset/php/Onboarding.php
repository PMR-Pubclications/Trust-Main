<?php
session_start();

// Simulated API/Database Authentication Layer
if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['action']) && $_POST['action'] === 'login') {
    $badge = trim($_POST['badge_number']);
    
    // Assign clearance based on master badges
    if ($badge === '9999') {
        $_SESSION['user'] = [
            'display_name' => 'Command Chief',
            'role' => 'first_responder_admin'
        ];
    } elseif ($badge === '1111') {
        $_SESSION['user'] = [
            'display_name' => 'Trust Executor',
            'role' => 'trust_executor'
        ];
    } elseif ($badge === '3333') {
        $_SESSION['user'] = [
            'display_name' => 'Lead Paramedic',
            'role' => 'ems'
        ];
    } else {
        // Default mock field officer
        $_SESSION['user'] = [
            'display_name' => 'Field Officer',
            'role' => 'police'
        ];
    }
    header("Location: " . $_SERVER['PHP_SELF']);
    exit;
}

if (isset($_GET['action']) && $_GET['action'] === 'logout') {
    session_destroy();
    header("Location: " . $_SERVER['PHP_SELF']);
    exit;
}

$is_logged_in = isset($_SESSION['user']);
$user_role = $is_logged_in ? $_SESSION['user']['role'] : '';
$is_admin = ($user_role === 'first_responder_admin' || $user_role === 'trust_executor');
$can_access_hospital = in_array($user_role, ['ems', 'fire', 'hospital', 'first_responder_admin', 'trust_executor']);
$user_name = $is_logged_in ? $_SESSION['user']['display_name'] : '';
?>
<!doctype html>
<html lang="en">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Trust Governance Login</title>
<style>
:root{--bg:#020617;--panel:#0f172a;--card:#1e293b;--line:#475569;--text:#f8fafc;--muted:#94a3b8;--blue:#0284c7;--green:#16a34a;--red:#dc2626;--gold:#eab308;--teal:#0d9488}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--text);font-family:system-ui,sans-serif}
.wrap{width:min(1100px,94vw);margin:3vh auto}
.card{background:var(--card);border:2px solid var(--line);border-radius:10px;padding:22px;margin-bottom:18px}
.admin-card{border-color:var(--gold)}
.hospital-card{border-color:var(--teal)}
h1,h2,h3,p{margin-top:0}
p{color:var(--muted);font-size:14px}
label{display:block;color:var(--muted);font-size:13px;font-weight:700;margin:12px 0 5px}
input,select{width:100%;padding:11px;background:var(--bg);color:var(--text);border:2px solid var(--line);border-radius:6px;font-size:15px}
.btn{border:0;border-radius:6px;padding:11px 16px;color:white;background:var(--green);font-weight:700;cursor:pointer;margin-top:14px;text-decoration:none;display:inline-block;text-align:center}
.btn.blue{background:var(--blue)}
.btn.red{background:var(--red)}
.btn.teal{background:var(--teal)}
.hidden{display:none}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:18px}
.status{min-height:22px;color:var(--muted);margin-top:10px}
.userbar{display:flex;justify-content:space-between;gap:15px;align-items:center;border-bottom:1px solid var(--line);padding-bottom:12px}
.userbar small{color:var(--muted)}
.notice{border-left:4px solid var(--blue);padding:10px;background:#082f49;color:#bae6fd;font-size:13px}
.admin-badge{background:rgba(234,179,8,0.1);color:var(--gold);padding:4px 8px;border-radius:4px;font-size:11px;text-transform:uppercase;font-weight:bold;margin-left:8px;vertical-align:middle}
.hospital-badge{background:rgba(13,148,136,0.1);color:var(--teal);padding:4px 8px;border-radius:4px;font-size:11px;text-transform:uppercase;font-weight:bold;margin-left:8px;vertical-align:middle}
@media(max-width:600px){.userbar{display:block}.userbar .btn{margin-top:10px}}
</style>
</head>
<body>
<main class="wrap">

<?php if (!$is_logged_in): ?>
<!-- LOGIN SCREEN -->
<section id="login-screen" class="card">
    <h1>Trust Governance Login</h1>
    <p>Use the assigned badge number to authenticate. Access is controlled by role: Trust Executor, Police, Fire, EMS, DOT, or Hospital.</p>
    <form method="POST" action="">
        <input type="hidden" name="action" value="login">
        <label for="login-badge">Badge number</label>
        <input id="login-badge" name="badge_number" inputmode="numeric" autocomplete="off" required pattern="[0-9]{3,20}" maxlength="20" autofocus>
        <button class="btn blue" type="submit">Sign in with badge</button>
    </form>
    <div class="status" style="margin-top:15px; font-size:12px;">Admin Override: Use badge 9999 | EMS Test: 3333</div>
</section>

<?php else: ?>
<!-- APPLICATION SCREEN -->
<section id="app-screen">
    <div class="card">
        <div class="userbar">
            <div>
                <h2>Governance Portal</h2>
                <small id="current-user">
                    <?= htmlspecialchars($user_name) ?> &middot; <?= ucwords(str_replace('_', ' ', $user_role)) ?>
                </small>
            </div>
            <a href="?action=logout" class="btn red">Sign out</a>
        </div>
        <div class="notice" style="margin-top:16px">
            Role-based access is active. Content is filtered by your assigned First Responder clearance level.
        </div>
    </div>

    <div class="grid">
        <!-- Standard Modules -->
        <section class="card">
            <h3>Personnel</h3>
            <p>Personnel records are visible to all signed-in mobile lab members.</p>
        </section>
        
        <section class="card">
            <h3>Operations</h3>
            <p>Standard operational access. Connects with field modules.</p>
        </section>

        <!-- Hospital / EMS Connectivity Module -->
        <?php if ($can_access_hospital): ?>
        <section class="card hospital-card">
            <h3>Hospital Network <span class="hospital-badge">HL7/FHIR Secure</span></h3>
            <p>Direct query access to regional hospital triage and patient databases. Ensure HIPAA compliance when transmitting data.</p>
            <form id="hospital-query">
                <label for="patient-id">Patient ID or Name</label>
                <input id="patient-id" required placeholder="Enter query parameters">
                <label for="facility">Target Facility</label>
                <select id="facility">
                    <option value="regional_general">Regional General Hospital</option>
                    <option value="trauma_center_1">Level 1 Trauma Center</option>
                    <option value="burn_unit">Specialized Burn Unit</option>
                </select>
                <button type="submit" class="btn teal" style="width: 48%;">Pull Records</button>
                <button type="button" class="btn blue" style="width: 48%; float: right;">Push ePCR</button>
            </form>
        </section>
        <?php endif; ?>

        <!-- Admin Level Modules -->
        <?php if ($is_admin): ?>
        <section class="card admin-card">
            <h3>Anon AI Overrides <span class="admin-badge">Admin</span></h3>
            <p>Manage continuous learning loops, adjust verbal suggestion engine parameters, and toggle audio/visual safety overrides.</p>
            <button class="btn blue" type="button">Trigger Trust sync</button>
        </section>

        <section class="card admin-card">
            <h3>Badge Assignment <span class="admin-badge">Admin</span></h3>
            <p>Assign credentials to cross-agency personnel.</p>
            <form method="POST" action="">
                <input type="hidden" name="action" value="assign_badge">
                <label for="personnel-id">Personnel ID</label>
                <input id="personnel-id" name="personnel_id" required pattern="[A-Za-z0-9-]{2,32}">
                
                <label for="badge-number">Badge number</label>
                <input id="badge-number" name="new_badge" inputmode="numeric" required pattern="[0-9]{3,20}">
                
                <label for="role">Role</label>
                <select id="role" name="role">
                    <option value="police">Police</option>
                    <option value="fire">Fire</option>
                    <option value="ems">EMS</option>
                    <option value="dot">DOT</option>
                    <option value="hospital">Hospital Administration</option>
                    <option value="trust_executor">Trust Executor</option>
                    <option value="first_responder_admin">First Responder Admin</option>
                </select>
                <button class="btn" type="button" onclick="alert('Assignment logic connects to backend API.')">Assign badge</button>
            </form>
        </section>
        <?php endif; ?>
    </div>
</section>
<?php endif; ?>

</main>
<script src="assets/js/api_bridge.js"></script>
</body>
</html>
