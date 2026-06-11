FROM python:3.12-slim
RUN pip install flask flask-cors
COPY app.py /app/app.py
WORKDIR /app
EXPOSE 5000
CMD ["python", "app.py"]
