import logging
from collections import namedtuple

import requests

from base import Base
from job import Job


class JobQuery:

    def __init__(self):
        self.base = Base()
        self.job_query_url = self.base.config['DEFAULT']['reed_jobs_url']
        self.Company = namedtuple('Company', ['id', 'name'])

    def run(self):
        jobs = self.build_jobs_list()
        self.init_email(jobs)
        self.send_email(jobs)

    def build_jobs_list(self):
        jobs = []
        for company in self.load_company():
            json = {}
            try:
                json = self.base.get_json_response(self.job_query_url, company.id, results_to_take=10)
            except requests.HTTPError:
                logging.error(f'Error fetching jobs for company {company}')

            job = Job(job_id=json['job_id'], job_title=json['job_title'], job_description=json['job_description'],
                      employer_name=json['employer_name'], location=json['location'], date=json['date'],
                      url=json['url'])
            jobs.append(job)
        return jobs

    def load_company(self):
        with open(self.base.ids_file) as f:
            for line in f.readlines():
                split = line.split(',')
                yield self.Company(id=split[0].strip(), name=split[1].strip())


query = JobQuery()
query.run()
