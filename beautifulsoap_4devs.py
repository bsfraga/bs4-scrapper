#   ./venv/bin/python3
import argparse
import logging
import os
import random
import pymongo
import sys
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests
from bs4 import BeautifulSoup
from psycopg2 import connect


def main():
    parser = argparse.ArgumentParser(
        description='This script will generate a company and insert it into a database.')
    parser.add_argument('-host', '--h', dest='host', required=False, help='Database hostname. If needed add port number after colon. Ex: localhost:5432')
    parser.add_argument('-database', '--d', dest='database',
                        help='Database name', required=False)
    parser.add_argument('-user', '--u', dest='user',
                        help='Database user', required=False)
    parser.add_argument('-password', '--p', dest='password',
                        help='Database password', required=False)
    parser.add_argument('-collection', '--c', dest='collection',
                        required=False, help='Database collection')
    parser.add_argument(
        '-table', '--t', dest='table', help='Database table name', required=False)
    parser.add_argument(
        '-state', '--s', dest='state', help='State of the company, default is a random value between all brazilian states abreviations', required=False,)
    parser.add_argument(
        '-age', '--a', dest='age', help='Age of the company, default is a random between 0 and 50', required=False, )
    parser.add_argument(
        '-mask', '--m', dest='mask', help='Data mask. Default value "S"', required=False, choices=['S', 'N'])
    parser.add_argument('-outputDir', '--o', dest='outputDir',
                        help='Specifies where to store the output. Only .csv and .json are supported.', required=False)
    args = parser.parse_args()

    if 'state' not in args or not args.state:
        logging.info("No state specified. Using random value")
        states = ['AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA', 'MT', 'MS',
                  'MG', 'PA', 'PB', 'PR', 'PE', 'PI', 'RJ', 'RN', 'RS', 'RO', 'RR', 'SC',
                  'SP', 'SE', 'TO']
        args.state = states[random.randint(0, len(states) - 1)]

    if 'age' not in args or not args.age:
        logging.info("No age specified. Using random value")
        args.age = random.randint(1, 50)

    if 'mask' not in args or not args.mask:
        logging.info("No mask specified. Using default value")
        args.mask = 'S'

    host = args.host
    database = args.database
    user = args.user
    password = args.password
    table = args.table
    collection = args.collection
    state = args.state
    age = args.age
    mask = args.mask
    outputDir = args.outputDir

    logging.info(f"Starting application with parameters: {args}")

    if outputDir and outputDir.split('.')[-1] not in ['csv', 'json']:
        logging.error(
            f"{outputDir} is not a valid output file. Only .csv and .json are supported.")
        print(parser.print_help())
        sys.exit(1)

    if not host or not database or not user or not password or not table:
        logging.error(
            "To perform database persistence all database information required must be specified.")
        parser.print_help()
        logging.error("Exiting application.")
        sys.exit(1)
    else:
        if not collection:
            results = []
            if 'empresa' in table:
                results = companyTask(state, mask, age)

            if 'pessoa' in table:
                results = personTask(mask, age)

            conn = connectDB(host, database, user, password)
            for item in as_completed(results):
                insertDB(conn, table, item.result())

            closeDBConn(conn)

    if collection and not table:
        results = []
        if 'empresa' in collection:
            results = companyTask(state, mask, age)

        if 'pessoa' in collection:
            results = personTask(mask, age)

        mongo_client = connectMongo(host, database, user, password)

        for item in as_completed(results):
            insertDocument(mongo_client, collection, item.result())

        mongo_client.close()


def personTask(mask, age):
    results = []
    with ThreadPoolExecutor() as executor:
        for _ in range(30):
            results.append(executor.submit(personGenerator, mask, age))
    return results


def companyTask(state, mask, age):
    generated = []
    results = []
    with ThreadPoolExecutor() as executor:
        for _ in range(30):
            generated.append(executor.submit(
                companyGenerator, state, mask, age))
        for item in as_completed(generated):
            results.append(executor.submit(parseHtml, item.result()))
    return results


def saveIntoFile(data, outputDir):
    try:
        with open(outputDir, 'w') as f:
            if outputDir.split('.')[-1] == 'json':
                f.write(data)

            if outputDir.split('.')[-1] == 'csv':
                f.write(','.join(data.keys()))
                f.write('\n')
                for line in data.values():
                    f.write(','.join(line))
                    f.write('\n')
    except Exception:
        logging.warning("Error saving into file")
        logging.warning(f"{traceback.format_exc()}")
        print("Exiting application.")
        sys.exit(1)


def closeDBConn(conn):
    if conn:
        conn.close()


def connectDB(host, database, user, password):
    try:
        conn = connect(host=host,
                       database=database,
                       user=user,
                       password=password,
                       port=5432)
        logging.info(f"Connected to database at {host}")
        return conn
    except Exception:
        logging.error(f"Error connecting to database")
        logging.error(f"{traceback.format_exc()}")
        logging.warning(
            "Error connecting to database. Exiting application.\n Check log for more details.")
        sys.exit(1)


def connectMongo(host, username, password, database):
    try:
        client = pymongo.MongoClient(
            f"mongodb+srv://{username}:{password}@{host}/{database}?retryWrites=true&w=majority")
        logging.info(f"Connected to MongoDB at {host}")
        return client
    except Exception:
        logging.error(f"Error connecting to MongoDB")
        logging.error(f"{traceback.format_exc()}")
        logging.warning(
            "Error connecting to MongoDB. Exiting application.\n Check log for more details.")
        sys.exit(1)


def insertDocument(mongo_client, collection, data):
    try:
        mongo_client[collection].insert_one(data)
    except Exception:
        logging.error(f"Error inserting document into MongoDB")
        logging.error(f"{traceback.format_exc()}")
        logging.warning(
            "Error inserting document into MongoDB. Exiting application.\n Check log for more details.")


def insertDB(conn, table, dict_input):
    query = ''
    try:
        cur = conn.cursor()
        columns = [x.lower().replace(' ', '_') for x in dict_input.keys()]
        values = str([f"'{x}'" for x in dict_input.values()])
        values = values.replace('[', '').replace(']', '').replace('\"', '')
        logging.info(f"Inserted into database table {table}")
        if len(columns) == 0 and len(values) == 0:
            return
        query = f'INSERT INTO {table} ({", ".join(columns)}) VALUES ({values})'
        cur.execute(query)
        conn.commit()
        logging.info(f"Inserted {dict_input} into {table}")
        cur.close()
    except Exception:
        logging.warning("Error inserting into database")
        logging.warning(f"{traceback.format_exc()}")
        logging.info(query)


def companyGenerator(state, mask, age):
    url = "https://www.4devs.com.br/ferramentas_online.php"

    payload = f'acao=gerar_empresa&pontuacao={mask}&estado={state}&idade={age}'
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    if response.status_code != 200:
        logging.warning(f'Error {response.status_code} at companyGenerator')
        logging.warning(response.text)
        sys.exit(1)

    return response.text


def personGenerator(mask, age):
    url = "https://www.4devs.com.br/ferramentas_online.php"

    payload = f'acao=gerar_pessoa&sexo=I&pontuacao={mask}&idade={age}&cep_estado=&txt_qtde=1&cep_cidade='
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    if response.status_code != 200:
        logging.warning(f'Error {response.status_code} at personGenerator')
        logging.warning(response.text)
        sys.exit(1)

    return response.json()


def parseHtml(html):
    soup = BeautifulSoup(html, 'html.parser')
    dict_output = {}
    for div in soup.find_all('div', class_='row small-collapse'):
        key = div.find('input').get('id')
        value = str(div.find('input').get('value'))
        if key == 'ie':
            key = 'inscricao_estadual'
        dict_output[key] = value
    return dict_output


if __name__ == '__main__':

    logging.basicConfig(level=logging.INFO,
                        filename=f'{os.path.dirname(__file__)}/beautifulsoap_4devs.log', encoding='utf-8',
                        datefmt="%m/%d/%Y %I:%M:%S %p", format='%(asctime)s %(message)s')
    main()
