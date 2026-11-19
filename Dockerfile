
FROM python:3.12-slim

WORKDIR /app

# Python 기본 설정
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Python 패키지 설치
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# 비-root 사용자 생성
RUN groupadd --system appgroup \
    && useradd --system \
        --gid appgroup \
        --create-home \
        appuser

# 애플리케이션 코드 복사
COPY --chown=appuser:appgroup backend/ ./backend/
COPY --chown=appuser:appgroup alembic/ ./alembic/
COPY --chown=appuser:appgroup alembic.ini .

# 비-root 사용자로 전환
USER appuser

EXPOSE 8000

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
