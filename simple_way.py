from pprint import pprint
import requests
import pandas as pd


def save_part(final_df, counter):
    try:
        filename = f'result_with_just_requests_{counter}.csv'
        final_df.to_csv(filename, encoding='utf-8', sep=';')
        print(f'file {filename} saved successfully')
    except IOError as exp:
        print(f'I/O error({exp.errno}): {exp.strerror}')


def get_requests(url):
    try:
        response = requests.get(url, headers={'x-requested-with': 'xmlhttprequest'})
        response.raise_for_status()
        if response.status_code == 200:
            return response
    except Exception as exp:
        print(exp, exp.args)


def main():
    page = 1
    final = pd.DataFrame()

    while True:
        url = f'https://xn--90adear.xn--p1ai/news/region?perPage=20&page={page}&region=65'

        response = get_requests(url)
        if response:
            json_data = response.json()
            items = response.json()['data']

            # convert parsed data from current page to pandas data-frame and put them to the final data-frame
            df = pd.DataFrame.from_records(items)
            final = pd.concat([final, df])

            page = json_data['paginator']['page'] + 1
            # each 10 page make back-up parsed data to the file
            backup_counter = page % 10
            if backup_counter == 0:
                save_part(final, backup_counter)

            totals = json_data['paginator']['total']
            per_page = json_data['paginator']['perPage']

            if totals // per_page + 1 < page:
                break


if __name__ == '__main__':
    main()
