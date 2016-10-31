import re
import nltk
from nltk.stem.porter import *
from nltk.corpus import stopwords

def parse_text(text):
    text = text.lower()

    # Only keep letters
    text = re.sub('[^a-zA-Z ]', '', text)
    while '  ' in text:
        text = text.replace('  ', ' ')

    tokens = nltk.word_tokenize(text)
    # Exclude stop words
    stopwords = nltk.corpus.stopwords.words('english')
    tokens = [t for t in tokens if t not in stopwords]

    # Lemmatize (shorten to core)
    wnl = nltk.WordNetLemmatizer()
    tokens = [wnl.lemmatize(t) for t in tokens]

    # Exclude one-letter words (even if they represent longer ones)
    tokens = [t for t in tokens if len(t) > 1]

    tagged = nltk.pos_tag(tokens)
    
    # Check for named entities (e.g. "Pride and Prejudice" vs. pride) - this step takes a long time
    entities = nltk.chunk.ne_chunk(tagged)
    # adjectives = [str(entity[0]) for entity in entities if entity[-1] == 'JJ']
    words = [str(entity[0]) for entity in entities]
    return words