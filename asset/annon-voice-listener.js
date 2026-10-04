/**
 * ANNON VOICE RECOGNITION & COMMAND EXECUTION ENGINE
 * File: annon-voice-listener.js
 */

const path = require('path');
const { exec, spawn } = require('child_process');

// ============================================================================
// 1. SPEECH RECOGNITION / MICROPHONE LISTENER INTERFACE
// ============================================================================

class AnnonVoiceListener {
    constructor(dispatcherCallback) {
        this.isListening = false;
        this.dispatcherCallback = dispatcherCallback;
        this.wakeWord = 'annon';
    }

    /**
     * Starts listening to microphone audio stream
     * (Integrates with local offline STT engines like Vosk or system speech APIs)
     */
    startListening(session) {
        this.isListening = true;
        console.log('[ANNON STT]: Microphone array active. Listening for wake word "Annon"...');

        // SIMULATED REAL-TIME MICROPHONE AUDIO FEED
        // In live deployment, audio buffer stream flows here from soundcard/mic input
        this.onAudioFrameCaptured = async (transcribedText) => {
            if (!this.isListening) return;

            const normalized = transcribedText.toLowerCase().trim();

            // Check for wake word trigger
            if (normalized.includes(this.wakeWord)) {
                console.log(`\n[VOICE RECOGNIZED]: "${transcribedText}"`);
                
                // Pass converted text into the Dispatcher Engine
                const result = await this.dispatcherCallback(transcribedText, session);
                
                // Speak confirmation back to officer earpiece
                this.speakAudioResponse(result.audioResponse);
            }
        };
    }

    stopListening() {
        this.isListening = false;
        console.log('[ANNON STT]: Microphone array muted.');
    }

    /**
     * Text-to-Speech (TTS) engine output to officer earpiece
     */
    speakAudioResponse(text) {
        console.log(`[EARPIECE AUDIO OUTPUT] 🔊 "${text}"`);
        
        // Triggers OS speech synthesis (Linux/macOS/Windows)
        const ttsCommand = process.platform === 'darwin' ? `say "${text}"` :
                           process.platform === 'win32' ? `powershell -c "Add-Type –AssemblyName System.Speech; (New-Object System.Speech.Synthesis.SpeechSynthesizer).Speak('${text}')"` :
                           `espeak "${text}"`;

        exec(ttsCommand, (err) => {
            if (err) console.error('[TTS ERROR]: Speech output failed', err);
        });
    }
}

// ============================================================================
// 2. DISPATCHER & PYTHON SUBSYSTEM BINDINGS
// ============================================================================

const REPO_URL = 'https://github.com/PMR-Pubclications/Trust-Main/tree/main/asset/py/legacyTrust-AI';
const LOCAL_PY_DIR = path.join(__dirname, 'asset', 'py', 'legacyTrust-AI');
const SCRIPT_PATH = path.join(LOCAL_PY_DIR, 'main.py');

const LegacyTrustModule = {
    // Executes the Python script inside asset/py/legacyTrust-AI
    runPythonScript: async (session) => {
        return new Promise((resolve, reject) => {
            const pyProcess = spawn('python3', [SCRIPT_PATH, '--session', session.sessionId]);
            let output = '';

            pyProcess.stdout.on('data', (data) => { output += data.toString(); });
            pyProcess.stderr.on('data', (data) => { console.error(`[Python Error]: ${data}`); });

            pyProcess.on('close', (code) => {
                if (code === 0) resolve({ status: 'SUCCESS', output: output.trim() });
                else reject(new Error(`Python process exited with code ${code}`));
            });
        });
    },

    // Opens GitHub repository URL in web browser
    openRepositoryUrl: async () => {
        const command = process.platform === 'win32' ? `start "" "${REPO_URL}"` :
                        process.platform === 'darwin' ? `open "${REPO_URL}"` :
                        `xdg-open "${REPO_URL}"`;

        return new Promise((resolve, reject) => {
            exec(command, (err) => {
                if (err) return reject(err);
                resolve({ status: 'URL_OPENED' });
            });
        });
    }
};

// ============================================================================
// 3. MASTER ROUTER REGISTRY
// ============================================================================

async function processCommandRouter(spokenText, session) {
    const text = spokenText.toLowerCase();

    // Match command pattern for Legacy Trust AI script execution
    if (/annon,?\s+(open|activate)\s+legacy\s+trust\s+ai/i.test(text)) {
        console.log('[ACTION]: Executing python script at asset/py/legacyTrust-AI...');
        await LegacyTrustModule.runPythonScript(session);
        return {
            tag: '@tag:trust.legacy.activate_ai',
            audioResponse: 'Legacy Trust AI subsystem initialized and running.'
        };
    }

    // Match command pattern for opening GitHub Repository URL
    if (/annon,?\s+open\s+repository/i.test(text)) {
        console.log('[ACTION]: Opening browser to GitHub repository...');
        await LegacyTrustModule.openRepositoryUrl();
        return {
            tag: '@tag:trust.legacy.open_repo',
            audioResponse: 'Opening Legacy Trust repository in default browser.'
        };
    }

    return {
        tag: '@tag:sys.unknown',
        audioResponse: 'Command not recognized. Please repeat.'
    };
}

// ============================================================================
// 4. INITIALIZE & RUN SYSTEM
// ============================================================================

const activeSession = { sessionId: 'SESS-7042', officerId: 'OFFICER-7042' };

// Create voice listener instance bound to router
const listener = new AnnonVoiceListener(processCommandRouter);

// Start listening
listener.startListening(activeSession);

// DEMONSTRATION: Simulating spoken audio captured by mic array
setTimeout(() => {
    listener.onAudioFrameCaptured('Annon open legacy trust AI');
}, 2000);
