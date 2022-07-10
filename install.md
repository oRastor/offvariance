# Install instructions

Create account on DO https://m.do.co/c/393ff2178842

Create new droplet based on ubuntu on DO

Add your droplet IP on https://offvariance.com/profile/api/ (not needed for rapid api)

Login to just created instance

Download project
```
cd /var
git clone https://github.com/oRastor/offvariance.git
cd offvariance/ 
```

Install some packages
```
apt install -y python3-pip mc
```

Install python libraries
```
pip3 install -r requirements.txt
```

Copy environment example file and settings example file
```
cp .env.example .env
cp settings.py.example settings.py 
```

Setup OFF_VARIANCE_KEY variable or RAPID_KEY (https://rapidapi.com/Wolf1984/api/football-xg-statistics/), save file (F2)
```
mcedit .env
```

Update database, it can take a more than hour for first time
```
make update-database
```

Check that script `make find-games` works 

```
make find-games
```

Create your own telegram bot with https://t.me/BotFather

Setup TELEGRAM_API_KEY variable, save file (F2)
```
mcedit .env
```

Setup telegram bot service
```
cp server/offvariance.service /etc/systemd/system/offvariance.service
```

Start telegram service
```
systemctl start offvariance
```

Check status
```
systemctl status offvariance
```

And automatically get it to start on boot
```
systemctl enable offvariance
```

Send /start to your telegram bot. He will send you your id, copy it and update .env file (variable TELEGRAM_USER_ID), save file (F2)
```
mcedit .env
```

Restart service with new configuration
```
systemctl restart offvariance
```

Send /start to your telegram bot. He will send you list of available commands. Click on /list. After that you will receive list of available bets.

Setup crontab to receive updates every minute
```
crontab server/crontab.txt
```

At the beginning of next minute you will receive list of available bets. After that you will receive only updates. Enjoy!
