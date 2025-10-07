# ---- Builder Stage ----
FROM python:3.11-slim AS builder

WORKDIR /app

# Create virtual environment
ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Copy dependency list
COPY requirements.txt .

# Upgrade pip and install dependencies cleanly
RUN pip install --upgrade pip wheel setuptools

# Install torch (CPU version)
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

# Install all Python dependencies
RUN pip install --no-cache-dir -r requirements.txt


# ---- Final Stage ----
FROM python:3.11-slim

# Create non-root user and group
RUN addgroup --system app && adduser --system --ingroup app app

# Set Hugging Face cache directory
ENV HF_HOME=/home/app/.cache/huggingface

WORKDIR /home/app

# Copy virtual environment and app code
COPY --from=builder /opt/venv /opt/venv
COPY ./app ./app

# Set ownership for the app directory and HF cache
RUN mkdir -p $HF_HOME && chown -R app:app /home/app

# Switch to non-root user
USER app

# Add virtualenv to PATH
ENV PATH="/opt/venv/bin:$PATH"

# Expose FastAPI port
EXPOSE 8000

# Run the backend
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
