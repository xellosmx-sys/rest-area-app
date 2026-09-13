import requests
import json
import time

# 기존에 사용하시던 도로공사 API 키 활용
EX_API_KEY = "5636311933"  
url = "https://data.ex.co.kr/openapi/business/curStateStation"

# 1. 마스터 데이터 로드
try:
    with open('rest_areas_master.json', 'r', encoding='utf-8') as f:
        master_list = json.load(f)
    print(f"기존 마스터 데이터 {len(master_list)}개 로드 완료.")
except Exception as e:
    print(f"파일 로드 실패: {e}")
    exit()

# 2. 전국 고속도로 주유소 유가 데이터 수집
all_oil_stations = []
page = 1
print("한국도로공사 주유소 유가 데이터 수집 시작...")

while True:
    params = {
        "key": EX_API_KEY,
        "type": "json",
        "numOfRows": "100",
        "pageNo": str(page)
    }
    
    try:
        res = requests.get(url, params=params, timeout=10)
        if res.status_code != 200:
            break
            
        res_data = res.json()
        items = res_data.get("list", [])
        
        if not items:
            break
            
        all_oil_stations.extend(items)
        print(f"페이지 {page} 완료 (누적 {len(all_oil_stations)}개 수집)")
        
        total_pages = int(res_data.get("pageSize", 1))
        if page >= total_pages:
            break
            
        page += 1
        time.sleep(0.2)
    except Exception as e:
        print(f"오류 발생: {e}")
        break

# 3. 휴게소명 기준으로 유가 정보 딕셔너리화
oil_dict = {}
for item in all_oil_stations:
    rest_name = (item.get("serviceAreaName") or "").strip()
    gas_price = item.get("gasolinePrice")
    diesel_price = item.get("diselPrice") # API 원본 스펠링 오류(disel) 그대로 적용
    lpg_price = item.get("lpgPrice")
    
    if rest_name:
        oil_dict[rest_name] = {
            "gas_price": gas_price,
            "diesel_price": diesel_price,
            "lpg_price": lpg_price
        }

# 4. 마스터 데이터에 병합
matched_count = 0
for r in master_list:
    r_name = r.get("name", "").replace("휴게소", "").strip()
    
    r["gas_price"] = None
    r["diesel_price"] = None
    r["lpg_price"] = None
    
    for api_rest_name, prices in oil_dict.items():
        clean_api_name = api_rest_name.replace("주유소", "").replace("휴게소", "").strip()
        if r_name and (r_name in clean_api_name or clean_api_name in r_name):
            r["gas_price"] = prices["gas_price"]
            r["diesel_price"] = prices["diesel_price"]
            r["lpg_price"] = prices["lpg_price"]
            matched_count += 1
            break

# 5. 저장
with open('rest_areas_master.json', 'w', encoding='utf-8') as f:
    json.dump(master_list, f, ensure_ascii=False, indent=2)

print(f"병합 완료: {matched_count}개 휴게소에 유가 정보가 성공적으로 반영되었습니다.")