// Inside your workspace graphic frontend script
function initializeWorkspaceTelemetry() {
    const ws = new WebSocket('ws://localhost:8080'); // Local secure IPC socket

    ws.onmessage = (event) => {
        const telemetry = JSON.parse(event.data);
        
        // Update Workspace UI Indicators
        document.getElementById('radioStatusIndicator').className = telemetry.radioArmed ? 'status-active' : 'status-standby';
        document.getElementById('meshLinkStatus').textContent = telemetry.meshNodeConnected ? 'MESH: SECURE (Fast Roaming)' : 'MESH: SEARCHING';
        
        if (telemetry.exitTriggered) {
            triggerVisualLockdownAlert(telemetry.triggeredCode);
        }
    };
}

function triggerVisualLockdownAlert(code) {
    const cockpit = document.getElementById('workspaceCockpit');
    cockpit.classList.add('lockdown-active');
    console.warn(`[!] CRITICAL: Exit triggered via radio code ${code}. Securing local cache.`);
}
