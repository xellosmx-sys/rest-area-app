import urllib.request
import json
import ssl

# 발급받으신 인증키
API_KEY = "c7cc395276cc7b8c5433bfad00d9499a1f3c6b3480ee0d15c59fd4c88f1ec372"

# 확인된 정확한 엔드포인트 URL (10건 조회)
url = f"https://api.odcloud.kr/api/15118977/v1/uddi:6b9e8fc2-34cf-4edb-a963-f9830622995d?page=1&perPage=10&serviceKey={API_KEY}"

# 공공데이터포털 인증 헤더 설정
headers = {
    "Authorization": API_KEY,
    "Accept": "application/json"
}

try:
    req = urllib.request.Request(url, headers=headers)
    context = ssl._create_unverified_context()
    
    with urllib.request.urlopen(req, context=context) as response:
        result = response.read().decode('utf-8')
        data = json.loads(result)
        
        print("API 응답 성공!")
        print(f"조회 건수: {data.get('currentCount')}건 / 전체: {data.get('totalCount')}건")
        print("\n[샘플 데이터 출력]")
        print(json.dumps(data.get('data', [])[:2], indent=2, ensure_ascii=False))

except urllib.error.HTTPError as e:
    print(f"HTTP Error: {e.code} - {e.reason}")
except Exception as e:
    print(f"오류 발생: {e}")