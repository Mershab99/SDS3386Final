FROM python:3.10

RUN pip3 install pymongo python-dotenv tweepy
#RUN pip3 install -r requirements.txt


RUN mkdir /app
WORKDIR /app
COPY ./src .


ENTRYPOINT ["python"]
CMD ["./main.py"]
