from typing import List

def read_file(file: str) -> List[str]:
    with open(file) as f:
        return f.readlines()


def get_country_key(country: str) -> str:
    return ' '.join(country.split()).replace(' ', '_').lower()


def get_country_dict(country_row: str) -> dict:
    country_dict = {}
    en, ru = country_row.strip('\n').split(';')
    language = 'language'
    value = 'value'
    country_dict['key'] = get_country_key(en)
    country_dict['descriptions'] = [
        {
            language: 'en',
            value: en
        },
        {
            language: 'ru',
            value: ru
        }
    ]
    return country_dict


if __name__ == '__main__':
    content = read_file('countries.txt')
    countries = []
    for row in content:
        countries.append(get_country_dict(row))
    print(countries)