# TripCS

여행 계획을 만들고 관리할 수 있는 웹 서비스 프로젝트입니다.

실제 배포와 서비스 운영을 목표로 개발하며,
백엔드부터 데이터베이스, 인증, 프론트엔드, 테스트, 배포까지 단계적으로 구현합니다.

---

## Project Goal

단순한 CRUD 연습 프로젝트가 아니라 실제 사용 가능한 여행 계획 서비스 구축을 목표로 합니다.

### 주요 목표

- 사용자 회원가입 및 로그인
- JWT 기반 인증
- 여행 생성 및 관리
- 여행 일정 관리
- 사용자별 데이터 권한 관리
- PostgreSQL 기반 데이터 저장
- 프론트엔드 연동
- 테스트 작성
- Docker 환경 구성
- 실제 온라인 배포

---

## 🛠️ Tech Stack

### Backend
- Python
- FastAPI
- SQLAlchemy
- Pydantic
- Uvicorn

### Database
- PostgreSQL
- Alembic

### Authentication
- bcrypt
- JWT
- python-jose

### Email
- Gmail SMTP
- SMTP SSL

---

## 📁 Project Structure

```text
trip_planner/
│
├── backend/
│   ├── dependencies/
│   │   └── auth.py
│   │
│   ├── routers/
│   │   ├── auth.py
│   │   ├── user.py
│   │   └── trip.py
│   │
│   ├── schemas/
│   │   ├── auth.py
│   │   ├── user.py
│   │   └── trip.py
│   │
│   ├── services/
│   │   ├── auth.py
│   │   ├── user.py
│   │   ├── email.py
│   │   └── email_verification.py
│   │
│   ├── database.py
│   ├── models.py
│   └── main.py
│
├── alembic/
│
├── .env
├── .gitignore
├── README.md
└── requirements.txt
```



# DAY 1 프로젝트 초기 세팅 및 PostgreSQL 연결

## 배운내용
- PostgreSQL 설치 및 DB 생성
- PostgreSQL Driver 설정
- SQLAlchemy 연결 및 Model 생성
- Alembic Migration 생성 및 적용


## 패키지 설치

```
pip install fastapi uvicorn sqlalchemy psycopg2-binary python-dotenv alembic
```

## 패키지 역할
- FastAPI : API 서버 구축
- Uvicorn : FastAPI 실행 서버
- SQLAlchemy : 파이썬에서 DB 사용
- psycopg2-binary : PostgreSQL 연결
- python-dotenv : 환경변수 관리
- ALembic : DB Migration 관리


# Day 2 회원 가입 및 로그인 

## 배운내용

- 회원가입 API 구현
- 비밀번호 bcrypt 해싱
- 이메일 인증 시스템 구현
- 이메일 인증번호 생성 및 검증
- Gmail SMTP를 이용한 인증 메일 발송
- PostgreSQL 이메일 인증 데이터 저장
- JWT 기반 로그인 구현
- JWT Access Token 발급
- JWT를 이용한 사용자 인증
- FastAPI Dependency를 이용한 로그인 사용자 확인
- 사용자별 API 접근 권한 처리
- `.env`를 이용한 비밀정보 관리


## 1. 회원가입 구현

사용자가 이메일 + 비번을 입력하여 계정을 생성할 수 있게 회원가입 API 구현


회원가입 과정:

```text
이메일 + 비밀번호
        ↓
기존 이메일 확인
        ↓
비밀번호 bcrypt 해싱
        ↓
users 테이블에 사용자 생성
        ↓
이메일 인증번호 생성
        ↓
인증번호 이메일 발송
```

## 2. 비밀번호 암호화

사용자의 비밀번호를 데이터베이스에 평문으로 저장하지 않고 `bcrypt`를 이용하여 해싱했습니다.

```python
def hash_password(password: str) -> str:
    password_bytes = password.encode("utf-8")

    if len(password_bytes) > 72:
        raise ValueError("Password must be 72 bytes or less")

    return bcrypt.hashpw(
        password_bytes,
        bcrypt.gensalt()
    ).decode("utf-8")
```

로그인할 때는 저장된 해시와 사용자가 입력한 비밀번호를 비교합니다.

```python
bcrypt.checkpw(
    password.encode("utf-8"),
    password_hash.encode("utf-8"),
)
```

## 3. 이메일 인증

회원가입 후 이메일 인증번호를 발송하도록 구현했습니다.

인증번호는 별도의 `email_verifications` 테이블에 저장합니다.

```text
users
│
├── id
├── email
├── password_hash
├── email_verified
└── created_at

email_verifications
│
├── id
├── user_id
├── code_hash
├── expires_at
├── verified_at
└── created_at
```

인증번호는 원본을 그대로 DB에 저장하지 않고 해시하여 저장합니다.

인증 API:

```text
POST /auth/verify-email
```

요청 데이터:

```json
{
    "email": "example@gmail.com",
    "code": "123456"
}
```

인증에 성공하면:

```text
users.email_verified = true
```

로 변경됩니다.

## 4. Gmail SMTP 이메일 발송

Gmail SMTP를 이용하여 실제 이메일로 인증번호를 전송하도록 구현했습니다.

SMTP 관련 정보는 `.env`에서 관리합니다.

```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=465
SMTP_USER=...
SMTP_PASSWORD=...
SMTP_FROM=...
```

SMTP 비밀번호는 Gmail 계정의 일반 비밀번호가 아니라 **Google 앱 비밀번호**를 사용합니다.

이메일 발송에는 Python의 `smtplib`과 `EmailMessage`를 사용했습니다.

```python
with smtplib.SMTP_SSL(
    SMTP_HOST,
    SMTP_PORT,
) as smtp:
    smtp.login(
        SMTP_USER,
        SMTP_PASSWORD,
    )

    smtp.send_message(message)
```

## 5. PostgreSQL 인증 관련 테이블

### users

```text
id
email
password_hash
email_verified
created_at
```

### social_accounts

SNS 로그인을 위한 계정 연결 정보를 저장합니다.

```text
id
user_id
provider
provider_user_id
created_at
```

Google, Kakao 등의 SNS 로그인 계정을 하나의 User 계정에 연결할 수 있도록 설계했습니다.

### email_verifications

이메일 인증번호를 관리합니다.

```text
id
user_id
code_hash
expires_at
verified_at
created_at
```

## 6. JWT 로그인

이메일과 비밀번호가 올바른 경우 JWT Access Token을 발급하도록 구현했습니다.

로그인 API:

```text
POST /auth/login
```

로그인 과정:

```text
이메일 + 비밀번호
        ↓
사용자 조회
        ↓
비밀번호 검증
        ↓
이메일 인증 여부 확인
        ↓
JWT Access Token 발급
        ↓
클라이언트에 Token 반환
```

JWT에는 사용자를 식별하기 위한 `sub` 값을 저장합니다.

현재 프로젝트에서는 `User.id`를 `sub`로 사용합니다.

```text
sub = user.id
```

## 7. JWT Secret Key

JWT 서명에 사용하는 Secret Key는 코드에 직접 작성하지 않고 `.env`에서 관리합니다.

```env
JWT_SECRET_KEY=...
JWT_ALGORITHM=HS256
```

`JWT_SECRET_KEY`는 직접 생성한 충분히 긴 랜덤 문자열을 사용합니다.

실제 Secret Key는 GitHub 등에 공개하면 안 됩니다.

따라서 `.gitignore`에 `.env`를 추가하여 비밀정보가 저장소에 올라가지 않도록 관리합니다.

## 8. 로그인 사용자 인증

JWT를 검증하는 FastAPI Dependency를 구현했습니다.

```text
backend/dependencies/auth.py
```

`get_current_user()`가 다음 과정을 담당합니다.

```text
Authorization Header
        ↓
Bearer Token 추출
        ↓
JWT Decode
        ↓
sub에서 User ID 확인
        ↓
PostgreSQL에서 User 조회
        ↓
현재 로그인한 User 반환
```

API 요청에는 다음과 같이 JWT를 전달합니다.

```http
Authorization: Bearer <access_token>
```

이를 통해 로그인한 사용자만 접근할 수 있는 API를 만들 수 있습니다.

## 9. 현재 인증 구조

```text
                    ┌───────────────┐
                    │   회원가입    │
                    │ POST /users   │
                    └───────┬───────┘
                            ↓
                    비밀번호 bcrypt
                            ↓
                      User 생성
                            ↓
                    인증번호 생성
                            ↓
                    Gmail SMTP 발송
                            ↓
                    이메일 인증
                            ↓
                 email_verified = true
                            ↓
                    ┌───────────────┐
                    │     로그인    │
                    │ POST /auth/login
                    └───────┬───────┘
                            ↓
                    비밀번호 검증
                            ↓
                       JWT 발급
                            ↓
                  Authorization Header
                            ↓
                  get_current_user()
                            ↓
                     현재 사용자 확인
```


# Day 3 Trip CRUD / 사용자 권한 / 구글 및 카카오 SNS 로그인

## 오늘의 목표
- trip CURD 완성
- 로그인 사용자별 소유권 관리 및 다른 사용자의 trip 접근 차단 테스트
- google oauth 및 kakao oauth 로그인
- sns 로그인 계정을 social_account 테이블과 연결
- google / kakao 로그인 후에도 trip planner 자체 JWT 발급

## Google SNS 로그인

### Google OAuth 설정

Google Cloud에서 OAuth Client를 생성했다.

```text
Application Type: Web application
Redirect URI: http://localhost:8000/auth/google/callback
```
Client Secret은 외부에 노출하면 안 되므로 `.env`에 저장한다.

### httpx 설치

```powershell
pip install httpx
```

`httpx`를 이용해 OAuth 서버에 토큰 요청과 사용자 정보 요청을 보낸다.

---

### Google OAuth Service

파일:

```text
backend/services/google_oauth.py
```

주요 함수:

```python
get_google_login_url()
get_google_access_token(code)
get_google_user_info(access_token)
```

전체 흐름:

```text
/auth/google/login
        ↓
Google 로그인 페이지
        ↓
authorization code
        ↓
/auth/google/callback
        ↓
Google access token
        ↓
Google 사용자 정보
        ↓
social_accounts 확인
        ↓
User 생성 또는 기존 User 연결
        ↓
Trip Planner JWT 발급
```

최종적으로 Google 토큰을 직접 사용하는 것이 아니라:

```python
create_access_token(user.id)
```

으로 Trip Planner 자체 JWT를 발급한다.


# Kakao SNS 로그인

## Kakao Developers 설정

사용한 값:

```text
REST API Key
Client Secret
Redirect URI
```
Client Secret은 외부에 노출하면 안 되므로 `.env`에 저장한다.

Redirect URI:

```text
http://localhost:8000/auth/kakao/callback
```

---

## Kakao OAuth Service

파일:

```text
backend/services/kakao_oauth.py
```

주요 함수:

```python
get_kakao_login_url()
get_kakao_access_token(code)
get_kakao_user_info(access_token)
```

흐름:

```text
카카오 로그인
      ↓
authorization code
      ↓
Kakao Token API
      ↓
Kakao access token
      ↓
Kakao UserInfo API
      ↓
Kakao 사용자 ID
```

로그인 API:

```text
GET /auth/kakao/login
GET /auth/kakao/callback
```

---

## 9. 카카오 이메일 권한 문제

처음에는 카카오 계정 이메일을 사용하려 했다.

```python
kakao_account = kakao_user.get("kakao_account", {})
email = kakao_account.get("email")
```

하지만 현재 앱에서는 이메일 동의항목이 `권한 없음` 상태여서 이메일을 받을 수 없었다.

따라서 이메일 없이 카카오 고유 ID를 사용하도록 변경했다.

```python
provider_user_id = str(kakao_user["id"])
```

`social_accounts`:

```text
provider = "kakao"
provider_user_id = Kakao 사용자 고유 ID
```

---

## users.email nullable 처리

카카오 로그인에서 이메일을 받지 못할 수 있으므로:

기존:

```python
email: Mapped[str] = mapped_column(
    String(255),
    unique=True,
    nullable=False,
    index=True,
)
```

변경:

```python
email: Mapped[str | None] = mapped_column(
    String(255),
    unique=True,
    nullable=True,
    index=True,
)
```

`UserResponse`도:

```python
email: EmailStr | None
```

로 변경한다.

일반 회원가입의 `UserCreate`에서는 여전히 이메일을 필수로 유지한다.

---

## SocialAccount의 역할

```text
users
   │
   └── social_accounts
```

Google:

```text
provider = "google"
provider_user_id = Google sub
```

Kakao:

```text
provider = "kakao"
provider_user_id = Kakao user id
```

외부 로그인 공급자가 달라도 최종적으로 모두 하나의 `User`와 연결한다.

---

# 오늘 완성된 로그인 구조

```text
                Trip Planner

       ┌────────────┼────────────┐
       │            │            │
       ▼            ▼            ▼

 Email Login    Google Login   Kakao Login
       │            │            │
       ▼            ▼            ▼

 password       Google sub     Kakao ID
       │            │            │
       └────────────┼────────────┘
                    │
                    ▼

                   User
                    │
                    ▼

          Trip Planner JWT 발급
                    │
                    ▼

            get_current_user()
                    │
                    ▼

          보호된 API 사용 가능
                    │
                    ▼

                 /trips
```

로그인 방법은 달라도 최종 인증 방식은 모두 Trip Planner JWT로 통일된다.

---

# 보안 및 추후 개선사항

현재 Google 로그인에서 `state`를 생성하지만 callback에서 실제 검증하는 부분은 추후 보강이 필요하다.

OAuth `state`는 로그인 요청과 callback 요청이 같은 흐름인지 확인하고 CSRF 공격 방어에 사용한다.

개발 중 사용한 디버깅 출력:

```python
print("KAKAO STATUS:", response.status_code)
print("KAKAO ERROR:", response.text)
```

은 운영 전 제거한다.

`.env`에 포함되는 비밀 정보는 GitHub에 올리지 않는다.

```text
DATABASE_URL
SMTP_PASSWORD
JWT_SECRET_KEY
GOOGLE_CLIENT_SECRET
KAKAO_CLIENT_SECRET
```

`.gitignore`:

```gitignore
.env
venv/
__pycache__/
.pytest_cache/
```

---

# TripCS - Day 4

## 오늘 목표

오늘은 여행 일정의 상세 구조를 만들었다.

전체 구조:

User
↓
Trip
↓
TripDay
↓
Schedule

즉 하나의 여행 안에 여러 날짜가 있고,
각 날짜 안에 여러 일정이 들어가는 구조다.

오늘 구현한 핵심 기능:

- `TripDay` 모델 및 API
- `Schedule` 모델 및 CRUD API
- TripDay 날짜 범위 검증
- 같은 Trip 안에서 `day_number` 중복 방지
- Schedule `start_time`을 문자열에서 PostgreSQL `TIME` 타입으로 변경
- Schedule 순서 재정렬 API
- Trip 상세 조회 시 Day + Schedule까지 한 번에 반환
- `joinedload()`를 이용한 관계 데이터 조회
- 주요 오류 해결 및 Alembic migration 수정

## 1. TripDay / Schedule 모델 추가

TripDay는 여행의 하루를 의미한다.

예:

Trip: 오사카 여행

- Day 1: 2026-10-05
- Day 2: 2026-10-06
- Day 3: 2026-10-07


Schedule은 각 날짜 안의 실제 일정을 의미한다.

예:

Day 1

- 09:00 오사카성
- 12:00 점심
- 15:00 도톤보리


## 2. 관계 구조

Trip

```python
days: Mapped[list["TripDay"]] = relationship(
    back_populates="trip",
    cascade="all, delete-orphan",
)
```

## 3. TripDay API

구현한 API:

```text
POST   /trips/{trip_id}/days
GET    /trips/{trip_id}/days
PUT    /trips/{trip_id}/days/{trip_day_id}
DELETE /trips/{trip_id}/days/{trip_day_id}
```

## 4. TripDay 날짜 검증

TripDay 날짜는 반드시 Trip의 시작일과 종료일 사이에 있어야 한다.

```python
if not (
    trip.start_date <= trip_day.date <= trip.end_date
):
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Trip day date must be within trip dates",
    )
```

## 5. Schedule CRUD

구현한 Schedule API:

```text
POST   /trip-days/{trip_day_id}/schedules
GET    /trip-days/{trip_day_id}/schedules
GET    /trip-days/{trip_day_id}/schedules/{schedule_id}
PUT    /trip-days/{trip_day_id}/schedules/{schedule_id}
DELETE /trip-days/{trip_day_id}/schedules/{schedule_id}
```

## 6. schedule_map

Schedule을 ID 기준으로 빠르게 찾기 위해 dictionary를 만들었다.

```python
schedule_map = {
    schedule.id: schedule
    for schedule in schedules
}
```
예:

```python
{
    1: Schedule(...),
    2: Schedule(...),
    3: Schedule(...),
}
```

이후:

```python
schedule = schedule_map[item.schedule_id]
```

처럼 바로 접근할 수 있다.


---

## 7. Trip 상세 전체 조회

기존에는 데이터를 여러 번 요청해야 했다.

```text
GET /trips/{trip_id}
GET /trips/{trip_id}/days
GET /trip-days/{trip_day_id}/schedules
```

이제는:

```text
GET /trips/{trip_id}/detail
```

한 번으로 다음 구조를 받을 수 있다.

```text
Trip
├── Day 1
│   ├── Schedule
│   └── Schedule
└── Day 2
    └── Schedule
```

---

## 8. N+1 문제

연관 데이터를 하나씩 접근할 때 추가 SQL이 반복 실행될 수 있다.

예:

```text
Trip 조회
→ Day 조회
→ Day마다 Schedule 조회
→ Schedule 조회 반복
```

이런 문제를 N+1 문제라고 한다.

이번에는 `joinedload()`를 사용해서 관련 데이터를 함께 로딩하도록 했다.


---

## 9. Day / Schedule 정렬

Day는 `day_number` 기준으로 정렬했다.

```python
trip.days.sort(
    key=lambda day: day.day_number
)
```

Schedule은 `order_index` 기준으로 정렬했다.

```python
for day in trip.days:
    day.schedules.sort(
        key=lambda schedule: schedule.order_index
    )
```


---

# TripCS - Day5

## 오늘의 목표

Day 5에서는 Trip과 TripDay의 자동 동기화, Schedule 정렬 개선, 권한 검사 리팩토링, reorder 검증 강화를 진행했다.

오늘 구현한 핵심 기능:

- Trip 생성 시 TripDay 자동 생성
- Trip 수정 시 TripDay 자동 추가/삭제
- Schedule 정렬 기준 개선
- ownership helper 분리
- `get_owned_trip()`
- `get_owned_trip_day()`
- `get_owned_schedule()`
- reorder 요청 검증 강화
- 중복 `schedule_id` 방지
- 중복 `order_index` 방지
- 음수 `order_index` 방지

---


## 1. Ownership 코드 리팩토링

반복되는 소유권 검사를 다음 파일로 분리했다.

```text
backend/dependencies/ownership.py
```

### get_owned_trip()

```python
def get_owned_trip(
    db: Session,
    trip_id: int,
    user_id: int,
) -> Trip:
    trip = (
        db.query(Trip)
        .filter(
            Trip.id == trip_id,
            Trip.user_id == user_id,
        )
        .first()
    )

    if not trip:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trip not found",
        )

    return trip
```

### get_owned_trip_day()

```python
def get_owned_trip_day(
    db: Session,
    trip_day_id: int,
    user_id: int,
) -> TripDay:
    trip_day = (
        db.query(TripDay)
        .join(Trip)
        .filter(
            TripDay.id == trip_day_id,
            Trip.user_id == user_id,
        )
        .first()
    )

    if not trip_day:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trip day not found",
        )

    return trip_day
```

### get_owned_schedule()

```python
def get_owned_schedule(
    db: Session,
    trip_day_id: int,
    schedule_id: int,
    user_id: int,
) -> Schedule:
    schedule = (
        db.query(Schedule)
        .join(TripDay)
        .join(Trip)
        .filter(
            Schedule.id == schedule_id,
            Schedule.trip_day_id == trip_day_id,
            Trip.user_id == user_id,
        )
        .first()
    )

    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Schedule not found",
        )

    return schedule
```

리팩토링 장점:

- 코드 중복 감소
- 권한 검사 로직 통합
- 라우터 가독성 향상
- 유지보수성 개선

---

## 2. Schedule reorder 검증 강화

다음 검증을 추가했다.

```text
중복 schedule_id
중복 order_index
음수 order_index
잘못된 schedule_id
```

### 음수 order_index 방지

```python
from pydantic import BaseModel, Field
```

```python
class ScheduleOrderItem(BaseModel):
    schedule_id: int
    order_index: int = Field(ge=0)
```

`ge=0`은 0 이상만 허용한다는 뜻이다.

### schedule_id 중복 검사

```python
schedule_ids = [
    item.schedule_id
    for item in request.schedules
]

if len(schedule_ids) != len(set(schedule_ids)):
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Duplicate schedule_id is not allowed",
    )
```

### order_index 중복 검사

```python
order_indexes = [
    item.order_index
    for item in request.schedules
]

if len(order_indexes) != len(set(order_indexes)):
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Duplicate order_index is not allowed",
    )
```

### 현재 TripDay에 속한 Schedule인지 검증

```python
schedules = (
    db.query(Schedule)
    .filter(
        Schedule.trip_day_id == trip_day.id,
        Schedule.id.in_(schedule_ids),
    )
    .all()
)

if len(schedules) != len(schedule_ids):
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="One or more schedules are invalid",
    )
```

---

# TripCS - Day 6

## 1. 오늘 목표

Day 6에서는 기존에 잘 동작하던 기능을 더 유지보수하기 좋은 구조로 리팩토링하고,
입력 검증과 트랜잭션 처리를 강화했다.

핵심 목표:

```text
Router
↓
Ownership
↓
Service
↓
DB
```

그리고 입력 검증은 Schema가 담당하도록 역할을 분리했다.

```text
Schema
↓
입력값 검증
```

오늘 구현한 핵심 내용:

- Trip 비즈니스 로직을 `services/trip.py`로 분리
- Schedule 비즈니스 로직을 `services/schedule.py`로 분리
- Router를 얇게 정리
- Service에서 `commit / rollback` 처리
- `db.flush()`를 이용한 하나의 트랜잭션 처리
- Trip / TripDay / Schedule Schema 검증 강화
- 공백 문자열 방지
- 길이 제한
- 양수 / 0 이상 숫자 검증
- reorder 빈 리스트 방지
- HTTP 상태 코드 기준 정리


---

## 2. Router와 Service 역할 분리

기존에는 Router 안에서 다음 작업을 모두 처리했다.

```text
요청 받기
인증
소유권 검사
비즈니스 로직
DB 생성/수정/삭제
commit
rollback
응답
```

Day 6부터는 역할을 분리했다.

### Router 역할

```text
요청 받기
↓
로그인 사용자 확인
↓
Ownership 확인
↓
Service 호출
↓
응답 반환
```

### Service 역할

```text
비즈니스 로직
↓
DB 변경
↓
commit
↓
실패 시 rollback
```

이 구조로 변경하면서 Router 코드가 훨씬 짧고 읽기 쉬워졌다.


---

## 3. Trip Service 구조

파일:

```text
backend/services/trip.py
```

현재 주요 함수:

```text
create_trip_with_days()
update_trip_with_days()
delete_trip_service()
```
---

## 3. db.flush()를 사용하는 이유

기존에는 Trip 생성 직후 `commit()`을 하고 TripDay를 만들 수 있었다.

하지만 그렇게 하면:

```text
Trip commit 성공
↓
TripDay 생성 중 실패
```

상황에서 Trip만 DB에 남을 수 있다.

그래서 Day 6에서는:

```python
db.add(new_trip)
db.flush()
```

를 사용했다.

`flush()`는:

```text
INSERT 내용을 DB에 보내서 new_trip.id 확보
하지만 아직 transaction 확정은 아님
```

상태다.

이후 TripDay까지 전부 만든 뒤:

```python
db.commit()
```

을 한 번만 실행한다.

즉:

```text
Trip 생성
+
TripDay 생성
=
하나의 transaction
```


---

---

## 4. Schedule Service 분리

파일:

```text
backend/services/schedule.py
```

주요 함수:

```text
create_schedule_service()
update_schedule_service()
delete_schedule_service()
reorder_schedules_service()
```


---


# TripCS - Day 7

## 1. 오늘 목표

Day 7에서는 Swagger로 직접 확인하던 기능 테스트를 `pytest`로 자동화했다.

핵심 흐름:

```text
기능 구현
↓
pytest 실행
↓
기존 기능이 깨졌는지 자동 확인
```

오늘 테스트한 범위:

- 인증 없이 `/trips` 접근
- 회원가입 / 로그인 / JWT
- Trip 생성
- TripDay 자동 생성
- Trip 수정 시 TripDay 증가 / 감소
- Schedule 생성 / 수정 / 삭제
- Schedule reorder
- Pydantic validation
- Ownership
- Trip validation

---

## 2. 테스트 폴더 구조

```text
trip_planner/
├── backend/
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_auth.py
│   ├── test_trip.py
│   ├── test_schedule.py
│   └── test_ownership.py
└── ...
```
pytest 자동 탐색 기본 규칙:

```text
파일 → test_*.py
함수 → test_...
```

---

## 3. conftest.py 역할

`conftest.py`는 여러 테스트에서 공통으로 사용하는 fixture를 정의하는 파일이다.

주요 역할:

```text
테스트용 DB 준비
↓
FastAPI DB 의존성 교체
↓
TestClient 준비
↓
테스트마다 DB 초기화
↓
인증된 사용자 준비
```

## 4. 테스트용 SQLite DB

실제 TripCS는 PostgreSQL을 사용하지만 테스트에서는 SQLite를 사용했다.

```python
TEST_DATABASE_URL = "sqlite://"
```

테스트 DB를 분리하는 이유:

- 실제 데이터 보호
- 테스트 속도 향상
- 테스트마다 DB 초기화하기 쉬움

---

## 5. 테스트 DB Engine

```python
engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={
        "check_same_thread": False
    },
    poolclass=StaticPool,
)
```

`check_same_thread=False`는 FastAPI `TestClient`가 다른 thread에서 요청을 처리할 수 있기 때문에 SQLite 연결을 다른 thread에서도 사용할 수 있도록 허용한다.

`StaticPool`은 메모리 SQLite 연결을 테스트 중 계속 재사용하도록 한다.

---

## 6. TestingSessionLocal

```python
TestingSessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)
```

실제 DB의 `SessionLocal` 대신 테스트에서 사용할 세션 생성기다.

---

## 7. FastAPI DB Dependency Override

실제 API:

```python
db: Session = Depends(get_db)
```

테스트에서는:

```python
app.dependency_overrides[get_db] = override_get_db
```

로 교체했다.

```text
실제 서버
Depends(get_db)
↓
PostgreSQL
```

```text
pytest
Depends(get_db)
↓
override_get_db()
↓
SQLite 테스트 DB
```

---

## 8. TestClient

```python
@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client
```

Swagger 대신 Python 코드에서 API를 호출할 수 있다.

예:

```python
response = client.get("/trips")
```

---

## 9. fixture란?

pytest fixture는 테스트에서 반복적으로 필요한 준비물을 제공한다.

예:

```python
@pytest.fixture
def client():
    ...
```

테스트에서는:

```python
def test_something(client):
```

처럼 매개변수 이름만 작성하면 pytest가 자동으로 fixture를 넣어준다.

---

## 10. 테스트마다 DB 초기화

중복 이메일 문제를 해결하기 위해 테스트마다 DB를 초기화했다.

```python
@pytest.fixture(autouse=True)
def reset_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    yield

    Base.metadata.drop_all(bind=engine)
```

`autouse=True`는 모든 테스트에 자동 적용된다는 뜻이다.

```text
테스트 시작
↓
DB 초기화
↓
테스트 실행
↓
테스트 종료
↓
DB 삭제
```

이 덕분에 테스트끼리 데이터가 서로 영향을 주지 않는다.

---


# TripCS - Day 8

## 1. 오늘 목표

Day 8에서는 새 기능 추가보다 기존 코드의 기술부채와 warning을 정리하고 테스트 구조를 개선했다.

핵심 작업:

- Pydantic v2 deprecated warning 제거
- `datetime.utcnow()` warning 제거
- `utc_now()` 공통 유틸 추가
- 이메일 인증코드 2번 생성 버그 수정
- 테스트 fixture 중복 제거
- `auth_headers` / `second_auth_headers` 최적화
- 테스트 속도 개선
- 전체 회귀 테스트 확인
- 최종 `23 passed, 1 warning`

---

## 2. Pydantic v2 warning 정리

기존:

```python
class Config:
    from_attributes = True
```

변경:

```python
model_config = {
    "from_attributes": True
}
```

Pydantic v2에서는 `class Config` 방식보다 `model_config` 사용을 권장한다.

---

## 3. datetime.utcnow() warning 정리

Python 3.14에서:

```python
datetime.utcnow()
```

사용 시 deprecation warning이 발생했다.

그래서 공통 시간 유틸을 만들었다.

파일:

```text
backend/utils/time.py
```

```python
from datetime import UTC, datetime


def utc_now() -> datetime:
    return datetime.now(UTC).replace(tzinfo=None)
```

현재 DB의 `DateTime` 컬럼이 timezone 없는 구조이므로,
UTC 기준 시간을 만든 뒤 timezone 정보만 제거해서 기존 구조와 맞췄다.

---

## 4. SQLAlchemy default 변경

기존:

```python
default=datetime.utcnow
```

변경:

```python
default=utc_now
```

중요:

```python
default=utc_now
```

처럼 함수 자체를 넘겨야 한다.

```python
default=utc_now()
```

처럼 괄호를 붙이면 import 시점에 바로 실행될 수 있다.

---

## 5. 이메일 인증 만료시간도 변경

기존:

```python
expires_at=datetime.utcnow() + timedelta(minutes=10)
```

변경:

```python
expires_at=utc_now() + timedelta(minutes=10)
```

만료 검사:

```python
if verification.expires_at < utc_now():
    return False
```

인증 성공 시간:

```python
verification.verified_at = utc_now()
```

---

## 6. 이메일 인증코드 2번 생성 버그

회원가입 한 번에 인증코드가 두 번 생성되는 문제가 있었다.

원인:

```text
register_user()
↓
create_user()
    ↓
    create_verification_code()  ← 1번

register_user()
↓
create_verification_code()      ← 2번
```

즉 `services/user.py`와 `routers/user.py` 양쪽에서 인증코드를 생성하고 있었다.

---

## 7. create_user() 역할 정리

`create_user()`는 사용자 생성만 담당하도록 변경했다.

최종 역할:

```text
이메일 중복 확인
↓
비밀번호 hash
↓
User 생성
↓
commit
↓
User 반환
```

인증코드 생성과 이메일 발송은 회원가입 Router에서 한 번만 수행하도록 정리했다.

---

## 8. 최종 회원가입 흐름

```text
POST /users
↓
create_user()
↓
User 생성
↓
create_verification_code()
↓
send_verification_email()
↓
완료
```

인증코드는 이제 한 번만 생성된다.

---
## 9. 테스트 warning 정리 결과

기존에는 Pydantic / datetime 관련 warning이 많이 발생했다.

정리 후:

```text
23 passed
1 warning
```

남은 warning:

```text
StarletteDeprecationWarning:
Using httpx with starlette.testclient is deprecated
```

현재 TripCS 로직 문제는 아니고 TestClient 의존성 관련 warning이므로 known warning으로 남겨두었다.

---

## 10. 기존 테스트 fixture 문제

기존 `auth_headers`는 테스트마다 실제 회원가입과 로그인을 수행했다.

흐름:

```text
회원가입 API
↓
bcrypt hash
↓
인증코드 생성
↓
이메일 발송
↓
email_verified=True
↓
로그인 API
↓
비밀번호 검증
↓
JWT
```

Trip / Schedule 테스트마다 이 과정을 반복하면서 테스트 속도가 느려졌다.

---

## 11. 테스트 목적 분리

```text
test_auth.py
→ 실제 인증 기능 테스트

test_trip.py
test_schedule.py
test_ownership.py
→ 인증된 상태만 필요
```

따라서 인증 기능 자체는 `test_auth.py`에서 실제 흐름으로 테스트하고,
다른 테스트는 빠르게 인증 상태만 준비하도록 변경했다.

---
## 12. Day 8 핵심 개념

오늘 배운 내용:

- deprecated warning 정리
- Pydantic v2 설정 방식
- `datetime.now(UTC)`
- 공통 시간 유틸
- SQLAlchemy default callable
- 중복 호출 디버깅
- 함수 역할 분리
- 테스트 fixture 최적화
- 테스트 helper 분리
- 테스트 목적 분리
- 테스트 속도 개선
- 회귀 테스트

---

# TripCS Day 9 - Place 기능과 Schedule 연결

## 1. 오늘 목표

Day 9에서는 여행 일정에 실제 장소 정보를 연결할 수 있도록 `Place` 기능을 추가했다.

- `Place` 모델 추가
- 장소 검색 API 추가
- 장소 저장 API 추가
- `Schedule`과 `Place` 연결
- `ScheduleResponse`에서 `place_info` 반환
- 잘못된 `place_id` 검증
- Alembic migration 적용
- Place/Schedule 연결 테스트 작성
- 전체 테스트 통과 확인

## 2. Place 모델

`backend/models.py`

```python
class Place(Base):
    __tablename__ = "places"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    address: Mapped[str | None] = mapped_column(String(300), nullable=True)
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    category: Mapped[str | None] = mapped_column(String(100), nullable=True)

    external_place_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=utc_now,
        nullable=False,
    )
```

## 3. Schedule과 Place 연결

기존 `Schedule.place` 문자열 필드는 유지하고, 새로 `place_id`를 추가했다.

```python
place_id: Mapped[int | None] = mapped_column(
    ForeignKey("places.id"),
    nullable=True,
    index=True,
)

place_info: Mapped["Place | None"] = relationship()
```

구조:

```text
Schedule
├── place        # 기존 문자열 장소명
├── place_id     # places.id FK
└── place_info   # 실제 Place 객체
```
## 4. Place Schema

`backend/schemas/place.py`

```python
class PlaceCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    address: str | None = Field(default=None, max_length=300)
    latitude: float | None = None
    longitude: float | None = None
    category: str | None = Field(default=None, max_length=100)
    external_place_id: str | None = Field(default=None, max_length=255)


class PlaceResponse(BaseModel):
    id: int
    name: str
    address: str | None
    latitude: float | None
    longitude: float | None
    category: str | None
    external_place_id: str | None
    created_at: datetime

    model_config = {"from_attributes": True}
```

## 5. Place 검색/저장 API

현재 실제 지도 API 연동 전 단계라 dummy 검색 데이터를 사용한다.

```text
GET  /places/search
POST /places
```

검색 흐름:

```text
사용자 검색
↓
GET /places/search
↓
dummy 결과 반환
↓
사용자가 장소 선택
↓
POST /places
↓
DB 저장
```

같은 `external_place_id`가 이미 존재하면 새 Place를 만들지 않고 기존 데이터를 재사용한다.

## 6. Schedule Schema에 place_id 추가

`ScheduleCreate`, `ScheduleUpdate`에 추가:

```python
place_id: int | None = Field(
    default=None,
    gt=0,
)
```

처음에는 `ScheduleCreate`가 파일 안에 두 번 정의되어 있었기 때문에 중복 정의를 제거하고 하나로 정리했다.

## 7. ScheduleResponse에 place_info 추가

```python
class ScheduleResponse(BaseModel):
    id: int
    trip_day_id: int
    title: str
    start_time: time | None
    place: str | None
    place_id: int | None
    place_info: PlaceResponse | None
    memo: str | None
    order_index: int
    created_at: datetime

    model_config = {"from_attributes": True}
```

응답 예시:

```json
{
  "id": 1,
  "trip_day_id": 7,
  "title": "오사카성 관광",
  "place": "오사카성",
  "place_id": 1,
  "place_info": {
    "id": 1,
    "name": "오사카성",
    "address": "1-1 Osakajo, Chuo Ward, Osaka",
    "latitude": 34.6873,
    "longitude": 135.5262,
    "category": "관광지",
    "external_place_id": "test-osaka-castle"
  }
}
```

## 8. place_id 검증

Schedule 생성/수정 시 실제 Place가 존재하는지 확인한다.

```python
if schedule_data.place_id is not None:
    place = (
        db.query(Place)
        .filter(Place.id == schedule_data.place_id)
        .first()
    )

    if not place:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid place_id",
        )
```

없는 Place id를 넣으면:

```text
400 Bad Request
Invalid place_id
```

를 반환한다.

# TripCS Day 10 - Google Places API (New) 연동

## 1. 오늘 목표

Day 10에서는 Day 9에서 만든 dummy 장소 검색을 실제 Google Places API (New)로 교체했다.

오늘 핵심 목표:

```text
dummy 장소 검색
→ 실제 Google Places 검색
```

완료한 작업:

- 기존 Google Cloud 프로젝트 `tipplanner` 사용
- Google 로그인용 OAuth 자격증명과 Places API Key 구분
- Places API (New) 활성화
- API Key 발급 및 제한 설정
- `.env`에 Places API Key 저장
- Google Places Text Search API 연동
- Google 응답을 `PlaceSearchResult`로 변환
- 500 / 502 / 403 / 400 에러 디버깅
- 실제 검색 200 응답 확인
- 외부 API 호출 테스트를 mock으로 교체
- 전체 pytest 통과

---

## 2. Google OAuth와 Places API Key 차이

기존 Google 로그인에서 사용하던 값:

```env
GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...
```

이 값들은 Google OAuth 로그인용이다.

```text
Google 로그인
→ OAuth
→ 사용자 인증
```

Places API는 별도의 API Key를 사용한다.

```env
GOOGLE_PLACES_API_KEY=...
```

즉 구조는 다음과 같다.

```text
tipplanner Google Cloud Project
├── OAuth Client ID / Secret
│   └── Google 로그인용
│
└── API Key
    └── Google Places API용
```

프로젝트는 같이 사용해도 되지만 자격증명 용도는 다르다.

---

## 3. .env 설정

프로젝트 루트의 `.env`에 추가:

```env
GOOGLE_PLACES_API_KEY=실제_API_KEY
```

API Key를 코드에 직접 작성하면 안 된다.

```python
import os

GOOGLE_PLACES_API_KEY = os.getenv(
    "GOOGLE_PLACES_API_KEY"
)
```

`.env` 수정 후에는 서버를 재시작한다.

```bash
Ctrl + C
uvicorn backend.main:app --reload
```

---

## 4. Google Places Text Search API

사용한 엔드포인트:

```text
POST https://places.googleapis.com/v1/places:searchText
```

Request Header:

```text
Content-Type: application/json
X-Goog-Api-Key: GOOGLE_PLACES_API_KEY
X-Goog-FieldMask:
    places.id,
    places.displayName,
    places.formattedAddress,
    places.location,
    places.primaryType
```

Request Body:

```json
{
  "textQuery": "오사카성"
}
```

---

## 5. Google 응답 → TripCS 데이터 매핑

```text
places.id
→ external_place_id

places.displayName.text
→ name

places.formattedAddress
→ address

places.location.latitude
→ latitude

places.location.longitude
→ longitude

places.primaryType
→ category
```

기존 `PlaceSearchResult` 구조를 그대로 활용했다.

---
## 6. 현재 검색 흐름

```text
사용자
↓
GET /places/search?query=오사카성
↓
TripCS
↓
search_places_service()
↓
Google Places Text Search
↓
PlaceSearchResult 변환
↓
검색 결과 반환
```

장소 선택 이후:

```text
POST /places
↓
Place DB 저장
↓
place_id 획득
↓
Schedule.place_id 연결
↓
Trip detail
↓
place_info 반환
```

---

## 7. 외부 API 테스트는 Mock 사용

테스트마다 실제 Google을 호출하면:

```text
느려짐
네트워크 영향
API Key 필요
쿼터/비용 영향
외부 장애 영향
```

이 생길 수 있다.

그래서:

```python
@patch(
    "backend.services.place.httpx.post"
)
```

를 사용해 실제 HTTP 요청 대신 가짜 Google 응답을 반환하도록 했다.

예시:

```python
mock_post.return_value.json.return_value = {
    "places": [
        {
            "id": "ChIJ_test_osaka_castle",
            "formattedAddress": (
                "1-1 Osakajo, Chuo Ward, Osaka, Japan"
            ),
            "location": {
                "latitude": 34.6872571,
                "longitude": 135.5258546,
            },
            "displayName": {
                "text": "Osaka Castle",
                "languageCode": "en",
            },
            "primaryType": "castle",
        }
    ]
}

mock_post.return_value.raise_for_status.return_value = None
```

---

## 8. API Key도 테스트용으로 Patch

테스트 환경에서 실제 API Key가 없어도 되도록:

```python
from backend.services import place as place_service


with patch.object(
    place_service,
    "GOOGLE_PLACES_API_KEY",
    "test-api-key",
):
    response = client.get(
        "/places/search",
        params={
            "query": "오사카성",
        },
    )
```

로 처리했다.

즉 테스트에서는:

```text
실제 Google API 호출 X
실제 API Key X

mock 응답 O
test-api-key O
```

---

# TripCS Day 11 - Google Places 개선

## 1. 오늘 목표

Day 11에서는 Day 10에서 연결한 Google Places 검색을 실제 서비스에서 쓰기 더 좋게 다듬었다.

오늘 핵심 목표:

```text
Google Places 연결
→ 사용자 친화적인 장소 검색으로 개선
```

완료한 작업:

- 검색 결과 한국어 우선
- 검색 결과 최대 5개 제한
- 서버에서도 `[:5]`로 한 번 더 제한
- 선택적으로 latitude / longitude 받기
- `locationBias`로 특정 위치 주변 검색 우선
- 좌표가 없어도 기존 검색 유지
- locationBias 유무 테스트 추가
- Place 이름 공백 validation
- latitude / longitude 범위 validation
- validation 테스트 추가
- Trip detail에서 `place_info` eager loading
- 전체 pytest 통과

## 2. 한국어 우선 + 결과 5개 제한

```python
body = {
    "textQuery": query,
    "languageCode": "ko",
    "pageSize": 5,
}
```

그리고 서버에서도:

```python
places = data.get(
    "places",
    [],
)[:5]
```

로 한 번 더 제한했다.

## 3. 위치 기반 검색 준비

```python
def search_places_service(
    query: str,
    latitude: float | None = None,
    longitude: float | None = None,
) -> list[PlaceSearchResult]:
```

좌표가 둘 다 있으면:

```python
if latitude is not None and longitude is not None:
    body["locationBias"] = {
        "circle": {
            "center": {
                "latitude": latitude,
                "longitude": longitude,
            },
            "radius": 10000.0,
        }
    }
```

현재 반경은 10km다.

## 4. Router에서 좌표 받기

```python
@router.get(
    "/search",
    response_model=list[PlaceSearchResult],
)
def search_places(
    query: str = Query(
        min_length=1,
        max_length=100,
    ),
    latitude: float | None = Query(
        default=None,
        ge=-90,
        le=90,
    ),
    longitude: float | None = Query(
        default=None,
        ge=-180,
        le=180,
    ),
):
    return search_places_service(
        query=query,
        latitude=latitude,
        longitude=longitude,
    )
```

Swagger에서는 직접 좌표를 넣어 테스트하지만, 실제 서비스에서는 사용자가 좌표를 직접 입력하지 않는 방향으로 간다.

## 5. 실제 서비스 UX 방향

사용자는:

```text
스타벅스
```

만 검색한다.

프론트 또는 백엔드가 여행 목적지 기준 좌표를 자동으로 붙인다.

```text
query=스타벅스
latitude=34.6937
longitude=135.5023
```

Day 12에서는 이를 `trip_id` 기반으로 자동화하는 방향을 생각할 수 있다.


# TripCS Day 12 - trip_id 기반 장소 검색 자동화

## 1. 오늘 목표

Day 12에서는 사용자가 latitude / longitude를 직접 넣지 않아도
현재 여행의 목적지를 기준으로 장소를 검색할 수 있게 만들었다.

핵심 목표:

```text
query + trip_id
↓
Trip 소유권 확인
↓
Trip.destination 확인
↓
destination 좌표 조회
↓
locationBias 자동 적용
↓
Google Places 검색
```

---

## 2. 기존 방식의 한계

Day 11까지는 장소 검색 시 좌표를 직접 넣을 수 있었다.

```text
query=스타벅스
latitude=34.6937
longitude=135.5023
```

하지만 실제 서비스에서는 사용자가 좌표를 직접 입력하게 만들면 UX가 좋지 않다.

그래서 Day 12에서는 `trip_id`만 받아서 백엔드가 자동으로 목적지를 찾도록 개선했다.

---

## 3. /places/search에 trip_id 추가

`backend/routers/place.py`

핵심 구조:

```python
def search_places(
    query: str,
    trip_id: int | None = None,
    latitude: float | None = None,
    longitude: float | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    destination = None

    if trip_id is not None:
        trip = get_owned_trip(
            db=db,
            trip_id=trip_id,
            user_id=current_user.id,
        )

        destination = trip.destination

    return search_places_service(
        query=query,
        latitude=latitude,
        longitude=longitude,
        destination=destination,
    )
```

핵심은:

```text
trip_id
↓
get_owned_trip()
↓
내 Trip인지 확인
↓
trip.destination 확보
```

이다.

---

## 4. destination 파라미터 추가

`backend/services/place.py`

```python
def search_places_service(
    query: str,
    latitude: float | None = None,
    longitude: float | None = None,
    destination: str | None = None,
) -> list[PlaceSearchResult]:
```

이제 service는:

```text
직접 좌표
또는
Trip destination
```

둘 중 하나를 이용할 수 있다.

---

## 5. destination을 좌표로 변환

좌표가 없고 destination이 있으면 Google Places API로 목적지 좌표를 먼저 조회한다.

```python
if (
    destination
    and latitude is None
    and longitude is None
):
    destination_body = {
        "textQuery": destination,
        "languageCode": "ko",
        "pageSize": 1,
    }
```

FieldMask는 좌표만 필요하기 때문에:

```python
"X-Goog-FieldMask": "places.location"
```

만 요청한다.

---

## 6. 1차 Google 호출

예:

```text
destination = 오사카
```

이면 먼저:

```text
Google Places
textQuery = 오사카
pageSize = 1
```

로 요청한다.

응답에서:

```python
latitude = destination_location.get(
    "latitude"
)

longitude = destination_location.get(
    "longitude"
)
```

로 좌표를 얻는다.

---

## 7. 2차 Google 호출

좌표를 얻은 뒤 실제 검색어를 다시 검색한다.

예:

```text
query = 스타벅스
```

최종 body:

```python
body = {
    "textQuery": query,
    "languageCode": "ko",
    "pageSize": 5,
}
```

좌표가 존재하면:

```python
body["locationBias"] = {
    "circle": {
        "center": {
            "latitude": latitude,
            "longitude": longitude,
        },
        "radius": 10000.0,
    }
}
```

를 넣는다.

---

## 8. 최종 동작 흐름

예:

```text
query = 스타벅스
trip_id = 3
```

백엔드:

```text
Trip 3 조회
↓
destination = 오사카
↓
Google Places에서 오사카 검색
↓
오사카 좌표 확보
↓
locationBias 10km 적용
↓
스타벅스 검색
↓
오사카 근처 스타벅스 최대 5개 반환
```

---

## 9. 실제 동작 확인

처음 테스트에서는 Trip.destination이 의미 없는 `"string"` 값이라
의정부 주변 검색 결과가 나왔다.

이후 destination을:

```text
오사카
```

로 저장한 Trip으로 다시 검색하자:

```text
스타벅스 커피 사쿠라바시 플라자 빌딩점
스타벅스 커피 히고바시 미나미점
스타벅스 다이마루 우메다
...
```

처럼 오사카 주변 결과가 정상적으로 반환되었다.

즉 `trip_id → destination → 좌표 → locationBias` 흐름이 제대로 작동함을 확인했다.

---

## 10. destination을 못 찾았을 때 fallback

destination 검색 결과가 비어 있으면:

```python
destination_places = []
```

가 된다.

이 경우 latitude / longitude가 설정되지 않기 때문에
`locationBias` 없이 일반 장소 검색으로 넘어간다.

즉:

```text
목적지 좌표 찾음
→ 위치 기반 검색

목적지 좌표 못 찾음
→ 일반 검색 fallback
```

이다.

---
# Day 12 완료

Day 12에서 TripCS의 장소 검색이
단순 키워드 검색에서 여행 컨텍스트를 이해하는 검색으로 발전했다.

```text
스타벅스
```

라는 같은 검색어도:

```text
오사카 Trip
→ 오사카 스타벅스

서울 Trip
→ 서울 스타벅스
```

처럼 현재 여행 목적지에 맞는 결과를 우선해서 반환할 수 있게 되었다.


# TripCS — Day 13 학습 README

## 오늘의 목표

Trip 생성 시 여행 목적지 좌표를 조회해서 DB에 저장하고, 이후 장소 검색에서는 저장된 좌표를 재사용한다.

- Day12: 장소 검색 1회당 Google Places API 호출 2회 (목적지 좌표 조회 + 장소 검색)
- Day13: 좌표가 저장된 Trip의 장소 검색 1회당 Google Places API 호출 1회 (장소 검색만)

## 1. Trip 모델과 DB 변경

Trip 모델에 다음 두 필드를 추가했다.

```python
destination_latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
destination_longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
```

Alembic으로 마이그레이션을 만들고 적용했다.

```bash
alembic revision --autogenerate -m "add destination coordinates to trips"
alembic upgrade head
```

모델 코드 변경만으로 실제 DB 테이블이 바뀌지는 않으므로 마이그레이션이 필요하다.

TripResponse에도 두 좌표 필드를 추가해 API 응답에서 확인할 수 있게 했다.

## 2. 목적지 좌표 조회 함수 분리

`backend/services/place.py`에 `resolve_destination_coordinates(destination)`를 두었다.

Google Places Text Search에 목적지를 보내고, 첫 결과의 위치를 `(latitude, longitude)`로 반환한다.
결과가 없으면 `(None, None)`을 반환한다. 요청 오류는 502로 처리한다.

```python
latitude, longitude = resolve_destination_coordinates("오사카")
```

이 함수는 Trip 생성 및 목적지 변경 시 재사용한다.

## 3. Trip 생성 시 좌표 저장

`backend/services/trip.py`의 `create_trip_with_days()`에서 Trip을 만들기 전 목적지 좌표를 조회한다.

```python
latitude, longitude = resolve_destination_coordinates(trip_data.destination)

new_trip = Trip(
    user_id=current_user.id,
    title=trip_data.title,
    destination=trip_data.destination,
    destination_latitude=latitude,
    destination_longitude=longitude,
    start_date=trip_data.start_date,
    end_date=trip_data.end_date,
)
```

기존처럼 `db.flush()`로 Trip ID를 확보한 뒤 TripDay를 생성하고 커밋한다.
현재 구현에서는 Google API 조회 오류가 나면 Trip 생성도 실패할 수 있다.

## 4. Trip 수정 시 필요한 경우에만 재조회

```python
destination_changed = trip.destination != trip_data.destination

if destination_changed:
    latitude, longitude = resolve_destination_coordinates(trip_data.destination)
    trip.destination_latitude = latitude
    trip.destination_longitude = longitude
```

여행 제목이나 날짜만 변경하면 좌표 조회를 다시 하지 않는다.
목적지 자체가 변경되면 좌표도 함께 갱신한다.

## 5. 장소 검색 시 저장 좌표 사용

`backend/routers/place.py`에서 `trip_id`가 주어지면 소유권 검사 후 Trip에 저장된 좌표를 읽는다.

```python
trip = get_owned_trip(db=db, trip_id=trip_id, user_id=current_user.id)

if latitude is None and longitude is None:
    latitude = trip.destination_latitude
    longitude = trip.destination_longitude

return search_places_service(query=query, latitude=latitude, longitude=longitude)
```

`search_places_service()`에서는 더 이상 `destination` 문자열을 받아 좌표를 먼저 조회할 필요가 없다.
좌표가 둘 다 존재하면 `locationBias`를 추가해 실제 장소 검색을 수행한다.

## 6. 테스트에서 확인한 내용

- Trip 생성 시 반환된 좌표가 예상값과 일치하는가?
- `trip_id`로 장소 검색할 때 저장된 좌표가 `locationBias`에 들어가는가?
- Trip 생성 시 1회 + 장소 검색 시 1회 호출되며, 장소 검색 구간에서 추가 호출은 1회뿐인가?
- 목적지가 오사카에서 도쿄로 바뀌면 좌표가 갱신되는가?
- 제목·날짜만 바뀌면 Google API를 다시 호출하지 않는가?

테스트에서는 `unittest.mock.patch`로 Google API 호출을 모의 응답으로 대체했다.
최종 `pytest -v` 전체 테스트 통과를 확인했다.


# TripCS Day 14 - Google Places API 장애 대응 및 자동 재시도

## 1. 오늘 목표

Day 13에서는 `Trip` 생성 시 목적지 좌표를 DB에 저장해서 장소 검색 때마다 Google Places API를 두 번 호출하던 구조를 개선했다.

Day 14에서는 **외부 API가 일시적으로 실패해도 여행 생성·수정을 계속할 수 있도록** fallback을 적용하고, **일시적인 장애에 한해서 제한적으로 재시도**하도록 개선했다.

오늘 구현한 내용:

- Trip 생성 시 Google 좌표 조회에 실패해도 여행 데이터 저장
- Trip 목적지 수정 시 Google 좌표 조회 실패하면 새 목적지만 저장하고 이전 좌표는 `None`으로 초기화
- Google Places 요청·예외 처리 공통 함수 `request_google_places()` 분리
- HTTP 오류 / 타임아웃 / 연결 실패를 구분
- 429·5xx·Timeout에 최대 3회 재시도
- Exponential Backoff(0.2초 → 0.4초) 적용
- Mock과 `pytest.mark.parametrize`로 장애 상황 검증
- 전체 `pytest -v` 통과

---

## 2. 기존 구조의 문제

Day 13에서는 Trip 생성 시 Google Places에 목적지 좌표를 요청했다.

```text
Trip 생성 요청
    ↓
resolve_destination_coordinates("오사카")
    ↓
Google Places 장애 발생
    ↓
HTTPException 발생
    ↓
Trip 생성 실패
```

좌표 조회는 편의 기능이지만, 해당 기능의 장애가 핵심 기능인 **여행 생성 전체를 막는 문제**가 있었다.

오늘은 여행 생성과 외부 API 장애의 영향을 분리하는 방향으로 개선했다.

---

## 3. Trip 생성·수정 fallback

파일: `backend/services/trip.py`

반복되는 오류 처리 코드를 공통 함수로 분리했다.

```python
from fastapi import HTTPException
from backend.services.place import resolve_destination_coordinates


def get_destination_coordinates_with_fallback(
    destination: str,
) -> tuple[float | None, float | None]:
    try:
        return resolve_destination_coordinates(destination)

    except HTTPException as exc:
        if exc.status_code not in (502, 503, 504):
            raise

        return None, None
```

- 정상 응답 → `(latitude, longitude)` 반환
- 허용한 외부 API 오류(502·503·504) → `(None, None)` 반환
- 그 외 오류 → `raise`로 다시 전달

Trip 생성 함수에서 사용한다.

```python
destination_latitude, destination_longitude = (
    get_destination_coordinates_with_fallback(
        trip_data.destination
    )
)

new_trip = Trip(
    user_id=current_user.id,
    title=trip_data.title,
    destination=trip_data.destination,
    destination_latitude=destination_latitude,
    destination_longitude=destination_longitude,
    start_date=trip_data.start_date,
    end_date=trip_data.end_date,
)
```

이제 좌표 조회에 실패해도 기존 `db.flush()` → `TripDay` 생성 → `db.commit()` 흐름을 이어갈 수 있다.

### 목적지 변경 시 주의할 점

기존 오사카 여행을 도쿄로 바꾸는데 도쿄 좌표를 조회하지 못했다면, 예전 오사카 좌표를 유지하면 안 된다.

```python
destination_changed = (
    trip.destination != trip_data.destination
)

if destination_changed:
    destination_latitude, destination_longitude = (
        get_destination_coordinates_with_fallback(
            trip_data.destination
        )
    )

# 기존 DB 수정 흐름 안에서
trip.destination = trip_data.destination

if destination_changed:
    trip.destination_latitude = destination_latitude
    trip.destination_longitude = destination_longitude
```

좌표 조회가 실패하면 두 좌표가 `None`이므로, **새 목적지에 이전 목적지의 좌표가 잘못 남는 문제**를 피한다.

---

## 4. Google Places 요청 함수 공통화

파일: `backend/services/place.py`

기존에는 `resolve_destination_coordinates()`와 `search_places_service()`가 각각 `httpx.post()`와 예외 처리를 직접 수행했다.

```text
이전
resolve_destination_coordinates() → httpx.post() + 예외 처리
search_places_service()         → httpx.post() + 예외 처리

변경
resolve_destination_coordinates() ─┐
                                   ├→ request_google_places()
search_places_service() ───────────┘
```

공통 함수는 요청을 전송하고, 성공하면 JSON을 반환하고, 실패하면 상황에 맞는 `HTTPException`을 발생시킨다.

호출 예시:

```python
data = request_google_places(
    body={
        "textQuery": destination,
        "languageCode": "ko",
        "pageSize": 1,
    },
    field_mask="places.location",
)
```

이렇게 하면 공통 오류 처리 정책을 한 곳에서 관리할 수 있다.

---

## 5. HTTP 오류 구분

Google Places API 오류를 우리 API의 오류로 변환했다.

| Google/API 상황 | TripCS 응답 | 재시도 |
|---|---|---|
| 400, 403 등 일반 HTTP 오류 | 502 Bad Gateway | 없음 |
| 429 호출 제한 | 503 Service Unavailable | 최대 3회 |
| 500 이상 서버 오류 | 503 Service Unavailable | 최대 3회 |
| Timeout | 504 Gateway Timeout | 최대 3회 |
| 일반 연결 실패 (`RequestError`) | 502 Bad Gateway | 없음 |

핵심 예외 처리:

```python
except httpx.TimeoutException as exc:
    # 마지막 시도까지 실패하면 504
    ...

except httpx.HTTPStatusError as exc:
    google_status = exc.response.status_code
    if google_status == 429 or google_status >= 500:
        # 마지막 시도까지 실패하면 503
        ...
    else:
        # 400, 403 등은 즉시 502
        ...

except httpx.RequestError as exc:
    # 연결 실패는 즉시 502
    ...
```

`TimeoutException`은 `RequestError` 계열이므로 **더 구체적인 예외를 먼저 검사**한다.

> 주의: 현재 구현은 Google의 400·403도 502로 변환한다. 그 결과 Trip의 fallback 함수가 이 오류까지 허용하게 된다. 실제 운영에서는 API Key 설정·권한 문제와 일시적 장애를 별도로 구분하는 개선이 필요하다.

---

## 6. Retry와 Exponential Backoff

일시적 오류가 발생했을 때 최대 세 번 요청하도록 구성했다.

```python
import time

max_attempts = 3

for attempt in range(max_attempts):
    try:
        response = httpx.post(
            GOOGLE_PLACES_SEARCH_URL,
            headers=headers,
            json=body,
            timeout=10.0,
        )
        response.raise_for_status()
        return response.json()

    except httpx.TimeoutException as exc:
        if attempt == max_attempts - 1:
            raise HTTPException(
                status_code=504,
                detail="Google Places API timeout",
            ) from exc

    except httpx.HTTPStatusError as exc:
        google_status = exc.response.status_code

        if google_status == 429 or google_status >= 500:
            if attempt == max_attempts - 1:
                raise HTTPException(
                    status_code=503,
                    detail="Google Places API temporarily unavailable",
                ) from exc
        else:
            raise HTTPException(
                status_code=502,
                detail="Google Places API request failed",
            ) from exc

    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=502,
            detail="Google Places API connection failed",
        ) from exc

    time.sleep(0.2 * (2 ** attempt))
```

**최대 3회**는 최초 요청까지 포함한 횟수다.

```text
1번째 요청 실패 → 0.2초 대기
2번째 요청 실패 → 0.4초 대기
3번째 요청 실패 → 최종 오류 반환 (추가 대기 없음)
```

`0.2 * (2 ** attempt)`는 실패가 이어질수록 대기 시간을 늘리는 **지수 백오프** 계산식이다.

성공하면 `return response.json()`으로 루프를 즉시 종료하므로 불필요한 재요청을 하지 않는다.

---

## 7. Mock 테스트

파일:

```text
tests/test_trip.py
tests/test_place.py
```

실제 Google API를 호출하면 네트워크 상태, 쿼터, 비용 등에 영향을 받기 때문에 `unittest.mock.patch`를 사용했다.

### Trip 생성·수정 fallback 테스트

- `test_create_trip_when_google_api_fails`: 좌표 조회 502여도 Trip 생성 201, 좌표는 `None`
- `test_update_trip_when_google_api_fails`: 오사카 → 도쿄 수정 중 502여도 200, 목적지는 도쿄로 변경하고 좌표 초기화

### HTTP 오류 매개변수 테스트

```python
@pytest.mark.parametrize(
    "google_status, expected_status, expected_calls",
    [
        (400, 502, 1),
        (403, 502, 1),
        (429, 503, 3),
        (500, 503, 3),
        (503, 503, 3),
    ],
)
```

`parametrize`를 사용하면 하나의 테스트 함수를 서로 다른 오류 코드에 반복 실행할 수 있다.

### Retry 성공 테스트

```python
mock_post.side_effect = [
    httpx.Response(503, request=request),
    httpx.Response(
        200,
        request=request,
        json={"places": []},
    ),
]

# 첫 호출 503 → 두 번째 호출 200
assert mock_post.call_count == 2
mock_sleep.assert_called_once_with(0.2)
```

`time.sleep()`도 Mock으로 대체하여 테스트 실행 중 실제로 기다리지 않게 했다.

### 요청 횟수 검증 기준

```text
400 / 403       → 1회
429 / 5xx       → 3회 (계속 실패할 때)
Timeout         → 3회 (계속 실패할 때)
ConnectError    → 1회
503 → 200       → 2회 (복구 성공)
```

---

## 9. 전체 테스트

프로젝트 루트(`D:\\code\\python\\trip_planner`)에서 실행:

```powershell
pytest tests/test_place.py -v
pytest tests/test_trip.py -v
pytest -v
```

Day 14 작업 후 전체 테스트 통과를 확인했다. 실제 Google API가 아닌 Mock 응답을 이용해 오류·재시도 흐름을 검증했다.

---

## 10. 현재 구조

```text
사용자 Trip 생성 / 목적지 수정
             ↓
get_destination_coordinates_with_fallback()
             ↓
resolve_destination_coordinates()
             ↓
request_google_places()
             ↓
Google Places API 요청 (최대 3회)
             ↓
     ┌───────┴────────┐
   성공              최종 실패
     ↓                   ↓
  좌표 저장           좌표 None
     └───────┬──────────┘
             ↓
         Trip 저장
```

장소 검색은 Trip에 저장된 좌표를 재사용한다. Google 장소 검색 자체가 최종 실패하면 그 검색 요청에는 502·503·504 등을 반환한다.

---

# TripCS Day 15 - Schedule 종료 시간 및 일정 충돌 검증

## 1. 오늘 목표

Day 15에서는 기존 Schedule의 시작 시간(`start_time`)에 종료 시간(`end_time`)을 추가하고, 같은 여행 날짜(`TripDay`) 안에서 일정 시간이 겹치지 않도록 검증했다.

완료한 작업:

- `Schedule.end_time` 컬럼 추가
- Alembic migration 생성 및 PostgreSQL 적용
- `ScheduleCreate` / `ScheduleUpdate` / `ScheduleResponse`에 `end_time` 반영
- 종료 시간이 시작 시간보다 늦은지 Pydantic에서 검증
- Schedule 생성·수정 시 시간 충돌 검사
- 수정할 때 현재 Schedule 자신을 충돌 대상에서 제외
- 기존 Place 검증, 삭제 및 reorder 기능 유지
- 정상·충돌·경계 시간·수정·다른 날짜·종료 시간 누락 테스트 추가
- `pytest` 전체 테스트 통과

---

## 2. 기존 Schedule 구조의 한계

Day 14까지 Schedule에는 시작 시간만 있었다.

```text
Schedule
├── title
├── start_time
├── place_id
├── memo
└── order_index
```

이 상태에서는 일정이 언제 끝나는지 알 수 없으므로 다음처럼 두 일정이 겹쳐도 확인하기 어려웠다.

```text
오사카성 관광   09:00 ~ 11:00
점심 식사      10:30 ~ 12:00
                      ↑ 30분 겹침
```

Day 15에서는 `end_time`을 추가해 일정의 시간 구간을 다루기 시작했다.

---

## 3. Schedule 모델과 DB 변경

파일: `backend/models.py`

기존 `start_time` 아래에 `end_time`을 추가했다.

```python
start_time: Mapped[time | None] = mapped_column(
    Time,
    nullable=True,
)

end_time: Mapped[time | None] = mapped_column(
    Time,
    nullable=True,
)
```

`nullable=True`로 설정한 이유는 기존에 생성된 일정에는 종료 시간 정보가 없기 때문이다. 기존 데이터를 삭제하거나 강제로 종료 시간을 채우지 않고 변경 사항을 적용할 수 있다.


## 4. Pydantic Schema 변경

파일: `backend/schemas/schedule.py`

```python
# ScheduleCreate
start_time: time | None = None
end_time: time | None = None

# ScheduleUpdate
start_time: time | None = None
end_time: time | None = None

# ScheduleResponse
start_time: time | None
end_time: time | None
```

Schedule 생성 및 수정 Schema에 시간 범위 검증을 추가했다.

```python
from pydantic import model_validator

@model_validator(mode="after")
def validate_time_range(self):
    if self.start_time is not None and self.end_time is not None:
        if self.end_time <= self.start_time:
            raise ValueError(
                "end_time must be later than start_time"
            )
    return self
```

검증 기준:

```text
09:00 ~ 11:00  → 정상
11:00 ~ 11:00  → 오류
15:00 ~ 13:00  → 오류
09:00 ~ None   → 허용 (기존 데이터 호환)
```

잘못된 시간 범위로 API 요청을 보내면 FastAPI의 입력 검증 단계에서 `422` 응답이 발생한다.

현재 정책은 **같은 날짜 안에서 시작하고 종료하는 일정**을 기준으로 한다. 자정을 넘기는 일정은 별도 정책이 필요하다.

---

## 5. 일정 시간 충돌 검사 함수

파일: `backend/services/schedule.py`

충돌 검사를 여러 함수에서 재사용하기 위해 `validate_schedule_conflict()`를 분리했다.

```python
from datetime import time


def validate_schedule_conflict(
    db: Session,
    trip_day_id: int,
    start_time: time | None,
    end_time: time | None,
    exclude_schedule_id: int | None = None,
) -> None:
    if start_time is None or end_time is None:
        return

    query = db.query(Schedule).filter(
        Schedule.trip_day_id == trip_day_id,
        Schedule.start_time.isnot(None),
        Schedule.end_time.isnot(None),
        Schedule.start_time < end_time,
        Schedule.end_time > start_time,
    )

    if exclude_schedule_id is not None:
        query = query.filter(
            Schedule.id != exclude_schedule_id
        )

    existing_schedule = query.first()

    if existing_schedule:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Schedule time conflicts with an existing schedule",
        )
```

### 충돌 판단 조건

두 일정 A(기존 일정), B(새 일정)가 겹치는 조건:

```python
existing.start_time < new.end_time and existing.end_time > new.start_time
```

SQLAlchemy에서는 이를 쿼리 조건으로 검사한다.

```python
Schedule.start_time < end_time,
Schedule.end_time > start_time,
```

예시:

| 기존 일정 | 새 일정 | 결과 |
|---|---|---|
| 09:00~11:00 | 10:30~12:00 | 충돌 → 400 |
| 09:00~11:00 | 11:00~12:00 | 허용 → 201 |
| 09:00~11:00 | 13:00~15:00 | 허용 → 201 |

종료 시각과 다음 일정 시작 시각이 **정확히 같으면 겹치지 않는 것으로 처리**한다.

---


# TripCS Day 16 - Schedule 정렬 옵션 및 조회 API 개선

## 1. 오늘 목표

Day 15에서 일정의 시작·종료 시간과 충돌 검사를 구현했다. Day 16에서는 사용자가 직접 지정한 순서와 실제 시작 시간 순서를 구분하여 일정 목록을 조회할 수 있도록 개선했다.

완료한 작업:

- `GET /trip-days/{trip_day_id}/schedules`에 `sort_by` 쿼리 파라미터 추가
- `manual` / `time` 두 가지 정렬 지원
- 기존 사용자를 위해 기본값을 `manual`로 설정
- 시작 시간이 없는 일정은 시간순 정렬에서 마지막에 배치
- Router의 직접 DB 조회를 Service 함수로 분리
- 기존 `get_owned_trip_day()` 소유권 검사 유지
- 기존 Schedule reorder 기능 유지 및 정렬 옵션 독립성 확인
- 잘못된 정렬 옵션에 422 응답 확인
- 다른 사용자 접근 시 404 응답 확인
- 전체 pytest 통과

---

## 2. 기존 방식의 한계

기존 목록 조회 Router는 다음과 같이 정렬했다.

```python
schedules = (
    db.query(Schedule)
    .filter(Schedule.trip_day_id == trip_day.id)
    .order_by(Schedule.order_index, Schedule.start_time)
    .all()
)
```

이 방식에서는 `order_index`가 우선이므로, 사용자가 실제 시작 시간순으로 일정을 보고 싶어도 별도 선택지가 없었다.

`order_index`는 **사용자 수동 순서**, `start_time`은 **일정 시작 시각**이라는 서로 다른 의미를 가진다.

---

## 3. API 변경

기존 엔드포인트를 그대로 사용하고 쿼리 파라미터만 추가했다.

```http
GET /trip-days/{trip_day_id}/schedules
GET /trip-days/{trip_day_id}/schedules?sort_by=manual
GET /trip-days/{trip_day_id}/schedules?sort_by=time
```

- `manual`: `order_index` 오름차순, 동률이면 `id` 오름차순
- `time`: `start_time` 오름차순, 시간이 없으면 마지막, 동률이면 `order_index`와 `id`로 정렬
- 파라미터 생략: `manual` 적용
- `random`처럼 허용하지 않은 옵션: 422 반환

기본값을 기존 수동 정렬로 유지하여 API 사용 방식의 하위 호환성을 확보했다.

---

## 4. Router 수정

파일: `backend/routers/schedule.py`

```python
from typing import Literal

from backend.services.schedule import get_schedules_sorted_service

@router.get("", response_model=list[ScheduleResponse])
def get_schedules(
    trip_day_id: int,
    sort_by: Literal["manual", "time"] = "manual",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    trip_day = get_owned_trip_day(
        db=db,
        trip_day_id=trip_day_id,
        user_id=current_user.id,
    )

    return get_schedules_sorted_service(
        db=db,
        trip_day_id=trip_day.id,
        sort_by=sort_by,
    )
```

`Literal["manual", "time"]`을 사용하면 FastAPI/Pydantic이 허용된 값만 받도록 검증한다.

Router는 요청과 인증·소유권 검사를 처리하고, 정렬에 관한 DB 조회는 Service에 위임했다.

---

## 5. Service에 정렬 함수 추가

파일: `backend/services/schedule.py`

```python
from typing import Literal
from sqlalchemy import nulls_last


def get_schedules_sorted_service(
    db: Session,
    trip_day_id: int,
    sort_by: Literal["manual", "time"] = "manual",
) -> list[Schedule]:
    query = db.query(Schedule).filter(
        Schedule.trip_day_id == trip_day_id
    )

    if sort_by == "time":
        query = query.order_by(
            nulls_last(Schedule.start_time.asc()),
            Schedule.order_index.asc(),
            Schedule.id.asc(),
        )
    else:
        query = query.order_by(
            Schedule.order_index.asc(),
            Schedule.id.asc(),
        )

    return query.all()
```

주요 개념:

- `.filter()`: 해당 TripDay의 일정만 조회한다.
- `.asc()`: 오름차순 정렬이다.
- `nulls_last()`: 시작 시간이 `NULL`인 항목을 맨 뒤로 보낸다.
- `Schedule.id.asc()`: 앞의 정렬 값이 같을 때 결과 순서를 안정적으로 결정한다.
- `.all()`: 조회 결과를 리스트로 반환한다.

---

## 6. pytest 테스트

파일: `tests/test_schedule.py`

검증한 내용:

1. 수동 정렬이 `order_index` 순서로 반환되는가?
2. 시간순 정렬이 `start_time` 순서로 반환되는가?
3. 시간 미정(`None`) 일정은 시간순 결과의 마지막에 나오는가?
4. 허용하지 않은 `sort_by` 값은 422를 반환하는가?
5. Reorder 뒤 수동 순서가 변경되는가?
6. Reorder 뒤에도 시간순 정렬은 영향을 받지 않는가?
7. 다른 사용자가 일정 목록을 조회하면 404를 반환하는가?
8. 기존 Day 1~15 기능에 회귀 오류가 없는가?

실행 명령:

```powershell
pytest tests/test_schedule.py -v
pytest -v
```

최종 결과: **전체 테스트 통과**. 구체적인 통과 개수는 실행 로그를 별도로 기록하지 않았다.

---


# TripCS Day 17 - Trip 상세 조회 정렬 옵션 통합

## 1. 오늘 목표

Day 16에서는 **특정 TripDay의 Schedule 목록 조회**에서 `sort_by=manual | time`을 지원했다. Day 17에서는 같은 정렬 옵션을 **여행 전체 상세 조회**인 `GET /trips/{trip_id}/detail`에도 적용하여, 화면에 표시되는 일정 순서가 API별로 달라지지 않도록 개선했다.

완료한 작업:

- Trip 상세 조회 API에 `sort_by` 쿼리 파라미터 추가
- 기본값 `manual`로 기존 호출 방식 유지
- 날짜(`TripDay`)는 항상 `day_number` 오름차순 정렬
- 각 날짜의 Schedule은 `manual` 또는 `time`에 따라 별도 정렬
- `start_time=None`인 일정은 시간순 조회에서 맨 뒤로 배치
- 동일한 시작 시간에는 `order_index`, `id`를 보조 정렬 키로 사용
- 기존 `joinedload()`와 사용자 소유권 검사 유지
- 잘못된 정렬 옵션 422, 다른 사용자 접근 404 확인
- pytest 전체 **68 passed** 확인

---

## 2. 기존 구조의 한계

Day 16에서 다음 API는 정렬 방식을 선택할 수 있었다.

```http
GET /trip-days/{trip_day_id}/schedules?sort_by=time
```

반면 여행 전체를 조회하는 다음 API는 정렬 옵션을 받지 않았다.

```http
GET /trips/{trip_id}/detail
```

따라서 사용자가 여행 전체 화면을 열었을 때도 **수동순 또는 시간순을 선택할 수 있도록** 상세 조회 API를 확장했다.

---

## 3. API 변경

```http
GET /trips/{trip_id}/detail
GET /trips/{trip_id}/detail?sort_by=manual
GET /trips/{trip_id}/detail?sort_by=time
```

| 요청 | 동작 |
| --- | --- |
| 옵션 없음 | `manual` 기본 적용 |
| `sort_by=manual` | `order_index`, `id` 순 |
| `sort_by=time` | `start_time`, `order_index`, `id` 순; 시간 미정은 마지막 |
| `sort_by=random` | 422 응답 |

날짜는 Schedule 정렬 옵션과 무관하게 `day_number` 기준으로 정렬한다.

---

## 4. Router에서 정렬 옵션 받기

파일: `backend/routers/trip.py`

```python
from datetime import time
from typing import Literal

@router.get(
    "/{trip_id}/detail",
    response_model=TripDetailResponse,
)
def get_trip_detail(
    trip_id: int,
    sort_by: Literal["manual", "time"] = "manual",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ...
```

`Literal["manual", "time"]`으로 허용되는 정렬 방식만 제한한다. 값이 잘못되면 FastAPI의 요청 검증 단계에서 422가 반환된다. 기본값을 `manual`로 설정하여 기존 클라이언트도 정렬 옵션 없이 호출할 수 있다.

---

## 5. 소유권 검사와 eager loading 유지

기존 상세 조회 쿼리는 유지했다.

```python
trip = (
    db.query(Trip)
    .options(
        joinedload(Trip.days)
        .joinedload(TripDay.schedules)
        .joinedload(Schedule.place_info)
    )
    .filter(
        Trip.id == trip_id,
        Trip.user_id == current_user.id,
    )
    .first()
)

if not trip:
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Trip not found",
    )
```

- `Trip.id == trip_id`: 조회할 여행을 지정한다.
- `Trip.user_id == current_user.id`: 로그인 사용자의 여행만 조회한다.
- `joinedload()`: Trip → TripDay → Schedule → Place 관계를 함께 로딩하여 관계 접근 시 반복 조회가 발생하는 문제를 줄인다.
- 결과가 없으면 404를 반환한다. 다른 사용자의 여행 존재 여부도 노출하지 않는다.

---

## 6. TripDay는 날짜 순으로 고정

```python
trip.days.sort(
    key=lambda day: day.day_number
)
```

`sort_by`는 날짜 내부의 Schedule 순서만 바꾸며, TripDay의 날짜 순서는 항상 유지한다.

---

## 7. Schedule의 두 가지 정렬

```python
for day in trip.days:
    if sort_by == "time":
        day.schedules.sort(
            key=lambda schedule: (
                schedule.start_time is None,
                schedule.start_time or time.max,
                schedule.order_index,
                schedule.id,
            )
        )
    else:
        day.schedules.sort(
            key=lambda schedule: (
                schedule.order_index,
                schedule.id,
            )
        )
```

### 수동순 (`manual`)

1. `order_index`: 사용자가 정한 순서
2. `id`: 순서가 같을 때 결과를 일정하게 만드는 보조 기준

### 시간순 (`time`)

1. `schedule.start_time is None`: 시간이 있는 일정이 먼저 오도록 정렬
2. `schedule.start_time or time.max`: 시작 시간이 빠른 순서
3. `order_index`: 같은 시작 시간일 때 수동 순서 사용
4. `id`: 최종 보조 정렬 기준

파이썬의 튜플 정렬은 **왼쪽 값부터 차례로 비교**한다. `False`가 `True`보다 먼저 정렬되므로 `start_time is None` 조건으로 시간이 없는 일정을 맨 뒤에 둘 수 있다.

예시:

| 일정 | 시작 시간 | order_index |
| --- | --- | ---: |
| 쇼핑 | 16:00 | 0 |
| 오사카성 | 09:00 | 1 |
| 점심 | 12:00 | 2 |

- `manual` 결과: **쇼핑 → 오사카성 → 점심**
- `time` 결과: **오사카성 → 점심 → 쇼핑**

시간이 정해지지 않은 일정은 `time` 정렬 시 맨 마지막에 표시한다.

---



