FROM python:3.12.11

LABEL authors="KSaMar"

WORKDIR /app

COPY . .

RUN pip3 install -r requirements.txt

EXPOSE 20521

CMD ["python3", "app.py"]