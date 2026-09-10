FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    AUDITOR_DB=/app/data/auditor.db
WORKDIR /app
RUN addgroup --system zcoin && adduser --system --ingroup zcoin --home /app zcoin
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY --chown=zcoin:zcoin app ./app
RUN mkdir -p /app/data && chown -R zcoin:zcoin /app/data
USER zcoin
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/healthz', timeout=2).read()" || exit 1
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers", "--forwarded-allow-ips=*"]
