from os import getcwd
from pathlib import Path
# Mysql
DB_HOST = 'localhost'
DB_USER = 'root'
DB_PASSWORD = ''
DB_NAME = 'spells'
SCHEMA_FILE = Path(getcwd(), 'schema.sql')

# Data
DATA_SOURCE = Path(getcwd(), 'spells.csv')


