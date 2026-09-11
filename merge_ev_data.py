import requests
import json
import xml.etree.ElementTree as ET

# data.go.kr에서 발급받은 일반 인증키 입력
EV_API_KEY = "c7cc395276cc7b8c5433bfad00d9499a1f3c6b3480ee0d15c59fd4c88f1ec372"

url = "http://apis.data.go.kr/B552584/EvCharger/getChargerInfo"

# 1. 기존 휴게소 마스터 데이터 로드
try:
    with open('rest_areas_master.json', 'r', encoding='utf-8') as f:
        master_list = json.load(f)
    print(f"기존 마스터 데이터 {len(master_list)}개 로드 완료.")
except Exception as e:
    print(f"파일 로드 실패: {e}")
    exit()

# 2. 전국 고속도로 휴게소 전기차 충전기 데이터 수집 (고속도로 검색)
print("한국환경공단 전기차 충전기 데이터 조회 중...")

params = {
    "serviceKey": EV_API_KEY,
    "pageNo": "1",
    "numOfRows": "9999",
    "dataType": "JSON"
}

ev_chargers = {}

try:
    res = requests.get(url, params=params, timeout=15)
    data = None
    
    # JSON 또는 XML 응답 대응
    if res.headers.get('content-type', '').startswith('application/json') or res.text.strip().startswith('{'):
        data = res.json()
        items = data.get("items", [{}])[0].get("item", []) if isinstance(data.get("items"), list) else data.get("items", {}).get("item", [])
    else:
        # 공공데이터포털 기본 XML 반환 시 파싱
        root = ET.fromstring(res.content)
        items = []
        for item in root.findall(".//item"):
            row = {child.tag: child.text for child in item}
            items.append(row)

    print(f"총 {len(items)}건의 전기차 충전기 레코드 확보.")

    # 3. 휴게소명 기준으로 운영사 및 충전기 스펙 집계
    for row in items:
        stat_nm = row.get("statNm", "").strip()
        busi_nm = row.get("busiNm", "환경부").strip()
        output = row.get("output", "")
        output_str = f"{output}kW" if output else "급속"
        
        # 휴게소 충전소만 분류
        if "휴게소" not in stat_nm:
            continue

        if stat_nm not in ev_chargers:
            ev_chargers[stat_nm] = {
                "operators": set(),
                "outputs": set(),
                "total_chargers": 0
            }

        ev_chargers[stat_nm]["operators"].add(busi_nm)
        if output:
            ev_chargers[stat_nm]["outputs"].add(output_str)
        ev_chargers[stat_nm]["total_chargers"] += 1

except Exception as e:
    print(f"충전기 API 호출 오류: {e}")

# 4. 마스터 데이터에 실제 충전기 정보 매핑
matched_count = 0
for r in master_list:
    r_name = r.get("name", "").replace("휴게소", "").strip()
    r["ev_detail"] = None

    for stat_name, info in ev_chargers.items():
        if r_name and r_name in stat_name:
            r["ev_detail"] = {
                "operators": list(info["operators"]),
                "outputs": sorted(list(info["outputs"]), key=lambda x: int(x.replace('kW','')) if x.replace('kW','').isdigit() else 0, reverse=True),
                "count": info["total_chargers"]
            }
            matched_count += 1
            break

# 5. 마스터 파일 저장
with open('rest_areas_master.json', 'w', encoding='utf-8') as f:
    json.dump(master_list, f, ensure_ascii=False, indent=2)

print(f"매핑 완료: 총 {matched_count}개 휴게소에 실제 전기차 충전소 세부 스펙(운영사, 출력, 충전기수)이 반영되었습니다.")