# -*- coding: utf-8 -*-

import os
import sys
import re
import datetime
import json
import validators
from tqdm import tqdm
import coloredlogs, logging

from base import NewsDataCollectionHelper
NDH = NewsDataCollectionHelper()

coloredlogs.install(level='DEBUG')

URL = 'http://www.ittefaq.com.bd'
DATE = datetime.datetime.today().strftime('%Y/%m/%d')
pages = ['first-page', 'last-page', 'city', 'country', 'world-news',
         'entertainment', 'sports-news', 'it-corner', 'trade', 'editorial',
         'sub-editorial', 'drishtikon', 'aiojon', 'aunoshilon', 
         'taronner-shomokalin-chinta', 'second-edition', 'others']

TITLE = 'ittefaq'

json_data = []


def generate_json(title, subject, image, caption, description):
    title = title.encode('utf8')
    subject = subject.encode('utf8')
    caption = caption.encode('utf8')
    description = description.encode('utf8')
    json_data.append({"SL": len(json_data) + 1, "title": title, "subject": subject, "image": image, "caption": caption, "description": description})
    

def get_input():
    try:
        url = URL
        date = DATE
        if not validators.url(url):
            logging.critical("INCORRECT URl, should be as http://www.xxxxxx.xx")
            return False
        try:
            if date:
                datetime.datetime.strptime(date, '%Y/%m/%d')
            else:
                date = ""
        except:
            logging.critical("INCORRECT DATE FORMAT, should be as YYYY-MM-DD")
            return False
    except:
        logging.critical("SOMETHINGS WENT WRONG!, Pleasee provide correct input")
        return False

    logging.debug("STARTED GET DATA FROM : {}".format(url))
    return url, date


def get_headlines(soup_parser, page):
    try:
        try:
            lead_headline = soup_parser.find("div", attrs={"class": "sitewidthleft"}).find("div", attrs={"class": "menuNewsLead"})
        except:
            lead_headline = None
        headlines = soup_parser.find("div", attrs={"class": "sitewidthleft"}).find_all("div", attrs={"class": "menuNewsMore"})
        if lead_headline:
            headlines.insert(0, lead_headline)

    except AttributeError:
        logging.warning("PAGE {} NOT AVAILABLE. PROCESSING THE NEXT PAGE".format(page))
        return []
    return headlines


def get_details_wrapper(soup_object):
    try:
        wrapper = soup_object.find("div", attrs={"class": "detailsNews"})
    except:
        logging.warning("ERROR WHILE PARSING DETAILS")  
        return False   
    return wrapper


def get_title(body):
    try:
        title = body.find("div", attrs={"class": "headline2"}).string
    except:
        return 'N/A'
    return title


def get_subject(body):
    try:
        subject = body.find("div", attrs={"class": "headline3"}).string
    except:
        return 'N/A'
    return subject


def get_description_body(body):
    try:
        description = body.find(
            "div", attrs={"class": "details"})
    except:
        return False
    return description


def get_main_image(body):
    try:
        image = body.find("div", attrs={"class": "detailsimage"}).img['src']
    except:
        return 'N/A'
    return 'http:' + image


def get_image_caption(body):
    try:
        caption = body.find("div", attrs={"class": "detailsimage"}).img['alt']
    except:
        return "N/A"
    return caption


def get_description(body):
    try:
        array = []
        paras = body.find_all('div')
        for para in paras:
            array.append(para.get_text())
        if array:
            description = '\n'.join(array) 
        else:
            description = 'N/A'
    except:
        return 'N/A'
    return description


def main():
    _input = get_input()
    base_url = _input[0]
    if not base_url:
        return
    req_url = os.path.join(base_url, 'print-edition/')
    for page in pages:
        prepared_url = os.path.join(req_url, '{}/{}'.format(page, _input[1]))
        resp = NDH.get_request_data(prepared_url)
        soup = NDH.get_bs4_object(resp)
        logging.debug("GETTING DATA OF PAGE {}".format(page))
        headlines = get_headlines(soup, page)

        for headline in tqdm(headlines):
            link = headline.a['href']
            detail_req = NDH.get_request_data(link)
            soup2 = NDH.get_bs4_object(detail_req)
            details_wrapper = get_details_wrapper(soup2)

            if details_wrapper:
                title = get_title(details_wrapper)
                subject = get_subject(details_wrapper)
                logging.debug("PROCESSING HEADLINE {}".format(title.encode('utf8')))
                image = get_main_image(details_wrapper)
                caption = get_image_caption(details_wrapper)
                # get artice body
                article_wrapper = get_description_body(details_wrapper)
                if article_wrapper:
                    description = get_description(article_wrapper)
                    generate_json(title, subject, image, caption, description)

    NDH.save_to_csv(TITLE, json_data)

if __name__ == '__main__':
    main()
