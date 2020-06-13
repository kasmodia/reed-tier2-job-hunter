import configparser
import logging

import requests
from requests.auth import HTTPBasicAuth


class Base:

    def __init__(self):
        self.init_logger()
        self.config = configparser.ConfigParser()
        self.config.read('crawler.ini')
        self.api_key = self.read_api_key()
        self.starting_from = self.config['DEFAULT']['start_id_search_from']
        self.tier_2_names_file = self.config['DEFAULT']['companies_names']
        self.ids_file = self.config['DEFAULT']['companies_ids']

    @staticmethod
    def init_logger():
        # File to log to
        log_file = 'crawler.log'
        logging.basicConfig(level=logging.DEBUG,
                            format='%(asctime)s %(name)-8s %(levelname)-8s %(message)s',
                            datefmt='%m-%d %H:%M',
                            filename=log_file,
                            filemode='w')
        # define a Handler which writes INFO messages or higher to the sys.stderr
        console = logging.StreamHandler()
        console.setLevel(logging.INFO)
        # set a format which is simpler for console use
        formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
        # tell the handler to use this format
        console.setFormatter(formatter)
        # add the handler to the root logger
        logging.getLogger('').addHandler(console)

    def read_api_key(self):
        key_file = self.config['DEFAULT']['api_key_file']
        with open(key_file) as f:
            key = f.readline()
        return key

    def get_json_response(self, url, company):
        json = {}
        try:
            response = requests.get(f'{url}{company}&resultsToTake=5', auth=HTTPBasicAuth(self.api_key, ''))
            response.raise_for_status()
            json = response.json()
        except requests.HTTPError as http_err:
            logging.error(f'HTTP error occurred: {http_err}')
            logging.error(f'response: {http_err.response.text}')
            self.set_config('start_id_search_from', company)
            raise http_err

        if 'results' not in json:
            logging.error('Unexpected response from Reed')
            logging.error(json)
            self.config['DEFAULT']['start_id_search_from'] = company
            raise requests.HTTPError()
        return json

    def set_config(self, key, value):
        self.config['DEFAULT'][key] = value
        with open('crawler.ini', 'w') as f:
            self.config.write(f)
