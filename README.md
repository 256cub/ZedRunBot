# ZedRunBot

Retrieves horse racing data by calling zed.run apis and store them to MySQL Database.
> API documentation is here: https://docs.zed.run/racing/getraceresults


### STEPS
 - cp env.local to .env and set DB credits
 - pip install -r requirement
 - pip install email-to
 - pip install discord-webhook
 - pip install pygobject
 - python migrations/migrate.py => will create all needed DB tables
 - a Bearer Token is needed, login into your ZedRun account and open Network(F12) and search for "authorization: Bearer {_LONG_STRING_}" and then set it in your .env
   - Bearer Token is valid 30 days, so each month you have to update the Token in .env
 



### Check FREE Races and Register if any ok
*/10 * * * * /usr/bin/python /PYTHON/ZedRunBot/run_free_races.py  > /PYTHON/ZedRunBot/logs/$(date +\%Y\%m\%d\%H\%M\%S).txt

### Fetch my horses from DB and Stable
33 * * * * /usr/bin/python /PYTHON/ZedRunBot/fetch_my_horses.py

### Check PAID Races and Send Email
*/15 * * * * /usr/bin/python /PYTHON/ZedRunBot/run_paid_races.py  > /PYTHON/ZedRunBot/logs/$(date +\%Y\%m\%d\%H\%M\%S).txt

### Check random Horse and send email if a good one detected
* * * * * /usr/bin/python /PYTHON/ZedRunBot/detect_good_horse_to_buy.py


 ### TODO
 - for races, then my hourse


pip install email-to
pip install discord-webhook
pip install pygobject

