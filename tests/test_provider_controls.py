import tempfile, unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from quarterguard.provider_controls import Ledger, Blocked
class ControlsTests(unittest.TestCase):
 def setUp(self):self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.path=Path(self.tmp.name)/'ledger.db'
 def test_reservation_is_atomic_and_survives_reopen(self):
  l=Ledger(self.path)
  def reserve(_):
   try:return l.reserve('openai','case',total=2,daily=2,cooldown=0)
   except Blocked:return None
  with ThreadPoolExecutor(max_workers=8) as pool:ids=list(pool.map(reserve,range(8)))
  self.assertEqual(sum(x is not None for x in ids),2)
  with self.assertRaises(Blocked):Ledger(self.path).reserve('openai','case',total=2,daily=2,cooldown=0)
 def test_failure_still_consumes_attempt_and_cache_has_provenance(self):
  l=Ledger(self.path);rid=l.reserve('dart','x',total=2,daily=2,cooldown=0);l.finish(rid,{'status':'failed'})
  self.assertIsNone(l.cached('dart','x'))
  rid=l.reserve('dart','x',total=2,daily=2,cooldown=0);l.finish(rid,{'status':'succeeded','value':12})
  self.assertEqual(l.cached('dart','x')['value'],12)
  self.assertEqual(l.usage('dart')['attempts_total'],2)
 def test_global_cooldown_blocks_different_target(self):
  l=Ledger(self.path);l.reserve('dart','x',total=10,daily=8,cooldown=60)
  with self.assertRaises(Blocked):l.reserve('dart','y',total=10,daily=8,cooldown=60)
if __name__=='__main__':unittest.main()
