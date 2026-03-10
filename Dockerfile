# Dockerfile - ALC Breach Screening Tool
FROM python:3.12-slim

# Non-root user for least-privilege execution
RUN adduser --disabled-password --gecos "" appuser

WORKDIR /app

# Install dependencies first
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application source
COPY src/ ./src/
COPY config/ ./config/
COPY email_list.csv .

RUN mkdir -p /app/output && chown appuser:appuser /app/output

USER appuser

# Default: dry-run (Runs with no API calls, not using IX_API_KEY)
ENTRYPOINT [ "python", "src/main.py" ]
CMD ["--dry-run", "--input", "email_list.csv", "--output", "output/output_result.csv"]