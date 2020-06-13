import base64
import logging
from Base import Base


def store_company_id(company_name, company_id):
    with open(base.ids_file, 'a') as f:
        f.write(f'{company_id},{company_name}\n')


def fetch_company_id(company_name):
    keyword_url = base.config['DEFAULT']['reed_keyword_url']
    json = base.get_json_response(keyword_url, company_name)
    for result in json['results']:
        if result.get('employerName').lower().strip() == company_name.lower().strip():
            logging.info(f'an ID is found for company {company_name}')
            return result.get('employerId')
    logging.info(f'{company_name} not found')


def fetch_and_store_companies_ids():
    get_started = True if base.starting_from is None else False
    with open(base.tier_2_names_file) as companies_names:
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
    base64string = base64.b64encode(f'{base.api_key}:'.encode())
    return b'Authorization: Basic %s' % base64string


if __name__ == '__main__':
    base = Base()
    fetch_and_store_companies_ids()
