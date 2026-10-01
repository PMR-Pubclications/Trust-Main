        async loadServerConfiguration() {
            const token = localStorage.getItem('secure_access_token') ? atob(localStorage.getItem('secure_access_token')) : '';
            if (!token) return;

            try {
                const res = await fetch(`https://api.github.com/repos/${this.owner}/${this.repo}/contents/config/terminal_settings.json`, {
                    headers: { 'Authorization': `Bearer ${token}` }
                });
                if (res.ok) {
                    const data = await res.json();
                    const config = JSON.parse(atob(data.content));
                    // Dynamically apply server settings
                    if (config.api_gateway_endpoint) {
                        this.apiEndpoint = config.api_gateway_endpoint;
                    }
                }
            } catch (e) {
                // Fallback to local defaults if server config is unreachable
            }
        }
