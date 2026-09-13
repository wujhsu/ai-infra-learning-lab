import importlib.util,json,os,socket,subprocess,sys,time,unittest,urllib.request,urllib.error
from pathlib import Path
root=Path(__file__).parents[1]
spec=importlib.util.spec_from_file_location('decision',root/'labs/rollouts/validate_decision.py')
decision=importlib.util.module_from_spec(spec);spec.loader.exec_module(decision)
class DecisionTest(unittest.TestCase):
 def test_rejects_unreviewed_deploy_and_missing_evidence(self):
  valid={'action':'hold','reason':'missing samples','evidence':['2 requests'],'patch_ref':''}
  self.assertEqual(decision.validate(valid)['action'],'hold')
  for bad in [{**valid,'action':'deploy'},{**valid,'evidence':[]},{**valid,'action':'propose_fix'},{**valid,'execute':'shell'}]:
   with self.assertRaises(ValueError):decision.validate(bad)
 def test_accepts_reviewable_proposal_without_executing_it(self):
  valid={'action':'propose_fix','reason':'configuration mismatch','evidence':['test failure'],'patch_ref':'branch/example'}
  self.assertEqual(decision.validate(valid),valid)
class FixtureTest(unittest.TestCase):
 def test_health_success_does_not_hide_business_failure(self):
  with socket.socket() as s:s.bind(('127.0.0.1',0));port=s.getsockname()[1]
  proc=subprocess.Popen([sys.executable,str(root/'labs/rollouts/app.py')],env={**os.environ,'PORT':str(port),'FAIL':'true'},stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
  try:
   deadline=time.monotonic()+5
   while True:
    try:
     with urllib.request.urlopen(f'http://127.0.0.1:{port}/health',timeout=.2) as response:self.assertEqual(response.status,200)
     break
    except urllib.error.URLError:
     if time.monotonic()>deadline:raise
     time.sleep(.05)
   with self.assertRaises(urllib.error.HTTPError) as raised:urllib.request.urlopen(f'http://127.0.0.1:{port}/',timeout=1)
   self.assertEqual(raised.exception.code,500)
  finally:proc.terminate();proc.wait(timeout=5)
if __name__=='__main__':unittest.main()
