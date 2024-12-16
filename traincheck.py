# Credit goes to Realtime Trains (realtimetrains.co.uk) for providing the API which is freely available
# visit https://api.rtt.io for more details

# Takes four arguments, station_from & station_to are strings in tiploc format. See the TIPLOC spreadsheet for information
# Also takes time_search a datetime variable for the search

def traincheck(station_from, station_to, time_search):

    import requests
    from requests.auth import HTTPBasicAuth
    from datetime import datetime, timedelta
    import traincheck_config

    # API & search details

    start = ""
    end = ""

    rtt_baseaddress = "https://api.rtt.io/api/v1/json/search/"
    rtt_search = "{}/to/{}/".format(station_from,station_to)
    auth = HTTPBasicAuth(traincheck_config.rtt_username, traincheck_config.rtt_password)

    # Time calculation

    rtt_time = "{}/{:0>2}/{:0>2}/{:0>2}{:0>2}".format(time_search.year, time_search.month, time_search.day, time_search.hour, time_search.minute)
    # Debug to show whole day
    #rtt_now = "{}/{:0>2}/{:0>2}".format(time_calc.year, time_calc.month, time_calc.day)

    #API Calls

    services_list = []

    request = requests.get(rtt_baseaddress + rtt_search +rtt_time, auth=auth)
    if request.status_code == 200:
        data = request.json()
        if data is not None:
            start = data['location']['name']
            end = data['filter']['destination']['name']
            
        if data['services'] is not None:
            services_list = services_list + data['services']

    # Return list is a list of tuples containing origin place, origin time, planned time, estimated time (can be zero for future departures), 
    # difference (can be zero for future departures) & service type (Actual, Estimated, Future)
    # [(origin, origin_time, planned, type, estimated, difference, start_station, end_station)]

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

            if service['locationDetail']['tiploc'] == station_from and service['isPassenger'] == True:

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

                return_list.append((origin_name, origin_time, planned, type, estimated, difference, start, end))

    except Exception as E:
        print (E)
        return []

    # Sort by planned arrival time/date

    return_list = sorted(return_list, key=lambda x: x[2])

    # Remove duplicates

    previous_date = datetime.min
    for x in range(len(return_list)-1,-1,-1):
        if return_list[x][1] != previous_date:
            previous_date = return_list[x][1]
        else:
            return_list.pop(x)

    return return_list
