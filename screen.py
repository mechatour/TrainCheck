import datetime
import traincheck
import time
import sys
import os
import traceback
import epaper
from PIL import Image, ImageDraw, ImageFont

#
# Pick up the lib directory which contains the libraries for the display & also the font to be uesd

libdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'lib')
if os.path.exists(libdir):
    sys.path.append(libdir)

#
# A separate call to get the train times for tomorrow. Takes today's date and makes amendments, based on the config
# This routine will use the display routines held in the file to draw the times. The boxes and other info are drawn separately.

def display_tomorrow_trains():

    import traincheck_config

    #
    # Calculate tomorrow's date and time

    time_now = datetime.datetime.now()
    tomorrow_time = time_now.replace(minute=0)
    tomorrow_time = tomorrow_time.replace(hour=traincheck_config.tomorrow_hour)
    tomorrow_time = tomorrow_time + datetime.timedelta(days=1)

    #
    # Get a list of tomorrow's trains, starting at the hour in the config and for 2 hours (currently hardcoded)
    # Format how the time will be displayed and the times to a list

    train_list = traincheck.traincheck(traincheck_config.from_tiploc, traincheck_config.to_tiploc, tomorrow_time, 120)
    
    tomorrow_list = []

    for train in train_list:

        planned_time = train[2].strftime("%H:%M")
        tomorrow_list.append(planned_time)

    #
    # Display Tomorrow's Trains - 23 maximum characters which equates to 4 times

    tomorrow_text = ""
    for text in tomorrow_list:
        tomorrow_text = tomorrow_text + " " + text 

    #
    # Trim if needed and right justify

    if len(tomorrow_text) > 23:
        tomorrow_text = tomorrow_text[len(tomorrow_text)-23:]

    tomorrow_text = tomorrow_text.rjust(34)
    draw.text((0,271), tomorrow_text, font = hn_font_19, fill = 0)

#
# Get train times for today, with a window either side to capture previous trains and future trains calling at the first station. 
# This routine will use the display routines held in the file to draw the times. The boxes and other info are drawn separately.

def display_current_trains():

    import traincheck_config

    time_now = datetime.datetime.now()
    previous_2hour = time_now - datetime.timedelta(hours=2)

    #
    # Get a list of trains due and the past actual arrivals (going back 2 hours in the past with 4 hours total)
    
    train_list = traincheck.traincheck(traincheck_config.from_tiploc, traincheck_config.to_tiploc, previous_2hour, 240)

    #
    # Sort the services by the planned arrival time/date and remove duplicates
    # This was implemented for the earlier version of the API. Commented out while testing the new (2026) API version.

    # Sort by planned arrival time/date
    #train_list = sorted(train_list, key=lambda x: x[2])

    #previous_date = time_now.min
    #for x in range(len(train_list)-1,-1,-1):
    #    if train_list[x][1] != previous_date:
    #        previous_date = train_list[x][1]
    #    else:
    #        train_list.pop(x)

    actual_list = []
    estimated_list = []

    title_printed = False

    #
    # Display the title and also compile the two lists of previous and future trains to be displayed later

    for train in train_list:
        if title_printed == False:
            main_title = train[6] + " to " + train[7]
            main_title = main_title.center(27)
            draw.text((0,2), main_title, font = hn_font_24, fill = 0)
            title_printed = True

        planned_time = train[2].strftime("%H:%M")
        
        if train[3] == "A":
            if train[5] <= 0:
                late_text = "on time"
            else:
                late_text = "+{:0d}".format(int(train[5]))
            actual_list.append((planned_time, late_text))
        elif train[3] == "E":
            estimated_time = train[4].strftime("%H:%M")
            if train[5] <= 0:
                late_text = "on time"
            else:
                late_text = "+{:0d} due {}".format(int(train[5]), estimated_time)
            estimated_list.append((planned_time, late_text))
        
    #
    # Display Current Date And Time

    now_text = datetime.datetime.now().strftime("%d %B %Y %H:%M")
    now_text = now_text.center(27)
    draw.text((0,42), now_text, font = hn_font_24, fill = 0)

    #
    # Display The Previous Trains from actual_list
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


    # Display the Estimated Trains from estimated_list
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

#
# Main update/display routine
#
# Estimated and Actual Train times are updated every 5 minutes. Two calls to the API are made. 
# Every hour two further calls are made to the API for tomorrow's trains.
# Every day at twelve o'clock, the display is cleared and repopulated with the graphical boxes. This is to help prevent stray pixels
# and keep the display "clean" looking.
# Every other draw to the screen for data population has the local area cleared first before populating.
# This prevents flicker on the e-ink display whilst maintaining legibility.

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

    #
    # Force draw on first time through loop
    display_minute = -1

    #
    # Loop every 15 seconds

    while True:
        hour_now = datetime.datetime.now().hour
        minute_now = datetime.datetime.now().minute

        # Five minute check
        if minute_now % 5 == 0 and minute_now != display_minute:
            # Midnight check for screen reset 
            if minute_now == 0 and hour_now == 0:
                clear_display()
            display_current_boxes()
            display_minute = minute_now
            display_current_trains()
            if minute_now == 0:
                display_tomorrow_box()
                display_tomorrow_trains()
            update_partial_image()
        else:
            time.sleep(15.0)
            #logging.info("minute: {}".format(time_now))

except KeyboardInterrupt:    
    epaper.epaper('epd4in2_V2').epdconfig.module_exit(cleanup=True)
    exit()

except Exception as e:
    print("Exception")
    print(e)
