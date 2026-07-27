FROM python:3.12-slim AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1
WORKDIR /app
RUN addgroup --system crmoney && adduser --system --ingroup crmoney crmoney
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY alembic ./alembic
COPY alembic.ini* ./
COPY entrypoint.sh ./
COPY app ./app
RUN mkdir -p /app/uploads && chmod +x /app/entrypoint.sh && chown -R crmoney:crmoney /app
USER crmoney
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --retries=3 CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/live')"
CMD ["/app/entrypoint.sh"]
