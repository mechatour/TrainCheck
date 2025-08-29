import datetime
import traincheck
import time
import sys
import os
#import logging
import traceback
import epaper
from PIL import Image, ImageDraw, ImageFont

libdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'lib')
if os.path.exists(libdir):
    sys.path.append(libdir)

#logging.basicConfig(level=logging.NOTSET)
#logging.info("TrainCheck")

def display_tomorrow_trains():
    import traincheck_config

    time_now = datetime.datetime.now()
    tomorrow_time = time_now.replace(minute=0)
    tomorrow_time = tomorrow_time.replace(hour=traincheck_config.tomorrow_hour)
    tomorrow_time = tomorrow_time + datetime.timedelta(days=1)

    train_list = traincheck.traincheck(traincheck_config.from_tiploc, traincheck_config.to_tiploc, tomorrow_time)
    
    tomorrow_list = []

    for train in train_list:

        planned_time = train[2].strftime("%H:%M")
        tomorrow_list.append(planned_time)

    # Display Tomorrow's Trains - 23 maximum characters which equates to 4 times
    tomorrow_text = ""
    for text in tomorrow_list:
        tomorrow_text = tomorrow_text + " " + text 

    # Trim if needed
    if len(tomorrow_text) > 23:
        tomorrow_text = tomorrow_text[len(tomorrow_text)-23:]

    tomorrow_text = tomorrow_text.rjust(34)
    draw.text((0,271), tomorrow_text, font = hn_font_19, fill = 0)

def display_current_trains():

    import traincheck_config

    time_now = datetime.datetime.now()
    this_hour = time_now.replace(minute=0)
    next_hour = this_hour + datetime.timedelta(hours=1)
    previous_hour = this_hour - datetime.timedelta(hours=1)
    previous_2hour = this_hour - datetime.timedelta(hours=2)

    # Get a list of trains due and the past actual arrivals
    
    train_list = traincheck.traincheck(traincheck_config.from_tiploc, traincheck_config.to_tiploc, this_hour)
    train_list += traincheck.traincheck(traincheck_config.from_tiploc, traincheck_config.to_tiploc, next_hour)
    train_list += traincheck.traincheck(traincheck_config.from_tiploc, traincheck_config.to_tiploc, previous_hour)
    train_list += traincheck.traincheck(traincheck_config.from_tiploc, traincheck_config.to_tiploc, previous_2hour)

    # Sort by planned arrival time/date

    train_list = sorted(train_list, key=lambda x: x[2])

    # Remove duplicates

    previous_date = time_now.min
    for x in range(len(train_list)-1,-1,-1):
        if train_list[x][1] != previous_date:
            previous_date = train_list[x][1]
        else:
            train_list.pop(x)

    actual_list = []
    estimated_list = []

    title_printed = False

    for train in train_list:
        if title_printed == False:
            main_title = train[6] + " to " + train[7]
            main_title = main_title.center(27)
            draw.text((0,2), main_title, font = hn_font_24, fill = 0)
            title_printed = True

        planned_time = train[2].strftime("%H:%M")
        estimated_time = train[4].strftime("%H:%M")
        
        if train[3] == "A":
            if train[5] == 0 or train[5] < 0:
                late_text = "on time"
            else:
                late_text = "+{:0d}".format(int(train[5]))
            actual_list.append((planned_time, late_text))
        elif train[3] == "E":
            if train[5] == 0 or train[5] < 0:
                late_text = "on time"
            else:
                late_text = "+{:0d} due {}".format(int(train[5]), estimated_time)
            estimated_list.append((planned_time, late_text))
        
    # Display Current time

    now_text = datetime.datetime.now().strftime("%d %B %Y %H:%M")
    now_text = now_text.center(27)
    draw.text((0,42), now_text, font = hn_font_24, fill = 0)

    # Display Previous Trains

    # Just the three boxes max and we want to show the 3 most recent, which will be
    # at the end of the list
    list_size = len(actual_list)
    first_index = 0
    if list_size > 3:
        first_index = list_size - 3

    position = 0
    for x in range(first_index, list_size):
        draw.text(((position*136)+9, 220), actual_list[x][0], font = hn_font_19, fill = 0)
        draw.text(((position*136)+9, 238), actual_list[x][1], font = hn_font_19, fill = 0)
        position = position + 1


    # Display the Estimated Trains

    # Four lines seem valid and we want to show the 4 most recent,
    # which will be at the end of the list
    list_size = len(estimated_list)
    first_index = 0
    if list_size > 4:
        first_index = list_size - 4

    position = 0
    for x in range(first_index, list_size):
        draw.text((5, (position*25)+85), estimated_list[x][0] + " " + estimated_list[x][1], font = hn_font_24, fill = 0)
        position = position + 1

def clear_display():
    epd.init()
    epd.Clear()

def display_current_boxes():
    display_date_box()
    display_previous_boxes()
    display_current_box()

def display_date_box():
    draw.rectangle((3,37,395,74), outline = 0, fill = 255)

def display_previous_boxes():
    draw.rectangle((3,217,123,261), outline = 0, fill = 255)
    draw.rectangle((139,217,259,261), outline = 0, fill = 255)
    draw.rectangle((276,217,395,261), outline = 0, fill = 255)
    draw.text((5,195), '        ', font = hn_font_19, fill = 0)
    draw.text((5,195), 'Previous', font = hn_font_19, fill = 0)

def display_tomorrow_box():
    draw.rectangle((3,268,395,295), outline = 0, fill = 255)
    draw.text((9,271), 'Tomorrow', font = hn_font_19, fill = 0)

def display_current_box():
    draw.rectangle((0,75,399,194), fill = 255)

def update_image():
    epd.display(epd.getbuffer(Himage))

def update_partial_image():
    epd.display_Partial(epd.getbuffer(Himage))

try:


    epd = epaper.epaper('epd4in2_V2').EPD()
    font24 = ImageFont.truetype(os.path.join('lib', 'Font.ttc'),24)
    hn_font_24 = ImageFont.truetype(os.path.join('lib', 'HackNerdFont-Regular.ttf'),24)
    hn_font_19 = ImageFont.truetype(os.path.join('lib', 'HackNerdFont-Regular.ttf'),19)
    hn_font_16 = ImageFont.truetype(os.path.join('lib', 'HackNerdFont-Regular.ttf'),16)
    
    Himage = Image.new('1', (epd.width, epd.height), 255)  # 255: clear the frame
    draw = ImageDraw.Draw(Himage)

    clear_display()
    display_current_boxes()
    display_tomorrow_box()
    display_current_trains()
    display_tomorrow_trains()
    update_partial_image()

    display_minute = -1

    # Loop every 15 seconds, checking for a minute change. Every 5 minutes update the current trains
    # Every hour, update the trains scheduled for tomorrow
    # Every day at 00:00, reset the display to clear out artifacts

    while True:
        time_now = datetime.datetime.now().minute

        if time_now % 5 == 0 and time_now != display_minute:
            if time_now == 0 and datetime.datetime.now().hour == 0:
                clear_display()
                time.sleep(5.0)
            display_minute = time_now               #unsure only updates once during a minute
            display_current_boxes()
            display_current_trains()
            update_partial_image()
            if time_now == 0:
                display_tomorrow_box()
                display_tomorrow_trains()
                update_partial_image()
        else:
            time.sleep(15.0)
            #logging.info("minute: {}".format(time_now))

except KeyboardInterrupt:    
    #logging.info("ctrl + c:")
    epaper.epaper('epd4in2_V2').epdconfig.module_exit(cleanup=True)
    exit()

except Exception as e:
    print("Exception")
    print(e)
