import base64
import logging

import requests
from requests.auth import HTTPBasicAuth


def save_company_id(company_name, company_id):
    with open('companies_ids.csv', 'a') as f:
        f.write(f'{company_id},{company_name}\n')


def find_company_id(company_name):
    json = {}
    try:
        response = requests.get(f'{REED_KEYWORD}{company_name}&resultsToTake=5', auth=HTTPBasicAuth(API_KEY, ''))
        response.raise_for_status()
        json = response.json()
    except requests.HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')
    except Exception as err:
        print(f'Other error occurred: {err}')

    if 'results' not in json:
        logging.error('Unexpected response from Reed')
        logging.error(json)
        raise Exception()

    for result in json['results']:
        if result.get('employerName').lower().strip() == company_name.lower().strip():
            return result.get('employerId')


def read_api_key():
    with open(KEY_FILE) as f:
        api_key = f.readline()
    return api_key


def store_companies_ids(starting_from=None):
    get_started = True if starting_from is None else False
    with open('tier2_companies.txt') as companies_names:
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
                logging.info(f'an ID is found for company {name}')
                save_company_id(name, company_id)
            logging.info(f'{name} not found')
            return


def generate_auth_header():
    base64string = base64.b64encode(f'{API_KEY}:'.encode())
    return b'Authorization: Basic %s' % base64string


def init_logger():
    # File to log to
    log_file = 'crawler.log'
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
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
    KEY_FILE = 'REED_API_KEY'
    REED_KEYWORD = 'https://www.reed.co.uk/api/1.0/search?keywords='
    API_KEY = read_api_key()
    init_logger()
    store_companies_ids(starting_from='Al-Emaan Centre')
