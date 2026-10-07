# MotoMoto Tech — Website + Video Blog

Brand hub + companion blog for the MotoMoto Tech short-video operation.
**Live:** https://motomototech-site-motomoto1.vercel.app

Template: [Massively by HTML5 UP](https://html5up.net/massively) (CCA 3.0, credit in footer),
dark-themed for our brand. Static site, no build step.

## Adding a new post when a video publishes
1. `python3 tools/build.py --post <NN>` — generates/updates that post
2. `python3 tools/deploy-vercel.py` — uploads + deploys to Vercel production
3. `git add -A && git commit -m "post: video <NN>" && git push` — keeps GitHub in sync

Full rebuild: `python3 tools/build.py` (then deploy + push as above).

Note: Vercel deploys via direct file upload (the Vercel GitHub App doesn't have
repo access, so there's no git auto-deploy). The deploy script handles it.
