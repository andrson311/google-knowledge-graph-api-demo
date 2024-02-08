import os
import json
import requests
import argparse
import pandas as pd
from urllib.parse import urlencode
from tqdm import tqdm
from dotenv import load_dotenv

load_dotenv()
pd.set_option('max_colwidth', 150)
ROOT = os.path.dirname(__file__)

def get_knowledge_graph(query):
    try:
        endpoint = 'https://kgsearch.googleapis.com/v1/entities:search'
        params = {
            'query': query,
            'limit': 100,
            'indent': True,
            'key': os.getenv('KGS_API_KEY')
        }
        url = endpoint + '?' + urlencode(params)
        response = requests.get(url)
        return json.loads(response.text)
    except:
        return

def get_data(query):

    df = pd.DataFrame(columns=[
        'Name',
        'URL',
        'Description'
    ])

    result = get_knowledge_graph(query)
    
    if not result:
        return

    for res in tqdm(result['itemListElement']):
        try:
            name = res['result']['name']
            description = res['result']['detailedDescription']
        except:
            continue

        data = {}
        data['Name'] = name
        data['URL'] = description['url']
        data['Description'] = description['articleBody']
        df = pd.concat([df, pd.DataFrame.from_dict([data])])

    df.reset_index(inplace=True)
    df.pop('index')
    return df

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='QReturns from Google Knowledge Graph')
    parser.add_argument('-q', '--query', help='Provide query to search for in Google Knowledge Graph')
    args = parser.parse_args()

    info = get_data(args.query)
    info.to_csv(os.path.join(ROOT, 'GKG_results_for_' + args.query + '.csv'))
    print(info.head(50))