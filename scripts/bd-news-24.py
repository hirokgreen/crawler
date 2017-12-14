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

URL = 'https://bangla.bdnews24.com/news/'
DATE = ''
TITLE = 'BDNews24'

json_data = []


def generate_json(title, category, subject, image, caption, description):
    title = title.encode('utf8')
    subject = subject.encode('utf8')
    caption = caption.encode('utf8')
    description = description.encode('utf8')
    category = category.encode('utf8')
    json_data.append(
        {"SL": len(json_data) + 1, "title": title, "category": category, "subject": subject,
        "image": image, "caption": caption, "description": description})
    

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
        headlines = soup_parser.find(
            "div", attrs={"id": "content"}).find(
                "div", attrs={"class": "content"}).find_all("li")
    except AttributeError:
        logging.warning("PAGE NOT AVAILABLE. COLLECTION OF DATA HAS BEEN FINISHED")
        return []
    return headlines


def get_details_wrapper(soup_object):
    try:
        wrapper = soup_object.find(
            "div", attrs={"id": "content"}
        ).find(
            "div", attrs={"id": "areas"}
        ).find(
            "div", attrs={"id": "main"}
        )
    except:
        logging.warning("ERROR WHILE PARSING DETAILS")
        return False
    return wrapper


def get_title(body):
    try:
        title = body.find(
            "div", attrs={"id": "news-details-page"}
        ).find("h1").string
    except:
        return 'N/A'
    return title


def get_subject(body):
    try:
        subject = body.find(
            "div", attrs={"class": "article_lead_text"}
        ).find(
            "h5", attrs={"class": "print-only"}
        ).string
    except:
        return 'N/A'
    return subject


def get_description_body(body):
    try:
        description = body.find(
            "div", attrs={"class": "wrappingContent"}
        ).find(
            "div", attrs={"class": "custombody"}
        )
    except:
        return False
    return description


def get_main_image(body):
    try:
        images = []
        main_image = body.find(
            "div", attrs={"id": "gallery_page_customize"}
        ).find(
            "div", attrs={"class": "media"}
        ).find(
            "img"
        )['src']
        
        images.append(main_image)

        other_images = body.find(
            "div", attrs={"class": "wrappingContent"}
        ).find_all(
            "img"
        )
        
        for item in other_images:
            images.append(item['src'])
    except:
        return 'N/A'
    return ', '.join(images)


def get_image_caption(body):
    try:
        caption = body.find(
            "h5", attrs={"class": " print-only"}
        ).text
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
    resp = NDH.get_request_data(base_url)
    soup = NDH.get_bs4_object(resp)
    logging.debug("GETTING DATA OF PAGE {}".format(base_url))
    headlines = get_headlines(soup)
    for headline in tqdm(headlines):
        heading = headline.find_all('a')
        category = heading[1].find("span").string
        link = heading[0].__dict__['attrs']['href']
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

                generate_json(title, category, subject, image, caption, description)

    NDH.save_to_csv(TITLE, json_data)


if __name__ == '__main__':
    main()
