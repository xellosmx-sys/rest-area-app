import requests
import json
import time

EX_API_KEY = "5636311933"
url = "https://data.ex.co.kr/openapi/restinfo/restBrandList"

# 1. 기존 마스터 데이터 로드
try:
    with open('rest_areas_master.json', 'r', encoding='utf-8') as f:
        master_list = json.load(f)
    print(f"기존 마스터 데이터 {len(master_list)}개 로드 완료.")
except Exception as e:
    print(f"파일 로드 실패: {e}")
    exit()

# 2. 브랜드 매장 전체 데이터 수집 (페이징 순회)
all_brands = []
page = 1
print("한국도로공사 브랜드 매장 데이터 수집 시작...")

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
            print(f"요청 종료: 상태 코드 {res.status_code}")
            break
            
        res_data = res.json()
        items = res_data.get("list", [])
        
        if not items:
            break
            
        all_brands.extend(items)
        print(f"페이지 {page} 완료 (누적 {len(all_brands)}개 브랜드 수집)")
        
        total_pages = int(res_data.get("pageSize", 1))
        if page >= total_pages:
            break
            
        page += 1
        time.sleep(0.2)
    except Exception as e:
        print(f"오류 발생: {e}")
        break

print(f"총 {len(all_brands)}개 브랜드 매장 수집 완료.")

# 3. 휴게소명 기준으로 브랜드 목록 정리 (NoneType 방어 처리)
brand_dict = {}
for item in all_brands:
    rest_name = (item.get("stdRestNm") or "").strip()
    brand_name = (item.get("brdName") or "").strip()
    desc = (item.get("brdDesc") or "").strip()
    s_time = (item.get("stime") or "").strip()
    e_time = (item.get("etime") or "").strip()
    
    if not rest_name or not brand_name:
        continue

    time_str = f"{s_time}~{e_time}" if s_time and e_time else "운영시간 현장확인"
    
    if rest_name not in brand_dict:
        brand_dict[rest_name] = []
        
    brand_dict[rest_name].append({
        "name": brand_name,
        "desc": desc,
        "hours": time_str
    })

# 4. 마스터 데이터에 병합
matched_count = 0
for r in master_list:
    r_name = r.get("name", "").replace("휴게소", "").strip()
    r["brand_list"] = []
    
    for api_rest_name, brands in brand_dict.items():
        clean_api_name = api_rest_name.replace("휴게소", "").strip()
        if r_name and (r_name in clean_api_name or clean_api_name in r_name):
            r["brand_list"] = brands
            matched_count += 1
            break

# 5. 저장
with open('rest_areas_master.json', 'w', encoding='utf-8') as f:
    json.dump(master_list, f, ensure_ascii=False, indent=2)

print(f"병합 완료: {matched_count}개 휴게소에 실제 브랜드 매장 데이터가 성공적으로 반영되었습니다.")