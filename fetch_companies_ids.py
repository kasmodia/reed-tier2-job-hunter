import base64
import logging
import sys

import requests

from base import Base


def store_company_id(company_name, company_id):
    logging.debug(f"Storing {company_name}'s ID {company_id} ..")
    with open(base.ids_file, 'a') as f:
        f.write(f'{company_id},{company_name}\n')


def fetch_company_id(company_name):
    logging.debug(f"Fetching {company_name}'s ID ..")
    keyword_url = base.config['DEFAULT']['reed_keyword_url']
    json = {}
    try:
        json = base.get_json_response(keyword_url, company_name)
    except requests.HTTPError as err:
        # save last queried company
        base.set_config('start_id_search_from', company_name)
        sys.exit()
    for result in json['results']:
        if result.get('employerName').lower().strip() == company_name.lower().strip():
            logging.info(f'an ID is found for company {company_name}')
            return result.get('employerId')
    logging.info(f'{company_name} not found')


def fetch_and_store_companies_ids():
    get_started = True if base.starting_from is None else False
    with open(base.tier_2_names_file) as companies_names:
        logging.debug(f'Reading {base.tier_2_names_file} ..')
        companies_names = companies_names.readlines()
        for name in companies_names:
            # remove trailing \n
            name = name.strip()

            if base.starting_from == name:
                get_started = True

            if not get_started:
                continue

            company_id = fetch_company_id(name)
            if company_id is not None:
                store_company_id(name, company_id)


def generate_auth_header():
    logging.debug('Generating Auth header ..')
    base64string = base64.b64encode(f'{base.api_key}:'.encode())
    return b'Authorization: Basic %s' % base64string


if __name__ == '__main__':
    logging.info('initializing Base ..')
    base = Base()
    logging.info('Fetching companies IDs ..')
    fetch_and_store_companies_ids()
