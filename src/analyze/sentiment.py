from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline

#tokenizer1 = AutoTokenizer.from_pretrained('distilbert-base-uncased-finetuned-sst-2-english')
#model1 = AutoModelForSequenceClassification.from_pretrained('distilbert-base-uncased-finetuned-sst-2-english')


#tokenizer2 = AutoTokenizer.from_pretrained('nlptown/bert-base-multilingual-uncased-sentiment')
#model2 = AutoModelForSequenceClassification.from_pretrained('nlptown/bert-base-multilingual-uncased-sentiment').to('cuda')

# edit device to 0 for GPU
sentiment_classifier = pipeline('sentiment-analysis', device=0)

bert_classifier = pipeline(model='nlptown/bert-base-multilingual-uncased-sentiment', device=0)


def classify_sentiment_analysis(text):
    output = sentiment_classifier(text)
    output[0]['model'] = 'distilbert-base-uncased-finetuned-sst-2-english'
    return output[0]


def classify_bert(text):
    output = bert_classifier(text)
    output[0]['model'] = 'nlptown/bert-base-multilingual-uncased-sentiment'
    return output[0]

