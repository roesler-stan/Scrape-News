"""
Clean HTML files, putting data into CSV

python parse_fox.py -id="../Data/Fox" -o="../Data/fox.csv"
"""

import os
import argparse
import urllib2
import urllib
import urlparse
from bs4 import BeautifulSoup
import csv
import datetime
import re
import find_date as fd

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-id', '--input_directory', dest = 'input_directory', type = str)
    parser.add_argument('-o', '--outfile', dest = 'outfile', type = str)
    input_values = parser.parse_args()
    input_directory = input_values.input_directory
    outfile = input_values.outfile

    headers = ['title', 'datetime_scraped', 'date', 'year', 'month', 'weekday', 'author', 'source', 'text',
    'keywords', 'url', 'filename']
    with open(outfile, 'w') as f:
        writer = csv.DictWriter(f, fieldnames = headers)
        writer.writeheader()

        for folder, nested_folders, filenames in os.walk(input_directory):
            if folder == input_directory:
                continue
            files = [os.path.join(folder, f) for f in filenames if f.endswith(".html")]
            date = fd.find_date(folder, input_directory)
            for filename in files:
                row = parse_page(filename)
                row['datetime_scraped'] = date
                if row:
                    writer.writerow(row)

def parse_page(filename):
    """
    Find article text and attributes and write result to output file

    Args:
        filename (str): filename of html page from which to get review text
        writer (csv object): csv writer for output file
    """
    row = {'filename': filename}

    # Encode the filename as ASCII to UTF-8 and then url quote its path in case it has non-ASCII symbols in it
    parsed_link = urlparse.urlsplit(filename.encode('utf8'))
    parsed_link = parsed_link._replace(path=urllib.quote(parsed_link.path))
    encoded_link = parsed_link.geturl()

    html = urllib2.urlopen('file:' + encoded_link)
    soup = BeautifulSoup(html, "html.parser")

    # If there's no text, continue to the next article and don't record this one
    text_tag = soup.find('div', {'class': 'article-text'})
    if text_tag:
        text = text_tag.text.strip()
        text = text.encode('utf-8', 'ignore')
        text = re.sub('\s\s+', ' ', text)
        row['text'] = text
    else:
        text_tag = soup.find('div', {'itemprop': 'articleBody'})
        if text_tag:
            text_tags = text_tag.find_all('p')
            text_paragraphs = [tag.text.strip() for tag in text_tags]
            text = '\n'.join(text_paragraphs)
            row['text'] = text
        else:
            print 'No text for ' + filename
            return {}

    url_tag = soup.find('link', {'rel': 'canonical'})
    if url_tag:
        url = str(url_tag['href'])
        row['url'] = url

    title = str(soup.find('title').text.strip())
    row['title'] = title

    date_tag = soup.find('time', {'itemprop': 'datePublished'})
    if date_tag and date_tag.has_attr('datetime'):
        date_str = date_tag['datetime'].split('T')[0]
        date = datetime.datetime.strptime(date_str, '%Y-%m-%d')
        row['date'] = date_str
        row['year'] = date.year
        row['month'] = date.month
        row['weekday'] = datetime.datetime.strftime(date, '%A')

    author_tag = soup.find('span', {'class': 'author'})
    if author_tag:
        author = author_tag.text
        author = re.sub('\s{2}', '', author)
        row['author'] = author

    keywords_tag = soup.find('meta', {'name': 'keywords'})
    if keywords_tag:
        keywords_str = str(keywords_tag['content'])
        if keywords_str:
            keywords = keywords_str.split(', ')
            row['keywords'] = keywords

    source_tag = soup.find('div', {'itemprop': 'sourceOrganization'})
    if source_tag:
        source = source_tag.text.strip()
        row['source'] = source

    return row

if __name__ == '__main__':
    main()