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

URL = 'https://www.dailyinqilab.com'
DATE = ''
TITLE = 'daily-inqilab'

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
                datetime.datetime.strptime(date, '%Y-%m-%d')
            else:
                date = ""
        except:
            logging.critical("INCORRECT DATE FORMAT, should be as YYYY-MM-DD")
            return False
    except:
        logging.critical("SOMETHINGS WENT WRONG!, Pleasee provide correct input")
        return False

    logging.debug("STARTED GETTING DATA FROM : {}".format(url))
    return url, date


def get_headlines(soup_parser):
    try:
        headlines = soup_parser.find("div", attrs={"class": "main_cont"}).find("div", attrs={"class": "bluebullet"}).find_all("li")
    except AttributeError:
        logging.warning("PAGE NOT AVAILABLE. COLLECTION OF DATA HAS BEEN FINISHED")
        sys.exit()
    return headlines


def get_details_wrapper(soup_object):
    try:
        wrapper = soup_object.find("div", attrs={"class": "home_top_left"})
    except:
        logging.warning("ERROR WHILE PARSING DETAILS")
        return False
    return wrapper


def get_title(body):
    try:
        title = body.find("h1").string
    except:
        return 'N/A'
    return title


def get_subject(body):
    try:
        subject = 'N/A'
    except:
        return 'N/A'
    return subject


def get_description_body(body):
    try:
        description = body.find("p").text
    except:
        return False
    return description


def get_main_image(body):
    try:
        image = body.find(
            "img", attrs={"class": "image-responsive2"}
        )["src"]
    except:
        return 'N/A'
    return image


def get_image_caption(body):
    try:
        caption = body.find(
            "img", attrs={"class": "image-responsive2"}
        )["alt"]
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
    req_url = os.path.join(base_url, 'archive/')
    resp = NDH.get_request_data(req_url)
    soup = NDH.get_bs4_object(resp)
    headlines = get_headlines(soup)
    logging.debug("GETTING DATA OF PAGE {}".format(req_url))
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
            description = get_description(details_wrapper)
            generate_json(title, subject, image, caption, description)

        NDH.save_to_csv(TITLE, json_data)


if __name__ == '__main__':
    main()
