# bs4 scrapper

Beautiful Soup script to obtain data from a third party website. 
The goal of the script is to help IT professionals to manage dynamic data.

## Requirements

- [Python 3.6+](https://www.python.org/downloads/)
- [pip](https://pip.pypa.io/en/stable/)
- [beautifulsoup4](https://pypi.python.org/pypi/beautifulsoup4)
- [requests](https://pypi.python.org/pypi/requests)
- [psycopg2](https://pypi.python.org/pypi/psycopg2)

## Usage

It's recomended the usage of a virtual environment.
```bash
$ python3 -m venv venv
```

Activating the virtual environment:
- Linux/Mac
```bash
$ source venv/bin/activate
```
- Windows
```cmd
$ venv\Scripts\activate
```

Installing requirements
```bash
$ pip install -r requirements.txt
```

Help Menu
```bash
$ python3 beautifulsoup_4devs.py --help
```
Help Menu Output:
```bash
usage: beautifulsoap_4devs.py [-h] [-host HOST] [-database DATABASE] [-user USER] [-password PASSWORD] [-table TABLE] [-state STATE] [-age AGE]
                              [-mask {S,N}] [-outputDir OUTPUTDIR]

This script will generate a company and insert it into a database.

optional arguments:
  -h, --help            show this help message and exit
  -host HOST, --h HOST  Database hostname
  -database DATABASE, --d DATABASE
                        Database name
  -user USER, --u USER  Database user
  -password PASSWORD, --p PASSWORD
                        Database password
  -table TABLE, --t TABLE
                        Database table name
  -state STATE, --s STATE
                        State of the company, default is a random value between all brazilian states abreviations
  -age AGE, --a AGE     Age of the company, default is a random between 0 and 50
  -mask {S,N}, --m {S,N}
                        Data mask. Default value "S"
  -outputDir OUTPUTDIR, --o OUTPUTDIR
                        Specifies where to store the output. Only .csv and .json are supported.
```

Example Usage using database persistance:
```bash
$ python3 beautifulsoup_4devs.py -host localhost -database test -user postgres -password postgres -table companies -state SP -age 20 -mask S
```

Example usage saving output to a file:
```bash
$ python3 beautifulsoup_4devs.py -host localhost -database test -user postgres -password postgres -table companies -state SP -age 20 -mask S -outputDir /home/user/output.json
```