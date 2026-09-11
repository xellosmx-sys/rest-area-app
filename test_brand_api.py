import requests
import json

# 앞서 발급받으신 도로공사 인증키 그대로 사용
EX_API_KEY = "5636311933"  # 사용 중인 도로공사 키

# 브랜드 매장 엔드포인트
url = "https://data.ex.co.kr/openapi/restinfo/restBrandList"

params = {
    "key": EX_API_KEY,
    "type": "json",
    "numOfRows": "5",
    "pageNo": "1"
}

try:
    res = requests.get(url, params=params, timeout=10)
    print("Status Code:", res.status_code)
    if res.status_code == 200:
        data = res.json()
        print("브랜드 매장 데이터 호출 성공!")
        print(json.dumps(data, indent=2, ensure_ascii=False))
    else:
        print("호출 실패:", res.text)
except Exception as e:
    print(f"오류 발생: {e}")