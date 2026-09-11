import json
import os

# 현재 파이썬 파일이 위치한 폴더 경로 구하기
current_dir = os.path.dirname(os.path.abspath(__file__))
input_file = os.path.join(current_dir, '전국휴게소정보표준데이터.json')
output_file = os.path.join(current_dir, 'rest_areas_cleaned.json')

# 1. 원본 파일 로드
with open(input_file, 'r', encoding='utf-8') as f:
    raw_data = json.load(f)

records = raw_data.get('records', [])
cleaned_rest_areas = []

for item in records:
    try:
        lat_str = str(item.get('위도', '')).strip()
        lng_str = str(item.get('경도', '')).strip()
        if not lat_str or not lng_str:
            continue
        
        lat = float(lat_str)
        lng = float(lng_str)
        
        # 대한민국 위경도 범위 체크 (위도 33~39, 경도 124~132)
        if not (33.0 <= lat <= 39.0 and 124.0 <= lng <= 132.0):
            continue

        rest_area = {
            "name": item.get("휴게소명"),
            "route_name": item.get("도로노선명"),
            "direction": item.get("도로노선방향"),
            "lat": lat,
            "lng": lng,
            "parking_count": int(item.get("주차면수", 0)) if item.get("주차면수") else 0,
            "best_food": item.get("휴게소대표음식명", "정보 없음"),
            "has_gas": item.get("주유소유무") == "Y",
            "has_lpg": item.get("LPG충전소유무") == "Y",
            "has_ev": item.get("전기차충전소유무") == "Y",
            "has_nursing": item.get("수유실유무") == "Y",
            "has_pharmacy": item.get("약국유무") == "Y",
            "tel": item.get("휴게소전화번호", "")
        }
        cleaned_rest_areas.append(rest_area)
    except Exception:
        continue

# 2. 정제된 경량 JSON 파일로 저장
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(cleaned_rest_areas, f, ensure_ascii=False, indent=2)

print(f"전처리 완료! 유효한 휴게소 총 {len(cleaned_rest_areas)}개가 'rest_areas_cleaned.json'에 저장되었습니다.")