import datetime
import traincheck
import time

def build_list():
    import traincheck_config
    train_list = traincheck.traincheck(traincheck_config.from_tiploc, traincheck_config.to_tiploc, datetime.datetime.now() - datetime.timedelta(hours=2),240)
    train_list += traincheck.traincheck(traincheck_config.from_tiploc, traincheck_config.to_tiploc, datetime.datetime.now().replace(minute=0, hour=traincheck_config.tomorrow_hour) + datetime.timedelta(days=1),120)
    return train_list

def display_trains():

    actual_list = []
    estimated_list = []
    tomorrow_list = []

    for train in train_list:
        origin_time = train[1].strftime("%d-%m %H:%M")
        planned_time = train[2].strftime("%H:%M")
        estimated_time = train[4].strftime("%H:%M")
        
        estimated_text = ""
        late_text = ""

        if train[3] == "A":
            estimated_text = "- Actual " + estimated_time
        elif train[3] == "E":
            estimated_text = "- Estimated " + estimated_time
        elif train[3] == "F":
            estimated_text = "- Future Booking"

        if train[3] != "F":
            if train[5] == 0:
                late_text = "- On time"
            elif train[5] == 1:
                late_text = "- 1 minute late"
            else:
                late_text = "- {:0d} minutes late".format(int(train[5]))
        
        train_text = "{} - {} - Planned {} {} {}".format(origin_time, train[0], planned_time, estimated_text, late_text)

        # put them in groups

        if train[1].day != datetime.datetime.now().day:
            tomorrow_list.append(train_text)
        else:
            if train[3] == "A" :
                actual_list.append(train_text)
            elif train[3] == "E":
                estimated_list.append(train_text)

    print ("Update time: {}".format(datetime.datetime.now().strftime("%d-%m-%Y %H:%M")))
    print ("Previous\n--------")
    for text in actual_list:
        print (text)
    print ("\nCurrent\n-------")
    for text in estimated_list:
        print (text)
    print ("\nTomorrow\n--------")
    for text in tomorrow_list:
        print (text)

#train_list = traincheck.traincheck("ELGH","SOTON")
# Display initially then enter loop
timer = time.perf_counter()
train_list = build_list()
display_trains()
while True:
    time_now = datetime.datetime.now().minute
    if time_now % 5 == 0:
        train_list = build_list()
        display_trains()
        time.sleep(70.0)
    else:
        time.sleep(50.0)