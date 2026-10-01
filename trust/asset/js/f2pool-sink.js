async function fetchMobileMiningStats() {
    const accountName = "avalondazrrj";
    // f2pool public worker/account stats endpoint
    const apiUrl = `https://api.f2pool.com/bitcoin/${accountName}`;

    try {
        const response = await fetch(apiUrl);
        if (response.ok) {
            const data = await response.json();
            
            // Extract live hash rate from f2pool response
            const hashrateTH = (data.hash_rate_24h || 0) / 1e12;
            
            document.getElementById('mining-hashrate').innerHTML = 
                `${hashrateTH.toFixed(1)} TH/s <span class="text-xs font-normal text-slate-400">f2pool</span>`;
        }
    } catch (error) {
        console.log("Using cached mobile telemetry.");
    }
}

// Run on phone app load
fetchMobileMiningStats();
