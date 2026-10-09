import json,unittest
from pathlib import Path
from main import *
class Tests(unittest.TestCase):
 def sample(self):return json.loads(Path(__file__).with_name("sample-input.json").read_text())

 def test_issue_classes(self):
  r={x["reason"] for x in run(self.sample())["issues"]};self.assertTrue({"arrival_time_rollback","conflicting_duplicate","gap","rate_exceeded","flatline"}<=r)
 def test_clean(self):
  d=self.sample();d["readings"]=[{"asset_id":"a","sensor_id":"s","time_s":i,"value":i} for i in range(4)];self.assertTrue(run(d)["valid"])
 def test_exact_duplicate(self):
  d=self.sample();d["readings"]=[{"asset_id":"a","sensor_id":"s","time_s":0,"value":1}]*2;self.assertEqual(run(d)["issues"][0]["reason"],"exact_duplicate")
 def test_bad(self):
  d=self.sample();d["flatline_count"]=1
  with self.assertRaises(ValueError):run(d)

if __name__=="__main__":unittest.main()
