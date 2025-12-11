FROM python:3.11-slim

WORKDIR /app

# Use CPU wheels for torch to avoid large CUDA downloads in container builds
ENV PIP_EXTRA_INDEX_URL=https://download.pytorch.org/whl/cpu
ENV PIP_NO_CACHE_DIR=1

# requirements.txt lives at repo root when build context is project root
COPY ./requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt

# backend code resides in backend/app under the project root
COPY ./backend/app /app/app

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
