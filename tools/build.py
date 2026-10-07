#!/usr/bin/env python3
"""MotoMoto Tech site generator — builds the static site + blog from published videos.
Usage:
  python3 tools/build.py            # full rebuild (seeds all published videos)
  python3 tools/build.py --post 29  # add/update a single video post by number
Posts are generated from ~/workspace/mmo/monitor/published_videos.json.
"""
import json, re, os, sys, html
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = ROOT  # site lives at repo root (GitHub Pages serves /)
PUB = '/home/hatch/workspace/mmo/monitor/published_videos.json'

SOCIALS = [
    ("YouTube", "https://www.youtube.com/@motomototech"),
    ("TikTok", "https://www.tiktok.com/@motomhvj3pv"),
    ("Facebook", "https://www.facebook.com/motomototech"),
    ("Threads", "https://www.threads.com/@motomototech"),
]
EMAIL = "motomototheyoutuber@gmail.com"
TAGLINE = "Tech news, explained in 60 seconds."

CSS = """*{margin:0;padding:0;box-sizing:border-box}
:root{--bg:#0a0f1a;--bg2:#101828;--blue:#2e9bff;--blue-d:#1a6fd4;--txt:#e8eef7;--mut:#93a1b8;--card:#141d31;--line:#1e2a44}
body{background:var(--bg);color:var(--txt);font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Inter,Arial,sans-serif;line-height:1.6}
a{color:var(--blue);text-decoration:none}
.wrap{max-width:960px;margin:0 auto;padding:0 20px}
header{border-bottom:1px solid var(--line);padding:14px 0;position:sticky;top:0;background:rgba(10,15,26,.92);backdrop-filter:blur(8px);z-index:10}
.nav{display:flex;align-items:center;gap:14px}
.nav img{width:38px;height:38px;border-radius:10px}
.nav .brand{font-weight:800;font-size:1.15rem;letter-spacing:.2px}
.nav .brand span{color:var(--blue)}
.nav nav{margin-left:auto;display:flex;gap:18px;font-size:.95rem}
.nav nav a{color:var(--mut)}
.nav nav a:hover{color:var(--txt)}
.hero{text-align:center;padding:64px 20px 48px}
.hero img{width:110px;height:110px;border-radius:28px;box-shadow:0 8px 40px rgba(46,155,255,.35);margin-bottom:20px}
.hero h1{font-size:2.4rem;font-weight:800;letter-spacing:-.5px}
.hero h1 span{color:var(--blue)}
.hero p{color:var(--mut);font-size:1.1rem;margin-top:8px}
.social-row{display:flex;gap:10px;justify-content:center;margin-top:24px;flex-wrap:wrap}
.btn{display:inline-block;background:var(--blue);color:#04121f;font-weight:700;padding:10px 22px;border-radius:999px;font-size:.95rem}
.btn:hover{background:var(--blue-d);color:#fff}
.btn.ghost{background:transparent;color:var(--blue);border:1px solid var(--blue)}
.sec{padding:36px 0}
.sec h2{font-size:1.4rem;margin-bottom:18px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:18px}
.card{background:var(--card);border:1px solid var(--line);border-radius:14px;overflow:hidden;transition:transform .15s}
.card:hover{transform:translateY(-3px)}
.card img{width:100%;aspect-ratio:16/9;object-fit:cover;display:block}
.card .pad{padding:14px 16px}
.card h3{font-size:1rem;line-height:1.35}
.card .meta{color:var(--mut);font-size:.82rem;margin-top:6px}
.post-hero{position:relative;padding:0}
.embed{position:relative;padding-bottom:56.25%;height:0;overflow:hidden;border-radius:14px;background:#000;margin:20px 0}
.embed iframe{position:absolute;top:0;left:0;width:100%;height:100%;border:0}
article.post{max-width:720px;margin:0 auto;padding:32px 20px}
article.post h1{font-size:1.8rem;line-height:1.3;margin:12px 0}
article.post .meta{color:var(--mut);font-size:.9rem;margin-bottom:8px}
.tags{margin-top:18px;display:flex;gap:8px;flex-wrap:wrap}
.tags span{background:var(--bg2);border:1px solid var(--line);color:var(--mut);font-size:.8rem;padding:4px 12px;border-radius:999px}
.back{display:inline-block;margin:24px 0 0;color:var(--mut);font-size:.9rem}
footer{border-top:1px solid var(--line);margin-top:48px;padding:28px 0;color:var(--mut);font-size:.88rem;text-align:center}
footer a{color:var(--mut)}
.about-blurb{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:22px;margin-top:8px}
@media(max-width:600px){.hero h1{font-size:1.8rem}.hero{padding:44px 20px 32px}}
"""

HEADER = """<header><div class="wrap nav">
<a href="/"><img src="/assets/logo-small.png" alt="MotoMoto Tech logo"></a>
<a href="/" class="brand">MotoMoto<span>Tech</span></a>
<nav><a href="/">Home</a><a href="/blog/">Blog</a><a href="/about.html">About</a></nav>
</div></header>"""

FOOTER = f"""<footer><div class="wrap">
<p><strong style="color:var(--txt)">MotoMoto Tech</strong> — {TAGLINE}</p>
<p style="margin-top:8px">""" + " · ".join(f'<a href="{u}">{n}</a>' for n, u in SOCIALS) + f"""</p>
<p style="margin-top:8px"><a href="mailto:{EMAIL}">{EMAIL}</a></p>
</div></footer>"""

def page(title, body, desc=""):
    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)} — MotoMoto Tech</title>
<meta name="description" content="{html.escape(desc or TAGLINE)}">
<link rel="icon" href="/assets/logo-small.png">
<style>{CSS}</style></head>
<body>{HEADER}<main>{body}</main>{FOOTER}</body></html>"""

def slugify(t):
    s = re.sub(r'[^a-z0-9]+', '-', t.lower()).strip('-')
    return s[:60] or 'post'

def yt_id_of(v):
    ytid = v.get('youtube_id')
    if ytid and len(ytid) == 11: return ytid
    for key in ('youtube_url', 'youtube'):
        u = v.get(key)
        if isinstance(u, str):
            m = re.search(r'(?:youtu\.be/|v=|shorts/)([A-Za-z0-9_-]{11})', u)
            if m: return m.group(1)
            if len(u) == 11: return u
        elif isinstance(u, dict) and u.get('video_id'):
            return u['video_id']
    return None

def post_date(v):
    for k in ('published_at', 'date'):
        d = v.get(k)
        if d:
            try: return datetime.fromisoformat(str(d).replace('Z', '+00:00')).strftime('%b %d, %Y')
            except: return str(d)[:10]
    return ''

def hook_text(v):
    cap = v.get('caption_file')
    if cap and os.path.exists(cap):
        try:
            t = open(cap).read().strip()
            paras = [p.strip() for p in t.split('\n\n') if p.strip()]
            first = paras[0] if paras else t[:300]
            return first[:500]
        except: pass
    return ''

def load_videos(only=None):
    d = json.load(open(PUB))
    vs = d.get('videos', d if isinstance(d, list) else [])
    out = []
    for v in vs:
        ytid = yt_id_of(v)
        if not ytid: continue
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
            'slug': f"{slugify(title)}",
        })
    return out

def build_post(p):
    tags = ['#MotoMotoTech']
    if p['category']: tags.append('#' + re.sub(r'[^A-Za-z]', '', p['category'].split()[0]))
    hook = p['hook'] or f"Watch the full story on {p['title']} — the latest from MotoMoto Tech."
    body = f"""<article class="post">
<div class="meta">{html.escape(p['date'])} · {html.escape(p['category'])}</div>
<h1>{html.escape(p['title'])}</h1>
<div class="embed"><iframe src="https://www.youtube.com/embed/{p['ytid']}" title="{html.escape(p['title'])}" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen loading="lazy"></iframe></div>
<p>{html.escape(hook)}</p>
<p style="margin-top:12px;color:var(--mut)">This is the companion post for our short video. Watch it above, then follow <strong>MotoMoto Tech</strong> on your favorite platform for a new tech story every day.</p>
<div class="tags">{''.join(f'<span>{html.escape(t)}</span>' for t in tags)}</div>
<a class="back" href="/blog/">← All posts</a>
</article>"""
    path = os.path.join(SITE, 'blog', p['slug'] + '.html')
    open(path, 'w').write(page(p['title'], body, hook[:150]))
    return p['slug']

def build(posts):
    os.makedirs(os.path.join(SITE, 'blog'), exist_ok=True)
    slugs = {}
    for p in posts:
        slugs[p['ytid']] = build_post(p)
    # blog index
    cards = []
    for p in sorted(posts, key=lambda x: x['date'], reverse=True):
        cards.append(f"""<a class="card" href="/blog/{p['slug']}.html">
<img src="https://i.ytimg.com/vi/{p['ytid']}/hqdefault.jpg" alt="{html.escape(p['title'])}" loading="lazy">
<div class="pad"><h3>{html.escape(p['title'])}</h3><div class="meta">{html.escape(p['date'])}{(' · ' + html.escape(p['category'])) if p['category'] else ''}</div></div></a>""")
    blog_body = f"""<div class="wrap sec"><h2>Video Blog</h2>
<p style="color:var(--mut);margin-bottom:20px">Every video, with the full story behind it.</p>
<div class="grid">{''.join(cards)}</div></div>"""
    open(os.path.join(SITE, 'blog', 'index.html'), 'w').write(page('Video Blog', blog_body))
    # home
    latest = sorted(posts, key=lambda x: x['date'], reverse=True)[:6]
    hcards = []
    for p in latest:
        hcards.append(f"""<a class="card" href="/blog/{p['slug']}.html">
<img src="https://i.ytimg.com/vi/{p['ytid']}/hqdefault.jpg" alt="{html.escape(p['title'])}" loading="lazy">
<div class="pad"><h3>{html.escape(p['title'])}</h3><div class="meta">{html.escape(p['date'])}</div></div></a>""")
    home_body = f"""<div class="hero wrap">
<img src="/assets/logo.png" alt="MotoMoto Tech">
<h1>MotoMoto <span>Tech</span></h1><p>{TAGLINE}</p>
<div class="social-row">{''.join(f'<a class="btn ghost" href="{u}">{n}</a>' for n, u in SOCIALS)}</div></div>
<div class="wrap sec"><h2>Latest videos</h2><div class="grid">{''.join(hcards)}</div>
<p style="margin-top:18px"><a href="/blog/">Browse all {len(posts)} posts →</a></p></div>
<div class="wrap sec"><h2>About</h2><div class="about-blurb">
<p>MotoMoto Tech breaks down the biggest tech stories — AI, science, gadgets, and the money dramas behind them — into sharp 60-second videos. New stories daily on TikTok, YouTube Shorts, Facebook, and Threads.</p>
<p style="margin-top:10px"><a href="/about.html">More about us →</a> · <a href="mailto:{EMAIL}">{EMAIL}</a></p></div></div>"""
    open(os.path.join(SITE, 'index.html'), 'w').write(page('MotoMoto Tech — Tech news in 60 seconds', home_body))
    # about
    about_body = f"""<div class="wrap sec" style="max-width:720px"><h2>About MotoMoto Tech</h2>
<div class="about-blurb">
<p><strong>MotoMoto Tech</strong> is a tech-news short-video channel. We take the biggest stories in AI, science, gadgets, and tech money-drama — and explain them in about 60 seconds, with zero fluff.</p>
<p style="margin-top:12px">Every day we publish across TikTok, YouTube Shorts, Facebook, and Threads. This site is our home base: every video gets a companion blog post with the full story.</p>
<p style="margin-top:12px"><strong>What we cover:</strong></p>
<p style="margin-top:6px;color:var(--mut)">▪ AI news — models, labs, breakthroughs<br>▪ Science explainers — space, physics, discoveries<br>▪ Tech vs law — trials, regulation, power fights<br>▪ Gadgets & startups — the hardware and hustle</p>
<p style="margin-top:12px"><strong>Contact:</strong> <a href="mailto:{EMAIL}">{EMAIL}</a></p>
<p style="margin-top:12px"><strong>Follow:</strong> {" · ".join(f'<a href="{u}">{n}</a>' for n, u in SOCIALS)}</p>
</div></div>"""
    open(os.path.join(SITE, 'about.html'), 'w').write(page('About', about_body, 'Who MotoMoto Tech is and what the channel covers.'))
    print(f'Built {len(posts)} posts + home + blog index + about')

if __name__ == '__main__':
    only = None
    if '--post' in sys.argv:
        only = sys.argv[sys.argv.index('--post') + 1]
    if only is not None:
        # single post only — indexes stay as-is (built from all videos)
        posts = load_videos(only)
        if not posts:
            print('No matching videos found'); sys.exit(1)
        os.makedirs(os.path.join(SITE, 'blog'), exist_ok=True)
        slug = build_post(posts[0])
        print(f'Post rebuilt: /blog/{slug}.html (indexes unchanged — run full build to refresh)')
    else:
        posts = load_videos()
        if not posts:
            print('No matching videos found'); sys.exit(1)
        build(posts)
