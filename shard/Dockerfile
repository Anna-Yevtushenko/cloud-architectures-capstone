FROM python:3.11-slim

WORKDIR /app

COPY shard/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY shard/ ./shard/

EXPOSE 8001

CMD ["python", "-m", "uvicorn", "shard.main:app", "--host", "0.0.0.0", "--port", "8001"]