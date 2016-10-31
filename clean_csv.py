import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
import textmining
import clean_text as ct

def main():
    data_directory = "../Data/"
    cnn_file = data_directory + "cnn.csv"
    fox_file = data_directory + "fox.csv"
    outfile = data_directory + "data.csv"
    counts_outfile = data_directory + "counts.csv"
    tfidf_outfile = data_directory + "tfidf.csv"
    
    df_cnn = pd.read_csv(cnn_file)
    df_fox = pd.read_csv(fox_file)
    df_cnn['site'] = 'CNN'
    df_fox['site'] = 'Fox'
    df = df_cnn.append(df_fox)

    # df = clean_keywords(df)
    df.to_csv(outfile, index = False)

    site_dict = sites_text(df)

    terms_df = count_terms(site_dict)
    terms_df.to_csv(counts_outfile, index = False)

    tfidf_data = tfidf(site_dict)
    tfidf_data.to_csv(tfidf_outfile, index = False)

def clean_keywords(df):
    df['keywords'] = df['keywords'].str.replace('\[|\]', '')
    df['keywords'] = df['keywords'].str.replace('" ?', '')
    df['keywords'] = df['keywords'].str.replace("' ?", '')
    df['keywords'] = df['keywords'].str.split(', ')

    keywords = pd.get_dummies(df['keywords'].apply(pd.Series).stack()).sum(level=0)
    keywords = keywords.drop('', axis = 1)

    # pd.concat([df, keywords], axis=1)
    # df = df.merge(keywords, how = 'left', on = None)
    return df

def count_terms(site_dict):
    terms_matrix = textmining.TermDocumentMatrix()
    for site, text in site_dict.items():
        terms_matrix.add_doc(text)

    terms_df = pd.DataFrame(terms_matrix.rows())
    terms_df.columns = terms_df.iloc[0]
    terms_df = terms_df[1:]
    terms_df.index = site_dict.keys()
    terms_df.index.name = 'site'
    terms_df = terms_df.T
    terms_df.index.name = 'term'
    terms_df = terms_df.reset_index()
    return terms_df

def tfidf(site_dict):
    """ Find 10 words with highest TF-IDF for each site """
    tfidf = TfidfVectorizer()
    tfs = tfidf.fit_transform(site_dict.values())
    tfidf_data = pd.DataFrame([ pd.SparseSeries(tfs[i].toarray().ravel()) for i in np.arange(tfs.shape[0]) ])
    columns = tfidf.get_feature_names()
    tfidf_data.columns = columns
    tfidf_data.index = site_dict.keys()

    tfidf_data = tfidf_data.stack().reset_index()
    tfidf_data = tfidf_data.rename(columns = {'level_0': 'site', 'level_1': 'term', 0: 'tfidf'})
    tfidf_data = tfidf_data.sort_values(by = ['site', 'tfidf'], ascending = False).groupby('site').head(10)
    return tfidf_data

def sites_text(df):
    """ Get cleaned text for each site """
    site_dict = {}
    sites = ['CNN', 'Fox']
    for site in sites:
        subset = df[df['site'] == site]
        text = subset['text'].to_string()
        words = ct.parse_text(text)
        text = ' '.join(words)
        site_dict[site] = text
    return site_dict

if __name__ == "__main__":
    main()