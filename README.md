# CHIPWeatherDisplay

How to use:

1. git clone https://github.com/HeatfanJohn/CHIPWeatherDisplay.git into /home/chip (or /opt)
2. Install requirements by performing:
  1. `sudo apt-get install python-pygame`
  2. `wget https://launchpad.net/python-weather-api/trunk/0.3.8/+download/python-pywapi_0.3.8-0ubuntu0ppa1_all.deb`
  3. `sudo dpkg -i python-pywapi_0.3.8-0ubuntu0ppa1_all.deb`
3. Default zip code is "33330", use `-z <zip code>` option to specify zip code for Weather report
4. `sudo cp /home/chip/CHIPWeatherDisplay/CHIPTFTWeatherApp.service /etc/systemd/system/`
5. `sudo systemctl enable CHIPTFTWeatherApp
6. `sudo systemctl start CHIPTFTWeatherApp


