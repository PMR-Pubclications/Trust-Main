<!-- Add this section to your transparency_portal.php -->
<div class="card" style="margin-top: 20px;">
    <h3>Ecosystem Component Integrity</h3>
    <table style="width:100%; text-align:left; color: var(--text); border-collapse: collapse;">
        <thead>
            <tr style="border-bottom: 1px solid var(--border);">
                <th style="padding: 8px;">Repository / Module</th>
                <th style="padding: 8px;">Role</th>
                <th style="padding: 8px;">Current Version</th>
                <th style="padding: 8px;">Ledger Status</th>
            </tr>
        </thead>
        <tbody>
            <tr style="border-bottom: 1px solid rgba(255,255,255,0.05);">
                <td style="padding: 8px;"><a href="https://github.com/PMR-Pubclications/Trust-Main" target="_blank">Trust-Main</a></td>
                <td style="padding: 8px;">Server Core & Ledger Engine</td>
                <td style="padding: 8px;">v<?= htmlspecialchars($appVersion) ?></td>
                <td style="padding: 8px; color: #34d399;">● Intact</td>
            </tr>
            <tr style="border-bottom: 1px solid rgba(255,255,255,0.05);">
                <td style="padding: 8px;"><a href="https://github.com/PMR-Pubclications/Trust-Shell" target="_blank">Trust-Shell</a></td>
                <td style="padding: 8px;">Secure Mobile Wrapper</td>
                <td style="padding: 8px;">v1.0.4</td>
                <td style="padding: 8px; color: #34d399;">● Verified Hash</td>
            </tr>
            <tr>
                <td style="padding: 8px;">C++ Hardware Engines</td>
                <td style="padding: 8px;">Audio/Video Processing</td>
                <td style="padding: 8px;">v2.1</td>
                <td style="padding: 8px; color: #34d399;">● Verified Hash</td>
            </tr>
        </tbody>
    </table>
</div>
