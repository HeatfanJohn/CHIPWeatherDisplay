# CHIPWeatherDisplay

How to use:
  1. git clone https://github.com/quarterturn/CHIPWeatherDisplay.git into /opt (or wherever)
  2. Install requirements by performing:
     a) `sudo apt-get install  python-pygame`
     b) `wget https://launchpad.net/python-weather-api/trunk/0.3.8/+download/python-pywapi_0.3.8-0ubuntu0ppa1_all.deb`
     c) `sudo dpkg -i python-pywapi_0.3.8-0ubuntu0ppa1_all.deb`
     d) `sudo apt-get -f`
  3. edit PiTFTWeather.py and change weatherDotComLocationCode to your own location
  4. edit /etc/rc.local and add '/usr/bin/python /opt/PiTFTWeather/PiTFTWeather.py start' before 'exit 0'
  5. start the program: '/usr/bin/python /opt/PiTFTWeather/PiTFTWeather.py start'
  6. throw something like this '0 5 * * * /usr/bin/python /opt/PiTFTWeather/PiTFTWeather.py restart' in your root crontab to restart it each night, since I haven't figured out all the ways in which it will throw an exception yet.
