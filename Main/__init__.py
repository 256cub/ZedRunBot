import json
import os
import smtplib
from datetime import datetime, timedelta, tzinfo
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

import cloudscraper
import mysql.connector
import requests
from bs4 import BeautifulSoup as beauty
from discord_webhook import DiscordWebhook
from dotenv import load_dotenv

load_dotenv()  # take environment variables from .env file


class MySQL:
    def __init__(self):
        self.connection = mysql.connector.connect(
            host=os.environ.get('DB_HOST'),
            user=os.environ.get('DB_USER'),
            passwd=os.environ.get('DB_PASSWORD'),
            database=os.environ.get('DB_DATABASE'),
            auth_plugin="mysql_native_password"
        )

    def select(self, query):
        sql_cursor = self.connection.cursor(dictionary=True)
        sql_cursor.execute(query)
        sql_result = sql_cursor.fetchall()
        sql_cursor.close()
        return sql_result

    def select_single(self, query):
        sql_cursor = self.connection.cursor(dictionary=True)
        sql_cursor.execute(query)
        sql_result = sql_cursor.fetchone()
        sql_cursor.close()
        return sql_result

    def update(self, query):
        sql_cursor = self.connection.cursor()
        sql_cursor.execute(query)
        self.connection.commit()
        last_row = sql_cursor.fetchone()
        sql_cursor.close()
        return last_row

    def insert(self, query):
        sql_cursor = self.connection.cursor()
        sql_cursor.execute(query)
        self.connection.commit()
        last_row_id = sql_cursor.lastrowid
        sql_cursor.close()
        return last_row_id

    def close(self):
        self.connection.close()


class Zone(tzinfo):
    def __init__(self, offset, isdst, name):
        self.offset = offset
        self.isdst = isdst
        self.name = name

    def utcoffset(self, dt):
        return timedelta(hours=self.offset) + self.dst(dt)

    def dst(self, dt):
        return timedelta(hours=1) if self.isdst else timedelta(0)

    def tzname(self, dt):
        return self.name


def add_beauty_space(data, length=10):
    data = str(data)
    if len(data) < length:
        for i in range(1, length - len(data)):
            data = data + ' '

    return data


def check_if_row_exist(table, column_name, column_value):
    try:
        query = "SELECT * FROM `{}` WHERE `{}` = \"{}\"".format(table, column_name, column_value)

        result = MySQL().select_single(query)

        if result:
            return result['id']
        else:
            return False
    except Exception as exception:
        print(query)
        print(exception)


def check_if_row_exist_multiple(table, column_name, column_value):
    try:
        query = "SELECT * FROM `{}` WHERE `{}` = \"{}\" AND `{}` = \"{}\"".format(table, column_name[0], column_value[0], column_name[1], column_value[1])

        result = MySQL().select_single(query)

        if result:
            return result['id']
        else:
            return False
    except Exception as exception:
        print(query)
        print(exception)


def update_row_into_table(table, columns, match_column='id'):
    try:
        query = "UPDATE `{}` SET ".format(table)

        for column_id, column_name in enumerate(columns):
            if column_name == match_column:
                continue

            if columns[column_name] is None or columns[column_name] == 'None':
                continue

            query += "`{}` = \"{}\", ".format(column_name, columns[column_name])

        size = len(query)
        query = query[:size - 2]
        query += " WHERE `{}` = '{}' ".format(match_column, columns[match_column])

        return MySQL().update(query)
    except Exception as exception:
        print(query)
        print(exception)


def insert_row_into_table(table, columns):
    try:
        query = "INSERT INTO `{}` ".format(table)

        columns_name = []
        columns_value = []
        for column_name in columns:
            columns_name.append('`' + column_name + '`')
            if columns[column_name] == None:
                columns_value.append('0')
            else:
                columns_value.append('"' + str(columns[column_name]) + '"')

        query += " ({}) VALUES ({}) ".format(', '.join(columns_name), ', '.join(columns_value))

        return MySQL().insert(query)
    except Exception as exception:
        print(query)
        print(exception)


def make_api_calls(url, method, body=None, attempt=1):
    try:

        if method == 'GET':
            return requests.get(url)

        elif method == 'POST':
            return requests.post(url, json=body)

    except Exception as e:
        attempt = attempt + 1
        if attempt <= int(os.environ.get('API_RETRY_COUNT')):
            make_api_calls(url, method, body, attempt)
        else:
            print("Retry attempts exceeded..")
            raise


def fetch_zed_run_future_race_data(timestamp, class_id, min_fee=0, max_fee=0):
    url = 'https://zed-ql.zed.run/graphql/'
    cursor = 'null'
    query = """query{
    GetRaceByStatus(first:10, input: {class: """ + str(class_id) + """, fee: {max:{2}, min:{1}}, status: "open"}, after: {0}) {
        edges {
        cursor
        node {
        country
        country_code
        city
        name
        length
        start_time
        fee
        race_id
        weather
        status
        class
        prize_pool {
            first
            second
            third
            total 
            }
        horses {
            horse_id 
            finish_time
            final_position
            name
            gate
            owner_address
            bloodline
            gender
            breed_type
            gen
            coat
            hex_color
            img_url
            class
            rating
            races
            free_win_rate
            paid_win_rate
            stable_name
            win_rate
            career   
            } 
        }
        } 

        page_info {
            end_cursor
            has_next_page
        }
     }

    } """

    method_name = 'GetRaceByStatus'

    i = 0
    while True:
        after_query = query.replace('{0}', cursor).replace('{1}', str(min_fee)).replace('{2}', str(max_fee))
        response = make_api_calls(url, method='POST', body={'query': after_query})

        json_data = response.json()

        save_json_to_file(json_data, os.environ.get('APP_PATH') + 'json/{}/races/opened/{}.json'.format(timestamp, timestamp))

        edges = json_data['data'][method_name]['edges']

        for edge_cycle, edge in enumerate(edges):
            parse_data(edge['node'])

        cursor = '"' + json_data['data'][method_name]['page_info']['end_cursor'] + '"'

        has_next_page = json_data['data'][method_name]['page_info']['has_next_page']

        # print('PAGE {}'.format(i))
        i = i + 1

        if not has_next_page:
            break


def fetch_zed_run_horse(timestamp, horse_id):
    url = 'https://zed-ql.zed.run/graphql/'
    query = """query{
       GetHorse(horseId: {class: {0}}) {
           edges {
           cursor
           node {
           country
           country_code
           city
           name
           length
           start_time
           fee
           race_id
           weather
           status
           class
           prize_pool {
               first
               second
               third
               total 
               }
           horses {
               horse_id 
               finish_time
               final_position
               name
               gate
               owner_address
               bloodline
               gender
               breed_type
               gen
               coat
               hex_color
               img_url
               class
               rating
               races
               free_win_rate
               paid_win_rate
               stable_name
               win_rate
               career   
               } 
           }
           } 

           page_info {
               end_cursor
               has_next_page
           }
        }

       } """

    method_name = 'GetHorse'

    after_query = query.replace('{0}', horse_id)
    response = make_api_calls(url, method='POST', body={'query': after_query})
    json_data = response.json()

    save_json_to_file(json_data, os.environ.get('APP_PATH') + 'json/{}/horse/opened/{}.json'.format('test', horse_id))

    edges = json_data['data'][method_name]['edges']

    for edge_cycle, edge in enumerate(edges):
        parse_data(edge['node'])

    cursor = '"' + json_data['data'][method_name]['page_info']['end_cursor'] + '"'


def fetch_zed_run_races_data(timestamp):
    url = 'https://zed-ql.zed.run/graphql/'
    cursor = 'null'
    query = """query{
    get_race_results(first:10, input: {only_my_racehorses: false, classes: [2,3]}, after: {0}) {
        edges {
        cursor
        node {
        country
        country_code
        city
        name
        length
        start_time
        fee
        race_id
        weather
        status
        class
        prize_pool {
            first
            second
            third
            total 
            }
        horses {
            horse_id 
            finish_time
            final_position
            name
            gate
            owner_address
            bloodline
            gender
            breed_type
            gen
            coat
            hex_color
            img_url
            class
            rating
            races
            stable_name 
            win_rate
            career   
            } 
        }
        } 

        page_info {
            end_cursor
            has_next_page
        }
     }

    } """

    method_name = 'get_race_results'

    i = 0
    while True:
        after_query = query.replace('{0}', cursor)
        response = make_api_calls(url, method='POST', body={'query': after_query})
        json_data = response.json()

        save_json_to_file(json_data, os.environ.get('APP_PATH') + 'json/{}/races/all/{}.json'.format(timestamp, timestamp))

        edges = json_data['data'][method_name]['edges']

        for edge_cycle, edge in enumerate(edges):
            parse_data(edge['node'])

        cursor = '"' + json_data['data'][method_name]['page_info']['end_cursor'] + '"'

        has_next_page = json_data['data'][method_name]['page_info']['has_next_page']

        print('PAGE {}'.format(i))
        i = i + 1

        if not has_next_page:
            break


def fetch_zed_run_horse_stamina(timestamp, horse_id):
    url = 'https://api.zed.run/api/v1/horses/stamina/{}'.format(horse_id)

    headers = {'Authorization': 'Bearer ' + os.environ.get('ZED_RUN_BEARER_TOKEN'), 'Content-Type': 'application/json'}

    response = requests.get(url, headers=headers)

    save_json_to_file(response.json(), os.environ.get('APP_PATH') + 'json/{}/horses/stamina_{}.json'.format(timestamp, horse_id))

    return parse_horse_stamina(response.json(), horse_id)


def fetch_zed_run_stable_data(timestamp, owner_address=os.environ.get('MY_METAMASK_ADDRESS')):
    url = 'https://api.zed.run/api/v1/horses/get_user_horses?public_address={0}&offset={1}&gen\[\]=1&gen\[\]=268&sort_by=created_by_desc'

    offset = 0

    current_url = url.format(owner_address, offset)
    response = make_api_calls(current_url, method='GET')
    json_data = response.json()

    save_json_to_file(json_data, os.environ.get('APP_PATH') + 'json/{}/stable/{}.json'.format(timestamp, owner_address))

    for json_data_single in json_data:
        print(json_data_single['horse_id'])
        fetch_zed_run_horse_data(timestamp, json_data_single['horse_id'])


def fetch_zed_run_horse_data(timestamp, horse_id):
    url = 'https://api.zed.run/api/v1/horses/get/{0}'

    current_url = url.format(horse_id)

    response = make_api_calls(current_url, method='GET')
    json_data = response.json()

    save_json_to_file(json_data, os.environ.get('APP_PATH') + 'json/{}/horses/{}.json'.format(timestamp, horse_id))

    my_horses_ids = []
    for my_horses_id in get_my_horses_id():
        my_horses_ids.append(my_horses_id['horse_id'])

    data = parse_horse_data(json_data, horse_id)

    print(my_horses_ids)
    print(horse_id)

    if horse_id in my_horses_ids:
        print('STAMINA')
        fetch_zed_run_horse_stamina(timestamp, horse_id)

    return data


def parse_data(node):
    # countries
    table = 'countries'
    column_name = 'code'

    countries_columns = dict()
    countries_columns[column_name] = node['country']
    countries_columns['code'] = node['country_code']

    countries_id = check_if_row_exist(table, column_name, countries_columns[column_name])
    if not countries_id:
        countries_id = insert_row_into_table(table, countries_columns)

    # cities
    table = 'cities'
    column_name = 'name'

    cities_columns = dict()
    cities_columns[column_name] = node['city']
    cities_columns['countries_id'] = countries_id

    cities_id = check_if_row_exist_multiple(table, [column_name, 'countries_id'], [cities_columns[column_name], cities_columns['countries_id']])
    if not cities_id:
        cities_id = insert_row_into_table(table, cities_columns)

    # races_lengths
    table = 'races_lengths'
    column_name = 'name'

    races_lengths_columns = dict()
    races_lengths_columns[column_name] = node['length']

    races_lengths_id = check_if_row_exist(table, column_name, races_lengths_columns[column_name])
    if not races_lengths_id:
        races_lengths_id = insert_row_into_table(table, races_lengths_columns)

    # weathers
    table = 'weathers'
    column_name = 'name'

    weathers_columns = dict()
    weathers_columns[column_name] = node['weather']

    weathers_id = check_if_row_exist(table, column_name, weathers_columns[column_name])
    if not weathers_id:
        weathers_id = insert_row_into_table(table, weathers_columns)

    # races
    table = 'races'
    column_name = 'race_id'

    races_columns = dict()
    races_columns[column_name] = node['race_id']
    races_columns['name'] = node['name']
    races_columns['cities_id'] = cities_id
    races_columns['countries_id'] = countries_id
    races_columns['class'] = node['class']
    races_columns['fee'] = node['fee']
    races_columns['races_lengths_id'] = races_lengths_id
    races_columns['prize_pool_first'] = node['prize_pool']['first']
    races_columns['prize_pool_second'] = node['prize_pool']['second']
    races_columns['prize_pool_third'] = node['prize_pool']['third']
    races_columns['prize_pool_total'] = node['prize_pool']['total']
    races_columns['status'] = node['status']
    races_columns['weathers_id'] = weathers_id

    if node['start_time']:
        races_columns['start_time'] = datetime.strptime(node['start_time'], '%Y-%m-%dT%H:%M:%SZ')

    races_id = check_if_row_exist(table, column_name, races_columns[column_name])
    if not races_id:
        races_id = insert_row_into_table(table, races_columns)
    else:
        update_row_into_table(table, races_columns, column_name)
        races_id = check_if_row_exist(table, column_name, races_columns[column_name])

    if not races_id:
        print(races_id)
        exit()

    if node['horses'] and len(node['horses']) > 0:
        for horse in node['horses']:

            # bloodlines
            table = 'bloodlines'
            column_name = 'name'

            bloodlines_columns = dict()
            bloodlines_columns[column_name] = ['bloodline']

            bloodlines_id = check_if_row_exist(table, column_name, bloodlines_columns[column_name])
            if not bloodlines_id:
                bloodlines_id = insert_row_into_table(table, bloodlines_columns)

            # breeds_types
            table = 'breeds_types'
            column_name = 'name'

            breeds_types_columns = dict()
            breeds_types_columns[column_name] = horse['breed_type']

            breeds_types_id = check_if_row_exist(table, column_name, breeds_types_columns[column_name])
            if not breeds_types_id:
                breeds_types_id = insert_row_into_table(table, breeds_types_columns)

            # coats
            table = 'coats'
            column_name = 'name'

            coats_columns = dict()
            coats_columns[column_name] = horse['coat']

            coats_id = check_if_row_exist(table, column_name, coats_columns[column_name])
            if not coats_id:
                coats_id = insert_row_into_table(table, coats_columns)

            # genotypes
            table = 'genotypes'
            column_name = 'name'

            genotypes_columns = dict()
            genotypes_columns[column_name] = horse['gen']

            genotypes_id = check_if_row_exist(table, column_name, genotypes_columns[column_name])
            if not genotypes_id:
                genotypes_id = insert_row_into_table(table, genotypes_columns)

            # genders
            table = 'genders'
            column_name = 'name'

            genders_columns = dict()
            genders_columns[column_name] = horse['gender']

            genders_id = check_if_row_exist(table, column_name, genders_columns[column_name])
            if not genders_id:
                genders_id = insert_row_into_table(table, genders_columns)

            # owners
            table = 'users'
            column_name = 'owner_address'

            owners_columns = dict()
            owners_columns['address'] = horse[column_name]
            owners_columns['stable_name'] = horse['stable_name']

            owners_id = check_if_row_exist(table, 'address', owners_columns['address'])
            if not owners_id:
                owners_id = insert_row_into_table(table, owners_columns)

            # horses
            table = 'horses'
            column_name = 'horse_id'

            if not horse['career']:
                horses_id = fetch_zed_run_horse_data(horse['horse_id'])
            else:
                horses_columns = dict()
                # horses_columns[column_name] = horse[column_name]
                horses_columns['bloodlines_id'] = bloodlines_id
                horses_columns['breeds_types_id'] = breeds_types_id
                horses_columns['class'] = horse['class']
                horses_columns['name'] = horse['name']
                horses_columns['coats_id'] = coats_id
                horses_columns['genotypes_id'] = genotypes_id
                horses_columns['genders_id'] = genders_id
                horses_columns['hash_info_hex_code'] = horse['hex_color']
                horses_columns['horse_id'] = horse['horse_id']
                horses_columns['img_url'] = horse['img_url']
                horses_columns['owners_id'] = owners_id
                horses_columns['win_rate'] = horse['win_rate']
                horses_columns['rating'] = horse['rating']
                horses_columns['number_of_races'] = horse['races']

                if horse['career']:
                    career = horse['career'].split('/')

                    horses_columns['career_first'] = career[0]
                    horses_columns['career_second'] = career[1]
                    horses_columns['career_third'] = career[2]

                horses_id = check_if_row_exist(table, column_name, horses_columns[column_name])
                if not horses_id:
                    horses_id = insert_row_into_table(table, horses_columns)

            # races_has_horses
            table = 'races_has_horses'

            races_has_horses_columns = dict()
            races_has_horses_columns['races_id'] = races_id
            races_has_horses_columns['horses_id'] = horses_id
            races_has_horses_columns['gate'] = horse['gate']
            races_has_horses_columns['final_position'] = horse['final_position']
            races_has_horses_columns['finish_time'] = horse['finish_time']

            # delete_if_row_exist(table, 'races_id', races_id)
            # races_has_horses_id = insert_row_into_table(table, races_has_horses_columns)

            races_has_horses_id = check_if_row_exist_multiple(table, ['races_id', 'horses_id'], [races_id, horses_id])
            if not races_has_horses_id:
                races_has_horses_id = insert_row_into_table(table, races_has_horses_columns)


def parse_horse_data(horse, horse_id):
    # bloodlines
    table = 'bloodlines'
    column_name = 'name'

    bloodlines_columns = dict()
    bloodlines_columns[column_name] = horse['bloodline']

    bloodlines_id = check_if_row_exist(table, column_name, bloodlines_columns[column_name])
    if not bloodlines_id:
        bloodlines_id = insert_row_into_table(table, bloodlines_columns)

    # breeds_types
    table = 'breeds_types'
    column_name = 'name'

    breeds_types_columns = dict()
    breeds_types_columns[column_name] = horse['breed_type']

    breeds_types_id = check_if_row_exist(table, column_name, breeds_types_columns[column_name])
    if not breeds_types_id:
        breeds_types_id = insert_row_into_table(table, breeds_types_columns)

    # coats
    # table = 'coats'
    # column_name = 'name'
    #
    # coats_columns = dict()
    # coats_columns[column_name] = horse['coat']
    #
    # coats_id = check_if_row_exist(table, column_name, coats_columns[column_name])
    # if not coats_id:
    #     coats_id = insert_row_into_table(table, coats_columns)

    # genotypes
    table = 'genotypes'
    column_name = 'name'

    genotypes_columns = dict()
    genotypes_columns[column_name] = horse['genotype']

    genotypes_id = check_if_row_exist(table, column_name, genotypes_columns[column_name])
    if not genotypes_id:
        genotypes_id = insert_row_into_table(table, genotypes_columns)

    # genders
    table = 'genders'
    column_name = 'name'

    genders_columns = dict()
    genders_columns[column_name] = horse['horse_type']

    genders_id = check_if_row_exist(table, column_name, genders_columns[column_name])
    if not genders_id:
        genders_id = insert_row_into_table(table, genders_columns)

    # owners
    table = 'users'
    column_name = 'owner'

    owners_columns = dict()
    owners_columns['address'] = horse[column_name]

    if horse['owner_stable'] and horse['owner_stable'] != 0:
        owners_columns['stable_name'] = horse['owner_stable']

    if horse['owner_stable_slug'] and horse['owner_stable_slug'] != 0:
        owners_columns['stable_slug'] = horse['owner_stable_slug']

    owners_id = check_if_row_exist(table, 'address', owners_columns['address'])
    if not owners_id:
        owners_id = insert_row_into_table(table, owners_columns)

    # horses
    table = 'horses'
    column_name = 'horse_id'

    horses_columns = dict()
    horses_columns[column_name] = horse_id
    horses_columns['skin'] = horse['skin']
    horses_columns['owners_id'] = owners_id
    horses_columns['img_url'] = horse['img_url']
    horses_columns['rating'] = int(horse['rating'])
    horses_columns['super_coat'] = int(horse['super_coat'])
    horses_columns['number_of_races'] = horse['number_of_races']
    horses_columns['is_in_stud'] = int(horse['is_in_stud'])
    horses_columns['class'] = horse['class']
    horses_columns['type'] = horse['type']
    horses_columns['genotypes_id'] = genotypes_id
    horses_columns['genders_id'] = genders_id
    horses_columns['is_on_racing_contract'] = 0

    #   "last_stud_timestamp": 1659331439,
    # if horse['last_stud_timestamp']:
    #     horses_columns['last_stud_timestamp'] = datetime.strptime(horse['last_stud_timestamp'], '%Y-%m-%dT%H:%M:%SZ')

    horses_columns['breeding_counter'] = horse['breeding_counter']
    horses_columns['breeding_decay_level'] = horse['breeding_decay_level']
    horses_columns['last_stud_duration'] = horse['last_stud_duration']

    # horses_columns['fathers_id'] = fetch_horse_data(horse['father']['horse_id'])
    # horses_columns['mothers_id'] = fetch_horse_data(horse['mother']['horse_id'])

    horses_columns['bloodlines_id'] = bloodlines_id
    horses_columns['class'] = horse['class']
    horses_columns['tx'] = horse['tx']
    horses_columns['breeding_decay_limit'] = horse['breeding_decay_limit']
    horses_columns['win_rate'] = horse['win_rate']
    horses_columns['paid_win_rate'] = horse['paid_win_rate']
    horses_columns['mating_price'] = horse['mating_price']

    horses_columns['hash_info_color'] = horse['hash_info']['color']
    horses_columns['hash_info_hex_code'] = horse['hash_info']['hex_code']
    horses_columns['hash_info_name'] = horse['hash_info']['name']

    horses_columns['is_upgraded'] = int(horse['is_upgraded'])

    horses_columns['career_first'] = horse['career']['first']
    horses_columns['career_second'] = horse['career']['second']
    horses_columns['career_third'] = horse['career']['third']

    horses_columns['offspring_count'] = horse['offspring_count']
    horses_columns['parents_win_rate'] = horse['parents_win_rate']
    horses_columns['is_on_racing_contract'] = int(horse['is_on_racing_contract'])
    horses_columns['offspring_win_rate'] = horse['offspring_win_rate']
    horses_columns['is_approved_for_racing'] = int(horse['is_approved_for_racing'])

    horses_columns['breeds_types_id'] = breeds_types_id

    horses_columns['is_trial_horse'] = int(horse['is_trial_horse'])

    if horse['breeding_cycle_reset']:
        horses_columns['breeding_cycle_reset'] = datetime.strptime(horse['breeding_cycle_reset'], '%Y-%m-%dT%H:%M:%SZ')

    if horse['tx_date']:
        horses_columns['tx_date'] = datetime.strptime(horse['tx_date'], '%Y-%m-%dT%H:%M:%SZ')

    horses_columns['surface_preference'] = horse['surface_preference']

    horses_id = check_if_row_exist(table, column_name, horses_columns[column_name])
    if not horses_id:
        horses_id = insert_row_into_table(table, horses_columns)
    else:
        update_row_into_table(table, horses_columns, column_name)
        horses_id = check_if_row_exist(table, column_name, horses_columns[column_name])

    return horses_id


def parse_horse_stamina(horse, horse_id):
    # horses
    table = 'horses'
    column_name = 'horse_id'

    horses_columns = dict()
    horses_columns[column_name] = horse_id
    # horses_columns['current_fatigue'] = horse['current_fatigue']

    horses_columns['current_stamina'] = horse['current_stamina']

    # if horse['time_to_full_recovery']:
    #     horses_columns['time_to_full_recovery'] = datetime.strptime(horse['time_to_full_recovery'], '%Y-%m-%dT%H:%M:%SZ')

    return update_row_into_table(table, horses_columns, column_name)


def get_races(status='open', horse_class=False, not_older_than=5, is_free=True):
    try:

        date_to_check = datetime.today() - timedelta(minutes=not_older_than)
        date_to_check = date_to_check.strftime("%Y-%m-%d %H:%M:%S")

        if is_free:
            query = "SELECT races.*, cities.name AS city_name, countries.name AS country_name, countries.code AS country_code, weathers.name AS weather_name, races_lengths.name AS races_length_name FROM `races` LEFT JOIN cities ON cities.id = races.cities_id LEFT JOIN countries ON countries.id = races.countries_id LEFT JOIN races_lengths ON races_lengths.id = races.races_lengths_id LEFT JOIN weathers ON weathers.id = races.weathers_id  WHERE races.status = '{}' AND races.fee = 0 AND (races.date_created > '{}' OR races.date_updated > '{}') ".format(status, date_to_check, date_to_check)
        else:
            query = "SELECT races.*, cities.name AS city_name, countries.name AS country_name, countries.code AS country_code, weathers.name AS weather_name, races_lengths.name AS races_length_name FROM `races` LEFT JOIN cities ON cities.id = races.cities_id LEFT JOIN countries ON countries.id = races.countries_id LEFT JOIN races_lengths ON races_lengths.id = races.races_lengths_id LEFT JOIN weathers ON weathers.id = races.weathers_id  WHERE races.status = '{}' AND races.fee > 0 AND (races.date_created > '{}' OR races.date_updated > '{}')  ".format(status, date_to_check, date_to_check)

        if horse_class:
            query += " AND class = '{}'".format(horse_class)

        query += " ORDER BY races_lengths.name ASC"
        return MySQL().select(query)
    except Exception as exception:
        print(exception)


def get_races_has_horses(race_id, sort_by='roi'):
    try:
        query = "SELECT *, horses.name AS horse_name, ((horses.career_first * {} + horses.career_second * {} + horses.career_third * {} - horses.number_of_races * {}) * 100 / (horses.number_of_races * {})) AS roi FROM `races_has_horses` LEFT JOIN horses ON horses.id = races_has_horses.horses_id LEFT JOIN races ON races.id = races_has_horses.races_id WHERE races.race_id = '{}' ORDER BY {} DESC".format(os.environ.get('ROI_PRIZE_1'), os.environ.get('ROI_PRIZE_2'), os.environ.get('ROI_PRIZE_3'), os.environ.get('ROI_FEE'), os.environ.get('ROI_FEE'), race_id, sort_by)
        return MySQL().select(query)
    except Exception as exception:
        print(exception)


def get_horses(owner_address=os.environ.get('MY_METAMASK_ADDRESS'), horse_class=False, horses_id=None):
    try:
        query = "SELECT *, horses.name AS horse_name, ((horses.career_first * {} + horses.career_second * {} + horses.career_third * {} - horses.number_of_races * {}) * 100 / (horses.number_of_races * {})) AS roi FROM users LEFT JOIN horses ON horses.owners_id = users.id WHERE users.address = '{}' AND is_in_stud = 0 AND current_stamina > 91 ".format(os.environ.get('ROI_PRIZE_1'), os.environ.get('ROI_PRIZE_2'), os.environ.get('ROI_PRIZE_3'), os.environ.get('ROI_FEE'), os.environ.get('ROI_FEE'), owner_address)

        if horse_class:
            query += " AND class = '{}'".format(horse_class)

        if horses_id:
            query += ' AND ('
            for cycle, horse_id in enumerate(horses_id):
                if cycle > 0:
                    query += " OR "

                query += " horses.horse_id = '{}' ".format(horse_id)
            query += ' ) '

        query += " ORDER BY horses.id DESC"

        return MySQL().select(query)
    except Exception as exception:
        print(exception)


def get_my_horses_id(owner_address=False, horse_class=False, force=False):
    try:

        date_to_check = datetime.today() - timedelta(minutes=20)
        date_to_check = date_to_check.strftime("%Y-%m-%d %H:%M:%S")

        if force:
            query = "SELECT horses.horse_id FROM users LEFT JOIN horses ON horses.owners_id = users.id WHERE users.address = '{}' AND `is_on_racing_contract` = 0 ".format(owner_address)
        else:
            query = "SELECT horses.horse_id FROM users LEFT JOIN horses ON horses.owners_id = users.id WHERE users.address = '{}' AND `is_on_racing_contract` = 0 AND horses.date_updated > '{}' ".format(owner_address, date_to_check)

        if horse_class:
            query += " AND class = '{}'".format(horse_class)

        query += " ORDER BY horses.id DESC"

        return MySQL().select(query)
    except Exception as exception:
        print(exception)


def register_to_race(timestamp, gates, horse_id, race_id):
    if not gates:
        return False

    my_horse = get_horse_detail(horse_id)
    races_has_horses = get_races_has_horses(race_id)
    params = calculate_my_chances(races_has_horses, my_horse)

    url = 'https://racing-api.zed.run/api/v1/races/register'

    for gate_id in gates:
        data = dict(gate=gate_id, horse_id=horse_id, race_id=race_id)

        headers = {'Authorization': 'Bearer ' + os.environ.get('ZED_RUN_BEARER_TOKEN')}

        register_status_code = False

        try:

            scraper = cloudscraper.create_scraper(delay=20, browser='chrome')

            response = scraper.post(url, json=data, headers=headers)

            print(response.text)
            print(data)

            soup = beauty(response.text, "html.parser")
            soup = soup.find_all('script')

            print(soup)

            for data in soup:
                print(data.get_text())

            register_status_code = response.status_code

            print(register_status_code)

        except Exception as exception:
            print(exception)

        if register_status_code == 200:
            # playsound(os.environ.get('APP_PATH') + 'audio/sarsound.mp3')

            # data_discord = render_html_for_discord(register_status_code, register_response)
            # post_to_discord(data_discord)

            # email_subject = 'ZedRunBot | Register to FREE Race'
            # email_html_content = render_html_for_email(register_status_code, register_response, params, my_horse, races_has_horses)
            # send_email(email_subject, email_html_content)

            return True
        elif register_status_code == 422:

            if response.json()['error'] == 'horse already in a race':
                print('horse already in a race')
                return False

            if response.json()['error'] == 'stable owner already in race':
                print('stable owner already in race')
                return False

            return False
        else:

            email_subject = 'ZedRunBot | ERROR: Register to Race'
            email_html_content = render_html_for_email(register_status_code, response.text, params, my_horse)
            send_email(email_subject, email_html_content)

            return False


def detect_free_gate(race_id):
    try:
        query = "SELECT gate FROM races_has_horses WHERE races_id = '{}' ORDER BY gate;".format(race_id)
        gates = MySQL().select(query)

        free_gates = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
        for gate in range(1, 12):
            for g in gates:
                if g['gate'] == gate:
                    free_gates.remove(gate)

        return free_gates
    except Exception as exception:
        print(exception)


def get_horse_detail(horse_id):
    try:
        query = "SELECT *, ((horses.career_first * {} + horses.career_second * {} + horses.career_third * {} - horses.number_of_races * {}) * 100 / (horses.number_of_races * {})) AS roi FROM horses WHERE horse_id = '{}';".format(os.environ.get('ROI_PRIZE_1'), os.environ.get('ROI_PRIZE_2'), os.environ.get('ROI_PRIZE_3'), os.environ.get('ROI_FEE'), os.environ.get('ROI_FEE'), horse_id)
        return MySQL().select_single(query)
    except Exception as exception:
        print(exception)


def delete_if_row_exist(table, column_name, column_value):
    try:
        query = "DELETE FROM `{}` WHERE `{}` = \"{}\"".format(table, column_name, column_value)
        return MySQL().update(query)
    except Exception as exception:
        print(query)
        print(exception)


def post_to_discord(html):
    webhook = DiscordWebhook(url=os.environ.get('DISCORD_WEBHOOKS'), content=html, username='256cub', avatar_url='https://birdopolis.256cub.com/img/logo.png',  # embeds=embed
                             )

    webhook.tts
    response = webhook.execute()


def render_html_for_discord(status_code, data):
    if data:
        post = '**' + str(status_code) + '**'
        post += '\n\n'

        for key in data:
            post += '**' + str(key) + '** | ' + str(data[key])
            post += '\n'

        post += '[' + data['name'] + ' | ' + str(data['length']) + ' | ' + str(data['race_id']) + ' | ' + str(data['usd_fee']) + '](https://zed.run/racing/events?raceId=' + str(data['race_id']) + ')'
        post += '\n ➖➖➖➖➖➖➖➖ \n'

        return post

    return False


def save_json_to_file(json_date, file_path):
    return

    # For DEBUG purpose
    dir_path = os.path.dirname(file_path)

    path = Path(dir_path)
    path.mkdir(parents=True, exist_ok=True)

    # if not os.path.exists(dir_path):
    #     os.mkdir(dir_path)

    with open(file_path, 'w') as outfile:
        json.dump(json_date, outfile)


def get_eth_gas_now():
    url = 'https://www.etherchain.org/api/gasnow'

    response = requests.get(url)

    if response.status_code == 200:
        return response.json()
    else:
        return False


def calculate_my_possible_position(races_has_horses, my_horse, by_column):
    horses = []
    for races_has_horse in races_has_horses:
        current = dict()
        current['career_first_general'] = races_has_horse['career_first']
        current['career_second_general'] = races_has_horse['career_second']
        current['career_third_general'] = races_has_horse['career_third']
        current['career_first'] = races_has_horse['career_first'] * 100 / races_has_horse['number_of_races']
        current['career_second'] = races_has_horse['career_second'] * 100 / races_has_horse['number_of_races']
        current['career_third'] = races_has_horse['career_third'] * 100 / races_has_horse['number_of_races']
        current['win_rate'] = races_has_horse['win_rate']
        current['rating'] = races_has_horse['rating']
        current['roi'] = races_has_horse['roi']
        current['is_my_horse'] = False

        horses.append(current)

    current = dict()
    current['career_first_general'] = my_horse['career_first']
    current['career_second_general'] = my_horse['career_second']
    current['career_third_general'] = my_horse['career_third']
    current['career_first'] = my_horse['career_first'] * 100 / my_horse['number_of_races']
    current['career_second'] = my_horse['career_second'] * 100 / my_horse['number_of_races']
    current['career_third'] = my_horse['career_third'] * 100 / my_horse['number_of_races']
    current['win_rate'] = my_horse['win_rate']
    current['rating'] = my_horse['rating']
    current['roi'] = my_horse['roi']
    current['is_my_horse'] = True

    horses.append(current)

    horses = sorted(horses, key=lambda dct: dct[by_column], reverse=True)

    # for horse_position, horse in enumerate(horses):
    #     print(horse)

    for horse_position, horse in enumerate(horses):
        if horse['is_my_horse']:
            return horse_position + 1


def send_email(email_subject, email_html_content):
    try:
        message = MIMEMultipart("alternative", None, [MIMEText(email_html_content, 'html')])
        message['Subject'] = email_subject
        message['From'] = os.environ.get('SENDER_EMAIL')
        message['To'] = os.environ.get('RECEIVER_EMAIL')

        server = smtplib.SMTP(os.environ.get('SERVER'))
        server.ehlo()
        server.starttls()
        server.login(os.environ.get('SENDER_EMAIL'), os.environ.get('SENDER_PASSWORD'))
        server.sendmail(os.environ.get('SENDER_EMAIL'), os.environ.get('RECEIVER_EMAIL'), message.as_string())
        server.quit()

        # print('Email confirmation send {}'.format(datetime.strftime("%Y-%m-%d")))
        print('Email confirmation send {}'.format('OK'))
    except Exception as exception:
        print(exception)


def calculate_my_chances(races_has_horses, my_horse, sort_by='rating'):
    total_participants = len(races_has_horses) + 1

    position_career_first = calculate_my_possible_position(races_has_horses, my_horse, 'career_first')
    position_career_second = calculate_my_possible_position(races_has_horses, my_horse, 'career_second')
    position_career_third = calculate_my_possible_position(races_has_horses, my_horse, 'career_third')
    position_win_rate = calculate_my_possible_position(races_has_horses, my_horse, 'win_rate')
    position_rating = calculate_my_possible_position(races_has_horses, my_horse, 'rating')
    position_roi = calculate_my_possible_position(races_has_horses, my_horse, 'roi')

    races_has_horses = sorted(races_has_horses, key=lambda dct: dct[sort_by], reverse=True)

    result = dict()
    result['position_career_first'] = position_career_first
    result['position_career_second'] = position_career_second
    result['position_career_third'] = position_career_third
    result['position_win_rate'] = position_win_rate
    result['position_rating'] = position_rating
    result['position_roi'] = position_roi
    result['total_participants'] = total_participants
    result['races_has_horses'] = races_has_horses

    return result


def render_html_for_email(status_code, register_response, params, my_horse, races_has_horses=False):
    try:

        if races_has_horses:
            my_horse_not_in_list = False
            for race_has_horse in races_has_horses:
                if race_has_horse['horse_id'] == my_horse['horse_id']:
                    my_horse_not_in_list = True

            if not my_horse_not_in_list:
                races_has_horses.append(my_horse)

        post = '<html>'

        post += '<head>'

        post += '<style>table {font-family: arial, sans-serif;border-collapse: collapse;width: 100%;}td, th {border: 1px solid #dddddd;text-align: left;padding: 8px;}tr:nth-child(even) {background-color: #dddddd;} .my_horse {background-color: #D5D1D1;}</style>'

        post += '<meta charset="utf-8">'
        post += '<meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">'

        post += '<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@4.0.0/dist/css/bootstrap.min.css" integrity="sha384-Gn5384xqQ1aoWXA+058RXPxPg6fy4IWvTNh0E263XmFcJlSAwiGgFAW/dAiS6JXm" crossorigin="anonymous">'
        # post += '<script src="https://code.jquery.com/jquery-3.2.1.slim.min.js" integrity="sha384-KJ3o2DKtIkvYIK3UENzmM7KCkRr/rE9/Qpg6aAZGJwFDMVNA/GpGFF93hXpG5KkN" crossorigin="anonymous"></script>'
        # post += '<script src="https://cdn.jsdelivr.net/npm/popper.js@1.12.9/dist/umd/popper.min.js" integrity="sha384-ApNbgh9B+Y1QKtv3Rn7W3mgPxhU9K/ScQsAP7hUibX39j7fakFPskvXusvfa0b4Q" crossorigin="anonymous"></script>'
        # post += '<script src="https://cdn.jsdelivr.net/npm/bootstrap@4.0.0/dist/js/bootstrap.min.js" integrity="sha384-JZR6Spejh4U02d8jOt6vLEHfe/JQGiRRSQQxSfFWpi1MquVdAyjUar5+76PVCmYl" crossorigin="anonymous"></script>'
        post += '</head>'

        # race details
        data = races_has_horses[0]
        race_link = 'https://zed.run/racing/events?class={}&raceId={}'.format(data['class'], data['race_id'])

        post += '<h2><a href="' + race_link + '">' + data['name'] + '</a> '
        post += ' ' + str(data['prize_pool_first']) + '/'
        post += '' + str(data['prize_pool_second']) + '/'
        post += '' + str(data['prize_pool_third']) + '=>'
        post += '' + str(data['prize_pool_total']) + '</h2>'

        # race details

        # my chances to win
        post += '<h2>My Chances:</h2>'

        chances = ['position_career_first', 'position_career_second', 'position_career_third', 'position_win_rate', 'position_rating', 'position_roi']

        post += '<ul>'

        for chance in chances:
            if params[chance] <= params['total_participants'] / 2:
                text_color = 'green'
            # elif params[chance] > params['total_participants'] / 3:
            #     text_color = 'green'
            # elif params[chance] > params['total_participants'] / 2:
            #     text_color = 'blue'
            else:
                text_color = 'black'

            try:
                data = my_horse[chance.replace('position_', '')]
            except Exception as exception:
                print('HERE')
                data = ''

            post += '<li style="color:' + text_color + ';"><strong>' + chance + '</strong>: ' + str(params[chance]) + ' from ' + str(params['total_participants']) + ' => ' + str(data) + '</li>'

        post += '</ul>'
        post += '\n ➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖ \n'

        columns = ['races_id', 'horses_id', 'gate', 'final_position', 'finish_time', 'date_updated', 'date_created', 'horse_id', 'bloodlines_id', 'breeds_types_id', 'breeding_counter', 'breeding_decay_level', 'breeding_decay_limit', 'career_first', 'career_second', 'career_third', 'offspring_count', 'parents_win_rate', 'offspring_win_rate', 'breeding_cycle_reset', 'surface_preference', 'class', 'type', 'genotypes_id', 'hash_info_color', 'hash_info_hex_code', 'hash_info_name', 'is_upgraded', 'genders_id', 'img_url', 'name', 'is_approved_for_racing', 'is_in_stud', 'is_on_racing_contract', 'is_trial_horse', 'last_stud_duration', 'last_stud_timestamp', 'mating_price', 'next_breeding_date', 'number_of_races', 'owners_id', 'fathers_id', 'mothers_id', 'rating', 'super_coat', 'skin', 'coats_id', 'tx', 'tx_date', 'win_rate', 'paid_win_rate', 'current_fatigue', 'current_stamina', 'time_to_full_recovery', 'roi']
        columns_to_show = ['career_first', 'career_second', 'career_third', 'img_url', 'horse_name', 'number_of_races', 'rating', 'win_rate', 'roi']

        positions_by = ['roi', 'rating', 'win_rate', 'career_first', 'career_second', 'career_third']
        for position_by in positions_by:

            # my chances to win
            post += '<h2>Possible position by {}:</h2>'.format(position_by)
            post += '<table class="table table-bordered">'

            post += '<thead class="thead-dark">'
            post += '<tr>'

            if races_has_horses:
                for column_id, column_name in enumerate(races_has_horses[0]):

                    if column_id == 0:
                        post += '<th>#</th>'

                    if column_name in columns_to_show:
                        if column_name:
                            post += '<th>' + str(column_name) + '</th>'
                        else:
                            post += '<th> ERROR ' + column_name + '</th>'

            post += '</tr>'
            post += '</thead>'

            post += '<tbody>'

            races_has_horses = sort_associative_array_by_key(races_has_horses, position_by)
            for races_has_horse_id, races_has_horse in enumerate(races_has_horses):

                if races_has_horse['horse_id'] == my_horse['horse_id']:
                    post += '<tr class="my_horse">'
                else:
                    post += '<tr>'

                if 'horse_name' not in races_has_horse:
                    races_has_horse['horse_name'] = races_has_horse['hash_info_name']

                for column_id, column_name in enumerate(races_has_horse):

                    if column_name == 'horse_name' and not races_has_horse[column_name]:
                        races_has_horse[column_name] = races_has_horse['hash_info_name']

                    if column_id == 0:
                        post += '<th>' + str(races_has_horse_id + 1) + ' </th>'

                    if column_name == 'img_url':
                        post += '<th><a href="https://zed.run/racehorse/' + str(races_has_horse['horse_id']) + '"><img src="' + races_has_horse['img_url'] + '" style="width:32px;height:32px;"></a></th>'
                    elif column_name in columns_to_show:
                        if str(races_has_horse[column_name]):
                            post += '<th>' + str(races_has_horse[column_name]) + '</th>'
                        else:
                            post += '<th> ERROR ' + column_name + '</th>'
                post += '</tr>'

            post += '</tbody>'

            post += '</table>'  # my chances to win

        # my horse details
        post += '<h2>My Horse:</h2>'
        post += '<ul>'
        for my_horse_element_id, my_horse_element in enumerate(my_horse):
            post += '<li><strong>' + str(my_horse_element) + '</strong>: ' + str(my_horse[my_horse_element]) + '</li>'
        post += '</ul>'
        post += '\n ➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖ \n'
        # my horse details

        # register details
        post += '<h2>Register to race response: TODO</h2>'
        post += '<ul>'
        # for response_element_id, response_element in enumerate(register_response):
        #     post += '<li><strong>' + response_element + '</strong>: ' + str(register_response[response_element]) + '</li>'
        # post += '</ul>'
        post += '\n ➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖ \n'
        # register details

        post += '</html>'

        return post
    except Exception as exception:
        print(exception)
        exit()
        post = '<h1>' + str(status_code) + '</h1>'
        post += '<h2>' + str(register_response) + '</h2>'
        post += '<hr>'

        post += '<pre>' + str(exception) + '</pre>'
        post += '<hr>'

        post += '<pre>' + str(params) + '</pre>'
        post += '<hr>'

        post += '<pre>' + str(my_horse) + '</pre>'
        post += '<hr>'

        post += '<pre>' + str(races_has_horses) + '</pre>'
        post += '<hr>'

        return post


def get_my_open_races(address):
    try:
        query = "SELECT * FROM users LEFT JOIN horses ON horses.owners_id = users.id LEFT JOIN races_has_horses ON races_has_horses.horses_id = horses.id LEFT JOIN races ON races.id = races_has_horses.races_id WHERE users.address = '{}' AND (races.status IS NULL OR races.status = 'open');".format(address)
        return MySQL().select(query)
    except Exception as exception:
        print(exception)


def detect_my_horses_not_in_race(timestamp):
    my_horses_id = get_my_horses_id()

    # url = 'https://racing-api.zed.run/api/v1/races/horses/running_races?horse_ids[]=448484&horse_ids[]=434185&horse_ids[]=432408&horse_ids[]=374989&horse_ids[]=340882&horse_ids[]=149091'
    url = 'https://racing-api.zed.run/api/v1/races/horses/running_races'

    for cycle, my_horse_id in enumerate(my_horses_id):
        if cycle == 0:
            url += '?horse_ids[]={}'.format(my_horse_id['horse_id'])
        else:
            url += '&horse_ids[]={}'.format(my_horse_id['horse_id'])

    response = requests.get(url)
    response_json = response.json()
    save_json_to_file(response_json, os.environ.get('APP_PATH') + 'json/{}/horses/my_horses_in_races/{}.json'.format(timestamp, timestamp))

    available_for_race = []
    for result in response_json:

        if result == 'error':
            continue

        # TODO  here sometime error
        if not result or not result['running_races']:
            available_for_race.append(result['horse_id'])

    return available_for_race


def sort_associative_array_by_key(array_data, key, reverse=True):
    return sorted(array_data, key=lambda dct: dct[key], reverse=reverse)


def calculate_rate_by_rating(good, bad, my_horse):
    if my_horse['class'] == 1:
        if my_horse['rating'] >= int(os.environ.get('CLASS_1_MAX')) - 5:
            good = good + 3
        elif my_horse['rating'] >= int(os.environ.get('CLASS_1_MAX')) - 10:
            good = good + 2
        elif my_horse['rating'] >= int(os.environ.get('CLASS_1_MAX')) - 15:
            good = good + 1  # elif my_horse['rating'] <= os.environ.get('CLASS_1_MIN') + 5:  #     good = good - 3  # elif my_horse['rating'] <= os.environ.get('CLASS_1_MIN') + 10:  #     good = good - 2  # elif my_horse['rating'] <= os.environ.get('CLASS_1_MIN') + 15:  #     good = good - 1

    if my_horse['class'] == 2:
        if my_horse['rating'] >= int(os.environ.get('CLASS_2_MAX')) - 5:
            good = good + 3
        elif my_horse['rating'] >= int(os.environ.get('CLASS_2_MAX')) - 10:
            good = good + 2
        elif my_horse['rating'] >= int(os.environ.get('CLASS_2_MAX')) - 15:
            good = good + 1  # elif my_horse['rating'] <= os.environ.get('CLASS_2_MIN') + 5:  #     good = good - 3  # elif my_horse['rating'] <= os.environ.get('CLASS_2_MIN') + 10:  #     good = good - 2  # elif my_horse['rating'] <= os.environ.get('CLASS_2_MIN') + 15:  #     good = good - 1

    if my_horse['class'] == 3:
        if my_horse['rating'] >= int(os.environ.get('CLASS_3_MAX')) - 5:
            good = good + 3
        elif my_horse['rating'] >= int(os.environ.get('CLASS_3_MAX')) - 10:
            good = good + 2
        elif my_horse['rating'] >= int(os.environ.get('CLASS_3_MAX')) - 15:
            good = good + 1  # elif my_horse['rating'] <= os.environ.get('CLASS_3_MIN') + 5:  #     good = good - 3  # elif my_horse['rating'] <= os.environ.get('CLASS_3_MIN') + 10:  #     good = good - 2  # elif my_horse['rating'] <= os.environ.get('CLASS_3_MIN') + 15:  #     good = good - 1

    if my_horse['class'] == 4:
        if my_horse['rating'] >= int(os.environ.get('CLASS_4_MAX')) - 5:
            good = good + 3
        elif my_horse['rating'] >= int(os.environ.get('CLASS_4_MAX')) - 10:
            good = good + 2
        elif my_horse['rating'] >= int(os.environ.get('CLASS_4_MAX')) - 15:
            good = good + 1  # elif my_horse['rating'] <= os.environ.get('CLASS_4_MIN') + 5:  #     good = good - 3  # elif my_horse['rating'] <= os.environ.get('CLASS_4_MIN') + 10:  #     good = good - 2  # elif my_horse['rating'] <= os.environ.get('CLASS_4_MIN') + 15:  #     good = good - 1

    if my_horse['class'] == 5:
        if my_horse['rating'] >= int(os.environ.get('CLASS_5_MAX')) - 5:
            good = good + 3
        elif my_horse['rating'] >= int(os.environ.get('CLASS_5_MAX')) - 10:
            good = good + 2
        elif my_horse['rating'] >= int(os.environ.get('CLASS_5_MAX')) - 15:
            good = good + 1  # elif my_horse['rating'] <= os.environ.get('CLASS_5_MIN') + 5:  #     good = good - 3  # elif my_horse['rating'] <= os.environ.get('CLASS_5_MIN') + 10:  #     good = good - 2  # elif my_horse['rating'] <= os.environ.get('CLASS_5_MIN') + 15:  #     good = good - 1

    if my_horse['class'] == 6:
        if my_horse['rating'] >= int(os.environ.get('CLASS_6_MAX')) - 5:
            good = good + 3
        elif my_horse['rating'] >= int(os.environ.get('CLASS_6_MAX')) - 10:
            good = good + 2
        elif my_horse['rating'] >= int(os.environ.get('CLASS_6_MAX')) - 15:
            good = good + 1  # elif my_horse['rating'] <= os.environ.get('CLASS_6_MIN') + 5:  #     good = good - 3  # elif my_horse['rating'] <= os.environ.get('CLASS_6_MIN') + 10:  #     good = good - 2  # elif my_horse['rating'] <= os.environ.get('CLASS_6_MIN') + 15:  #     good = good - 1

    return good


def parse_horse_histories_data(node):
    # races_lengths
    table = 'races_lengths'
    column_name = 'name'

    races_lengths_columns = dict()
    races_lengths_columns[column_name] = node['race_length']

    races_lengths_id = check_if_row_exist(table, column_name, races_lengths_columns[column_name])
    if not races_lengths_id:
        races_lengths_id = insert_row_into_table(table, races_lengths_columns)

    # races_lengths
    table = 'horses_stats'
    column_name = 'race_id'

    horses_stats_columns = dict()
    horses_stats_columns[column_name] = node['race_id']
    horses_stats_columns['races_lengths_id'] = races_lengths_id
    horses_stats_columns['horse_id'] = node['horse_id']
    horses_stats_columns['entry_rating'] = node['entry_rating']

    if node['entry_fee'] == 'FREE':
        horses_stats_columns['entry_fee'] = 0
    else:
        horses_stats_columns['entry_fee'] = float(node['entry_fee'].replace('$', ''))

    horses_stats_columns['horse_class'] = node['horse_class']

    if node['horse_class'] == 'I':
        horses_stats_columns['horse_class'] = 1
    elif node['horse_class'] == 'II':
        horses_stats_columns['horse_class'] = 2
    elif node['horse_class'] == 'III':
        horses_stats_columns['horse_class'] = 3
    elif node['horse_class'] == 'IV':
        horses_stats_columns['horse_class'] = 4
    elif node['horse_class'] == 'V':
        horses_stats_columns['horse_class'] = 5
    elif node['horse_class'] == 'VI':
        horses_stats_columns['horse_class'] = 6
    elif node['horse_class'] == 'Griffin':
        horses_stats_columns['horse_class'] = -1
    elif node['horse_class'] == 'Discovery':
        horses_stats_columns['horse_class'] = 0
    elif node['horse_class'] == 'Tournament':
        horses_stats_columns['horse_class'] = 99

    horses_stats_columns['date_entry'] = node['date_entry']
    horses_stats_columns['position'] = node['position']

    if node['is_fire']:
        horses_stats_columns['is_fire'] = node['is_fire']

    horses_stats_columns['time_finish'] = node['time_finish']

    races_has_horses_id = check_if_row_exist(table, 'race_id', node['race_id'])
    if not races_has_horses_id:
        races_has_horses_id = insert_row_into_table(table, horses_stats_columns)
    else:
        update_row_into_table(table, horses_stats_columns, column_name)
        horses_id = check_if_row_exist(table, column_name, horses_stats_columns[column_name])
