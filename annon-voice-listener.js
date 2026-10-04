/**
 * ANNON VOICE ENGINE - LIVE PROCESS PIPE
 */

const path = require('path');
const { spawn, exec } = require('child_process');

const binPath = path.join(__dirname, 'asset', 'cpp', 'AudioVideoEngine-CPP', 'build', 'av_engine');
const SCRIPT_PATH = path.join(__dirname, 'asset', 'py', 'legacyTrust-AI', 'main.py');

// Spawns the live binary directly
const avProcess = spawn(binPath, ['--live'], { stdio: ['pipe', 'pipe', 'pipe'] });

// Real-time stdout stream parser
avProcess.stdout.on('data', async (chunk) => {
    const raw = chunk.toString().trim();
    if (!raw) return;

    try {
        const event = JSON.parse(raw);
        if (event.type === 'STT_RESULT' && event.text.toLowerCase().includes('annon')) {
            handleVoiceCommand(event.text);
        }
    } catch (e) {
        // Direct string stream parsing
        if (raw.toLowerCase().includes('annon')) {
            handleVoiceCommand(raw);
        }
    }
});

async function handleVoiceCommand(phrase) {
    const text = phrase.toLowerCase();

    if (/annon,?\s+(open|activate)\s+legacy\s+trust\s+ai/i.test(text)) {
        spawn('python3', [SCRIPT_PATH, '--session', 'SESS-7042']);
        speak('Legacy Trust AI active.');
    } else if (/annon,?\s+capture\s+3d\s+scan/i.test(text)) {
        // Write direct instruction to C++ stdin stream
        avProcess.stdin.write(JSON.stringify({ cmd: 'START_LIDAR' }) + '\n');
        speak('3D scan started.');
    }
}

function speak(text) {
    const cmd = process.platform === 'win32' ? `powershell -c "Add-Type –AssemblyName System.Speech; (New-Object System.Speech.Synthesis.SpeechSynthesizer).Speak('${text}')"` : `espeak "${text}"`;
    exec(cmd);
}
