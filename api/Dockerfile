FROM python:3.10-slim
WORKDIR /app
COPY . /app
RUN pip install --upgrade pip && pip install --upgrade -r requirements.txt
EXPOSE 5001
CMD ["python", "API.py"]
