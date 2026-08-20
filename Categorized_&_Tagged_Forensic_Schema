class ForensicFieldSync {
    constructor() {
        this.storageKey = 'forensic_offline_queue';
    }

    // Save field record with categories, tags, and geographic coordinates
    saveFieldRecord(category, subcategory, tagsArray, geoData, caseDetails) {
        const queue = this.getOfflineQueue();
        
        const formattedTags = tagsArray.map(tag => tag.toLowerCase().trim().replace(/\s+/g, '_'));

        // Check proximity against existing local records
        const proximityAlerts = this.checkGeographicProximity(geoData.latitude, geoData.longitude, queue);

        const enrichedRecord = {
            record_id: `CASE_${Date.now()}`,
            logged_timestamp: new Date().toISOString(),
            sync_status: navigator.onLine ? 'synced' : 'pending_upload',
            classification: {
                primary_category: category,
                subcategory: subcategory
            },
            search_tags: formattedTags,
            geographic_location: {
                latitude: geoData.latitude,
                longitude: geoData.longitude,
                description: geoData.description || 'Unspecified Location',
                proximity_alerts: proximityAlerts
            },
            case_data: caseDetails
        };

        queue.push(enrichedRecord);
        localStorage.setItem(this.storageKey, JSON.stringify(queue));

        if (proximityAlerts.length > 0) {
            console.warn(`[GEOGRAPHIC ALERT] Spatial clustering detected! ${proximityAlerts.length} past case(s) within close proximity.`);
        }

        return enrichedRecord;
    }

    // Calculate distance (in miles) between two sets of coordinates using Haversine formula
    calculateDistance(lat1, lon1, lat2, lon2) {
        const R = 3958.8; // Radius of the earth in miles
        const dLat = (lat2 - lat1) * Math.PI / 180;
        const dLon = (lon2 - lon1) * Math.PI / 180;
        const a = 
            Math.sin(dLat/2) * Math.sin(dLat/2) +
            Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) * 
            Math.sin(dLon/2) * Math.sin(dLon/2);
        const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
        return R * c; // Distance in miles
    }

    // Scan local queue for cases within a specific threshold (e.g., 5 miles)
    checkGeographicProximity(currentLat, currentLon, existingQueue, thresholdMiles = 5.0) {
        const alerts = [];
        
        for (let record of existingQueue) {
            if (record.geographic_location && record.geographic_location.latitude) {
                const prevLat = record.geographic_location.latitude;
                const prevLon = record.geographic_location.longitude;
                
                const distance = this.calculateDistance(currentLat, currentLon, prevLat, prevLon);
                
                if (distance <= thresholdMiles) {
                    alerts.push({
                        matched_case_id: record.record_id,
                        distance_miles: parseFloat(distance.toFixed(2)),
                        previous_location: record.geographic_location.description
                    });
                }
            }
        }
        return alerts;
    }

    getOfflineQueue() {
        const data = localStorage.getItem(this.storageKey);
        return data ? JSON.parse(data) : [];
    }

    async synchronizeQueue(githubToken, owner, repo) {
        const queue = this.getOfflineQueue();
        const pending = queue.filter(item => item.sync_status === 'pending_upload');

        if (pending.length === 0) return;

        for (let record of pending) {
            try {
                const filePath = `database/forensics/field-uploads/${record.record_id}.json`;
                const contentEncoded = btoa(JSON.stringify(record, null, 2));

                const res = await fetch(`https://api.github.com/repos/${owner}/${repo}/contents/${filePath}`, {
                    method: 'PUT',
                    headers: {
                        'Authorization': `Bearer ${githubToken}`,
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        message: `[Field Sync] Upload geo-tagged case record ${record.record_id}`,
                        content: contentEncoded
                    })
                });

                if (res.ok) record.sync_status = 'synced';
            } catch (err) {
                console.error(`[SYNC_ERROR] Failed to upload ${record.record_id}:`, err);
            }
        }

        localStorage.setItem(this.storageKey, JSON.stringify(queue));
    }
}

const fieldSyncManager = new ForensicFieldSync();
