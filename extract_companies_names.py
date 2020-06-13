def extract_tier2_company_names():
    lines = open('registry.txt', 'r').readlines()
    companies = []
    name = ''
    for line in lines:
        if ',' not in line:
            print(f"WARNING: {line} does not contain a comma")
            continue
        split = line.split(',')
        if split[0] == 'cls_008':
            name = split[1]
        else:
            if name != '' and split[1].startswith('Tier 2'):
                companies.append(name.strip())
                name = ''

    return companies


def main():
    companies = extract_tier2_company_names()
    with open('tier2_companies.txt', 'w') as output:
        for company in companies:
            output.write(f'{company}\n')

    print('file "tier2_companies.txt" is written successfully')


if __name__ == '__main__':
    main()
