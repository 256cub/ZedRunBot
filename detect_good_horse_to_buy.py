import random
from termcolor import colored

from Main import *

load_dotenv()  # take environment variables from .env file

try:

    timestamp = datetime.today()
    timestamp = timestamp.strftime("%Y%m%d_%H%M%S")

    token_id = random.randint(1, 407843)

    fetch_zed_run_horse_data(timestamp, token_id)
    horse_detail = get_horse_detail(token_id)

    cost = horse_detail['number_of_races'] * int(os.environ.get('ROI_FEE'))
    income = horse_detail['career_first'] * os.environ.get('ROI_PRIZE_1') + horse_detail['career_second'] * os.environ.get('ROI_PRIZE_2') + horse_detail['career_third'] * os.environ.get('ROI_PRIZE_3')
    profit = income - cost

    if cost:
        roi = profit * 100 / cost

    url = 'https://opensea.io/assets/matic/0xa5f1ea7df861952863df2e8d1312f7305dabf215/{}'.format(token_id)

    price = 0.003

    color = 'red'
    if cost and horse_detail['number_of_races'] > 10:
        if roi > 50:
            color = 'green'
            price = 0.0042
            send_email('Very High 50 < ROI Horse', '<h2>' + url + '</h2><h3>' + str(roi) + '</h3>')
        elif roi > 0:
            color = 'blue'
            price = 0.004
            send_email('Good 0 < ROI Horse', '<h2>' + url + '</h2><h3>' + str(roi) + '</h3>')
        elif roi < -50:
            color = 'red'
            price = 0.003
        else:
            color = 'red'
            price = 0.0032

    print(colored('Horse ID: {} | Price: {} | ROI: {}'.format(token_id, price, roi), color))

except Exception as exception:
    print(exception)
