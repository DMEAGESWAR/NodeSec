FROM python:3.11-slim

# ── No apt-get needed ────────────────────────────────────────────────────────
# All Python packages in requirements.txt ship pre-built binary wheels for
# linux/amd64 (asyncpg, psycopg2-binary, bcrypt, cryptography, etc.).
# This means gcc/libpq-dev are NOT required and the build works without
# internet access to apt repos (avoids DNS failures in corporate/restricted networks).
#
# weasyprint is intentionally excluded — it requires native GTK/Cairo libs
# which cannot be installed without apt-get. PDF export is disabled in Docker.
# See requirements.txt for instructions to enable it on your host machine.

WORKDIR /app

# Install Python deps with --prefer-binary to guarantee pre-built wheels.
# The grep excludes weasyprint since it needs GTK native libs.
COPY requirements.txt .
RUN pip install --no-cache-dir --prefer-binary \
    $(grep -v "weasyprint\|^#" requirements.txt | tr '\n' ' ')

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