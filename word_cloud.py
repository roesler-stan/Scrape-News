import pandas as pd
import numpy as np
from PIL import Image
import wordcloud as wc
import clean_text as ct

def main():
    mask_file = '../Output/speech_bubble.png'
    infile = '../Data/data.csv'
    outfile_cnn = '../Output/wordcloud_cnn.png'
    outfile_fox = '../Output/wordcloud_fox.png'

    df = pd.read_csv(infile)
    draw_cloud(df, 'CNN', outfile_cnn, mask_file)
    draw_cloud(df, 'Fox', outfile_fox, mask_file)

def draw_cloud(df, site, outfile, mask_file):
    MAX_WORDS = 2000
    subset = df[df['site'] == site]
    text = subset['text'].to_string()
    words = ct.parse_text(text)
    text = ' '.join(words)
    masked_cloud(text, outfile, MAX_WORDS, mask_file)

def masked_cloud(text, outfile, MAX_WORDS, mask_file):
    """ Make a word cloud in the shape of the mask file's black parts """
    mask_shape = np.array(Image.open(mask_file))
    word_cloud = wc.WordCloud(max_words = MAX_WORDS, background_color = "white", mask = mask_shape)
    word_cloud.generate(text)
    word_cloud.to_file(outfile)

if __name__ == '__main__':
    main()