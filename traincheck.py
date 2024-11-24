# Credit goes to Realtime Trains (realtimetrains.co.uk) for providing the API which is freely available
# visit https://api.rtt.io for more details

def traincheck(station_from="ELGH", station_to="COSHAM"):

    import requests
    from requests.auth import HTTPBasicAuth
    from datetime import datetime, timedelta
    import api_details

    # API & search details


    rtt_baseaddress = "https://api.rtt.io/api/v1/json/search/"
    rtt_search = "{}/to/{}/".format(station_from,station_to)
    auth = HTTPBasicAuth(api_details.rtt_username, api_details.rtt_password)

    # Time calculation

    time_now = datetime.now()

    time_calc = time_now
    rtt_now = "{}/{:0>2}/{:0>2}/{:0>2}00".format(time_calc.year, time_calc.month, time_calc.day, time_calc.hour)
    # Debug to show whole day
    #rtt_now = "{}/{:0>2}/{:0>2}".format(time_calc.year, time_calc.month, time_calc.day)

    time_calc = time_now + timedelta(hours=1)
    rtt_next_hour = "{}/{:0>2}/{:0>2}/{:0>2}00".format(time_calc.year, time_calc.month, time_calc.day, time_calc.hour)

    time_calc = time_now - timedelta(hours=1)
    rtt_last_hour = "{}/{:0>2}/{:0>2}/{:0>2}00".format(time_calc.year, time_calc.month, time_calc.day, time_calc.hour)

    time_calc = time_now + timedelta(days=1)
    rtt_next_day = "{}/{:0>2}/{:0>2}/0700".format(time_calc.year, time_calc.month, time_calc.day)

    #API Calls

    services_list = []

    request = requests.get(rtt_baseaddress + rtt_search + rtt_last_hour + "/arrivals", auth=auth)
    if request.status_code == 200:
        data = request.json()
        if data['services'] is not None:
            services_list = services_list + data['services']

    request = requests.get(rtt_baseaddress + rtt_search + rtt_now, auth=auth)
    if request.status_code == 200:
        data = request.json()
        if data['services'] is not None:
            services_list = services_list + data['services']

    request = requests.get(rtt_baseaddress + rtt_search + rtt_next_hour, auth=auth)
    if request.status_code == 200:
        data = request.json()
        if data['services'] is not None:
            services_list = services_list + data['services']
    
    request = requests.get(rtt_baseaddress + rtt_search + rtt_next_day, auth=auth)
    if request.status_code == 200:
        data = request.json()
        if data['services'] is not None:
            services_list = services_list + data['services']
    
    # Return list is a list of tuples containing origin place, origin time, planned time, estimated time (can be zero for future departures), 
    # difference (can be zero for future departures) & service type (Actual, Estimated, Future)
    # [(origin, origin_time, planned, estimated, difference, type)]

    return_list = []

    # Service computations

    #print (services_list)

    try:
        for service in services_list:

            origin_name = ""
            origin_time = 0
            planned = 0
            estimated = 0
            difference = 0
            type = ""


            if service['locationDetail']['tiploc'] == station_from and service['locationDetail']['isPublicCall'] == True and service['isPassenger'] == True:

                origin_name = service['locationDetail']['origin'][0]['description']
                origin_time = datetime.strptime(service['runDate'] + service['locationDetail']['origin'][0]['publicTime'],"%Y-%m-%d%H%M")
                planned = datetime.strptime(service['runDate'] + service['locationDetail']['gbttBookedDeparture'],"%Y-%m-%d%H%M")
                
                try:
                    if service['locationDetail']['realtimeDepartureActual'] == True:
                        type = "A"
                    else:
                        type = "E"

                    estimated = datetime.strptime(service['runDate'] + service['locationDetail']['realtimeDeparture'],"%Y-%m-%d%H%M")
                    difference = (estimated - planned).total_seconds() / 60

                except Exception as E:
                    type = "F"
                    estimated = datetime.strptime(service['runDate'] + "0000","%Y-%m-%d%H%M")
                    difference = 0

                return_list.append((origin_name, origin_time, planned, type, estimated, difference))

    except Exception as E:
        print (E)
        return []

    # Remove duplicates

    previous_date = datetime.min
    for x in range(len(return_list)-1,-1,-1):
        if return_list[x][1] != previous_date:
            previous_date = return_list[x][1]
        else:
            return_list.pop(x)

    return return_list

