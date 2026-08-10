<?xml version="1.0" encoding="utf-8"?>
<!--
  A human-readable face for feed.xml.

  Browsers dropped their built-in feed readers, so an Atom file opened in one
  renders as raw XML and looks broken. This stylesheet is applied by the browser
  when a person opens the feed, and explains what they are looking at. Feed
  readers ignore it entirely and parse the XML underneath, unchanged.

  No JavaScript: browsers do not execute script injected via XSLT.
-->
<xsl:stylesheet version="1.0"
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:atom="http://www.w3.org/2005/Atom"
    exclude-result-prefixes="atom">

<xsl:output method="html" encoding="utf-8" indent="yes"
            doctype-system="about:legacy-compat"/>

<xsl:template match="/">
<html lang="en">
<head>
    <meta charset="utf-8"/>
    <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
    <title>Subscribe to <xsl:value-of select="atom:feed/atom:title"/></title>
    <style>
        :root { color-scheme: dark; }
        * { box-sizing: border-box; }
        body {
            margin: 0; padding: 3rem 1.5rem 5rem; background: #080a0f; color: #cbd5e1;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            line-height: 1.6; -webkit-font-smoothing: antialiased;
        }
        .wrap { max-width: 760px; margin: 0 auto; }
        .mark {
            font-size: 2.6rem; font-weight: 900; letter-spacing: -2px; color: #fff;
            margin: 0 0 .4rem; text-decoration: none; display: inline-block;
        }
        .mark span { color: #818cf8; }
        .sub { color: #94a3b8; margin: 0 0 2.5rem; max-width: 62ch; }

        .box {
            padding: 1.6rem 1.8rem; border-radius: 18px; margin-bottom: 2.5rem;
            background: rgba(99,102,241,.08); border: 1px solid rgba(129,140,248,.25);
        }
        .box h2 { margin: 0 0 .7rem; font-size: 1.1rem; color: #fff; }
        .box p { margin: 0 0 .9rem; color: #cbd5e1; }
        .box p:last-child { margin-bottom: 0; }
        code {
            display: block; padding: .8rem 1rem; margin: .8rem 0;
            background: rgba(0,0,0,.35); border: 1px solid rgba(255,255,255,.12);
            border-radius: 10px; color: #a5b4fc; font-size: .95rem; word-break: break-all;
            font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
        }
        .readers { color: #94a3b8; font-size: .93rem; }
        .readers a { color: #a5b4fc; }

        h3.count {
            font-size: .78rem; text-transform: uppercase; letter-spacing: 2.5px;
            color: #6366f1; margin: 0 0 1.2rem; font-weight: 800;
        }
        .entry {
            padding: 1.4rem 0; border-top: 1px solid rgba(255,255,255,.1);
        }
        .entry .date {
            color: #94a3b8; font-size: .78rem; font-weight: 700;
            letter-spacing: 1.2px; text-transform: uppercase;
        }
        .entry a.title {
            display: block; color: #fff; font-size: 1.3rem; font-weight: 800;
            letter-spacing: -.4px; text-decoration: none; margin: .3rem 0 .5rem;
        }
        .entry a.title:hover { color: #a5b4fc; }
        .entry .summary { color: #94a3b8; margin: 0; }

        .back { display: inline-block; margin-top: 2.5rem; color: #a5b4fc; }
        @media (max-width: 600px) { .mark { font-size: 2rem; } body { padding-top: 2rem; } }
    </style>
</head>
<body>
    <div class="wrap">
        <a class="mark" href="{atom:feed/atom:link[@rel='alternate']/@href}">My<span>Th</span></a>
        <p class="sub"><xsl:value-of select="atom:feed/atom:subtitle"/></p>

        <div class="box">
            <h2>This is a web feed, not a broken page.</h2>
            <p>You have reached the raw subscription file for MyTh. Browsers stopped
            reading feeds themselves, which is why this needs explaining &#8212; but the
            file still does its job. Copy the address below into any feed reader and new
            entries will arrive there automatically, with no email address, no account,
            and no way for me to know who you are.</p>
            <code><xsl:value-of select="atom:feed/atom:link[@rel='self']/@href"/></code>
            <p class="readers">Readers that take that address:
            <a href="https://netnewswire.com/">NetNewsWire</a> (free, Mac and iOS),
            <a href="https://feedly.com/">Feedly</a>,
            <a href="https://www.inoreader.com/">Inoreader</a>,
            <a href="https://reederapp.com/">Reeder</a>. Most browsers also have a feed
            extension. If you would rather not bother with any of this, just
            <a href="{atom:feed/atom:link[@rel='alternate']/@href}">read the entries on the site</a>.</p>
        </div>

        <h3 class="count">In this feed</h3>
        <xsl:for-each select="atom:feed/atom:entry">
            <div class="entry">
                <span class="date"><xsl:value-of select="substring(atom:published, 1, 10)"/></span>
                <a class="title" href="{atom:link/@href}"><xsl:value-of select="atom:title"/></a>
                <p class="summary"><xsl:value-of select="atom:summary"/></p>
            </div>
        </xsl:for-each>

        <a class="back" href="{atom:feed/atom:link[@rel='alternate']/@href}">&#8592; Back to MyTh</a>
    </div>
</body>
</html>
</xsl:template>

</xsl:stylesheet>
