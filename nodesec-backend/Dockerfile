FROM python:3.11-slim

# ── No apt-get needed ────────────────────────────────────────────────────────
# All Python packages ship pre-built binary wheels for linux/amd64.
# weasyprint is excluded — it requires native GTK/Cairo libs.
# See requirements.txt for instructions to enable it on your host machine.

WORKDIR /app

# Install Python deps using a pre-filtered requirements file (no shell tricks).
# --prefer-binary guarantees pre-built wheels; --timeout handles slow networks.
COPY requirements-docker.txt .
RUN pip install --no-cache-dir --prefer-binary --timeout 120 \
    -r requirements-docker.txt

# Copy application code
COPY . .

# Convert entrypoint to Unix line endings and make executable
# (handles Windows CRLF if repo was checked out on Windows)
RUN sed -i 's/\r$//' entrypoint.sh && chmod +x entrypoint.sh

# Create non-root user for security
RUN addgroup --system appgroup && \
    adduser --system --ingroup appgroup --no-create-home appuser && \
    chown -R appuser:appgroup /app

USER appuser

EXPOSE 8000

HEALTHCHECK --interval=15s --timeout=5s --start-period=30s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"

ENTRYPOINT ["./entrypoint.sh"]
