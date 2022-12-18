from sklearn.feature_extraction.text import CountVectorizer
import pandas as pd


#------For wordcloud
import os
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
import numpy as np 
import requests
from PIL import Image
from io import BytesIO 
from matplotlib import cm
from matplotlib.colors import ListedColormap, LinearSegmentedColormap
import wget
#------------------



# Stop words: words to ignore

#import built-in stop words
from nltk.corpus import stopwords

custom_list = ['co','like','https','one','get','know','could','make','see','want','got','really','would',
 'says','take','actually','even','last','least','let','may','never','said','say','vs',
 'better','called','check','every','happened','made','might','must','still','back','maybe',
 'going','much','sure','also','done','go','though', 'told','usually', 'via', 'absolutely','accept','although','apparently', 'around','however','often','saw', 'seeing','thats','thinking', 'thinks','another','big','cause','come','encore', 'ever', 'evs', 'except', 'far', 'hear', 'heard','enough','hi','im','lot', 'nothing', 'plus', 'probably', 'quoi', 'soon', 'without', 'ago','certain','completely','considered', 'dont','dès','entire', 'entre', 'especially', 'fortunately','hui', 'imma', 'later','less', 'lets','beugrefidelpio','faire', 'si', 'comme', 'ça', 'iempyreen', 'nessouwww', 'oui', 'peut', 'toumi386', 'fait', 'grand', 'non', 'très', 'va', 'être', 'aller', 'amp', 'ans', 'auj', 'aujourd', 'aussi', 'cela', 'cette', 'depuis', 'dire', 'eto', 'façon','hackedyayonne11', 'jeaneti86705066', 'mouhafadel_', 'nlp78767029','parle','petit', 'possible', 'quand', 'quelle', 'rien', 'sais', 'sans', 'sdm__92', 'seulement', 'tkt', 'toujours', 'tous', 'tout', 'tpmp','vraiment','yvesdidier9', '0rtopcm4dlune', '0skil0pyfm', '1jcgagnon', '2022vraiment',  '2gixcafhzqèface', '2sbm8q164a', '3nddoyla9won', '4p4houbkzc', '4zsubb7jxc', '5si88xzukd', '614iuc5gtele', '6mgha7wcp8', '7fewfrktsble', '7kf2jqjmxxle', '7ym38xpavctous', '9f95piqvir', '9nilvfdjgiemployés', '9qn8a3jpi9', '_befootball', 'abdaniellesmith', 'actuellement', 'aihzthk3sfnotre',
'alors', 'ananascap', 'andrbilodeau3', 'après', 'arrivent', 'artcgreen', 'attendais', 'attendez', 'attestent','autre', 'autres', 'avant','avoir', 'bah','barth_gelo', 'bcp', 'beaucoup', 'bfgcci2qwlmise','brchvfftg7', 'bt5zeymuyb', 'cawvjy7ad2', 'centaines', 'cesser', 'chaleureusement', 'chaque','chez', 'comment','communiquez', 'corsaire999', 'cound686f0111', 'crit_role69', 'crois', 'croyais', "c'est","N'importe","per", "e", "qu'on"
, "mise", 'importe', "là", "trop","quel","souhaite","déjà","p","moins", "petite", "où", "parce", "que", "passe", "regarde", "vais", "veux", "veut", "j'ai", "voir", "u","already"]

stop_words = stopwords.words('english') + stopwords.words('french')+ custom_list



def count(text, stop_words = [], strip_accents = "ascii" ):
    """Returns a dataframe containing the words in text and their counts, excluding the words in stop_words
       text : sequence of items that can be of type string or byte.
       stop_words: list of string
       --------------------------------------------------------------
       word.stop_word can be used as the stop_word argument
       It contains noise words in french and english
       
    """
    vectorizer = CountVectorizer(stop_words = stop_words)
    # tokenize and build vocab
    vectorizer.fit(text)
    # encode document
    vector = vectorizer.transform(text)

    count_df = pd.DataFrame(data = vector.toarray()).transpose()
    count_df = count_df.rename(columns = { 0:'count'} )
    vocab = vectorizer.vocabulary_
    count_df['word'] = ""
    count_df = count_df[['word','count']]
    for key in vocab:
        count_df.loc[ vocab[key], 'word']= key
    

    return count_df


def tweet_cloud(text, stop_words=[]):
    """Returns a wordcloud object made with the most common words in text (excluding the words in stop_words)
    
       text : sequence of items that can be of type string or byte.
       stop_words: list of string
       
       word.stop_word can be used as the stop_word argument
       It contains noise words in french and english
       
    """
    #Assets
    image_url = "https://raw.githubusercontent.com/rasbt/datacollect/master/dataviz/twitter_cloud/twitter_mask.png"
     
    # Image Path
    path = './Assets/twitter_mask.png'
    # Check if the image file exists
    if (not os.path.isfile(path)):
        twitter_png = wget.download(image_url, out ='./Assets/twitter_mask.png' )
    else:
         twitter_png = './Assets/twitter_mask.png'


    
    twitter_mask = np.array(Image.open(twitter_png))
    Blues = cm.get_cmap('Blues', 512)
    blue_palette = ListedColormap(Blues(np.linspace(0.4, 0.9, 256)))
    
    
    # Word cloud image
    wordcloud = WordCloud(stopwords = stop_words, 
                      background_color="white",
                       font_path='./Assets/FredokaOne-Regular.ttf',
                      colormap = blue_palette,
                      mask = twitter_mask
                     ).generate("".join(text))
    return wordcloud

