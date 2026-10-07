#!/usr/bin/env python3
"""MotoMoto Tech site generator — Massively (HTML5 UP, CCA 3.0) edition.
Usage:
  python3 tools/build.py            # full rebuild (seeds all published videos)
  python3 tools/build.py --post 29  # add/update a single video post by number
Posts are generated from ~/workspace/mmo/monitor/published_videos.json.
Template: Massively by HTML5 UP (html5up.net), dark-themed for our brand.
"""
import json, re, os, sys, html
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = ROOT
PUB = '/home/hatch/workspace/mmo/monitor/published_videos.json'

SOCIALS = [
    ("YouTube", "https://www.youtube.com/@motomototech", "fa-youtube"),
    ("TikTok", "https://www.tiktok.com/@motomhvj3pv", "fa-tiktok"),
    ("Facebook", "https://www.facebook.com/motomototech", "fa-facebook-f"),
    ("Threads", "https://www.threads.com/@motomototech", "fa-at"),
]
EMAIL = "motomototheyoutuber@gmail.com"
TAGLINE = "Tech news, explained in 60 seconds."
ABOUT_BLURB = ("MotoMoto Tech breaks down the biggest tech stories — AI, science, "
    "gadgets, and the money dramas behind them — into sharp 60-second videos. "
    "New stories daily on TikTok, YouTube Shorts, Facebook, and Threads.")


def head(title, desc, depth):
    pre = "../" * depth
    return f"""<!DOCTYPE HTML>
<html>
<head>
<title>{html.escape(title)} — MotoMoto Tech</title>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1, user-scalable=no" />
<meta name="description" content="{html.escape(desc or TAGLINE)}" />
<link rel="icon" href="{pre}assets/logo-small.png" />
<link rel="stylesheet" href="{pre}assets/css/main.css" />
<link rel="stylesheet" href="{pre}assets/css/custom.css" />
<noscript><link rel="stylesheet" href="{pre}assets/css/noscript.css" /></noscript>
</head>
<body class="is-preload">
<div id="wrapper">"""


def intro(depth):
    pre = "../" * depth
    return f"""
<div id="intro">
<img class="brand-logo" src="{pre}assets/logo.png" alt="MotoMoto Tech logo" />
<h1>MotoMoto<br />Tech</h1>
<p>{html.escape(TAGLINE)}<br />AI · Science · Gadgets · Tech money-drama — daily.</p>
<ul class="actions">
<li><a href="#header" class="button icon solid solo fa-arrow-down scrolly">Continue</a></li>
</ul>
</div>
<header id="header">
<a href="{pre}index.html" class="logo"><img src="{pre}assets/logo-small.png" alt="" />MotoMoto Tech</a>
</header>"""


def nav(active, depth):
    pre = "../" * depth
    links = [("Home", f"{pre}index.html"), ("Blog", f"{pre}blog/index.html"),
             ("About", f"{pre}about.html")]
    lis = "".join(
        f'<li class="active"><a href="{u}">{n}</a></li>' if n == active
        else f'<li><a href="{u}">{n}</a></li>' for n, u in links)
    icons = "".join(
        f'<li><a href="{u}" class="icon brands {ic}"><span class="label">{n}</span></a></li>'
        for n, u, ic in SOCIALS)
    return f"""
<nav id="nav">
<ul class="links">{lis}</ul>
<ul class="icons">{icons}</ul>
</nav>"""


def featured(p, depth):
    pre = "../" * depth
    return f"""
<article class="post featured">
<header class="major">
<span class="date">{html.escape(p['date'])}{(' · ' + html.escape(p['category'])) if p['category'] else ''}</span>
<h2><a href="{pre}blog/{p['slug']}.html">{html.escape(p['title'])}</a></h2>
<p>{html.escape(p['hook'] or 'The latest from MotoMoto Tech.')}</p>
</header>
<div class="video-embed"><iframe src="https://www.youtube.com/embed/{p['ytid']}" title="{html.escape(p['title'])}" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen loading="lazy"></iframe></div>
<ul class="actions special">
<li><a href="{pre}blog/{p['slug']}.html" class="button large">Full Story</a></li>
</ul>
</article>"""


def card(p, depth):
    pre = "../" * depth
    return f"""
<article>
<header>
<span class="date">{html.escape(p['date'])}</span>
<h2><a href="{pre}blog/{p['slug']}.html">{html.escape(p['title'])}</a></h2>
</header>
<a href="{pre}blog/{p['slug']}.html" class="image fit post-card-thumb"><img src="https://i.ytimg.com/vi/{p['ytid']}/hqdefault.jpg" alt="{html.escape(p['title'])}" loading="lazy" /></a>
<p>{html.escape((p['hook'] or '')[:160])}</p>
<ul class="actions special">
<li><a href="{pre}blog/{p['slug']}.html" class="button">Full Story</a></li>
</ul>
</article>"""


def footer(depth):
    pre = "../" * depth
    socials = "".join(
        f'<li><a href="{u}" class="icon brands alt {ic}"><span class="label">{n}</span></a></li>'
        for n, u, ic in SOCIALS)
    return f"""
<footer id="footer">
<section>
<h3>About</h3>
<p>{html.escape(ABOUT_BLURB)}</p>
</section>
<section class="split contact">
<section class="alt">
<h3>Follow</h3>
<ul class="icons alt">{socials}</ul>
</section>
<section>
<h3>Email</h3>
<p class="contact-email"><a href="mailto:{EMAIL}">{EMAIL}</a></p>
</section>
</section>
</footer>
<div id="copyright">
<ul><li>&copy; MotoMoto Tech</li><li>Design: <a href="https://html5up.net">HTML5 UP</a></li></ul>
</div>"""


def scripts(depth):
    pre = "../" * depth
    return f"""
</div>
<script src="{pre}assets/js/jquery.min.js"></script>
<script src="{pre}assets/js/jquery.scrollex.min.js"></script>
<script src="{pre}assets/js/jquery.scrolly.min.js"></script>
<script src="{pre}assets/js/browser.min.js"></script>
<script src="{pre}assets/js/breakpoints.min.js"></script>
<script src="{pre}assets/js/util.js"></script>
<script src="{pre}assets/js/main.js"></script>
</body>
</html>"""


def slugify(t):
    return re.sub(r'[^a-z0-9]+', '-', t.lower()).strip('-')[:60] or 'post'


def yt_id_of(v):
    ytid = v.get('youtube_id')
    if ytid and len(ytid) == 11:
        return ytid
    for key in ('youtube_url', 'youtube'):
        u = v.get(key)
        if isinstance(u, str):
            m = re.search(r'(?:youtu\.be/|v=|shorts/)([A-Za-z0-9_-]{11})', u)
            if m:
                return m.group(1)
            if len(u) == 11:
                return u
        elif isinstance(u, dict) and u.get('video_id'):
            return u['video_id']
    return None


def post_date(v):
    for k in ('published_at', 'date'):
        d = v.get(k)
        if d:
            try:
                return datetime.fromisoformat(str(d).replace('Z', '+00:00')).strftime('%B %d, %Y')
            except Exception:
                return str(d)[:10]
    return ''


def hook_text(v):
    cap = v.get('caption_file')
    if cap and os.path.exists(cap):
        try:
            t = open(cap).read().strip()
            paras = [p.strip() for p in t.split('\n\n') if p.strip()]
            first = paras[0] if paras else t[:300]
            return first[:500]
        except Exception:
            pass
    return ''


def load_videos(only=None):
    d = json.load(open(PUB))
    vs = d.get('videos', d if isinstance(d, list) else [])
    out = []
    for v in vs:
        ytid = yt_id_of(v)
        if not ytid:
            continue
        num = v.get('number') or v.get('video')
        vid = v.get('id') or (f'video{num}' if num else 'video')
        title = v.get('title') or v.get('topic') or f'Video {num}'
        if only is not None and str(num) != str(only) and vid != f'video{only}':
            continue
        out.append({
            'num': num, 'id': vid,
            'title': title,
            'date': post_date(v),
            'ytid': ytid,
            'category': v.get('category', ''),
            'hook': hook_text(v),
            'slug': slugify(title),
        })
    return out


def build_post(p):
    tags = ['#MotoMotoTech']
    if p['category']:
        tags.append('#' + re.sub(r'[^A-Za-z]', '', p['category'].split()[0]))
    hook = p['hook'] or f"Watch the full story on {p['title']} — the latest from MotoMoto Tech."
    body = f"""
<div id="main">
<section class="post">
<header class="major">
<span class="date">{html.escape(p['date'])}{(' · ' + html.escape(p['category'])) if p['category'] else ''}</span>
<h1>{html.escape(p['title'])}</h1>
<p>{html.escape(hook)}</p>
</header>
<div class="video-embed"><iframe src="https://www.youtube.com/embed/{p['ytid']}" title="{html.escape(p['title'])}" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen loading="lazy"></iframe></div>
<p>This is the companion post for our short video. Watch it above, then follow <strong>MotoMoto Tech</strong> on your favorite platform for a new tech story every day.</p>
<div class="tag-row">{''.join(f'<span>{html.escape(t)}</span>' for t in tags)}</div>
<a class="back-link" href="../blog/index.html">&larr; All posts</a>
</section>
</div>"""
    page = (head(p['title'], hook[:150], 1) + intro(1) + nav("Blog", 1)
            + body + footer(1) + scripts(1))
    path = os.path.join(SITE, 'blog', p['slug'] + '.html')
    open(path, 'w').write(page)
    return p['slug']


def build(posts):
    os.makedirs(os.path.join(SITE, 'blog'), exist_ok=True)
    for p in posts:
        build_post(p)
    ordered = sorted(posts, key=lambda x: x['date'], reverse=True)
    # blog index
    bi = (head("Video Blog", "Every video, with the full story behind it.", 1)
          + intro(1) + nav("Blog", 1)
          + '<div id="main">' + featured(ordered[0], 1)
          + '<section class="posts">' + "".join(card(p, 1) for p in ordered[1:]) + "</section></div>"
          + footer(1) + scripts(1))
    open(os.path.join(SITE, 'blog', 'index.html'), 'w').write(bi)
    # home
    hm = (head("MotoMoto Tech — Tech news in 60 seconds", TAGLINE, 0)
          + intro(0) + nav("Home", 0)
          + '<div id="main">' + featured(ordered[0], 0)
          + '<section class="posts">' + "".join(card(p, 0) for p in ordered[1:7]) + "</section>"
          + f'<footer><div class="pagination"><a href="blog/index.html" class="page">Browse all {len(posts)} posts</a></div></footer></div>'
          + footer(0) + scripts(0))
    open(os.path.join(SITE, 'index.html'), 'w').write(hm)
    # about
    ab = (head("About", "Who MotoMoto Tech is and what the channel covers.", 0)
          + intro(0) + nav("About", 0) + """
<div id="main">
<section class="post">
<header class="major">
<h1>About MotoMoto Tech</h1>
<p>Tech news, explained in 60 seconds.</p>
</header>
<p><strong>MotoMoto Tech</strong> is a tech-news short-video channel. We take the biggest stories in AI, science, gadgets, and tech money-drama — and explain them in about 60 seconds, with zero fluff.</p>
<p>Every day we publish across TikTok, YouTube Shorts, Facebook, and Threads. This site is our home base: every video gets a companion blog post with the full story.</p>
<h3>What we cover</h3>
<ul>
<li><strong>AI news</strong> — models, labs, breakthroughs</li>
<li><strong>Science explainers</strong> — space, physics, discoveries</li>
<li><strong>Tech vs law</strong> — trials, regulation, power fights</li>
<li><strong>Gadgets &amp; startups</strong> — the hardware and the hustle</li>
</ul>
<h3>Contact</h3>
<p><a href="mailto:""" + EMAIL + f"""">{EMAIL}</a></p>
</section>
</div>""" + footer(0) + scripts(0))
    open(os.path.join(SITE, 'about.html'), 'w').write(ab)
    print(f'Built {len(posts)} posts + home + blog index + about (Massively edition)')


if __name__ == '__main__':
    only = None
    if '--post' in sys.argv:
        only = sys.argv[sys.argv.index('--post') + 1]
    if only is not None:
        posts = load_videos(only)
        if not posts:
            print(f'No video {only} found'); sys.exit(1)
        build_post(posts[0])
        print(f'Updated post for video {only}')
    else:
        posts = load_videos()
        build(posts)
