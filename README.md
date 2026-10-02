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

# Tech Stack

## Backend

- Python
- FastAPI
- Uvicorn
- SQLAlchemy
- Alembic
- PostgreSQL
- Pydantic

## Frontend

- React
- JavaScript / TypeScript

## Development

- Git
- GitHub
- VS Code

---

# Project Structure

```text
trip_planner/
├── backend/
│   ├── main.py
│   ├── database.py
│   └── models.py
│
├── frontend/
│
├── alembic/
│   ├── versions/
│   ├── env.py
│   └── script.py.mako
│
├── .env
├── .gitignore
├── alembic.ini
├── requirements.txt
└── README.md
```



## DAY 1 프로젝트 초기 세팅 및 PostgreSQL 연결

### 배운내용
- PostgreSQL 설치 및 DB 생성
- PostgreSQL Driver 설정
- SQLAlchemy 연결 및 Model 생성
- Alembic Migration 생성 및 적용


### 패키지 설치

```
pip install fastapi uvicorn sqlalchemy psycopg2-binary python-dotenv alembic
```

#### 패키지 역할
- FastAPI : API 서버 구축
- Uvicorn : FastAPI 실행 서버
- SQLAlchemy : 파이썬에서 DB 사용
- psycopg2-binary : PostgreSQL 연결
- python-dotenv : 환경변수 관리
- ALembic : DB Migration 관리