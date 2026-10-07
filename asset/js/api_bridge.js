// assets/js/api_bridge.js

document.addEventListener('DOMContentLoaded', () => {
    // 1. Link up the Hospital / EMS Data Pull
    const hospitalForm = document.getElementById('hospital-query');
    
    if (hospitalForm) {
        hospitalForm.addEventListener('submit', async (event) => {
            event.preventDefault(); // Stops the page from refreshing
            
            const patientId = document.getElementById('patient-id').value;
            const facility = document.getElementById('facility').value;
            
            // Create a status message on the UI
            let statusDiv = document.getElementById('query-status');
            if (!statusDiv) {
                statusDiv = document.createElement('div');
                statusDiv.id = 'query-status';
                statusDiv.className = 'status';
                hospitalForm.appendChild(statusDiv);
            }
            
            statusDiv.style.color = 'var(--muted)';
            statusDiv.innerText = `Querying ${facility} databases for patient ${patientId}...`;

            try {
                // Link to the Python AgencyBridge Hospital Endpoint
                const response = await fetch(`http://localhost:5005/api/health_records/query?patient_id=${encodeURIComponent(patientId)}&facility=${encodeURIComponent(facility)}`, {
                    method: 'GET',
                    headers: {
                        'Content-Type': 'application/json',
                        'Accept': 'application/json'
                    }
                });

                const data = await response.json();
                
                if (response.ok) {
                    statusDiv.style.color = 'var(--green)';
                    statusDiv.innerText = `Success: Records retrieved. Check console for HL7_FHIR_COMPLIANT payload.`;
                    console.log("Secure Medical Data Retrieved:", data);
                } else {
                    throw new Error(data.error || 'Hospital network connection failed.');
                }
            } catch (error) {
                statusDiv.style.color = 'var(--red)';
                statusDiv.innerText = `Connection Error: ${error.message}`;
            }
        });

        // 2. Link up the "Push ePCR" Button
        const pushBtn = hospitalForm.querySelector('.btn.blue');
        if (pushBtn) {
            pushBtn.addEventListener('click', async (event) => {
                event.preventDefault();
                
                // Example of formatting an ePCR_COMPLIANT JSON payload
                const epcrPayload = {
                    incident_type: "Trauma",
                    patient_id: document.getElementById('patient-id').value,
                    destination: document.getElementById('facility').value,
                    format: "ePCR_COMPLIANT",
                    timestamp: new Date().toISOString()
                };

                try {
                    // Pushing report to the EMS API endpoint
                    const response = await fetch('http://localhost:5003/api/ems/receive', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify(epcrPayload)
                    });

                    if (response.ok) {
                        alert("ePCR successfully transmitted to EMS network.");
                    }
                } catch (error) {
                    alert("Failed to push ePCR report: " + error.message);
                }
            });
        }
    }
});
