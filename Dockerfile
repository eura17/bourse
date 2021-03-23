FROM python:3.8-slim-buster
COPY . .
RUN pip install -r requirements.txt
CMD ["python", "./main.py"]
EXPOSE 4444:5000
VOLUME /home/eura/PycharmProjects/bourse/order_logs
