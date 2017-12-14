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

URL = 'http://www.bdlive24.com/home/allnewstitle'
DATE = ''
TITLE = 'BDLive24'

json_data = []


def generate_json(title, category, sub_category, subject, image, caption, description):
    title = title.encode('utf8')
    category = category.encode('utf8')
    sub_category = sub_category.encode('utf8')
    subject = subject.encode('utf8')
    caption = caption.encode('utf8')
    description = description.encode('utf8')
    json_data.append({"SL": len(json_data) + 1, "title": title,
                      "category": category, "sub_category": sub_category, 
                      "subject": subject, "image": image, "caption": caption,
                      "description": description})
    

def get_input():
    try:
        url = URL
        date = DATE
        if not validators.url(url):
            logging.critical("INCORRECT URl, should be as http://www.xxxxxx.xx")
            return False
        try:
            if date:
                datetime.datetime.strptime(date, '%Y-%m-%d')
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
        headlines = soup_parser.find_all(
            "div", attrs={"class": "container-fluid"}
        )[-1].find(
            "table", attrs={"class": "table"}
        ).find(
            'tbody'
        ).find_all('td')
    except AttributeError:
        logging.warning("PAGE {} NOT AVAILABLE. COLLECTION OF DATA HAS BEEN FINISHED".format(page + 1))
        return []
    return headlines

def get_category(headline):
    try:
        return headline.find("a", attrs={"class": "category"}).string
    except:
        return 'N/A'

def get_sub_category(soup_object):
    try:
        sub_category = soup_object.find("div", attrs={"class": "breadcrumb "}).find_all('li')[-1].a.string
    except:
        return 'N/A'
    return sub_category


def get_details_wrapper(soup_object):
    try:
        wrapper = soup_object.find("div", attrs={"class": "detail_widget"}).find("div", attrs={"class": "content_detail"})
    except:
        logging.warning("ERROR WHILE PARSING DETAILS")  
        return False   
    return wrapper


def get_title(body):
    try:
        title = body.find("div", attrs={"class": "right_title"}).h1.string
    except:
        return 'N/A'
    return title


def get_subject(body):
    try:
        subject = body.find("div", attrs={"class": "right_title"}).h2.string
    except:
        return 'N/A'
    return subject


def get_description_body(body):
    try:
        description = body.find(
            "div", attrs={"class": "detail_holder"}).find(
                "div", attrs={"class": "right_part"}).find(
                    "div", attrs={"itemprop": "articleBody"})
    except:
        return False
    return description


def get_main_image(body):
    try:
        image = body.img['src']
    except:
        return 'N/A'
    return 'http:' + image


def get_image_caption(body):
    try:
        caption = body.img['alt']
    except:
        return "N/A"
    return caption


def get_description(body):
    try:
        array = []
        paras = body.find_all('p')
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
    
    # process first 500 news
    for page in range(0, 550, 50):
        prepared_url = os.path.join(base_url, '{}'.format(page))
        resp = NDH.get_request_data(prepared_url)
        soup = NDH.get_bs4_object(resp)
        logging.debug("GETTING DATA OF PAGE {}".format(page + 1))        
        headlines = get_headlines(soup, page)
        for headline in tqdm(headlines[:-1]):
            link = headline.a['href']
            print link
    #         category = get_category(headline)
    #         detail_req = NDH.get_request_data(link)
    #         soup2 = NDH.get_bs4_object(detail_req)
    #         details_wrapper = get_details_wrapper(soup2)
    #         if details_wrapper:
    #             title = get_title(details_wrapper)
    #             sub_category = get_sub_category(soup2)
    #             subject = get_subject(details_wrapper)
    #             logging.debug("PROCESSING HEADLINE {}".format(title.encode('utf8')))
    #             image = get_main_image(details_wrapper)
    #             caption = get_image_caption(details_wrapper)
    #             # get artice body
    #             article_wrapper = get_description_body(details_wrapper)
    #             if article_wrapper:
    #                 description = get_description(article_wrapper)
    #                 generate_json(title, category, sub_category, subject, image, caption, description)
    # NDH.save_to_csv(TITLE, json_data)

if __name__ == '__main__':
    main()
