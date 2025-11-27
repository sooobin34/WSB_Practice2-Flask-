"""
웹서비스설계 - 백엔드 프레임워크 실습 (Flask 버전)

요구사항
- HTTP 메소드별 API 2개씩 구현 (POST / GET / PUT / DELETE → 총 8개)
- 미들웨어 구현 (요청 로그 / 응답 헤더)
- 2xx / 4xx / 5xx 응답 코드 다양하게 사용
- 수업에서 나온 표준 응답 포맷 사용
"""

from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)


# =====================================
# 공통 응답 포맷 함수
# =====================================
def make_response(status: str, http_status: int, data=None, message: str = None):
    """
    응답을 항상 같은 형태(JSON)로 보내기 위한 헬퍼 함수.

    예시 포맷:
    {
      "status": "success" 또는 "error",
      "data": {...} 또는 null,
      "message": "상태 메시지"
    }

    - status: 비즈니스 로직 기준 성공/실패 여부
    - http_status: 실제 HTTP 상태 코드 (200, 201, 400, 404, 500 등)
    - data: 클라이언트에 전달할 데이터 (dict, list 등)
    - message: 추가 설명
    """
    body = {
        "status": status,
        "data": data,
        "message": message
    }
    return jsonify(body), http_status


# =====================================
# 간단한 인메모리 "DB" 역할
# (실제 DB 대신 파이썬 딕셔너리 사용)
# =====================================
# items: 상품 정보 저장
#   - key: item_id (int)
#   - value: {"id": 1, "name": "연필", "price": 500}
items = {}

# users: 사용자 정보 저장
#   - key: user_id (int)
#   - value: {"id": 1, "username": "soo", "email": "test@test.com"}
users = {}

# 새로 생성될 때 사용할 ID 값 (자동 증가처럼 사용)
next_item_id = 1
next_user_id = 1


# =====================================
# Middleware 구현
# =====================================

@app.before_request
def log_request():
    """
    요청이 들어올 때마다 실행되는 미들웨어.

    하는 일:
    - 현재 시간
    - HTTP 메소드 (GET, POST 등)
    - 요청 경로 (/items, /users/1 등)
    를 터미널에 출력해서 간단한 로그로 사용.
    """
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{now}] {request.method} {request.path}")


@app.after_request
def add_custom_header(response):
    """
    응답이 나가기 전에 실행되는 미들웨어.

    하는 일:
    - 응답 헤더에 'X-Backend-Framework: Flask' 값을 추가.
      → 나중에 클라이언트에서 어떤 백엔드를 쓰는지 확인 가능.
    """
    response.headers["X-Backend-Framework"] = "Flask"
    return response


# =====================================
# A. POST API 2개
# =====================================

@app.route("/items", methods=["POST"])
def create_item():
    """
    [POST] /items
    - 아이템(상품) 생성 API
    - body(JSON) 예시:
      {
        "name": "연필",
        "price": 500
      }
    - 성공 시: 201 Created + 생성된 아이템 정보 반환
    - 실패 시: 400 Bad Request (필드 누락 등)
    """
    global next_item_id

    # JSON Body 읽기 (없으면 빈 dict)
    body = request.get_json(silent=True) or {}

    name = body.get("name")
    price = body.get("price")

    # name 또는 price가 없으면 클라이언트 잘못 → 400
    if not name or price is None:
        return make_response(
            status="error",
            http_status=400,
            data=None,
            message="name과 price는 필수입니다."
        )

    # 새 아이템 생성
    item = {
        "id": next_item_id,
        "name": name,
        "price": price
    }
    items[next_item_id] = item
    next_item_id += 1

    # 생성이므로 201 코드 사용
    return make_response(
        status="success",
        http_status=201,
        data=item,
        message="아이템이 성공적으로 생성되었습니다."
    )


@app.route("/users", methods=["POST"])
def create_user():
    """
    [POST] /users
    - 사용자 생성 API
    - body(JSON) 예시:
      {
        "username": "soo",
        "email": "soo@test.com"
      }
    - 성공 시: 201 Created + 생성된 유저 정보
    - 실패 시: 400 Bad Request
    """
    global next_user_id

    body = request.get_json(silent=True) or {}
    username = body.get("username")
    email = body.get("email")

    if not username or not email:
        return make_response(
            status="error",
            http_status=400,
            data=None,
            message="username과 email은 필수입니다."
        )

    user = {
        "id": next_user_id,
        "username": username,
        "email": email
    }
    users[next_user_id] = user
    next_user_id += 1

    return make_response(
        status="success",
        http_status=201,
        data=user,
        message="유저가 성공적으로 생성되었습니다."
    )


# =====================================
# B. GET API 2개
# =====================================

@app.route("/items", methods=["GET"])
def get_items():
    """
    [GET] /items
    - 아이템 전체 리스트 조회 API

    쿼리스트링 옵션:
    - /items?force_error=true
      → 강제로 예외를 발생시켜서 500 응답 테스트용

    기본:
    - 200 OK + 아이템 리스트
    """
    # 5xx 응답을 보여주기 위한 테스트용 옵션
    if request.args.get("force_error") == "true":
        # 일부러 예외 발생 → 아래 500 핸들러로 감
        raise Exception("강제로 발생시킨 서버 오류입니다.")

    return make_response(
        status="success",
        http_status=200,
        data=list(items.values()),
        message="아이템 목록 조회 성공"
    )


@app.route("/items/<int:item_id>", methods=["GET"])
def get_item(item_id):
    """
    [GET] /items/<item_id>
    - 특정 아이템 한 개 조회

    예:
    - /items/1

    - 성공 시: 200 OK
    - 아이템이 없으면: 404 Not Found
    """
    item = items.get(item_id)
    if not item:
        return make_response(
            status="error",
            http_status=404,
            data=None,
            message=f"id={item_id} 아이템을 찾을 수 없습니다."
        )

    return make_response(
        status="success",
        http_status=200,
        data=item,
        message="아이템 상세 조회 성공"
    )


# =====================================
# C. PUT API 2개
# =====================================

@app.route("/items/<int:item_id>", methods=["PUT"])
def update_item(item_id):
    """
    [PUT] /items/<item_id>
    - 아이템 정보 수정

    body(JSON) 예시:
    {
      "name": "지우개",
      "price": 700
    }

    둘 중 하나만 보내도 부분 수정 가능:
    {
      "price": 700
    }

    - 존재하지 않는 id → 404
    - 성공 → 200 OK
    """
    item = items.get(item_id)
    if not item:
        return make_response(
            status="error",
            http_status=404,
            data=None,
            message=f"id={item_id} 아이템을 찾을 수 없습니다."
        )

    body = request.get_json(silent=True) or {}
    name = body.get("name")
    price = body.get("price")

    # 보내준 값만 수정
    if name is not None:
        item["name"] = name
    if price is not None:
        item["price"] = price

    items[item_id] = item

    return make_response(
        status="success",
        http_status=200,
        data=item,
        message="아이템이 성공적으로 수정되었습니다."
    )


@app.route("/users/<int:user_id>", methods=["PUT"])
def update_user(user_id):
    """
    [PUT] /users/<user_id>
    - 유저 정보 수정 API

    body(JSON) 예시:
    {
      "username": "새이름",
      "email": "new@test.com"
    }

    - 유저 없으면: 404
    - 성공: 200 OK
    """
    user = users.get(user_id)
    if not user:
        return make_response(
            status="error",
            http_status=404,
            data=None,
            message=f"id={user_id} 유저를 찾을 수 없습니다."
        )

    body = request.get_json(silent=True) or {}
    username = body.get("username")
    email = body.get("email")

    if username is not None:
        user["username"] = username
    if email is not None:
        user["email"] = email

    users[user_id] = user

    return make_response(
        status="success",
        http_status=200,
        data=user,
        message="유저 정보가 성공적으로 수정되었습니다."
    )


# =====================================
# D. DELETE API 2개
# =====================================

@app.route("/items/<int:item_id>", methods=["DELETE"])
def delete_item(item_id):
    """
    [DELETE] /items/<item_id>
    - 아이템 삭제 API

    - id가 없으면: 404 Not Found
    - 성공하면: 200 OK + 삭제된 id 반환
    """
    item = items.get(item_id)
    if not item:
        return make_response(
            status="error",
            http_status=404,
            data=None,
            message=f"id={item_id} 아이템을 찾을 수 없습니다."
        )

    del items[item_id]

    return make_response(
        status="success",
        http_status=200,
        data={"deleted_id": item_id},
        message="아이템이 성공적으로 삭제되었습니다."
    )


@app.route("/users/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    """
    [DELETE] /users/<user_id>
    - 유저 삭제 API

    - 없는 유저: 404
    - 성공: 200 OK + 삭제된 id
    """
    user = users.get(user_id)
    if not user:
        return make_response(
            status="error",
            http_status=404,
            data=None,
            message=f"id={user_id} 유저를 찾을 수 없습니다."
        )

    del users[user_id]

    return make_response(
        status="success",
        http_status=200,
        data={"deleted_id": user_id},
        message="유저가 성공적으로 삭제되었습니다."
    )


# =====================================
# 전역 에러 핸들러 (500 응답용)
# =====================================
@app.errorhandler(500)
def handle_500_error(e):
    """
    서버 내부 오류(예외)가 발생했을 때 호출되는 핸들러.

    - /items?force_error=true 처럼 일부러 예외를 발생시키면
      여기로 들어와서 500 응답 + 표준 포맷으로 메시지 반환.
    """
    return make_response(
        status="error",
        http_status=500,
        data=None,
        message="서버 내부 오류가 발생했습니다. (테스트용 500 응답)"
    )

@app.route("/test500", methods=["GET"])
def test_500():
    # 강제 예외 발생
    raise Exception("테스트용 서버 에러입니다.")

if __name__ == "__main__":
    # 로컬 개발용 실행 설정
    # - host: 0.0.0.0 → 외부에서도 접속 가능하게 (같은 네트워크라면)
    # - port: 5000 (Flask 기본 포트)
    # - debug: True 로 두면 코드 변경 시 자동 리로드 + 에러 페이지 디버깅 가능
    app.run(host="0.0.0.0", port=5000, debug=True)
