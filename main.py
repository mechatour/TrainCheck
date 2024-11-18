import datetime
import traincheck

actual_list = []
estimated_list = []
tomorrow_list = []

#train_list = traincheck.traincheck("ELGH","SOTON")
train_list = traincheck.traincheck("ELGH","COSHAM")

for train in train_list:
    origin_time = train[1].strftime("%H:%M")
    planned_time = train[2].strftime("%H:%M")
    estimated_time = train[4].strftime("%H:%M")
    
    if train[1].day != datetime.datetime.now().day:
        estimated_text = ""
        late_text = ""
    else:
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
        else:
            late_text = ""
    
    train_text = "{} ({}) - Planned {} {} {}".format(train[0], origin_time, planned_time, estimated_text, late_text)

    # put them in groups

    if train[1].day != datetime.datetime.now().day:
        tomorrow_list.append(train_text)
    else:
        if train[3] == "A" :
            actual_list.append(train_text)
        elif train[3] == "E":
            estimated_list.append(train_text)

print ("Previous\n--------")
for text in actual_list:
    print (text)
print ("\nCurrent\n-------")
for text in estimated_list:
    print (text)
print ("\nTomorrow\n--------")
for text in tomorrow_list:
    print (text)