from Main import *

load_dotenv()  # take environment variables from .env file

timestamp = datetime.today()
timestamp = timestamp.strftime("%Y%m%d_%H%M%S")

print(' FETCH MY HORSES FROM DB')

my_horses_id = get_my_horses_id(force=True)
for my_horse_id in my_horses_id:
    fetch_zed_run_horse_data(timestamp, my_horse_id['horse_id'])

print(' FETCH MY HORSES FROM STABLE')

fetch_zed_run_stable_data('123', owner_address=os.environ.get('MY_METAMASK_ADDRESS'))
