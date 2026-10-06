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
