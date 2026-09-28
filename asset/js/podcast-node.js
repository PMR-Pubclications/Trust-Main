const express = require('express');
const app = express();
const PORT = process.env.PORT || 3000;

app.use(express.json());

// In-memory database array (you can replace this with a real database later)
let episodes = [
  {
    id: 1,
    title: "Episode 01: The Trust Forensics App",
    audioUrl: "/audio /the_trust_ferensics_app.mp3",
    tag: "Latest Release"
  },
  {
    id: 2,
    title: "Episode 02: Deep Dive",
    audioUrl: "/audio/episode2.mp3",
    tag: ""
  },
  {
    id: 3,
    title: "Episode 03: The Turning Point",
    audioUrl: "/audio/episode3.mp3",
    tag: ""
  },
  {
    id: 4,
    title: "Episode 04: Advanced Mechanics",
    audioUrl: "/audio/episode4.mp3",
    tag: ""
  },
  {
    id: 5,
    title: "Episode 05: Future Horizons",
    audioUrl: "/audio/episode5.mp3",
    tag: ""
  }
];

// GET API Endpoint to fetch all episodes
app.get('/api/episodes', (req, res) => {
  res.json(episodes);
});

// POST API Endpoint to drop a new episode dynamically
app.post('/api/episodes', (req, res) => {
  const { title, audioUrl, tag } = req.body;
  
  if (!title || !audioUrl) {
    return res.status(400).json({ error: "Title and audioUrl are required." });
  }

  const newEpisode = {
    id: episodes.length + 1,
    title,
    audioUrl,
    tag: tag || "New Drop"
  };

  episodes.push(newEpisode);
  res.status(201).json({ message: "Episode dropped successfully!", episode: newEpisode });
});

app.listen(PORT, () => {
  console.log(`Podcast API server running on port ${PORT}`);
});


######Press This######

javascript:(function(a,b,c,d){function e(a,c){if("undefined"!=typeof c){var d=b.createElement("input");d.name=a,d.value=c,d.type="hidden",p.appendChild(d)}}var f,g,h,i,j,k,l,m,n,o=a.encodeURIComponent,p=b.createElement("form"),q=b.getElementsByTagName("head")[0],r="_press_this_app",s=!0;if(d){if(!c.match(/^https?:/))return void(top.location.href=d);if(d+="&u="+o(c),c.match(/^https:/)&&d.match(/^http:/)&&(s=!1),a.getSelection?h=a.getSelection()+"":b.getSelection?h=b.getSelection()+"":b.selection&&(h=b.selection.createRange().text||""),d+="&buster="+(new Date).getTime(),s||(b.title&&(d+="&t="+o(b.title.substr(0,256))),h&&(d+="&s="+o(h.substr(0,512)))),f=a.outerWidth||b.documentElement.clientWidth||600,g=a.outerHeight||b.documentElement.clientHeight||700,f=f<800||f>5e3?600:.7*f,g=g<800||g>3e3?700:.9*g,!s)return void a.open(d,r,"location,resizable,scrollbars,width="+f+",height="+g);i=q.getElementsByTagName("meta")||[];for(var t=0;t<i.length&&!(t>200);t++){var u=i[t],v=u.getAttribute("name"),w=u.getAttribute("property"),x=u.getAttribute("content");x&&(v?e("_meta["+v+"]",x):w&&e("_meta["+w+"]",x))}j=q.getElementsByTagName("link")||[];for(var y=0;y<j.length&&!(y>=50);y++){var z=j[y],A=z.getAttribute("rel");"canonical"!==A&&"icon"!==A&&"shortlink"!==A||e("_links["+A+"]",z.getAttribute("href"))}b.body.getElementsByClassName&&(k=b.body.getElementsByClassName("hfeed")[0]),k=b.getElementById("content")||k||b.body,l=k.getElementsByTagName("img")||[];for(var B=0;B<l.length&&!(B>=100);B++)n=l[B],n.src.indexOf("avatar")>-1||n.className.indexOf("avatar")>-1||n.width&&n.width<256||n.height&&n.height<128||e("_images[]",n.src);m=b.body.getElementsByTagName("iframe")||[];for(var C=0;C<m.length&&!(C>=50);C++)e("_embeds[]",m[C].src);b.title&&e("t",b.title),h&&e("s",h),p.setAttribute("method","POST"),p.setAttribute("action",d),p.setAttribute("target",r),p.setAttribute("style","display: none;"),a.open("about:blank",r,"location,resizable,scrollbars,width="+f+",height="+g),b.body.appendChild(p),p.submit()}})(window,document,top.location.href,"https:\/\/innovativeconceptsdotblog.wordpress.com\/wp-admin\/press-this.php?v=8");
#######/Presss This#########

#######RSS Feed##########
app.get('/api/rss-feed', (req, res) => {
  // In production, you can read this from a database or parse your XML file dynamically
  const feedData = {
    items: [
      {
        title: "Episode 05: Future Horizons & Advanced Architecture",
        pubDate: "2026-09-26"
      },
      {
        title: "Episode 04: Advanced Mechanics & Design",
        pubDate: "2026-09-19"
      },
      {
        title: "Episode 03: The Turning Point",
        pubDate: "2026-09-12"
      }
    ]
  };
  res.json(feedData);
});

##########/RSS Feed##########

##########XML RSS Feed#######
app.get('/xml/auto-feed.xml', (req, res) => {
  res.set('Content-Type', '/js/dynamicExpress.js');
  
  const rssXml = `<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd">
  <channel>
    <title>Innovative Concepts The Podcast</title>
    <link>https://yourdomain.com</link>
    <description>Discussions on advanced engineering, software architecture, and system design.</description>
    <language>en-us</language>
    
    <item>
      <title>Episode 05: Future Horizons</title>
      <pubDate>Fri, 26 Sep 2026 00:00:00 GMT</pubDate>
      <enclosure url="https://yourdomain.com/audio/episode5.mp3" type="audio/mpeg" length="12345678"/>
      <guid>https://yourdomain.com/audio/episode5.mp3</guid>
    </item>
    
        <item>
      <title>Episode 04: Future Horizons</title>
      <pubDate>Fri, 26 Sep 2026 00:00:00 GMT</pubDate>
      <enclosure url="https://yourdomain.com/audio/episode4.mp3" type="audio/mpeg" length="12345678"/>
      <guid>https://yourdomain.com/audio/episode4.mp3</guid>
    </item>
    
        <item>
      <title>Episode 03: Future Horizons</title>
      <pubDate>Fri, 26 Sep 2026 00:00:00 GMT</pubDate>
      <enclosure url="https://yourdomain.com/audio/episode3.mp3" type="audio/mpeg" length="12345678"/>
      <guid>https://yourdomain.com/audio/episode3.mp3</guid>
    </item>
    
        <item>
      <title>Episode 02: Future Horizons</title>
      <pubDate>Fri, 26 Sep 2026 00:00:00 GMT</pubDate>
      <enclosure url="https://yourdomain.com/audio/episode2.mp3" type="audio/mpeg" length="12345678"/>
      <guid>https://yourdomain.com/audio/episode2.mp3</guid>
    </item>
    
 <item>
  <title>Episode 01: Future Horizons</title>
  <description>In this episode, the host talks about walking away from his podcast to keep his sanity.</description>
  <itunes:summary>In this episode, the host talks about walking away from his podcast to keep his sanity.</itunes:summary>
  <itunes:keywords>podcast, ferensics, Trust, first responders, PMR Publications, Patriots Must Rise, INNOVATIVE CONCEPTS</itunes:keywords>
  <pubDate>Fri, 26 Sep 2026 00:00:00 GMT</pubDate>
  <enclosure url="https://yourdomain.com/audio/episode1.mp3" type="audio/mpeg" length="12345678"/>
  <guid>https://yourdomain.com/audio/episode1.mp3</guid>
</item>

    
  </channel>
</rss>`;

  res.send(rssXml);
});
#############/XML RSS Feed#######