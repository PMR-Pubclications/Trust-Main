            // Scan physical NFC token/fob to authenticate instantly
            async scanNFCBadge() {
                if (!('NDEFReader' in window)) {
                    alert('Web NFC is not supported on this device/browser.');
                    return;
                }

                try {
                    this.log('[NFC] Initializing reader... Tap your security fob to the device.');
                    const ndef = new NDEFReader();
                    await ndef.scan();

                    ndef.onreading = (event) => {
                        const decoder = new TextDecoder();
                        for (const record of event.message.records) {
                            const payload = decoder.decode(record.data);
                            this.log(`[NFC SUCCESS] Fob detected: ${payload}`);
                            
                            // Map NFC payload or trigger login
                            document.getElementById('oper-id').value = payload.trim();
                            this.authenticate();
                        }
                    };
                } catch (err) {
                    this.log(`[NFC ERROR] Scan failed: ${err.message}`);
                    alert('NFC reading failed or permission denied.');
                }
            },
