# 설치 및 실행 방법

이 프로젝트는 Python과 Flask 기반으로 실행됩니다.
아래 단계를 순서대로 실행하면 로컬 환경에서 API 서버를 구동할 수 있습니다.

### 1. 가상환경 생성 및 활성화 (optional)

python -m venv venv

Windows PowerShell 기준:

venv\Scripts\activate


### 2. 패키지 설치
프로젝트에 필요한 Flask 라이브러리는 requirements.txt 파일을 통해 설치합니다.

pip install -r requirements.txt

### 3. 서버 실행
아래 명령어를 사용하여 Flask 서버를 실행할 수 있습니다.

python app.py


실행 후 브라우저 또는 Postman에서 아래 주소로 API를 테스트할 수 있습니다.

http://127.0.0.1:5000


(※ flask run 방식도 가능하지만, 본 과제에서는 python app.py 방식으로 실행하였습니다.)


# WSB Practice2 – Flask API 구현

### 1. POST / GET / PUT / DELETE 각각 2개씩, 총 8개의 API 구현

- POST /items : 아이템 생성
- POST /users : 사용자 생성

- GET /items : 아이템 전체 조회
- GET /items/<id> : 특정 아이템 조회

- PUT /items/<id> : 아이템 정보 수정
- PUT /users/<id> : 사용자 정보 수정

- DELETE /items/<id> : 아이템 삭제
- DELETE /users/<id> : 사용자 삭제

모든 API는 정상/오류 상황에 따른 적절한 응답 코드를 반환하도록 구성하였습니다.

### 2. 미들웨어(Middleware) 구현

Flask의 before_request, after_request 기능을 이용하여 다음과 같은 미들웨어를 구현하였습니다.

#### 2-1. 요청 로깅 미들웨어
모든 요청이 들어올 때마다 현재 시간, HTTP 메소드, 요청 경로를 콘솔에 출력합니다.
예: [2025-11-27 12:02:10] POST /items

#### 2-2. 응답 헤더 추가 미들웨어
모든 응답에 X-Backend-Framework: Flask 라는 커스텀 헤더를 추가하여 서버 정보를 확인할 수 있도록 하였습니다.

### 3. 응답 코드 다양성 확보 (2xx, 4xx, 5xx 각각 최소 2개 이상 사용)

과제 요구사항에 따라 2xx, 4xx, 5xx 상태 코드를 각각 2개 이상 사용하였습니다.

- 2xx 응답: GET, PUT, DELETE 요청의 정상 처리 시 사용된 200 OK와 POST 요청 성공 시 사용된 201 Created로 다양하게 반환됩니다.

- 4xx 응답:  잘못된 요청 데이터가 들어올 때 400 Bad Request를 구현하였습니다. 존재하지 않는 리소스를 조회,수정,삭제할 때 사용된 404 Not Found를 구현하였습니다.

- 5xx 응답: /items?force_error=true 요청 시 일부러 예외를 발생시켜 500 Internal Server Error를 반환하도록 하였습니다. 전역 에러 핸들러에서도 동일하게 500 오류를 처리합니다.

### 4. 응답 포맷 통일

모든 API는 동일한 JSON 구조로 응답하도록 make_response() 헬퍼 함수를 사용하였습니다.

응답 형식은 아래와 같습니다.

status: "success" 또는 "error"
data: 실제 응답 데이터 또는 null
message: 상태 메시지

성공, 실패, 서버 오류 등 모든 상황에서 동일한 구조의 JSON을 반환하도록 구현하여 일관성을 유지하였습니다.

### 5. 실행 및 테스트 화면 캡처 내용

Postman을 활용해 구현한 API들을 모두 테스트하였습니다.

1) POST /items 성공 및 실패 테스트
- 성공: ![post_items_success](images/post_items_success.png)

- 실패: ![post_items_error](images/post_items_error.png)


2) POST /users 성공 및 실패 테스트
- 성공: ![post_users_success](images/post_users_success.png)

- 실패: ![post_users_error](images/post_users_error.png)


3) GET /items 전체 조회 결과
- ![get_items_all](images/get_items_all.png)


4) GET /items/<id> 성공 및 실패 테스트 
- 성공: ![get_items_id_success](images/get_items_id_success.png)

- 실패: ![get_items_id_error](images/get_items_id_error.png)


5) PUT /items/<id> 수정 성공 및 실폐 테스트
- 성공: ![put_items_id_success](images/put_items_id_success.png)

- 실패: ![put_items_id_error](images/put_items_id_error.png)


6) PUT /users/<id> 수정 성공 및 실폐 테스트
- 성공: ![put_users_id_success](images/put_users_id_success.png)

- 실패: ![put_users_id_error](images/put_users_id_error.png)


7) DELETE /items/<id> 삭제 성공 및 삭제 후 재삭제 시 404 응답
- 성공: ![delete_items_id_success](images/delete_items_id_success.png)

- 재삭제: ![delete_items_id_error](images/delete_items_id_error.png)


8) DELETE /users/<id> 삭제 성공 및 삭제 후 재삭제 시 404 응답
- 성공: ![delete_users_id_success](images/delete_users_id_success.png)

- 재삭제: ![delete_users_id_error](images/delete_users_id_error.png)


9) 500 Internal Server Error 테스트
- GET /items?force_error=true → 강제 예외 발생 (500)
![server_error_1](images/server_error_1.png)


- app.errorhandler(500) – 전역 500 오류 핸들러 직접 테스트
![server_error_2](images/server_error_2.png)




