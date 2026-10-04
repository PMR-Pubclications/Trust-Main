/**
 * ANNON VOICE ENGINE - NOISE-CANCELED C++ IPC PIPELINE
 * Subsystems:
 *  - C++ A/V Engine (Native DSP/Noise Canceling): ./asset/cpp/AudioVideoEngine-CPP/build/av_engine
 *  - Forensics AI Brain:                        ./asset/py/ferensics-ai/main.py
 *  - Legacy Trust AI:                           ./asset/py/legacyTrust-AI/main.py
 */

const path = require('path');
const { spawn, exec } = require('child_process');

// ============================================================================
// 1. PATH CONFIGURATION
// ============================================================================
const BIN_PATH = path.join(__dirname, 'asset', 'cpp', 'AudioVideoEngine-CPP', 'build', 'av_engine');
const FORENSICS_AI_PATH = path.join(__dirname, 'asset', 'py', 'ferensics-ai', 'main.py');
const LEGACY_AI_PATH = path.join(__dirname, 'asset', 'py', 'legacyTrust-AI', 'main.py');

const ACTIVE_SESSION = { sessionId: 'SESS-7042', officerId: 'OFFICER-7042' };

// ============================================================================
// 2. LIVE C++ PROCESS (WITH NATIVE DSP/NOISE SUPPRESSION)
// ============================================================================
// Passing --noise-cancel flag if required by C++ binary CLI configuration
const avProcess = spawn(BIN_PATH, ['--live', '--dsp-noise-suppression=on'], {
    stdio: ['pipe', 'pipe', 'pipe']
});

// Receive pre-cleared transcriptions/events directly from native C++ stdout
avProcess.stdout.on('data', async (chunk) => {
    const raw = chunk.toString().trim();
    if (!raw) return;

    try {
        const event = JSON.parse(raw);
        // Pre-filtered STT result stream
        if (event.type === 'STT_RESULT' && event.text.toLowerCase().includes('annon')) {
            handleVoiceCommand(event.text);
        }
    } catch (e) {
        if (raw.toLowerCase().includes('annon')) {
            handleVoiceCommand(raw);
        }
    }
});

avProcess.stderr.on('data', (data) => {
    console.error(`[C++ ENGINE LOG]: ${data.toString().trim()}`);
});

// ============================================================================
// 3. MASTER ROUTER
// ============================================================================
async function handleVoiceCommand(phrase) {
    const text = phrase.toLowerCase().trim();
    console.log(`[CLEANED STT INGEST]: "${phrase}"`);

    // GLOBAL COMMAND: Trust Forensics AI
    if (/annon,?\s+(activate|open)\s+trust\s+(forensics|ferensics)/i.test(text)) {
        console.log('[DISPATCH]: Invoking Forensics AI Engine...');
        await executePythonScript(FORENSICS_AI_PATH, ['--mode', 'forensic_analysis', '--session', ACTIVE_SESSION.sessionId]);
        speak('Trust Forensics AI engine activated.');
        return;
    }

    // GLOBAL COMMAND: Legacy Trust AI
    if (/annon,?\s+(open|activate)\s+legacy\s+trust\s+ai/i.test(text)) {
        console.log('[DISPATCH]: Invoking Legacy Trust AI...');
        await executePythonScript(LEGACY_AI_PATH, ['--session', ACTIVE_SESSION.sessionId]);
        speak('Legacy Trust AI active.');
        return;
    }

    // C++ HARDWARE CONTROL: LiDAR / 3D Scanning
    if (/annon,?\s+capture\s+3d\s+scan/i.test(text)) {
        avProcess.stdin.write(JSON.stringify({ cmd: 'START_LIDAR' }) + '\n');
        speak('3D spatial scan started.');
        return;
    }
}

// ============================================================================
// 4. UTILITIES & SYSTEM FEEDBACK
// ============================================================================
function executePythonScript(scriptPath, args = []) {
    return new Promise((resolve, reject) => {
        const pyProc = spawn('python3', [scriptPath, ...args]);
        
        pyProc.stdout.on('data', (data) => console.log(`[PY OUT]: ${data.toString().trim()}`));
        pyProc.stderr.on('data', (data) => console.error(`[PY ERR]: ${data.toString().trim()}`));

        pyProc.on('close', (code) => {
            if (code === 0) resolve();
            else reject(new Error(`Process exited with code ${code}`));
        });
    });
}

function speak(text) {
    console.log(`[EARPIECE TTS]: "${text}"`);
    const cmd = process.platform === 'win32'
        ? `powershell -c "Add-Type –AssemblyName System.Speech; (New-Object System.Speech.Synthesis.SpeechSynthesizer).Speak('${text}')"`
        : process.platform === 'darwin'
        ? `say "${text}"`
        : `espeak "${text}"`;
    
    exec(cmd);
}
