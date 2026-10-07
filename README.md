# MotoMoto Tech — Website + Video Blog

Brand hub + companion blog for the MotoMoto Tech short-video operation.
Static site, no build step, deploys on Vercel free.

## Adding a new post when a video publishes
1. `python3 tools/build.py --post <NN>` (rebuilds that post + indexes)
2. `git add -A && git commit -m "post: video <NN>" && git push`
3. Vercel redeploys automatically from `main`.

Full rebuild: `python3 tools/build.py`
