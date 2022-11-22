# Wikirastaa
## Run on Heroku
 1.  Go to [BotFather](https://telegram.me/BotFather) chat and create a new bot. Copy API token in ```tb_tutorial/views.py``` file. Set admin username(s) in ```tb_tutorial/views.py``` as well. Now, these admins are able to run admin commands. Now run ```main.py```. Create an account in wikirasta and enter the username and password in ```tb_tutorial/views.py```.
 2. Go to [Heroku](heroku.com) and create an account.
 3. Heroku provides an easy-to-use command line interface called Heroku Toolbelt. It is a command line tool to manage your Heroku apps. You'll find installation guides on the [Heroku Toolbelt page](https://toolbelt.heroku.com/).
 4. Open cmd and run these commands
 ```bash
 heroku login
 heroku create wikirastaa
 git init
 heroku git:remote -a wikirastaa
 git add .
 git commit -m "lanat be in zendegi"
 heroku config:set     DISABLE_COLLECTSTATIC=1 
 git push heroku master
 heroku run python manage.py makemigrations
 heroku run python manage.py migrate
 ```
 5. Open this url in your browser once:
 ```bash
 https://api.telegram.org/bot<token>/setWebhook?url=<url>/webhooks/tutorial/ 
 ```
 Put your bot token instead of ```<token>``` and the url of your heroku application instead of ```url```.
