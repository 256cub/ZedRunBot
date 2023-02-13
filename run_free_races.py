import time

import config
from termcolor import colored

from Main import *

timestamp = datetime.today()
timestamp = timestamp.strftime("%Y%m%d_%H%M%S")

# if random.randint(1, 5) == 1:
#     print()
#     print(' FETCH MY HORSES RAND 1 FROM 5 TIMES')
#
#     fetch_zed_run_stable_data(timestamp)

horse_classes = [1, 2, 3, 4, 5, 6]
horse_in_race = []

for horse_class in horse_classes:

    fetch_zed_run_future_race_data(timestamp, horse_class)
    races = get_races(status='open', horse_class=horse_class)

    print()
    print(' Found {} races for class {}'.format(len(races), horse_class))

    for race_cycle, race in enumerate(races):

        my_horse_id_available = detect_my_horses_not_in_race(timestamp)

        print(my_horse_id_available)

        my_horses = get_horses(horses_id=my_horse_id_available, horse_class=horse_class)

        if len(my_horses) == 0:
            print(colored(' No Horse available of Class {} '.format(horse_class), 'red'))
            break

        print(' {} Horse Available for class {}'.format(len(my_horses), horse_class))

        race_link = 'https://zed.run/racing/events?class={}&raceId={}'.format(race['class'], race['race_id'])

        races_has_horses = get_races_has_horses(race['race_id'])

        total_participants = len(races_has_horses) + 1

        print(colored('    {} | {} | Total: {} | {} '.format(race_cycle + 1, race['name'], total_participants, race_link), 'magenta'))

        if total_participants < config.POSITION_LIMIT:
            continue

        for my_horse in my_horses:

            if my_horse['horse_id'] in horse_in_race:
                continue

            position_career_first = calculate_my_possible_position(races_has_horses, my_horse, 'career_first')
            position_career_second = calculate_my_possible_position(races_has_horses, my_horse, 'career_second')
            position_career_third = calculate_my_possible_position(races_has_horses, my_horse, 'career_third')
            position_win_rate = calculate_my_possible_position(races_has_horses, my_horse, 'win_rate')
            position_rating = calculate_my_possible_position(races_has_horses, my_horse, 'rating')
            position_roi = calculate_my_possible_position(races_has_horses, my_horse, 'roi')

            good = 0
            bad = 0

            # if position_career_first >= total_participants / 2:
            #     bad = bad + 1
            # else:
            #     good = good + 1

            # if position_career_second >= total_participants / 2:
            #     bad = bad + 1
            # else:
            #     good = good + 1

            # if position_career_third >= total_participants / 2:
            #     bad = bad + 1
            # else:
            #     good = good + 1

            if position_win_rate >= total_participants / 2:
                bad = bad + 1
            else:
                good = good + 1

            if position_rating >= total_participants / 2:
                bad = bad + 1
            else:
                good = good + 1

            if position_roi >= total_participants / 2:
                bad = bad + 1
            else:
                good = good + 1

            good = calculate_rate_by_rating(good, bad, my_horse)

            if my_horse['roi'] == 0:
                good = good + 1

            if my_horse['win_rate'] == 0:
                good = good + 1

            if good >= bad:
                text_color = 'blue'
            else:
                text_color = 'white'

            print(colored('      1st: {} | 2nd: {} | 3th: {} | win_rate: {} | rating: {} | roi: {} | {} <> {} '.format(position_career_first, position_career_second, position_career_third, position_win_rate, position_rating, position_roi, good, bad), text_color))

            if good >= bad - 100:
                print('REGISTER TO RACE | {} | {} | {} | {} '.format(my_horse['hash_info_name'], my_horse['horse_id'], race_link, my_horse['hash_info_name']))

                free_gates = detect_free_gate(race['id'])
                print(free_gates)

                # webbrowser.open_new_tab(race_link)
                # webbrowser.open_new(race_link)
                # time.sleep(30)

                register_to_race(timestamp, free_gates, my_horse['horse_id'], race['race_id'])

                params = dict()
                params['horse_id'] = my_horse['horse_id']
                params['is_on_racing_contract'] = 1

                update_row_into_table('horses', params, 'horse_id')

                time.sleep(1)
                # fetch_zed_run_horse_data(timestamp, my_horse['horse_id'])

                horse_in_race.append(my_horse['horse_id'])

                # break

timestamp = datetime.today()
timestamp = timestamp.strftime("%Y%m%d_%H%M%S")

print(' FETCH MY HORSES FROM DB')

my_horses_id = get_my_horses_id(force=True)
for my_horse_id in my_horses_id:
    fetch_zed_run_horse_data(timestamp, my_horse_id['horse_id'])

print(' FETCH MY HORSES FROM STABLE')

fetch_zed_run_stable_data('123', owner_address=os.environ.get('MY_METAMASK_ADDRESS'))
