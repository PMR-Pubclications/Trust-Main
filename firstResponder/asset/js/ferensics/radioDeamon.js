const RadioDaemon = require('../daemons/radioDaemon');
const radioListener = new RadioDaemon();

// Example: Kick off monitoring when an active case is loaded into the workspace
app.post('/api/cases/activate', (req, res) => {
    const { caseNumber, metadataURI } = req.body;
    
    // Start listening for radio triggers for this specific case
    radioListener.startMonitoring(caseNumber, metadataURI);
    
    res.status(200).json({ success: true, message: "Radio daemon armed and listening." });
});
