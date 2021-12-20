#   ./venv/bin/python3

import requests
import sys
import random
import argparse
import traceback
from bs4 import BeautifulSoup
from pprint import pprint
from psycopg2 import connect, Error
from concurrent.futures import ThreadPoolExecutor, as_completed


def main():
    parser = argparse.ArgumentParser(
        description='This script will generate a company and insert it into a database.')
    parser.add_argument('-host', '--h', dest='host',
                        help='Database hostname', required=True)
    parser.add_argument('-database', '--d', dest='database',
                        help='Database name', required=True)
    parser.add_argument('-user', '--u', dest='user',
                        help='Database user', required=True)
    parser.add_argument('-password', '--p', dest='password',
                        help='Database password', required=True)
    parser.add_argument(
        '-table', '--t', dest='table', help='Database table name', required=True)
    parser.add_argument(
        '-state', '--s', dest='state', help='State of the company, default is a random value between all brazilian states abreviations', required=False,)
    parser.add_argument(
        '-age', '--a', dest='age', help='Age of the company, default is a random between 0 and 100', required=False, )
    parser.add_argument(
        '-mask', '--m', dest='mask', help='Data mask. Default value "S"', required=False)
    args = parser.parse_args()

    if 'state' not in args or not args.state:
        states = ['AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA', 'MT', 'MS',
                  'MG', 'PA', 'PB', 'PR', 'PE', 'PI', 'RJ', 'RN', 'RS', 'RO', 'RR', 'SC',
                  'SP', 'SE', 'TO']
        args.state = states[random.randint(0, len(states) - 1)]

    if 'age' not in args or not args.age:
        args.age = random.randint(1, 50)

    if 'mask' not in args or not args.mask:
        args.mask = 'S'

    host = args.host
    database = args.database
    user = args.user
    password = args.password
    table = args.table
    state = args.state
    age = args.age
    mask = args.mask

    genereated = []
    results = []

    if 'empresa' in table:
        with ThreadPoolExecutor() as executor:
            for i in range(30):
                genereated.append(executor.submit(companyGenerator, state, mask, age))
            for item in as_completed(genereated):
                results.append(executor.submit(parseHtml, item.result()))

    if 'pessoa' in table:
        with ThreadPoolExecutor() as executor:
            for i in range(30):
                results.append(executor.submit(personGenerator, mask, age))

    conn = connectDB(host, database, user, password)
    for item in as_completed(results):
        insertDB(conn, table, item.result())

    closeDBConn(conn)

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
        return conn
    except Error as e:
        print(e)
        sys.exit(1)


def insertDB(conn, table, dict_input):
    try:
        cur = conn.cursor()
        columns = [x.lower().replace(' ', '_') for x in dict_input.keys()]
        values = tuple(dict_input.values())
        if len(columns) == 0 and len(values) == 0:
            return
        query = f'INSERT INTO {table} ({", ".join(columns)}) VALUES {values}'
        cur.execute(query)
        conn.commit()
        cur.close()
    except Error as e:
        print(columns)
        print("\n")
        print(values)
        print(traceback.print_exc())
        sys.exit(1)


def companyGenerator(state, mask, age):
    url = "https://www.4devs.com.br/ferramentas_online.php"

    payload = f'acao=gerar_empresa&pontuacao={mask}&estado={state}&idade={age}'
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    if response.status_code != 200:
        print(f'Error {response.status_code}')
        pprint(response.text)
        sys.exit(1)

    return response.text

def personGenerator(mask, age):
    url = "https://www.4devs.com.br/ferramentas_online.php"

    payload=f'acao=gerar_pessoa&sexo=I&pontuacao={mask}&idade={age}&cep_estado=&txt_qtde=1&cep_cidade='
    headers = {
    'Content-Type': 'application/x-www-form-urlencoded'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

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
    main()
