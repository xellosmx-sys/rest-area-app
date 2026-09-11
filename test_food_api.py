import requests
import json
import time

# 도로공사 포털에서 발급받은 인증키 입력
EX_API_KEY = "5636311933"

url = "https://data.ex.co.kr/openapi/restinfo/restBestfoodList"

# 1. 기존 휴게소 마스터 데이터 로드
try:
    with open('rest_areas_master.json', 'r', encoding='utf-8') as f:
        master_list = json.load(f)
    print(f"기존 마스터 데이터 {len(master_list)}개 로드 완료.")
except Exception as e:
    print(f"파일 로드 실패: {e}")
    exit()

# 2. 도로공사 실제 푸드메뉴 데이터 전량 수집 (페이징 순회)
all_foods = []
page = 1

print("도로공사 공식 푸드메뉴/가격 데이터 수집 시작...")

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
            print(f"요청 중단: 상태 코드 {res.status_code}")
            break
            
        res_data = res.json()
        items = res_data.get("list", [])
        
        if not items:
            # 더 이상 가져올 데이터가 없으면 종료
            break
            
        all_foods.extend(items)
        print(f"페이지 {page} 완료 (누적 {len(all_foods)}건 수집)")
        
        # 전체 페이지 수에 도달했는지 체크
        total_pages = int(res_data.get("pageSize", 1))
        if page >= total_pages:
            break
            
        page += 1
        time.sleep(0.2)
        
    except Exception as e:
        print(f"오류 발생: {e}")
        break

print(f"총 {len(all_foods)}개의 실제 음식 메뉴 수집 완료.")

# 3. 휴게소명 기준으로 메뉴 및 가격 매핑
food_dict = {}
for item in all_foods:
    rest_name = item.get("stdRestNm", "").strip()
    food_name = item.get("foodNm", "").strip()
    food_cost = item.get("foodCost", "").strip()
    is_best = item.get("bestfoodyn", "N")
    
    if not rest_name or not food_name:
        continue
        
    if rest_name not in food_dict:
        food_dict[rest_name] = []
        
    food_dict[rest_name].append({
        "name": food_name,
        "price": f"{int(food_cost):,}원" if food_cost.isdigit() else f"{food_cost}원",
        "is_best": (is_best == "Y")
    })

# 4. 마스터 데이터에 실제 메뉴 배열 병합
matched_count = 0
for r in master_list:
    r_name = r.get("name", "")
    r["menu_list"] = []
    
    # 휴게소명 유사도 매칭 (예: '선산' in '선산(창원)')
    for api_rest_name, menus in food_dict.items():
        clean_name = r_name.replace("휴게소", "").strip()
        if clean_name and (clean_name in api_rest_name or api_rest_name in clean_name):
            r["menu_list"] = menus
            matched_count += 1
            break

# 5. 업데이트된 파일 저장
with open('rest_areas_master.json', 'w', encoding='utf-8') as f:
    json.dump(master_list, f, ensure_ascii=False, indent=2)

print(f"병합 완료: {matched_count}개 휴게소에 실제 음식/가격 데이터가 성공적으로 반영되었습니다.")