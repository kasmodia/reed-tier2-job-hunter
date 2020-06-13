import base64
import configparser
import logging
import sys

import requests
from requests.auth import HTTPBasicAuth


def save_company_id(company_name, company_id):
    with open(ids_files, 'a') as f:
        f.write(f'{company_id},{company_name}\n')


def find_company_id(company_name):
    json = {}
    try:
        reed_url = config['DEFAULT']['ReedKeywordUrl']
        response = requests.get(f'{reed_url}{company_name}&resultsToTake=5', auth=HTTPBasicAuth(api_key, ''))
        response.raise_for_status()
        json = response.json()
    except requests.HTTPError as http_err:
        logging.error(f'HTTP error occurred: {http_err}')
        logging.error(f'response: {http_err.response.text}')
        config['DEFAULT']['StartIdSearchFrom'] = company_name
        sys.exit()
    except Exception as err:
        logging.error(f'Other error occurred: {err}')

    if 'results' not in json:
        logging.error('Unexpected response from Reed')
        logging.error(json)
        config['DEFAULT']['StartIdSearchFrom'] = company_name
        return

    for result in json['results']:
        if result.get('employerName').lower().strip() == company_name.lower().strip():
            logging.info(f'an ID is found for company {company_name}')
            return result.get('employerId')
    logging.info(f'{company_name} not found')


def read_api_key():
    key_file = config['DEFAULT']['ApiKeyFile']
    with open(key_file) as f:
        api_key = f.readline()
    return api_key


def store_companies_ids():
    get_started = True if starting_from is None else False
    with open(tier_2_names_file) as companies_names:
        companies_names = companies_names.readlines()
        for name in companies_names:
            # remove trailing \n
            name = name.strip()

            if starting_from == name:
                get_started = True

            if not get_started:
                continue

            company_id = find_company_id(name)
            if company_id is not None:
                save_company_id(name, company_id)
            elif config['DEFAULT']['ContinueOnError'] == 'False':
                return


def generate_auth_header():
    base64string = base64.b64encode(f'{api_key}:'.encode())
    return b'Authorization: Basic %s' % base64string


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


if __name__ == '__main__':
    init_logger()
    config = configparser.ConfigParser()
    config.read('crawler.ini')
    api_key = read_api_key()
    starting_from = config['DEFAULT']['StartIdSearchFrom']
    tier_2_names_file = config['DEFAULT']['CompaniesNames']
    ids_files = config['DEFAULT']['CompaniesIDs']
    store_companies_ids()
