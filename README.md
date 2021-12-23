# bs4 scrapper

Beautiful Soup script to obtain data from a third party website. 
The goal of the script is to help IT professionals to manage dynamic data.

Beautiful Soup actual usage in this project is just to parse HTML from HTTP responses to extract data.

## Requirements

- [Python 3.6+](https://www.python.org/downloads/)
- [pip](https://pip.pypa.io/en/stable/)
- [beautifulsoup4](https://pypi.python.org/pypi/beautifulsoup4)
- [requests](https://pypi.python.org/pypi/requests)
- [psycopg2](https://pypi.python.org/pypi/psycopg2)
- [pymongo](https://pypi.python.org/pypi/pymongo)

## Usage

It's recomended the usage of a virtual environment.
```bash
$ python -m venv venv
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
$ python beautifulsoup_4devs.py --help
```
Help Menu Output:
```bash
usage: beautifulsoap_4devs.py [-h] [-host HOST] [-database DATABASE] [-user USER] [-password PASSWORD] [-collection COLLECTION]
                              [-table TABLE] [-state STATE] [-age AGE] [-mask {S,N}] [-outputDir OUTPUTDIR]

This script will generate a company and insert it into a database.

optional arguments:
  -h, --help            show this help message and exit
  -host HOST, --h HOST  Database hostname. If needed add port number after colon. Ex: localhost:5432
  -database DATABASE, --d DATABASE
                        Database name
  -user USER, --u USER  Database user
  -password PASSWORD, --p PASSWORD
                        Database password
  -collection COLLECTION, --c COLLECTION
                        Database collection
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
$ python beautifulsoup_4devs.py -host localhost -database test -user postgres -password postgres -table companies -state SP -age 20 -mask S
```

Example usage saving output to a file:
```bash
$ python beautifulsoup_4devs.py -host localhost -database test -user postgres -password postgres -table companies -state SP -age 20 -mask S -outputDir /home/user/output.json
```

# - Usage notes

You can only use one database at a time. When passing `-collection` as argument, the script doesn't expect a `-table` argument.

You can use `-outputDir` to save the output to a file. This feature is only available for .json and .csv files. Also, this feature can work with `-collection` option and `-table` option.