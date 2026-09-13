"""Fail-closed validation of an advisory Agent result. Never executes fixes."""
import json,sys
def validate(value):
 if not isinstance(value,dict) or set(value)!={'action','reason','evidence','patch_ref'}:raise ValueError('Unexpected decision schema')
 if value['action'] not in ['hold','rollback','propose_fix']:raise ValueError('Unsupported action')
 if not isinstance(value['reason'],str) or not value['reason'].strip():raise ValueError('Missing reason')
 if not isinstance(value['evidence'],list) or not value['evidence'] or not all(isinstance(x,str) and x.strip() for x in value['evidence']):raise ValueError('Missing evidence')
 if not isinstance(value['patch_ref'],str):raise ValueError('Invalid patch reference')
 if value['action']=='propose_fix' and not value['patch_ref'].strip():raise ValueError('A fix proposal needs a reviewable patch reference')
 return value
if __name__=='__main__':
 try:print(json.dumps(validate(json.load(sys.stdin)),ensure_ascii=False))
 except (ValueError,TypeError) as e:print(f'HOLD: {e}',file=sys.stderr);sys.exit(1)
