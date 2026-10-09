"""장비 센서 스트림의 시간 역행, 중복, 결측 간격, 고정값, 비정상 변화율을 분리해 보고합니다."""
import argparse,html,json,math
from pathlib import Path
def finite(v,n,minimum=None):
 if type(v) not in (int,float) or not math.isfinite(v):raise ValueError(n+": finite number required")
 if minimum is not None and v<minimum:raise ValueError(n+": below minimum")
 return v
def report(x,t):
 p=html.escape(json.dumps(x,ensure_ascii=False,indent=2,allow_nan=False))
 return '<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>'+html.escape(t)+'</title><style>body{font:16px/1.6 system-ui;max-width:1000px;margin:30px auto;padding:20px;background:#101b2b;color:#eef7ff}pre{background:#192b40;padding:22px;border-radius:12px;white-space:pre-wrap}h1{color:#79e3c2}</style><h1>'+html.escape(t)+'</h1><p>오프라인 합성 예제 · 실물 장비 연결 없음</p><pre>'+p+'</pre>'
def cli(fn,title):
 p=argparse.ArgumentParser();p.add_argument("--input",default=str(Path(__file__).with_name("sample-input.json")));p.add_argument("--html");a=p.parse_args()
 try:
  x=fn(json.loads(Path(a.input).read_text(encoding="utf-8")))
  if a.html:Path(a.html).write_text(report(x,title),encoding="utf-8")
  print(json.dumps(x,ensure_ascii=False,indent=2,allow_nan=False))
 except (ValueError,KeyError,TypeError) as e:p.exit(2,"input error: "+str(e)+"\n")

def run(d):
 gap=finite(d["max_gap_s"],"max_gap_s",0);flat_n=d["flatline_count"];rate=finite(d["max_rate_per_s"],"max_rate_per_s",0)
 if type(flat_n) is not int or flat_n<2:raise ValueError("flatline_count must be >=2")
 g={}
 for r in d["readings"]:
  k=(r["asset_id"],r["sensor_id"]);g.setdefault(k,[]).append((finite(r["time_s"],"time_s",0),finite(r["value"],"value")))
 issues=[];streams=[]
 for (a,s),rows in sorted(g.items()):
  seen={};arrival=None
  for t,v in rows:
   b={"asset_id":a,"sensor_id":s,"time_s":t}
   if arrival is not None and t<arrival:issues.append({**b,"reason":"arrival_time_rollback"})
   arrival=t
   if t in seen:issues.append({**b,"reason":"exact_duplicate" if seen[t]==v else "conflicting_duplicate"});continue
   seen[t]=v
  ordered=sorted(seen.items());flat=1
  for i,(t,v) in enumerate(ordered):
   if i:
    pt,pv=ordered[i-1];dt=t-pt
    if dt>gap:issues.append({"asset_id":a,"sensor_id":s,"time_s":t,"reason":"gap","gap_s":dt})
    slope=abs(v-pv)/dt
    if slope>rate:issues.append({"asset_id":a,"sensor_id":s,"time_s":t,"reason":"rate_exceeded","rate_per_s":round(slope,6)})
    flat=flat+1 if v==pv else 1
    if flat==flat_n:issues.append({"asset_id":a,"sensor_id":s,"time_s":t,"reason":"flatline","count":flat_n})
  streams.append({"asset_id":a,"sensor_id":s,"unique_samples":len(ordered)})
 return {"valid":not issues,"streams":streams,"issues":issues,"policy":"report_only_no_imputation"}

if __name__=="__main__":cli(run,'센서 데이터 품질 감사기')
