#!/usr/bin/env python3

#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License in the file LICENSE.txt or at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import time

# Masashi Added 01/03/2018
import json
import requests
import datetime
import math
try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    sys.exit("Cannot import from PIL. Do `pip3 install --user Pillow` to install")

import cozmo
import cozmo_utils
import api_accuweather

SHOW_ANALOG_CLOCK = False

# get a font - location depends on OS so try a couple of options
# failing that the default of None will just use a default font
_clock_font = None
try:
    _clock_font = ImageFont.truetype("arial.ttf", 50)
except IOError:
    try:
        _clock_font = ImageFont.truetype("/Library/Fonts/Arial.ttf", 50)
    except IOError:
        pass



# City name. Put something very explicit, this acts as a search string in AccuWeather's API
CITY_NAME = "Tokyo, Japan"

# nakatani Spire accessToken
accessToken = 'a738c6b9570a84b9bbc4cc1da8da62d711c231d5c64abb3959ca6a560170ac4d'


url = 'https://app.spire.io/api/v2/events'
event_type  = 'br'
dateSpire   = '20180103'
accessUrl = url + '?access_token=' + accessToken + '&type=' + event_type + '&date=' + dateSpire

def make_resp_image(text_to_draw):
    # make a blank image for the background
    bkgd_img = Image.new('RGBA', cozmo.oled_face.dimensions(), (0,0,0,255))

    # get drawing context
    dc = ImageDraw.Draw(bkgd_img)

    # calculate position of clock elements
    text_height = 9
    screen_width, screen_height = cozmo.oled_face.dimensions()
    analog_width = screen_width
    analog_height = screen_height - text_height
    cen_x = analog_width * 0.5
    cen_y = analog_height * 0.5

    x = screen_width/2
    y = screen_height - text_height
    print(screen_width,screen_height)

    # draw the text
    dc.text((cen_x,cen_y), text_to_draw, fill=(255,255,255,255), font = None)

    return bkgd_img

def make_text_image(text_to_draw, x, y, font=None):
    '''Make a PIL.Image with the given text printed on it

    Args:
        text_to_draw (string): the text to draw to the image
        x (int): x pixel location
        y (int): y pixel location
        font (PIL.ImageFont): the font to use

    Returns:
        :class:(`PIL.Image.Image`): a PIL image with the text drawn on it
    '''

    # make a blank image for the text, initialized to opaque black
    text_image = Image.new('RGBA', cozmo.oled_face.dimensions(), (0, 0, 0, 255))

    # get a drawing context
    dc = ImageDraw.Draw(text_image)

    # draw the text
    dc.text((x, y), text_to_draw, fill=(255, 255, 255, 255), font=font)

    return text_image

def make_clock_image(current_time):
    '''Make a PIL.Image with the current time displayed on it

    Args:
        text_to_draw (:class:`datetime.time`): the time to display

    Returns:
        :class:(`PIL.Image.Image`): a PIL image with the time displayed on it
    '''

    time_text = time.strftime("%I:%M:%S %p")

    if not SHOW_ANALOG_CLOCK:
        return make_text_image(time_text, 8, 6, _clock_font)

    # make a blank image for the text, initialized to opaque black
    clock_image = Image.new('RGBA', cozmo.oled_face.dimensions(), (0, 0, 0, 255))

    # get a drawing context
    dc = ImageDraw.Draw(clock_image)

    # calculate position of clock elements
    text_height = 9
    screen_width, screen_height = cozmo.oled_face.dimensions()
    analog_width = screen_width
    analog_height = screen_height - text_height
    cen_x = analog_width * 0.5
    cen_y = analog_height * 0.5

    # calculate size of clock hands
    sec_hand_length = (analog_width if (analog_width < analog_height) else analog_height) * 0.5
    min_hand_length = 0.85 * sec_hand_length
    hour_hand_length = 0.7 * sec_hand_length

    # calculate rotation for each hand
    sec_ratio = current_time.second / 60.0
    min_ratio = (current_time.minute + sec_ratio) / 60.0
    hour_ratio = (current_time.hour + min_ratio) / 12.0

    # draw the clock hands
    draw_clock_hand(dc, cen_x, cen_y, hour_ratio, hour_hand_length)
    draw_clock_hand(dc, cen_x, cen_y, min_ratio, min_hand_length)
    draw_clock_hand(dc, cen_x, cen_y, sec_ratio, sec_hand_length)

    # draw the digital time_text at the bottom
    x = 32
    y = screen_height - text_height
    dc.text((x, y), time_text, fill=(255, 255, 255, 255), font=None)

    return clock_image



# Main function
def cozmo_program(robot: cozmo.robot.Robot):


# Get respiration infomation from Spire website
    #print(accessUrl)
    '''
    jsonTexts = requests.get(accessUrl).json()
    timeData = {}

    i = 0
    #print(jsonTexts)
    #print(time)
    for time in jsonTexts:
        timeData['timestamp'] = datetime.datetime.fromtimestamp(time['timestamp'])
        jsonSmallTexts = json.dumps(jsonTexts[i]["value"], indent=2)

        # print jsonSmallTexts
        # print 'start time is, ' + timeData['start_at'].strftime('%Y-%m-%d %H:%M:%S') + ', stop time is, ' + timeData['stop_at'].strftime('%Y-%m-%d %H:%M:%S') + ', this data is number, ' + str(i) + ', ' + jsonSmallTexts
        # print str(i) + ', Time, ' + timeData['timestamp'].strftime('%Y-%m-%d %H:%M:%S')  + ', ' + jsonSmallTexts
        print (str(i) + ', Time, ' + timeData['timestamp'].strftime('%Y-%m-%d') + ', ' + timeData['timestamp'].strftime(
        '%H') + ', ' + timeData['timestamp'].strftime('%M') + ', ' + jsonSmallTexts)
        # print str(i)
        i = i + 1
    '''



    ''' Retrieves the weather forecast from AccuWeather and asks Cozmo to read it out loud '''

    # Put a lot of volume so we can hear Cozmo across home
    robot.set_robot_volume(1.0)

    # Some light effect, lift and head animation
    robot.set_backpack_lights(cozmo.lights.red_light,
                              cozmo.lights.green_light,
                              cozmo.lights.blue_light,
                              cozmo.lights.white_light,
                              cozmo.lights.red_light)
    robot.set_lift_height(0).wait_for_completed()
    robot.set_lift_height(0.25).wait_for_completed()
    robot.set_lift_height(0).wait_for_completed()
    robot.set_head_angle(cozmo.util.Angle(degrees=20)).wait_for_completed()
    robot.set_head_angle(cozmo.util.Angle(degrees=0)).wait_for_completed()

    # Get the forecast from AccuWeather
    # forecasts = api_accuweather.get_forecasts(CITY_NAME)



    # Cozmo requests your attention
    #action = robot.say_text("Weather Forecast")
    action = robot.say_text("あなたの呼吸")

    cozmo_utils.display_image_file_on_face(robot, "images/weather.png")
    action.wait_for_completed()

    '''
    # For each day's forecast, read it out loud
    for fc in forecasts["Forecasts"]:
        # Get the date from the forecast (yyyy-mm-dd)
        date = fc["Date"]

        # Get the forecast itself (sunny, cloudy, etc.)
        fc_text = fc["Forecast"]

        # Converts the date from the format 'yyyy-mm-dd' to the name of the
        # weekday (Tuesday, Monday, etc.)
        date_text = time.strftime("%A", time.strptime(date, "%Y-%m-%d"))

        # Finally, Cozmo tells the forecast
        cozmo_utils.say_forecast(robot, date_text, fc_text)
    '''
    #date_text = timeData['timestamp'].strftime('%H') + '時' + timeData['timestamp'].strftime('%M') + 'ふん'
    # for debug without accessing server
    date_text = '21時10分'
    #fc_text   = int(jsonSmallTexts)
    # fc_text    = jsonSmallTexts
    fc_text    = "13.0"
    cozmo_utils.say_forecast(robot, date_text, fc_text)
    # Turn off the lights, although it seems to be automatic

    print(date_text)
    resp_num = float("13.0")
    print(resp_num)

    print("Press CTRL-C to quit")

    i = 0

    #robot.set_head_angle(cozmo.util.Angle(degrees=20)).wait_for_completed()


    while True:

        current_time = datetime.datetime.now().time()

        resp_image  = make_resp_image(fc_text)


        clock_image = make_clock_image(current_time)

        oled_face_data = cozmo.oled_face.convert_image_to_screen_data(resp_image)

        # display for 1 second
        robot.display_oled_face_image(oled_face_data, 1.0, True).wait_for_completed()
        # you should stop showing face image before you move your cozmo....


        last_displayed_time = current_time
        # only sleep for a fraction of a second to ensure we update the seconds as soon as they change
        time.sleep(0.1)

        i=i+1
        if(i>20):
            if(resp_num < 15):
                print('yes')
                robot.set_head_angle(cozmo.util.Angle(degrees=20)).wait_for_completed()
                robot.set_head_angle(cozmo.util.Angle(degrees=0)).wait_for_completed()
                time.sleep(1)
                i=0



    #make_resp_image(date_text)
    #clock_image = make_clock_image(current_time)

    robot.set_backpack_lights_off()


# Start the program
if __name__ == "__main__":
    cozmo.run_program(cozmo_program)
