#!/usr/bin/python -u

import sys, getopt
import os, syslog
import pygame
import time
from time import sleep, strftime
from datetime import datetime
import pywapi
import string
import random
import glob
import systemd.daemon

#from daemon import Daemon

# Weather Icons used with the following permissions:
#
# VClouds Weather Icons
# Created and copyrighted by VClouds - http://vclouds.deviantart.com/
#
# The icons are free to use for Non-Commercial use, but If you use want to use it with your art please credit me and put a link leading back to the icons DA page - http://vclouds.deviantart.com/gallery/#/d2ynulp
#
# *** Not to be used for commercial use without permission!
# if you want to buy the icons for commercial use please send me a note - http://vclouds.deviantart.com/ ***

#installPath = "/opt/CHIPWeatherDisplay/"
installPath = "./"
picturePath = "/home/chip/flickr/photoframe/"
pidFile = "/var/run/CHIPTFTWeatherApp.pid"

# location for Raleigh, NC on weather.com
weatherDotComLocationCode = '33330:4:US'
# convert mph = kpd / kphToMph
kphToMph = 1.60934400061

# font colours
colourWhite = (255, 255, 255)
colourBlack = (0, 0, 0)

# update interval
updateRate = 60 # seconds

class pitft :
    screen = None;
    colourBlack = (0, 0, 0)
    size = (640,480)

    def __init__(self):
        "Ininitializes a new pygame screen using the framebuffer"
        # Based on "Python GUI in Linux frame buffer"
        # http://www.karoltomala.com/blog/?p=679
        disp_no = os.getenv("DISPLAY")
        if disp_no:
            print "I'm running under X display = {0}".format(disp_no)
            driver = 'x11'
        else:
            os.putenv('SDL_FBDEV', '/dev/fb0')
            # Select frame buffer driver
            driver = 'fbcon'

        print "Using driver: " + driver
        # Make sure that SDL_VIDEODRIVER is set
        if not os.getenv('SDL_VIDEODRIVER'):
            os.putenv('SDL_VIDEODRIVER', driver)

        try:
            pygame.display.init()
            print 'Driver: {0} initialized.'.format(driver)
        except pygame.error:
            print 'Driver: {0} failed.'.format(driver)
            exit(0)

        if disp_no:
            self.screen = pygame.display.set_mode(self.size)
        else:
            self.size = (pygame.display.Info().current_w, pygame.display.Info().current_h)
            self.screen = pygame.display.set_mode(self.size, pygame.FULLSCREEN)
        # Clear the screen to start
        self.screen.fill((0, 0, 0))
        # Initialise font support
        pygame.font.init()
        # Render the screen
        pygame.display.update()

    def __del__(self):
        "Destructor to make sure pygame shuts down, etc."

class MyDisplay:
    """
    aspect_scale.py - Scaling surfaces keeping their aspect ratio
    Raiser, Frank - Sep 6, 2k++
    crashchaos at gmx.net

    This is a pretty simple and basic function that is a kind of
    enhancement to pygame.transform.scale. It scales a surface
    (using pygame.transform.scale) but keeps the surface's aspect
    ratio intact. So you will not get distorted images after scaling.
    A pretty basic functionality indeed but also a pretty useful one.

    Usage:
    is straightforward.. just create your surface and pass it as
    first parameter. Then pass the width and height of the box to
    which size your surface shall be scaled as a tuple in the second
    parameter. The aspect_scale method will then return you the scaled
    surface (which does not neccessarily have the size of the specified
    box of course)

    Dependency:
    a pygame version supporting pygame.transform (pygame-1.1+)
    """

    def aspect_scale(self,img,(bx,by)):
        """ Scales 'img' to fit into box bx/by.
         This method will retain the original image's aspect ratio """
        ix,iy = img.get_size()
        if ix > iy:
            # fit to width
            scale_factor = bx/float(ix)
            sy = scale_factor * iy
            if sy > by:
                scale_factor = by/float(iy)
                sx = scale_factor * ix
                sy = by
            else:
                sx = bx
        else:
            # fit to height
            scale_factor = by/float(iy)
            sx = scale_factor * ix
            if sx > bx:
                scale_factor = bx/float(ix)
                sx = bx
                sy = scale_factor * iy
            else:
                sy = by

        return pygame.transform.scale(img, (int(sx),int(sy)))

    # implement run method
    def run(self):
        images = []
        for filename in glob.glob(picturePath + '*.jpg'):
            images.append(filename)

        while True:

            # extract current data for today
            try:
                weather_com_result = pywapi.get_weather_from_weather_com(weatherDotComLocationCode,units = 'imperial')
                today = weather_com_result['forecasts'][0]['day_of_week'][0:3] + " " \
                    + weather_com_result['forecasts'][0]['date'][4:] + " " \
                    + weather_com_result['forecasts'][0]['date'][:3]
            except:
                print "Unexpected error:", sys.exc_info()[0]
                print weather_com_result
                sleep(updateRate/4)
                continue

            windSpeed = weather_com_result['current_conditions']['wind']['speed']
            if windSpeed == "calm":
                windSpeed = '0'
            currWind = windSpeed + " mph " + weather_com_result['current_conditions']['wind']['text']
            currTemp = weather_com_result['current_conditions']['temperature'] + u'\N{DEGREE SIGN}' + "F"
            # currPress = weather_com_result['current_conditions']['barometer']['reading'][:-3] + " in"
            currPress = weather_com_result['current_conditions']['barometer']['reading'] + " in"
            uv = "UV {}".format(weather_com_result['current_conditions']['uv']['text'])
            humid = "Hum {}%".format(weather_com_result['current_conditions']['humidity'])

            # extract forecast data
            forecastDays = {}
            forecaseHighs = {}
            forecaseLows = {}
            forecastPrecips = {}
            forecastWinds = {}

            start = 0
            try:
                test = float(weather_com_result['forecasts'][0]['day']['wind']['speed'])
            except ValueError:
                start = 1

            for i in range(start, 5):

                if not(weather_com_result['forecasts'][i]):
                    break
                forecastDays[i] = weather_com_result['forecasts'][i]['day_of_week'][0:3]
                forecaseHighs[i] = weather_com_result['forecasts'][i]['high'] + u'\N{DEGREE SIGN}' + "F"
                forecaseLows[i] = weather_com_result['forecasts'][i]['low'] + u'\N{DEGREE SIGN}' + "F"
                forecastPrecips[i] = weather_com_result['forecasts'][i]['day']['chance_precip'] + "%"
                forecastWinds[i] = "{:.0f}".format(int(weather_com_result['forecasts'][i]['day']['wind']['speed'])) + \
                    weather_com_result['forecasts'][i]['day']['wind']['text']

            # blank the screen
            mytft.screen.fill(colourBlack)

            # Render the weather logo at 0,0
            icon = installPath + "icons/" + (weather_com_result['current_conditions']['icon']) + ".png"
            logo = pygame.image.load(icon).convert()
            mytft.screen.blit(logo, (0, 0))

            # set the anchor for the current weather data text
            textAnchorX = 140
            textAnchorY = 5
            textYoffset = 40

            # add current weather data text artifacts to the screen
            text_surface = font.render(today, True, colourWhite)
            mytft.screen.blit(text_surface, (textAnchorX, textAnchorY))
            textAnchorY+=textYoffset
            text_surface = font.render(currTemp, True, colourWhite)
            mytft.screen.blit(text_surface, (textAnchorX, textAnchorY))
            textAnchorY+=textYoffset
            text_surface = font.render(currWind, True, colourWhite)
            mytft.screen.blit(text_surface, (textAnchorX, textAnchorY))
            textAnchorY+=textYoffset
            text_surface = font.render(currPress, True, colourWhite)
            mytft.screen.blit(text_surface, (textAnchorX, textAnchorY))
            textAnchorY+=textYoffset
            text_surface = font.render(uv, True, colourWhite)
            mytft.screen.blit(text_surface, (textAnchorX, textAnchorY))
            textAnchorY+=textYoffset
            text_surface = font.render(humid, True, colourWhite)
            mytft.screen.blit(text_surface, (textAnchorX, textAnchorY))

            # set X axis text anchor for the forecast text
            textAnchorX = 0
            textXoffset = 130
            textYoffset = 30

            # add each days forecast text
            for i in forecastDays:
                textAnchorY = 260
                text_surface = fontSm.render(forecastDays[int(i)], True, colourWhite)
                mytft.screen.blit(text_surface, (textAnchorX, textAnchorY))
                textAnchorY+=textYoffset
                text_surface = fontSm.render(forecaseHighs[int(i)], True, colourWhite)
                mytft.screen.blit(text_surface, (textAnchorX, textAnchorY))
                textAnchorY+=textYoffset
                text_surface = fontSm.render(forecaseLows[int(i)], True, colourWhite)
                mytft.screen.blit(text_surface, (textAnchorX, textAnchorY))
                textAnchorY+=textYoffset
                text_surface = fontSm.render(forecastPrecips[int(i)], True, colourWhite)
                mytft.screen.blit(text_surface, (textAnchorX, textAnchorY))
                textAnchorY+=textYoffset
                text_surface = fontSm.render(forecastWinds[int(i)], True, colourWhite)
                mytft.screen.blit(text_surface, (textAnchorX, textAnchorY))
                textAnchorX+=textXoffset

            text_surface = fontVSm.render('Last updated: ' + weather_com_result['current_conditions']['last_updated'], True, colourWhite)
            mytft.screen.blit(text_surface, (5, textAnchorY+textYoffset))

            # set x axis text anchor for the time
            textAnchorX = 420
            textAnchorY = 5

            # print the time
            text_surface = fontTime.render(datetime.now().strftime('%H:%M'), True, colourWhite)
            mytft.screen.blit(text_surface, (textAnchorX, textAnchorY))
            # refresh the screen with all the changes
            pygame.display.update()

            sleep(updateRate/2)

            # blank out display
            mytft.screen.fill(colourBlack)
            img=pygame.image.load(random.choice(images))  # get a random image
            img=self.aspect_scale(img,pitft.size)         # scale it to screen
            ax, ay=img.get_size()
            bx, by=pitft.size
            if(bx>ax):                                    # center the image on the x-axis
                ix=(bx-ax)/2
            else:
                ix=0
            if(by>ay):                                    # center the image on the y-axis
                iy=(by-ay)/4
            else:
                iy=0

            print(ax,ay,bx,by,ix,iy)

            mytft.screen.blit(img,(ix,iy))
            pygame.display.flip()                         # update the display
            sleep(updateRate/2)

if __name__ == "__main__":
    print sys.argv[0] + " " + str(datetime.now())

    try:
        opts, args = getopt.getopt(sys.argv[1:],"hi:p:",["installPath=","picturePath="])

    except getopt.GetoptError:
        print "Invalid argument(s) specified, command line is:"
        print sys.argv[0] + " -i <InstallPath> -p <PathToPictures>"
        sys.exit(2)

    for opt, arg in opts:
        if opt == "-h":
            print sys.argv[0] + " -i <InstallPath> -p <PathToPictures>"
            sys.exit()
        elif opt in ("-i", "--installPath"):
            installPath = arg
        elif opt in ("-p", "--picturePath"):
            picturePath = arg

    print "Using Install path = \"" + installPath + "\""
    print "Using Picture path = \"" + picturePath + "\""

    # Create an instance of the PyScope class
    mytft = pitft()

    pygame.mouse.set_visible(False)

    # set up the fonts
    # choose the font
    fontpath = pygame.font.match_font('dejavusansmono')
    # set up 3 sizes
    font = pygame.font.Font(fontpath, 40)
    fontSm = pygame.font.Font(fontpath, 30)
    fontTime = pygame.font.Font(fontpath, 40)
    fontVSm = pygame.font.Font(fontpath, 20)

    myDisplay = MyDisplay()

    out = open( pidFile, "w" )
    print >> out, os.getpid()
    out.close()

    systemd.daemon.notify("READY=1")

    try:
        myDisplay.run()

    finally:
        print "Executing finally clause ..."
        pygame.quit()
        print "pygame.quit() was called"
