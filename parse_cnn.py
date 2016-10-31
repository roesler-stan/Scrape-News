"""
Clean HTML files, putting data into CSV

python parse_cnn.py -id="../Data/CNN" -o="../Data/cnn.csv"
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

    headers = ['title', 'datetime_scraped', 'date', 'year', 'month', 'weekday', 'author', 'text', 'section',
    'keywords', 'url', 'filename']
    with open(outfile, 'w') as f:
        writer = csv.DictWriter(f, fieldnames = headers)
        writer.writeheader()

        for folder, nested_folders, filenames in os.walk(input_directory):
            if folder == input_directory:
                continue
            date = fd.find_date(folder, input_directory)
            files = [os.path.join(folder, f) for f in filenames if f.endswith(".html")]
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

    # If there's no text (e.g. for a video, don't bother recording the article)
    text_tags = soup.find_all('div', {'class': 'zn-body__paragraph'})
    if text_tags:
        text_paragraphs = [tag.text.strip() for tag in text_tags]
        text = '\n'.join(text_paragraphs)
    else:
        text_tag = soup.find('div', {'id': 'storytext'})
        if text_tag:
            text_tags = text_tag.find_all('p')
            text_paragraphs = [tag.text.strip() for tag in text_tags]
            text = '\n'.join(text_paragraphs)
        else:
            text_tag = soup.find('div', {'itemprop': 'articleBody'})
            if text_tag:
                text = text_tag.text.strip()
            else:
                print 'No text for ' + filename
                return {}
    text = text.encode('utf-8', 'ignore')
    text = re.sub('\s\s+', ' ', text)
    row['text'] = text

    url_tag = soup.find('link', {'rel': 'canonical'})
    if url_tag:
        url = str(url_tag['href'])
        row['url'] = url

    section_tag = soup.find('meta', {'name': 'section'})
    if section_tag:
        section = str(section_tag['content'])
        row['section'] = section

    title = str(soup.find('title').text.strip())
    row['title'] = title

    datePresent = True
    date_tag = soup.find('meta', {'name': 'date'})
    if date_tag:
        date_str = date_tag['content'].split(' ')[0]
        date = datetime.datetime.strptime(date_str, '%Y-%m-%d')
    else:
        date_tag = soup.find('meta', {'name': 'pubdate'})
        if date_tag:
            date_str = date_tag['content']
            date_str = re.split('T\d{2}', date_str)[0]
            date = datetime.datetime.strptime(date_str, '%Y-%m-%d')
        else:
            datePresent = False

    if datePresent:
        # date = datetime.datetime.strptime(date_str, '%B %d, %Y: %I:%M %p')
        row['date'] = date_str
        row['year'] = date.year
        row['month'] = date.month
        row['weekday'] = datetime.datetime.strftime(date, '%A')

    author_tag = soup.find('meta', {'name': 'author'})
    if author_tag:
        author = str(author_tag['content'])
        row['author'] = author

    keywords_tag = soup.find('meta', {'name': 'keywords'})
    if keywords_tag:
        keywords = str(keywords_tag['content']).split(', ')
        row['keywords'] = keywords

    return row

if __name__ == '__main__':
    main()