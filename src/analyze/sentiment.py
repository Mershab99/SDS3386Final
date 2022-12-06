from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline

sentiment_classifier = pipeline('sentiment-analysis')

bert_classifier = pipeline(model='nlptown/bert-base-multilingual-uncased-sentiment')


def classify_sentiment_analysis(text):
    output = sentiment_classifier(text)
    output[0]['model'] = 'distilbert-base-uncased-finetuned-sst-2-english'
    return output[0]


def classify_bert(text):
    output = bert_classifier(text)
    output[0]['model'] = 'nlptown/bert-base-multilingual-uncased-sentiment'
    return output[0]

