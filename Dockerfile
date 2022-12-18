FROM python:3.10

RUN pip3 install pymongo~=4.3.3 python-dotenv tweepy~=4.12.1 transformers~=4.24.0 torch datasets accelerate

RUN mkdir /app
WORKDIR /app
COPY . .
#RUN pip3 install -r requirements.txt

ENTRYPOINT ["python"]
CMD ["./src/main.py"]
