const express = require('express');
const app = express();

// Sample or database-driven episodes array
const episodes = [
  {
    title: "Episode 01: Future Horizons",
    description: "In this episode, the host talks about walking away from his podcast to keep his sanity.",
    keywords: "podcast, ferensics, Trust, first responders, PMR Publications, Patriots Must Rise, INNOVATIVE CONCEPTS",
    pubDate: "Fri, 26 Sep 2026 00:00:00 GMT",
    audioUrl: "https://yourdomain.com/audio/the_trust_ferensics_app.mp3",
    guid: "innovative-concepts-ep-01"
  },
  {
    title: "Episode 02: Deep Dive",
    description: "A technical deep dive into system architecture and operational frameworks.",
    keywords: "podcast, ferensics, Trust, PMR Publications, Patriots Must Rise, INNOVATIVE CONCEPTS",
    pubDate: "Fri, 19 Sep 2026 00:00:00 GMT",
    audioUrl: "https://yourdomain.com/audio/episode2.mp3",
    guid: "innovative-concepts-ep-02"
  }
];

// Dynamic XML feed route
app.get('/feed.xml', (req, res) => {
  // Set the precise MIME type required for RSS feeds
  res.setHeader('Content-Type', 'application/xml; charset=utf-8');

  // Build XML items dynamically from your data source
  const itemsXml = episodes.map(ep => `
    <item>
      <title><![CDATA[${ep.title}]]></title>
      <description><![CDATA[${ep.description}]]></description>
      <itunes:summary><![CDATA[${ep.description}]]></itunes:summary>
      <itunes:keywords>${ep.keywords}</itunes:keywords>
      <pubDate>${ep.pubDate}</pubDate>
      <enclosure url="${ep.audioUrl}" type="audio/mpeg" length="12345678"/>
      <guid isPermaLink="false">${ep.guid}</guid>
    </item>`).join('');

  // Assemble the complete RSS feed template
  const rssFeed = `<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd" xmlns:content="http://purl.org/rss/1.0/modules/content/">
  <channel>
    <title>Innovative Concepts The Podcast</title>
    <link>https://yourdomain.com</link>
    <language>en-us</language>
    <description>Discussions on advanced engineering, software architecture, trust forensics, and system design.</description>
    <itunes:author>PMR Publications</itunes:author>
    <itunes:summary>Discussions on advanced engineering, software architecture, trust forensics, and system design.</itunes:summary>
    <itunes:explicit>false</itunes:explicit>
    <itunes:image href="https://yourdomain.com/graphics/1790466786981.jpg"/>
    ${itemsXml}
  </channel>
</rss>`;

  // Send the raw XML string to the client
  res.send(rssFeed.trim());
});

app.listen(3000, () => {
  console.log('RSS Feed generator active at /feed.xml');
});
