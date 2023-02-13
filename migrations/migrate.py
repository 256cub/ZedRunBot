import mysql.connector
import os
import re
from operator import itemgetter

from dotenv import load_dotenv

load_dotenv()  # take environment variables from .env file

DB_USER = os.environ.get('DB_USER')
DB_PASSWORD = os.environ.get('DB_PASSWORD')
DB_HOST = os.environ.get('DB_HOST')
DB_DATABASE = os.environ.get('DB_DATABASE')
APP_PATH = os.environ.get('APP_PATH')

cnx = mysql.connector.connect(user=DB_USER, password=DB_PASSWORD, host=DB_HOST, database=DB_DATABASE)
cursor = cnx.cursor()


def execute_scripts_from_file(filename):
    fd = open(filename, 'r')
    sql_file_to_process = fd.read()
    fd.close()
    sql_commands = sql_file_to_process.split(';')

    for command in sql_commands:
        try:
            if command.strip() != '':
                cursor.execute(command)
        except IOError as msg:
            print("Command skipped: ", msg)


dir_path = APP_PATH + 'migrations'

# list to store files
res = []

# Iterate directory
for path in os.listdir(dir_path):
    # check if current path is a file
    if os.path.isfile(os.path.join(dir_path, path)):
        res.append(path)

res.sort()
# print(res)

files = []
# files = dict()
for file in res:

    if '.sql' not in file:
        continue

    current = dict()

    parts = re.search('(\d+)_', file)

    file_id = parts.group(1)
    current['id'] = int(file_id)
    current['file'] = file

    files.append(current)

files.sort(key=itemgetter('id'), reverse=False)

for cycle, file in enumerate(files):
    sql_file = APP_PATH + 'migrations/' + file['file']

    print(' {} | {}'.format(cycle + 1, sql_file))
    execute_scripts_from_file(sql_file)

    cnx.commit()
