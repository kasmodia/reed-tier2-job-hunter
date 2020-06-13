import logging
from collections import namedtuple
from datetime import date

import requests

from base import Base


class JobQuery:

    def __init__(self):
        self.base = Base()
        self.job_query_url = self.base.config['DEFAULT']['reed_jobs_url']
        self.Company = namedtuple('Company', ['id', 'name'])

    def run(self):
        jobs = self.build_jobs_list()
        self.compose_email(jobs)
        self.send_email(jobs)

    def build_jobs_list(self):
        jobs = []
        for company in self.load_company():
            json_response = {}
            try:
                json_response = self.base.get_json_response(self.job_query_url, company.id, results_to_take=100)
            except requests.HTTPError:
                logging.error(f'Error fetching jobs for company {company}')

            company_jobs = json_response['results']
            self.filter_jobs(company_jobs, 'date', date.today().strftime("%d/%m/%y"))
            jobs.extend(company_jobs)
        return jobs

    def load_company(self):
        with open(self.base.ids_file) as f:
            for line in f.readlines():
                split = line.split(',')
                yield self.Company(id=split[0].strip(), name=split[1].strip())

    # TODO:
    def compose_email(self, jobs):
        pass

    # TODO:
    def send_email(self, jobs):
        pass

    @staticmethod
    def filter_jobs(jobs, key, value):
        jobs[:] = [job for job in jobs if job[key] == value]


query = JobQuery()
query.run()
