# -*- coding: utf-8 -*-

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
        return bs4.BeautifulSoup(resp.text, 'html.parser')
