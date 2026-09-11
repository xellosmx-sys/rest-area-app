import urllib.request
import json
import ssl
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
cleaned_file = os.path.join(current_dir, 'rest_areas_cleaned.json')
master_file = os.path.join(current_dir, 'rest_areas_master.json')

# 1. 기존 정제된 210개 데이터 불러오기
with open(cleaned_file, 'r', encoding='utf-8') as f:
    cleaned_list = json.load(f)

# 빠른 검색을 위해 휴게소명을 key로 하는 딕셔너리로 변환
rest_dict = {item['name']: item for item in cleaned_list}

# 2. 도로공사 API에서 전체 207건 데이터 한 번에 가져오기 (perPage=300)
API_KEY = "c7cc395276cc7b8c5433bfad00d9499a1f3c6b3480ee0d15c59fd4c88f1ec372"
url = f"https://api.odcloud.kr/api/15118977/v1/uddi:6b9e8fc2-34cf-4edb-a963-f9830622995d?page=1&perPage=300&serviceKey={API_KEY}"

headers = {
    "Authorization": API_KEY,
    "Accept": "application/json"
}

print("전체 통행량 및 상세 주차 데이터 수집 중...")
req = urllib.request.Request(url, headers=headers)
context = ssl._create_unverified_context()

with urllib.request.urlopen(req, context=context) as response:
    api_data = json.loads(response.read().decode('utf-8')).get('data', [])

# 3. 두 데이터 병합하기
matched_count = 0
for traffic_item in api_data:
    name = traffic_item.get('휴게소명', '').strip()
    
    # 이름 매칭 (예: '건천(부산)' 매칭)
    target = rest_dict.get(name)
    if not target:
        # 괄호나 공백 차이가 있는 경우 부분 검색 매칭
        for key in rest_dict:
            if name in key or key in name:
                target = rest_dict[key]
                break

    if target:
        matched_count += 1
        # 세부 주차면수 및 24년 통행량 결합
        small_p = int(traffic_item.get('소형', 0) or 0)
        large_p = int(traffic_item.get('대형', 0) or 0)
        dis_p = int(traffic_item.get('장애인', 0) or 0)
        traffic_val = int(str(traffic_item.get('1일 차량 통행량(24년)', 0)).replace(',', '').strip() or 0)
        
        target['parking_detail'] = {
            "small": small_p,
            "large": large_p,
            "disabled": dis_p
        }
        target['daily_traffic_24'] = traffic_val
        
        # 단순 혼잡도 등급 계산 (통행량 대비 총 주차면수 기준)
        total_slots = small_p + large_p + dis_p
        if total_slots > 0 and traffic_val > 0:
            ratio = traffic_val / total_slots
            if ratio > 25:
                target['crowded_level'] = "혼잡"
            elif ratio > 15:
                target['crowded_level'] = "보통"
            else:
                target['crowded_level'] = "원활"
        else:
            target['crowded_level'] = "보통"

# 4. 최종 마스터 데이터 파일 저장
final_list = list(rest_dict.values())
with open(master_file, 'w', encoding='utf-8') as f:
    json.dump(final_list, f, ensure_ascii=False, indent=2)

print(f"병합 완료! {matched_count}개 휴게소의 상세 정보가 결합되어 '{master_file}'에 저장되었습니다.")