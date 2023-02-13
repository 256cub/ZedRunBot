from termcolor import colored

from Main import *

timestamp = datetime.today()
timestamp = timestamp.strftime("%Y%m%d_%H%M%S")

# if random.randint(1, 5) == 1:
#     print()
#     print(' FETCH MY HORSES')
#
#     fetch_zed_run_stable_data(timestamp)

eth_gas_now = get_eth_gas_now()
eth_usd_price = eth_gas_now['data']['priceUSD']

min_fee = 1 / eth_usd_price
max_fee = 5 / eth_usd_price

my_horse_id_available = detect_my_horses_not_in_race(timestamp)

my_horses = get_horses(horses_id=my_horse_id_available)

print()
print(' TOTAL HORSES: ' + colored('{} '.format(len(my_horses)), 'green'))

for my_horse in my_horses:
    horse_with_error = False

    if my_horse['name']:
        my_horse_name = my_horse['name']
    else:
        my_horse_name = my_horse['hash_info_name']

    print()
    print(colored(' {} | CLASS {} | RATING {} | {}/{}/{} | {} % '.format(my_horse_name, my_horse['class'], my_horse['rating'], my_horse['career_first'], my_horse['career_second'], my_horse['career_third'], my_horse['win_rate']), 'green'))
    print()

    fetch_zed_run_future_race_data(timestamp, my_horse['class'], min_fee=min_fee, max_fee=max_fee)
    races = get_races(status='open', horse_class=my_horse['class'], is_free=False)

    print(' Found {} races'.format(len(races)))

    for race_cycle, race in enumerate(races):

        if horse_with_error:
            break

        race_link = 'https://zed.run/racing/events?class={}&raceId={}'.format(race['class'], race['race_id'])

        races_has_horses = get_races_has_horses(race['race_id'])

        total_participants = len(races_has_horses) + 1

        print(colored(' {} | {} | Total: {} | {} '.format(race_cycle + 1, race['name'], total_participants, race_link), 'magenta'))

        if total_participants < int(os.environ.get('POSITION_LIMIT')):
            continue

        position_career_first = calculate_my_possible_position(races_has_horses, my_horse, 'career_first')
        position_career_second = calculate_my_possible_position(races_has_horses, my_horse, 'career_second')
        position_career_third = calculate_my_possible_position(races_has_horses, my_horse, 'career_third')
        position_win_rate = calculate_my_possible_position(races_has_horses, my_horse, 'win_rate')
        position_rating = calculate_my_possible_position(races_has_horses, my_horse, 'rating')
        position_roi = calculate_my_possible_position(races_has_horses, my_horse, 'roi')

        good = 0
        bad = 0

        # if position_career_first > total_participants / 2:
        #     bad = bad + 1
        # else:
        #     good = good + 1

        # if position_career_second > total_participants / 2:
        #     print('       BAD | {} from {}'.format(position_career_second, total_participants))
        #     bad = bad + 1
        # else:
        #     print(colored('       OK | {} from {}'.format(position_career_second, total_participants), 'green'))
        #     good = good + 1
        #
        # if position_career_third > total_participants / 2:
        #     print('       BAD | {} from {}'.format(position_career_third, total_participants))
        #     bad = bad + 1
        # else:
        #     print(colored('       OK | {} from {}'.format(position_career_third, total_participants), 'green'))
        #     good = good + 1

        # if position_win_rate > total_participants / 2:
        # print('     BAD | {} from {}'.format(position_win_rate, total_participants))
        # bad = bad + 1
        # else:
        # print(colored('     OK | {} from {}'.format(position_win_rate, total_participants), 'green'))
        # good = good + 1

        if position_rating >= total_participants / 2:
            bad = bad + 1
        else:
            good = good + 1

        if position_roi >= total_participants / 2:
            bad = bad + 1
        else:
            good = good + 1

        good = calculate_rate_by_rating(good, bad, my_horse)

        if good >= bad:
            text_color = 'blue'
        else:
            text_color = 'white'

        print(colored('    1st: {} | 2nd: {} | 3th: {} | win_rate: {} | rating: {} | roi: {} '.format(position_career_first, position_career_second, position_career_third, position_win_rate, position_rating, position_roi), text_color))

        if good >= bad:
            print('TO REGISTER')

            # my_horse = get_horse_detail(my)
            races_has_horses = get_races_has_horses(race['id'])
            params = calculate_my_chances(races_has_horses, my_horse)

            email_subject = 'ZedRunBot | Register to PAID Race'
            email_html_content = render_html_for_email(1, [], params, my_horse, races_has_horses)
            send_email(email_subject, email_html_content)

            break
