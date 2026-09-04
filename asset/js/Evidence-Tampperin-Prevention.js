// Integrated submission workflow: Updates SQL (via GitHub API) and mirrors to the blockchain simultaneously
async function submitAndMirrorEvidence(incidentId, agencyCategory, evidenceData) {
    const messageDiv = document.getElementById('response-message');
    
    try {
        messageDiv.style.color = "blue";
        messageDiv.textContent = "Step 1/2: Submitting data to the secure database repository...";

        // 1. Execute SQL database record update via your endpoint logic
        const newSqlEntry = `\nINSERT INTO scene_evidence (case_number, general_category, description) VALUES ('${incidentId}', '${agencyCategory}', '${evidenceData}');`;
        await handleGitHubCommit(newSqlEntry, agencyCategory, incidentId);

        messageDiv.textContent = "Step 2/2: Mirroring immutable record to the blockchain...";

        // 2. Connect to Web3 provider (MetaMask or institutional node)
        if (!window.ethereum) {
            throw new Error("No Web3 wallet detected for blockchain mirroring.");
        }

        const provider = new ethers.providers.Web3Provider(window.ethereum);
        await provider.send("eth_requestAccounts", []);
        const signer = provider.getSigner();

        const contractAddress = "0xYourDeployedContractAddressHere";
        const contractABI = [
            "function recordEvidence(string memory _caseNumber, string memory _category, string memory _description) public"
        ];
        
        const contract = new ethers.Contract(contractAddress, contractABI, signer);

        // 3. Push identical data onto the blockchain
        const tx = await contract.recordEvidence(incidentId, agencyCategory, evidenceData);
        messageDiv.textContent = "Waiting for blockchain network confirmation...";
        await tx.wait();

        messageDiv.style.color = "green";
        messageDiv.textContent = `Success! Evidence for case ${incidentId} is safely locked on the database and mirrored to the blockchain.`;
        document.getElementById('firstResponseForm').reset();

    } catch (error) {
        messageDiv.style.color = "red";
        messageDiv.textContent = `Submission Error: ${error.message}`;
        console.error(error);
    }
}
