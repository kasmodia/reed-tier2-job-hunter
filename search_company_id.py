import base64
import logging

import requests
from requests.auth import HTTPBasicAuth

KEY_FILE = 'REED_API_KEY'
REED_KEYWORD = 'https://www.reed.co.uk/api/1.0/search?keywords='


def save_company_id(company_name, company_id):
    with open('companies_ids.csv', 'a') as f:
        f.write(f'{company_id},{company_name}\n')


def get_company_id(company_name):
    with open(KEY_FILE) as f:
        api_key = f.readline()

    json = {}
    try:
        response = requests.get(f'{REED_KEYWORD}{company_name}&resultsToTake=5', auth=HTTPBasicAuth(api_key, ''))
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

            company_id = get_company_id(name)
            if company_id is not None:
                logging.info(f'an ID is found for company {name}')
                save_company_id(name, company_id)
            logging.info(f'{name} not found')


def generate_auth_header(api_key):
    base64string = base64.b64encode(f'{api_key}:'.encode())
    return b'Authorization: Basic %s' % base64string


if __name__ == '__main__':
    # File to log to
    logFile = 'crawler.log'

    # Setup File handler
    file_handler = logging.FileHandler(logFile)
    file_handler.setLevel(logging.INFO)

    # Setup Stream Handler (i.e. console)
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)

    # Get our logger
    app_log = logging.getLogger('root')
    app_log.setLevel(logging.INFO)

    # Add both Handlers
    app_log.addHandler(file_handler)
    app_log.addHandler(stream_handler)
    store_companies_ids(starting_from='Al-Emaan Centre')
