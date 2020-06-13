import logging
from collections import namedtuple

import requests

from Base import Base


class QueryJob:

    def __init__(self):
        self.base = Base()
        self.job_query_url = self.base.config['DEFAULT']['reed_jobs_url']
        self.Company = namedtuple('Company', ['id', 'name'])

    def run(self):
        for company in self.load_company():
            json = {}
            try:
                json = self.base.get_json_response(self.job_query_url, company.id)
            except requests.HTTPError as http_err:
                logging.error(f'Error fetching jobs for company {company}')
            print(f'>> {company.id}: {company.name}:')
            print(json)
            return

    def load_company(self):
        with open(self.base.ids_file) as f:
            for line in f.readlines():
                split = line.split(',')
                yield self.Company(id=split[0], name=split[1])


query = QueryJob()
query.run()
