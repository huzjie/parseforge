FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml README.md ./
COPY parseforge ./parseforge
COPY configs ./configs

RUN pip install --no-cache-dir .

EXPOSE 8000

ENTRYPOINT ["parseforge"]
CMD ["serve", "--host", "0.0.0.0", "--port", "8000"]
