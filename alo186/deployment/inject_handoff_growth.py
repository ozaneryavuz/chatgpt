from __future__ import annotations
import argparse,json
from pathlib import Path
from inject_handoff_growth_base import run as run_handoff_base
from inject_proposal_scope_growth import run as run_proposal_scope

def run(site:Path,base_path:str)->dict:
 result=run_handoff_base(site,base_path)
 result['proposalScope']=run_proposal_scope(site,base_path)
 return result

def main()->None:
 parser=argparse.ArgumentParser()
 parser.add_argument('--site',type=Path,required=True)
 parser.add_argument('--base-path',default='')
 args=parser.parse_args()
 print(json.dumps(run(args.site.resolve(),args.base_path),ensure_ascii=False,indent=2))

if __name__=='__main__':main()
