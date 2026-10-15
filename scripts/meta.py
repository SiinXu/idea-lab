#!/usr/bin/env python3
"""Idea status + last-updated dates -> docs/meta.js (window.IMETA). Status lives in scripts/status.json
({id: "idea|validating|paused|dropped|live"}); default "idea". Updated = last git commit touching docs/d/<id>.json."""
import json,glob,os,subprocess
R=os.path.dirname(os.path.dirname(os.path.abspath(__file__)));os.chdir(R)
S=json.load(open('scripts/status.json')) if os.path.exists('scripts/status.json') else {}
M={}
for f in sorted(glob.glob('docs/d/*.json')):
    i=os.path.basename(f)[:-5]
    up=subprocess.run(['git','log','-1','--format=%cI','--',f],capture_output=True,text=True).stdout.strip()[:10]
    M[i]={'s':S.get(i,'idea'),'u':up}
open('docs/meta.js','w').write('window.IMETA='+json.dumps(M)+';')
print(len(M),'ideas')
