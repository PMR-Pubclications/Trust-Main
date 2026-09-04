            // Universal helper to safely commit files to any path, auto-handling missing folders
            async commitFileToGitHub(filePath, payloadObject, commitMessage) {
                if (!this.token) {
                    this.log('[CLOUD ERROR] No active authentication token.');
                    return false;
                }

                const apiUrl = `https://api.github.com/repos/${this.owner}/${this.repo}/contents/${filePath}`;
                
                // 1. Check if file already exists to get its SHA (required by GitHub API for updates)
                let sha = null;
                try {
                    const getRes = await fetch(apiUrl, {
                        headers: { 'Authorization': `Bearer ${this.token}` }
                    });
                    if (getRes.ok) {
                        const fileData = await getRes.json();
                        sha = fileData.sha;
                    }
                } catch (e) {
                    // File doesn't exist yet, which is fine (will be created as a new file)
                }

                // 2. Perform the PUT request to create or update the file
                const putRes = await fetch(apiUrl, {
                    method: 'PUT',
                    headers: { 
                        'Authorization': `Bearer ${this.token}`, 
                        'Content-Type': 'application/json' 
                    },
                    body: JSON.stringify({
                        message: commitMessage,
                        content: btoa(JSON.stringify(payloadObject, null, 2)),
                        ...(sha && { sha })
                    })
                });

                if (putRes.ok) {
                    this.log(`[CLOUD SUCCESS] Committed: ${filePath}`);
                    return true;
                } else {
                    const errJson = await putRes.json();
                    this.log(`[CLOUD ERROR] Failed to commit ${filePath}: ${errJson.message}`);
                    return false;
                }
            },
