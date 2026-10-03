# Trip Planner

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
