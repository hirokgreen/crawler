# -*- coding: utf-8 -*-

import os, sys
import time
import csv
import requests
import bs4
import coloredlogs, logging
from user_agent import generate_user_agent
from TorCtl import TorCtl

coloredlogs.install(level='DEBUG')

class NewsDataCollectionHelper(object):
    def __init__(self):
        self.header =  {'User-agent': generate_user_agent()}

    def renew_identity(self):
        self.check_directory()
        try:
            conn = TorCtl.connect(controlAddr="127.0.0.1", controlPort=9051, passphrase="@hirok32")
            conn.send_signal("NEWNYM")
            conn.close()
        except:
            logging.critical("SOMETHINGS WENT WRONG!!, YOUR IP MAY BE BLOCKED IF CONTINUE. PLEASE EXIT AND BE SAFE")

    def get_request_data(self, url):
        self.renew_identity()
        resp = requests.get(url, headers=self.header)
        return resp

    def get_bs4_object(self, resp):
        return bs4.BeautifulSoup(resp.content, 'html.parser')

    def check_directory(self):
        directory = "data/"
        try:
            os.stat(directory)
        except OSError:
            logging.critical("YOU HAVEN'T CREATE /DATA DIRECTORY. PLEASE CREATE IT AND AFTER THAT RE-RUN THE SCRIPT")
            sys.exit()

    def save_to_csv(self, title, json_data):
        timestr = time.strftime("%Y%m%d-%H%M%S")
        directory = "data/{}/".format(title)
        try:
            try:
                os.stat(directory)
            except:
                os.mkdir(directory)
            fp = csv.writer(open(directory + title +'_'+ timestr + ".csv", "wb+"))
            fp.writerow(["SL", "title", "category", "sub_category", "subject", "image", "caption", "description"])
            for item in json_data:
                try:
                    item["category"]
                except:
                    item["sub_category"] = "N/A"
                try:
                    item["sub_category"]
                except:
                    item["sub_category"] = "N/A"
                fp.writerow([item["SL"], item["title"], item["category"], item["sub_category"],
                             item["subject"], item["image"], item["caption"], item["description"]])
            logging.debug("FINISHED DATA COLLECTION OF #{}. THANK YOU".format(title))
        except OSError:
            logging.critical("YOU HAVEN'T CREATE /DATA DIRECTORY. PLEASE CREATE IT AND THEN RE-RUN THE SCRIPT")
