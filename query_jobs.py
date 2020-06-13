from collections import namedtuple

from Base import Base


class QueryJob:

    def __init__(self):
        self.base = Base()
        self.job_query_url = self.base.config['DEFAULT']['reed_jobs_url']
        self.Company = namedtuple('Company', ['id', 'name'])

    def run(self):
        for company in self.load_company():
            json = self.base.get_json_response(self.job_query_url, company.id)
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
