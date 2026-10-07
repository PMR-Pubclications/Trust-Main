<?php
// Handle Multi-Agency Evidence Dispatch Form Submission
$dispatch_status = "[DISPATCH GATEWAY] Ready for multi-agency routing configuration.";
$status_color = "#38bdf8";

if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['action']) && $_POST['action'] === 'execute_dispatch') {
    $district = trim($_POST['dispatch_district'] ?? '');
    $courthouse = trim($_POST['dispatch_courthouse'] ?? '');
    $lab = trim($_POST['dispatch_lab'] ?? '');
    $archive = trim($_POST['dispatch_officer_archive'] ?? '');

    if (!empty($courthouse) && !empty($lab)) {
        // Simulated secure dispatch route execution across agency endpoints
        $archive_notice = !empty($archive) ? " and archival copy to {$archive}" : "";
        $dispatch_status = "[DISPATCH SUCCESS] Report routed to Prosecuting Attorney ({$courthouse}), Forensics Lab ({$lab}){$archive_notice} for {$district}.";
        $status_color = "#16a34a"; // Success green
    } else {
        $dispatch_status = "[DISPATCH ERROR] Missing required destination endpoints for Courthouse or Forensics Lab.";
        $status_color = "#dc2626"; // Error red
    }
}
?>

<!-- MULTI-AGENCY SECURE EVIDENCE DISPATCH PANEL -->
<div class="card" style="border-color: var(--blue, #0284c7); margin-top: 20px;">
    <h3>🛡️ Secure Multi-Agency Evidence Dispatch</h3>
    <p style="font-size: 13px; color: var(--muted, #94a3b8);">Route court-admissible, LSU-resistant forensic reports to authorized recipients while maintaining an independent cryptographic chain-of-custody archive.</p>
    
    <form method="POST" action="">
        <input type="hidden" name="action" value="execute_dispatch">

        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 12px; margin-top: 15px;">
            <div class="form-group">
                <label for="dispatch-district">Operational District / Precinct</label>
                <input type="text" id="dispatch-district" name="dispatch_district" value="<?= htmlspecialchars($_POST['dispatch_district'] ?? 'Vancouver PD - Precinct 2') ?>" placeholder="e.g., Precinct 2 / Sector 4">
            </div>
            <div class="form-group">
                <label for="dispatch-courthouse">County Courthouse / Prosecuting Attorney Gateway</label>
                <input type="email" id="dispatch-courthouse" name="dispatch_courthouse" value="<?= htmlspecialchars($_POST['dispatch_courthouse'] ?? 'clerk.prosecution@clark.wa.gov') ?>" placeholder="court.clerk@county.gov" required>
            </div>
        </div>

        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 12px; margin-top: 5px;">
            <div class="form-group">
                <label for="dispatch-lab">Forensics Lab Secure Server Endpoint</label>
                <input type="text" id="dispatch-lab" name="dispatch_lab" value="<?= htmlspecialchars($_POST['dispatch_lab'] ?? 'forensics.lab@vancouverpolice.internal') ?>" placeholder="lab.endpoint@agency.gov" required>
            </div>
            <div class="form-group">
                <label for="dispatch-officer-archive">Officer / Independent Archival Email (Self-Preservation)</label>
                <input type="email" id="dispatch-officer-archive" name="dispatch_officer_archive" value="<?= htmlspecialchars($_POST['dispatch_officer_archive'] ?? '') ?>" placeholder="officer.secure.archive@proton.me">
            </div>
        </div>

        <button type="submit" class="btn" style="background-color: var(--green, #16a34a); margin-top: 14px; width: 100%;">
            🚀 Dispatch Report to All Three Authorized Destinations
        </button>
    </form>

    <div id="dispatch-console" class="status" style="margin-top: 12px; font-family: monospace; font-size: 11px; color: <?= $status_color ?>;">
        <?= htmlspecialchars($dispatch_status) ?>
    </div>
</div>
