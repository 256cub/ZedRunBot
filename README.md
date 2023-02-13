# ZedRunBot

Retrieves horse racing data by calling zed.run apis and store them to MySQL Database.
> API documentation is here: https://docs.zed.run/racing/getraceresults


### STEPS
 - cp env.local to .env and set DB credits
 - pip install -r requirement
 - python migrations/migrate.py => will create all needed DB tables
 - a Bearer Token is needed, login into your ZedRun account and open Network(F12) and search for "authorization: Bearer {_LONG_STRING_}" and then set it in your .env ONLY TOKEN, WITHOUT WORD "Bearer"
   - Bearer Token is valid 30 days, so each month you have to update the Token in .env
 
### Is still some error
 - pip install email-to
 - pip install discord-webhook
 - pip install pygobject



### Check FREE Races and Register if any ok
*/10 * * * * /usr/bin/python /PYTHON/ZedRunBot/run_free_races.py  > /PYTHON/ZedRunBot/logs/$(date +\%Y\%m\%d\%H\%M\%S).txt

### Fetch my horses from DB and Stable
33 * * * * /usr/bin/python /PYTHON/ZedRunBot/fetch_my_horses.py

### Check PAID Races and Send Email
*/15 * * * * /usr/bin/python /PYTHON/ZedRunBot/run_paid_races.py  > /PYTHON/ZedRunBot/logs/$(date +\%Y\%m\%d\%H\%M\%S).txt

### Check random Horse and send email if a good one detected
* * * * * /usr/bin/python /PYTHON/ZedRunBot/detect_good_horse_to_buy.py



---

## Support

The team is always here to help you. 
Happen to face an issue? Want to report a bug? 
You can submit one here on GitHub using the [Issue Tracker](https://github.com/256cub/ZedRunBot/issues/new). 


<!-- CONTRIBUTING -->

## Contributing

Contributions are what make the open-source community such an amazing place to learn, inspire, and create.
Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request.
You can also simply open an issue with the tag "feature". 
Don't forget to give the project a star! 

**Thanks again !!!**


1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/YourNewFeature`)
3. Commit your Changes (`git commit -m 'Add some YourNewFeature'`)
4. Push to the Branch (`git push origin feature/YourNewFeature`)
5. Open a Pull Request

<p align="right">(<a href="#top">back to top</a>)</p>



## Security

If you discover any security-related issues, please email 256cub@gmail.com instead of using the issue tracker.


## Buy Me a Coffee

This project will be always an open source, even if I don't get donations. 
That being said, I know there are amazing people who may still want to donate just to show their appreciation.


<a href="https://www.buymeacoffee.com/256cub" target="_blank">
<img src="https://cdn.buymeacoffee.com/buttons/arial-orange.png" alt="Buy Me A Coffee" style="height: 51px !important;width: 217px !important;" ></a>


**Thank you very much in advance !!!**


We accept donations through Ko-fi, PayPal, BTC or ETH. 
You can use the buttons below to donate through your method of choice.

|   Donate With   |                      Address                       |
|:---------------:|:--------------------------------------------------:|
|      Ko-fi      |       [Click Here](https://ko-fi.com/256cub)       |
|     PayPal      | [Click Here](https://paypal.me/256cub) |
|   BTC Address   |         3MsUYeUfmpwVS2QrnRbLpCjGaVn2WDD6sj         |
|   ETH Address   |     0x10cd16ba338661d2FB683B2481f8F5000FEd5663     |


## Credits

- [256cub](https://github.com/256cub)

## License

The MIT License (MIT). Please see [License File](LICENSE) for more information.

<p align="right">(<a href="#top">back to top</a>)</p>
