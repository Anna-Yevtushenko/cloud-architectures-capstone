FROM python:3.11-slim

WORKDIR /app

COPY coordinator/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY coordinator/ ./coordinator/

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "coordinator.main:app", "--host", "0.0.0.0", "--port", "8000"]