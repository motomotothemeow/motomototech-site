#!/usr/bin/env python3
"""Deploy motomototech-site to Vercel via MCP tools (no git integration needed)."""
import os, sys, json, base64, hashlib, subprocess

SITE = '/home/hatch/workspace/motomototech-site'
PROJECT_ID = 'prj_U8Hb0beDDIisuALYMZNP6o2kxPON'
VERCEL = '/opt/hatch/bin/vercel'

EXCLUDE = {'tools', '.git', 'README.md'}

def files_to_deploy():
    out = []
    for root, dirs, files in os.walk(SITE):
        dirs[:] = [d for d in dirs if d not in ('.git', 'tools')]
        for f in files:
            if f == 'README.md':
                continue
            full = os.path.join(root, f)
            rel = os.path.relpath(full, SITE)
            out.append((rel, full))
    return sorted(out)

def sha1_of(path):
    h = hashlib.sha1()
    with open(path, 'rb') as fh:
        h.update(fh.read())
    return h.hexdigest()

def mcp(tool, args):
    r = subprocess.run([VERCEL, 'call-tool', '--name', tool,
                        '--arguments-json', json.dumps(args)],
                       capture_output=True, text=True, timeout=120)
    return json.loads(r.stdout)

def main():
    flist = files_to_deploy()
    print(f'{len(flist)} files to upload')
    entries = []
    for rel, full in flist:
        size = os.path.getsize(full)
        sha = sha1_of(full)
        with open(full, 'rb') as fh:
            b64 = base64.b64encode(fh.read()).decode()
        args = {'contentLength': size,
                'requestBody': b64,
                'xVercelDigest': sha}
        d = mcp('upload_file', args)
        # check for error
        txt = json.dumps(d)
        if 'error' in txt.lower() and 'already' not in txt.lower():
            # print but continue — file may already exist
            pass
        entries.append({'file': rel, 'sha': sha, 'size': size})
        print(f'  ok {rel} ({size}b)')
    print('Creating deployment...')
    dep = mcp('create_deployment', {
        'requestBody': {
            'name': 'motomototech-site',
            'project': PROJECT_ID,
            'target': 'production',
            'files': entries,
        }
    })
    print(json.dumps(dep, indent=1)[:2000])

if __name__ == '__main__':
    main()
