<?php
/**
 * Active Duty Roster & Clock-In Dashboard
 * Path: trust-main/index.php
 */

if (session_status() === PHP_SESSION_NONE) {
    session_start();
}

// 1. Load Application Manifest
$manifestPath = __DIR__ . '/config/guide_manifest.json';
$manifest = file_exists($manifestPath) ? json_decode(file_get_contents($manifestPath), true) : [];

$appVersion  = $manifest['version'] ?? '1.2.0';
$activeRole  = strtoupper($_GET['role'] ?? 'ALL');
$statusFilter = strtolower($_GET['status'] ?? 'all'); // 'all', 'online', 'offline'
$pageTitle   = ($manifest['app_name'] ?? 'Trust-Shell') . ' // Duty Roster & Shift Tracking';

// 2. Sample Duty Roster Dataset (In production, replace with DB query or live session store)
$dutyRoster = [
    [
        'id'           => 'OFF-1042',
        'name'         => 'Anatolie Antolic',
        'badge'        => '4408',
        'role'         => 'POLICE',
        'unit'         => 'Precinct 2 - Tactical Command',
        'shift'        => 'Day Shift (06:00 - 18:00)',
        'clocked_in'   => '2026-10-05 05:45:00',
        'is_online'    => true,
        'photo'        => 'asset/officers/badge-4408.jpg'
    ],
    [
        'id'           => 'OFF-2189',
        'name'         => 'Sarah Jenkins',
        'badge'        => '1204',
        'role'         => 'FIRE',
        'unit'         => 'Station 7 - Engine 3',
        'shift'        => 'Swing Shift (14:00 - 02:00)',
        'clocked_in'   => '2026-10-05 06:15:00',
        'is_online'    => true,
        'photo'        => null // Fallback avatar used automatically
    ],
    [
        'id'           => 'OFF-3110',
        'name'         => 'Marcus Vance',
        'badge'        => '8821',
        'role'         => 'EMS',
        'unit'         => 'District 4 - Medic Unit 12',
        'shift'        => 'Night Shift (18:00 - 06:00)',
        'clocked_in'   => null,
        'is_online'    => false,
        'photo'        => null
    ],
    [
        'id'           => 'OFF-4002',
        'name'         => 'Elena Rostova',
        'badge'        => '3319',
        'role'         => 'DOT',
        'unit'         => 'Highway Operations - Patrol 5',
        'shift'        => 'Day Shift (06:00 - 18:00)',
        'clocked_in'   => '2026-10-05 05:30:00',
        'is_online'    => true,
        'photo'        => 'asset/officers/badge-3319.jpg'
    ]
];

// 3. Filter Roster Logic
$filteredRoster = array_filter($dutyRoster, function ($responder) use ($activeRole, $statusFilter) {
    if ($activeRole !== 'ALL' && $responder['role'] !== $activeRole) {
        return false;
    }
    if ($statusFilter === 'online' && !$responder['is_online']) {
        return false;
    }
    if ($statusFilter === 'offline' && $responder['is_online']) {
        return false;
    }
    return true;
});

// Helper Function: Calculate Elapsed Time on Shift
function formatOnClockDuration(?string $clockInTime): string {
    if (!$clockInTime) return 'N/A';
    $start = new DateTime($clockInTime);
    $now   = new DateTime();
    $diff  = $start->diff($now);
    
    $parts = [];
    if ($diff->h > 0) $parts[] = $diff->h . 'h';
    $parts[] = $diff->i . 'm';
    return implode(' ', $parts) . ' ago';
}

// 4. Render Header
require_once __DIR__ . '/includes/header.php';
?>

<!-- Duty Dashboard Top Controls -->
<div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 25px; flex-wrap: wrap; gap: 15px;">
    <div>
        <h1 style="font-size: 1.5rem; margin: 0 0 6px 0; color: var(--accent-white);">
            Active First Responder Duty Roster
        </h1>
        <div style="font-size: 0.85rem; color: var(--text-muted);">
            Real-time shift log & clock-in telemetry across precincts and units.
        </div>
    </div>

    <!-- Status Toggle Filter Buttons -->
    <div style="display: flex; gap: 6px; background-color: var(--panel-bg); padding: 4px; border-radius: 6px; border: 1px solid var(--border-bright);">
        <a href="index.php?role=<?= $activeRole ?>&status=all" class="role-btn <?= $statusFilter === 'all' ? 'active' : '' ?>">ALL</a>
        <a href="index.php?role=<?= $activeRole ?>&status=online" class="role-btn <?= $statusFilter === 'online' ? 'active' : '' ?>" style="color: #10b981;">ONLINE</a>
        <a href="index.php?role=<?= $activeRole ?>&status=offline" class="role-btn <?= $statusFilter === 'offline' ? 'active' : '' ?>" style="color: #dc2626;">OFFLINE</a>
    </div>
</div>

<!-- Grid Layout for Personnel Cards -->
<div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 20px;">

<!-- Real-Time Microphone Telemetry Sine Wave Visualizer -->
<div class="card mic-telemetry-card" style="margin-top: 20px; background-color: var(--term-black, #050b05); border: 1px solid var(--term-green-dark, #003311); padding: 12px; position: relative; overflow: hidden;">
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
        <span style="font-size: 0.78rem; color: var(--term-green-dim, #009933); font-family: var(--font-terminal, monospace); font-weight: bold;">
            &gt; MIC AUDIO TELEMETRY GAIN
        </span>
        <div style="display: flex; align-items: center; gap: 10px;">
            <span id="micDbReadout" style="font-size: 0.75rem; color: var(--term-blue, #00ccff); font-family: var(--font-terminal, monospace);">
                [ GAIN: 0.0 dB ]
            </span>
            <button id="startMicBtn" onclick="initMicTelemetry()" style="background: none; border: 1px solid var(--term-green, #00ff66); color: var(--term-green, #00ff66); font-family: var(--font-terminal, monospace); font-size: 0.75rem; padding: 2px 8px; cursor: pointer;">
                [ START MIC ]
            </button>
        </div>
    </div>

    <!-- Responsive Waveform Canvas Container -->
    <div style="width: 100%; height: 80px; position: relative; background-color: #010801; border: 1px solid var(--term-green-dark, #003311);">
        <canvas id="micWaveformCanvas" style="width: 100%; height: 100%; display: block;"></canvas>
    </div>
</div>

<script>
    let audioCtx = null;
    let analyser = null;
    let micStream = null;
    let dataArray = null;
    let isMicActive = false;
    let phase = 0;

    const canvas = document.getElementById('micWaveformCanvas');
    const ctx = canvas.getContext('2d');
    const micDbReadout = document.getElementById('micDbReadout');
    const startMicBtn = document.getElementById('startMicBtn');

    // Handle high-DPI and responsive window resizing
    function resizeCanvas() {
        if (!canvas) return;
        const rect = canvas.getBoundingClientRect();
        canvas.width = rect.width * window.devicePixelRatio;
        canvas.height = rect.height * window.devicePixelRatio;
        ctx.scale(window.devicePixelRatio, window.devicePixelRatio);
    }

    window.addEventListener('resize', resizeCanvas);
    resizeCanvas();

    async function initMicTelemetry() {
        if (isMicActive) return;

        try {
            micStream = await navigator.mediaDevices.getUserMedia({ audio: true, video: false });
            audioCtx = new (window.AudioContext || window.webkitAudioContext)();
            
            const source = audioCtx.createMediaStreamSource(micStream);
            analyser = audioCtx.createAnalyser();
            analyser.fftSize = 512;
            analyser.smoothingTimeConstant = 0.8;

            source.connect(analyser);

            const bufferLength = analyser.frequencyBinCount;
            dataArray = new Uint8Array(bufferLength);

            isMicActive = true;
            startMicBtn.innerText = '[ MIC ACTIVE ]';
            startMicBtn.style.borderColor = 'var(--term-blue, #00ccff)';
            startMicBtn.style.color = 'var(--term-blue, #00ccff)';

            drawWaveform();
        } catch (err) {
            console.error('Microphone access denied or unsupported:', err);
            startMicBtn.innerText = '[ PERMISSION DENIED ]';
            startMicBtn.style.borderColor = 'var(--term-red, #ff3333)';
            startMicBtn.style.color = 'var(--term-red, #ff3333)';
        }
    }

    function drawWaveform() {
        requestAnimationFrame(drawWaveform);

        const width = canvas.getBoundingClientRect().width;
        const height = canvas.getBoundingClientRect().height;
        const centerY = height / 2;

        ctx.clearRect(0, 0, width, height);

        // Draw background grid lines (Terminal style)
        ctx.strokeStyle = 'rgba(0, 51, 17, 0.4)';
        ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.moveTo(0, centerY);
        ctx.lineTo(width, centerY);
        ctx.stroke();

        let volumeRms = 0;

        if (isMicActive && analyser) {
            analyser.getByteFrequencyData(dataArray);

            // Compute Root Mean Square (RMS) volume level
            let sum = 0;
            for (let i = 0; i < dataArray.length; i++) {
                sum += dataArray[i] * dataArray[i];
            }
            volumeRms = Math.sqrt(sum / dataArray.length);

            // Update dB Gain Display
            const dbVal = Math.min(Math.round((volumeRms / 255) * 100), 100);
            micDbReadout.innerText = `[ GAIN: ${dbVal.toFixed(1)} dB ]`;
        }

        // Render Sine Wave
        ctx.beginPath();
        ctx.lineWidth = 2;
        ctx.strokeStyle = isMicActive ? '#00ff66' : '#003311';
        ctx.shadowBlur = isMicActive ? 8 : 0;
        ctx.shadowColor = '#00ff66';

        // Amplitude scales smoothly with mic volume
        const maxAmplitude = height * 0.4;
        const targetAmplitude = (volumeRms / 128) * maxAmplitude;
        const baseBaselineAmp = isMicActive ? Math.max(3, targetAmplitude) : 1;

        phase += 0.08;

        for (let x = 0; x < width; x++) {
            // Complex multi-frequency sine equation for organic oscilloscope appearance
            const freq1 = 0.02;
            const freq2 = 0.04;
            const sineY = Math.sin(x * freq1 + phase) * baseBaselineAmp 
                        + Math.sin(x * freq2 - phase * 0.5) * (baseBaselineAmp * 0.3);

            const y = centerY + sineY;

            if (x === 0) {
                ctx.moveTo(x, y);
            } else {
                ctx.lineTo(x, y);
            }
        }

        ctx.stroke();
    }

    // Initial render call to show stationary baseline
    drawWaveform();
</script>

    <?php if (empty($filteredRoster)): ?>
        <div class="feature-card" style="grid-column: 1 / -1;">
            <div class="feature-title" style="color: var(--accent-red);">No Active Personnel Found</div>
            <p style="color: var(--text-muted); margin-top: 8px;">No responders match the current role or online filter settings.</p>
        </div>
    <?php else: ?>
        <?php foreach ($filteredRoster as $officer): ?>
            <?php 
                $isOnline = $officer['is_online'];
                $statusColor = $isOnline ? '#10b981' : '#dc2626';
                $statusLabel = $isOnline ? 'ONLINE' : 'OFFLINE';
                
                // Fallback Avatar SVG if photo doesn't exist
                $hasPhoto = !empty($officer['photo']) && file_exists(__DIR__ . '/' . $officer['photo']);
            ?>
            <div class="feature-card" style="display: flex; flex-direction: column; height: 100%; border-top: 3px solid <?= $statusColor ?>;">
                
                <!-- Card Top Bar: Photo / Avatar + Name & Badge -->
                <div style="display: flex; gap: 16px; align-items: center; margin-bottom: 16px; border-bottom: 1px solid var(--border); padding-bottom: 14px;">
                    
                    <!-- Officer Photo / Fallback Avatar -->
                    <div style="width: 64px; height: 64px; border-radius: 8px; overflow: hidden; background-color: var(--bg-dark); border: 1px solid var(--border-bright); flex-shrink: 0; display: flex; align-items: center; justify-content: center;">
                        <?php if ($hasPhoto): ?>
                            <img src="<?= htmlspecialchars($officer['photo']) ?>" alt="<?= htmlspecialchars($officer['name']) ?>" style="width: 100%; height: 100%; object-fit: cover;">
                        <?php else: ?>
                            <!-- Fallback Shield / Silhouette Icon -->
                            <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="var(--text-muted)" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
                                <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path>
                                <circle cx="12" cy="10" r="3"></circle>
                            </svg>
                        <?php endif; ?>
                    </div>

                    <!-- Officer Identity Details -->
                    <div style="flex: 1;">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 2px;">
                            <span class="badge badge-ver" style="font-size: 0.65rem;"><?= htmlspecialchars($officer['role']) ?></span>
                            <span style="color: <?= $statusColor ?>; font-weight: 700; font-size: 0.75rem; letter-spacing: 0.5px;">
                                &#9673; <?= $statusLabel ?>
                            </span>
                        </div>
                        <h2 style="font-size: 1.1rem; margin: 2px 0 0 0; color: var(--accent-white); font-weight: 700;">
                            <?= htmlspecialchars($officer['name']) ?>
                        </h2>
                        <div style="font-size: 0.8rem; color: var(--code-text); font-family: monospace; margin-top: 2px;">
                            BADGE #<?= htmlspecialchars($officer['badge']) ?>
                        </div>
                    </div>
                </div>

                <!-- Assignment Metadata Table -->
                <div style="display: flex; flex-direction: column; gap: 8px; font-size: 0.85rem; flex: 1;">
                    <div style="display: flex; justify-content: space-between;">
                        <span style="color: var(--text-muted);">Assigned Unit:</span>
                        <strong style="color: var(--text-main); text-align: right;"><?= htmlspecialchars($officer['unit']) ?></strong>
                    </div>

                    <div style="display: flex; justify-content: space-between;">
                        <span style="color: var(--text-muted);">Current Shift:</span>
                        <span style="color: var(--text-main);"><?= htmlspecialchars($officer['shift']) ?></span>
                    </div>

                    <div style="display: flex; justify-content: space-between;">
                        <span style="color: var(--text-muted);">Clock-In Time:</span>
                        <span style="color: var(--text-main); font-family: monospace;">
                            <?= $officer['clocked_in'] ? date('H:i:s T', strtotime($officer['clocked_in'])) : 'Not Clocked In' ?>
                        </span>
                    </div>
<!-- Voice Control Notice Banner -->
<div class="voice-marquee-container">
    <div class="voice-marquee-text">
        &#9888;&#65039; THIS APP IS COMPLETELY VOICE ACTIVATED. PLEASE REFER TO THE USER'S MANUAL. &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; &#9888;&#65039; THIS APP IS COMPLETELY VOICE ACTIVATED. PLEASE REFER TO THE USER'S MANUAL.
    </div>
</div>

<style>
.voice-marquee-container {
    width: 100%;
    overflow: hidden;
    background-color: #facc15; /* High-visibility yellow */
    color: #000000;            /* Black lettering */
    padding: 8px 0;
    margin: 20px 0;
    border-top: 2px solid #000000;
    border-bottom: 2px solid #000000;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
    white-space: nowrap;
}

.voice-marquee-text {
    display: inline-block;
    padding-left: 100%;
    animation: marquee-scroll 18s linear infinite;
    font-family: monospace, sans-serif;
    font-size: 0.95rem;
    font-weight: 800;
    letter-spacing: 1px;
    text-transform: uppercase;
}

@keyframes marquee-scroll {
    0% {
        transform: translate(0, 0);
    }
    100% {
        transform: translate(-100%, 0);
    }
}

/* Pause animation on hover if operator needs to read closely */
.voice-marquee-container:hover .voice-marquee-text {
    animation-play-state: paused;
}
</style>

  <?php if ($isOnline && $officer['clocked_in']): ?>
                        <div style="display: flex; justify-content: space-between; background-color: var(--bg-dark); padding: 8px 10px; border-radius: 4px; margin-top: 6px; border: 1px solid var(--border);">
                            <span style="color: var(--text-muted);">Time on Duty:</span>
                            <strong style="color: #10b981; font-family: monospace;">
                                <?= formatOnClockDuration($officer['clocked_in']) ?>
                            </strong>
                        </div>
                    <?php endif; ?>
                </div>

            </div>
        <?php endforeach; ?>
    <?php endif; ?>
</div>

<?php
// 5. Render Footer
require_once __DIR__ . '/includes/footer.php';
?>
