const express = require('express');
const axios = require('axios');
const cors = require('cors');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 3000;

// Provided OpenSea API Key
const OPENSEA_API_KEY = 'f25c57a885754235a82996ee8ed9b342';
const BASE_URL = 'https://api.opensea.io/api/v2';

app.use(cors());
app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

// Headers required for OpenSea API v2 requests
const getHeaders = () => ({
  'accept': 'application/json',
  'x-api-key': OPENSEA_API_KEY
});

/**
 * Main API Receiver Endpoint
 * GET /api/nft/:chain/:address/:tokenId
 */
app.get('/api/nft/:chain/:address/:tokenId', async (req, res) => {
  const { chain, address, tokenId } = req.params;

  try {
    // 1. Fetch NFT details and metadata
    const nftRes = await axios.get(
      `${BASE_URL}/chain/${chain}/contract/${address}/nfts/${tokenId}`,
      { headers: getHeaders() }
    );
    const nftData = nftRes.data.nft || {};

    const collectionSlug = nftData.collection;

    // 2. Fetch Collection Stats (Trading Volume & Floor Price)
    let volumeStats = { totalVolume: 'N/A', floorPrice: 'N/A' };
    if (collectionSlug) {
      try {
        const statsRes = await axios.get(
          `${BASE_URL}/collections/${collectionSlug}/stats`,
          { headers: getHeaders() }
        );
        const totalStats = statsRes.data.total || {};
        volumeStats = {
          totalVolume: totalStats.volume ? totalStats.volume.toFixed(2) + ' ETH' : 'N/A',
          floorPrice: totalStats.floor_price ? totalStats.floor_price.toFixed(4) + ' ETH' : 'N/A'
        };
      } catch (err) {
        console.warn('Could not fetch collection stats:', err.message);
      }
    }

    // 3. Fetch Last Purchased Event (Sale Event)
    let lastSale = { price: 'No prior sales found', date: 'N/A' };
    try {
      const eventRes = await axios.get(
        `${BASE_URL}/events/chain/${chain}/contract/${address}/nfts/${tokenId}?event_type=sale&limit=1`,
        { headers: getHeaders() }
      );

      const events = eventRes.data.asset_events || [];
      if (events.length > 0) {
        const sale = events[0];
        const decimals = sale.payment?.decimals || 18;
        const priceEth = sale.payment?.quantity 
          ? (parseFloat(sale.payment.quantity) / Math.pow(10, decimals)).toFixed(4)
          : 'N/A';
        const saleDate = sale.event_timestamp 
          ? new Date(sale.event_timestamp * 1000).toLocaleString() 
          : 'N/A';

        lastSale = {
          price: `${priceEth} ${sale.payment?.symbol || 'ETH'}`,
          date: saleDate
        };
      }
    } catch (err) {
      console.warn('Could not fetch sale events:', err.message);
    }

    // Combine response payload
    const responsePayload = {
      name: nftData.name || `#${tokenId}`,
      description: nftData.description || 'No description available',
      image: nftData.image_url || nftData.display_image_url || 'https://via.placeholder.com/400',
      contractAddress: address,
      tokenId: tokenId,
      chain: chain,
      collectionSlug: collectionSlug,
      cost: volumeStats.floorPrice,
      tradingVolume: volumeStats.totalVolume,
      lastPurchased: lastSale,
      openseaUrl: `https://opensea.io/assets/${chain}/${address}/${tokenId}`
    };

    res.json({ success: true, data: responsePayload });

  } catch (error) {
    console.error('API Error:', error.response?.data || error.message);
    res.status(500).json({ 
      success: false, 
      error: error.response?.data?.detail || error.message || 'Failed to fetch NFT data' 
    });
  }
});

app.listen(PORT, () => {
  console.log(`NFT Receiver Server running on http://localhost:${PORT}`);
});
