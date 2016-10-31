"""
CNN takes about 25 minutes, Fox takes about 75 minutes.
Might want to change ".close()" to ".quit()"
"""

import os
from bs4 import BeautifulSoup
import datetime
import time
import random
from collections import OrderedDict
from selenium import webdriver
import selenium.webdriver.support.ui as ui
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException

def main():
    cnn_directory = '../Data/CNN/'
    fox_directory = '../Data/Fox/'
    download_pages(cnn_directory, fox_directory)

def download_pages(cnn_directory, fox_directory):
    """ Save HTML pages into this month/day/hour directory
    Randomly decide which one to download first """
    CNN_LINK = 'http://www.cnn.com'
    FOX_LINK = 'http://www.foxnews.com'
    # website_dict = {'CNN': {'link': CNN_LINK, 'directory': cnn_directory}, 'Fox': {'link': FOX_LINK, 'directory': fox_directory}}
    website_dict = {'Fox': {'link': FOX_LINK, 'directory': fox_directory}}
    # website_dict = {'CNN': {'link': CNN_LINK, 'directory': cnn_directory}}
    dict_list = sorted(website_dict.items(), key = lambda x: random.random())
    website_dict = OrderedDict(dict_list)

    year = datetime.datetime.now().year
    month = datetime.datetime.now().month
    day = datetime.datetime.now().day
    hour = datetime.datetime.now().hour
    minute = datetime.datetime.now().minute

    for site, site_info in website_dict.items():
        LINK = site_info['link']
        DIRECTORY = site_info['directory']
        out_directory = DIRECTORY + '_'.join([str(year), str(month), str(day), str(hour), str(minute)]) + '/'
        if not os.path.exists(out_directory):
            os.makedirs(out_directory)

        homepage_file = out_directory + 'homepage.html'
        urls_file = out_directory + 'urls.txt'
        failed_file = out_directory + 'failed.txt'
        failed_final_file = out_directory + 'failed_final.txt'

        driver = new_driver()
        driver.get(LINK)
        save_page(driver, homepage_file)
        page_no = get_articles(driver, out_directory, site, urls_file, failed_file)
        get_failed(out_directory, page_no, failed_file, failed_final_file)

def get_articles(driver, directory, site, urls_file, failed_file):
    """ Starting on the homepage, open each visible article link in a new tab and download its page """
    NEWDRIVER_FREQ = 15
    SLEEP_FREQ = 1
    SLEEP_TIME = 3
    page_no = 0

    if site == 'CNN':
        urls = cnn_urls(driver)
    if site == 'Fox':
        urls = fox_urls(driver)

    print 'You are going to retrieve ' + str(len(urls)) + ' articles from ' + site + '.'
    with open(urls_file, 'w') as f:
        f.write('\n'.join(urls))

    for url in urls:
        if page_no % NEWDRIVER_FREQ == 0:
            driver.close()
            driver.quit()
            driver = new_driver()

        if page_no % SLEEP_FREQ == 0:
            time.sleep(SLEEP_TIME)

        try:
            driver.get(url)
        except:
            with open(failed_file, 'a') as f:
                f.write(url + '\n')
            continue

        outfile = directory + str(page_no) + '.html'
        save_page(driver, outfile)
        page_no += 1

    driver.close()
    driver.quit()
    return page_no

def fox_urls(driver):
    # Scroll down to the bottom because it makes more links appear
    SCROLL_TIMES = 10
    for i in range(SCROLL_TIMES):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)

    main_doc = driver.find_element_by_id('doc')

    top_box = main_doc.find_element_by_id("big-top")
    top_links = top_box.find_elements_by_xpath(".//a")
    top_urls = [link.get_attribute('href') for link in top_links]

    line_links = main_doc.find_elements_by_xpath(".//a[@data-adv='latestnews']")
    line_urls = [link.get_attribute('href') for link in line_links]

    article_boxes = main_doc.find_elements_by_xpath(".//div[@class='bkt article-ct']")
    box_links = [box.find_element_by_xpath(".//a") for box in article_boxes]
    box_urls = [link.get_attribute('href') for link in box_links]

    features_box = main_doc.find_element_by_id("features-faces")
    features_links = features_box.find_elements_by_xpath(".//a")
    features_urls = [link.get_attribute('href') for link in features_links]

    market_section = main_doc.find_element_by_id("mkt-snap")
    market_box = market_section.find_element_by_xpath(".//div[@class='mkt-rel']")
    market_links = market_box.find_elements_by_xpath(".//a")
    market_urls = [link.get_attribute('href') for link in market_links]

    dont_miss_box = main_doc.find_element_by_xpath(".//div[@class='ob-widget-section ob-first']")
    dont_miss_links = dont_miss_box.find_elements_by_xpath(".//a")
    dont_miss_urls = [link.get_attribute('href') for link in dont_miss_links]

    urls = top_urls + line_urls + box_urls + features_urls + market_urls + dont_miss_urls
    urls = list(set(urls))
    return urls

def cnn_urls(driver):
    """ Use selenium to find the displayed article links, then store their urls in a list (b/c otherwise get stale) """
    articles = driver.find_elements_by_xpath("//article")
    articles = [article for article in articles if article.is_displayed()]
    urls = []
    for article in articles:
        try:
            link = article.find_element_by_xpath(".//a")
        except NoSuchElementException:
            continue
        url = link.get_attribute('href')
        urls.append(url)
    return urls

def get_failed(directory, page_no, infile, outfile):
    if os.path.exists(infile):
        driver = new_driver()
        with open(infile, 'r') as f:
            urls = f.readlines()
            urls = [url.strip() for url in urls]

        for url in urls:
            try:
                driver.get(url)
            except:
                with open(outfile, 'a') as outf:
                    outf.write(url + '\n')
                continue
            outfile = directory + str(page_no) + '.html'
            save_page(driver, outfile)
            page_no += 1
        driver.close()
        driver.quit()

def new_driver():
    # Wait to find each element if not immediately available
    IMPLICIT_WAIT = 80
    TIMEOUT = 120
    # driver = webdriver.PhantomJS(service_args=["--webdriver-loglevel=NONE"])
    profile = webdriver.FirefoxProfile()
    profile.set_preference("media.volume_scale", "0.0")
    driver = webdriver.Firefox(profile)
    driver.implicitly_wait(IMPLICIT_WAIT)
    driver.set_page_load_timeout(TIMEOUT)
    return driver

def save_page(driver, outfile):
    """ Save page to html file """
    source = driver.page_source
    source = source.replace(u"\u2019", "'")
    source = source.replace(u"\u201c", '"')
    source = source.replace(u"\u201d", '"')
    source = source.replace(u"\u2014", '-')
    source = source.encode('ascii', 'ignore').encode('utf-8')
    soup = BeautifulSoup(source, "html.parser")
    with open(outfile, 'w') as f:
        f.write(soup.prettify())

if __name__ == "__main__":
    main()