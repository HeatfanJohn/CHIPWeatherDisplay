# CHIPWeatherDisplay

How to use:
  1. git clone https://github.com/quarterturn/CHIPWeatherDisplay.git into /opt (or wherever)
  2. Install requirements by performing: `sudo apt-get python-pygame python-pywapi python-daemon`
  3. edit PiTFTWeather.py and change weatherDotComLocationCode to your own location
  4. edit /etc/rc.local and add '/usr/bin/python /opt/PiTFTWeather/PiTFTWeather.py start' before 'exit 0'
  5. start the program: '/usr/bin/python /opt/PiTFTWeather/PiTFTWeather.py start'
  6. throw something like this '0 5 * * * /usr/bin/python /opt/PiTFTWeather/PiTFTWeather.py restart' in your root crontab to restart it each night, since I haven't figured out all the ways in which it will throw an exception yet.
