# 센서 데이터 품질 감사기

장비 센서 스트림의 시간 역행, 중복, 결측 간격, 고정값, 비정상 변화율을 분리해 보고합니다.

## 핵심 기능

도착 순서 오류와 event-time 품질 문제를 구분합니다. 중복은 exact/conflicting으로 나누고 결측값을 임의 보간하지 않습니다.

## 설치·실행

Python 3.10 이상, 외부 패키지·유료 API·장비 연결이 필요 없습니다.

~~~bash
git clone https://github.com/MetaSonGi/sensor-quality-auditor.git
cd sensor-quality-auditor
python -m pip install -r requirements.txt
python main.py
python main.py --input sample-input.json --html result.html
python -m unittest -v
~~~

example-report.html 또는 result.html을 브라우저에서 열 수 있습니다. CDN과 서버 없이 동작하며 문자열은 HTML escape됩니다.

## 입출력 예제

[sample-input.json](sample-input.json), [example-output.json](example-output.json), [example-report.html](example-report.html)을 포함합니다.

~~~json
{
  "max_gap_s": 3,
  "flatline_count": 3,
  "max_rate_per_s": 3,
  "readings": [
    {
      "asset_id": "press-1",
      "sensor_id": "temperature",
      "time_s": 0,
      "value": 30
    },
    {
      "asset_id": "press-1",
      "sensor_id": "temperature",
      "time_s": 1,
      "value": 30
    },
    {
      "asset_id": "press-1",
      "sensor_id": "temperature",
      "time_s": 2,
      "value": 30
    },
    {
      "asset_id": "press-1",
      "sensor_id": "temperature",
      "time_s": 7,
      "value": 50
    },
    {
      "asset_id": "press-1",
      "sensor_id": "temperature",
      "time_s": 1,
      "value": 31
    }
  ]
}
~~~

출력 미리보기:

~~~text
{
  "valid": false,
  "streams": [
    {
      "asset_id": "press-1",
      "sensor_id": "temperature",
      "unique_samples": 4
    }
  ],
  "issues": [
    {
      "asset_id": "press-1",
      "sensor_id": "temperature",
      "time_s": 1,
      "reason": "arrival_time_rollback"
    },
    {
      "asset_id": "press-1",
      "sensor_id": "temperature",
      "time_s": 1,
      "reason": "conflicting_duplicate"
    },
    {
      "asset_id": "press-1",
      "sensor_id": "temperature",
      "time_s": 2,
      "reason": "flatline",
      "count": 3
    },
    {
      "asset_id": "press-1",
      "sensor_id": "temperature",
      "time_s": 7,
      "reason": "gap",
      "gap_s": 5
    },
    {
      "asset_id": "press-1",
      "sensor_id": "temperature",
      "time_s": 7,
      "reason": "rate_exceeded",
      "rate_per_s": 4.0
    }
  ],
  "policy": "report_only_no_imputation"
}

~~~

## 설계 판단

도착 순서 오류와 event-time 품질 문제를 구분합니다. 중복은 exact/conflicting으로 나누고 결측값을 임의 보간하지 않습니다. JSON 입출력으로 Python 작업 큐, Nest.js 자동화, XR/WebGL 모니터링 앞단에 연결할 수 있습니다. 실제 장비 상태는 변경하지 않습니다.

## 한계

통계적 드리프트·교정·단위 검증은 포함하지 않으며 임계값은 장비별로 정해야 합니다. 가상의 경력, 논문 성능, 모델 재현, 실물 제조 검증을 주장하지 않습니다.

## 검증·근거

정상·경계·오류 테스트 4개를 실행했습니다. [VALIDATION.txt](VALIDATION.txt)와 [TRENDS.md](TRENDS.md)에 결과와 근거를 구분했습니다.

실행 기준일: 2026-10-10 (Asia/Seoul). 기존 저장소를 수정하지 않은 독립 프로그램입니다.
