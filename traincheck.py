# Credit goes to Realtime Trains (realtimetrains.co.uk) for providing the API which is freely available
# visit https://api-portal.rtt.io/ for more details

# Takes four arguments, station_from & station_to are strings in tiploc format. See the TIPLOC spreadsheet for information
# Also takes time_search a datetime variable for the search - the API will get the previous 2 hours of trains up to the date/time given
# and time_window number of hours after.

# The return_list includes the name of the origin station and time it left. Also the planned time to arrive at the destination, 
# the type (which can be "A" for trains already left and "E" for those estimated). The departure will either be the estimated time 
# or the actual time, depending on the type. The difference relates to how far ahead/behind the time train is (either estimated or actual).
# The start and end hold the details of the start and end stations, as reported by the API. This is their proper names, not TIPLOC
# return_list.append((origin_name, origin_time, planned, type, departure, difference, start, end))

def traincheck(station_from, station_to, time_search, time_window):

    import requests
    from requests.auth import HTTPBasicAuth
    from datetime import datetime, timedelta
    import traincheck_config

    start = ""
    end = ""

    rtt_baseaddress = "https://data.rtt.io"

    #
    # Get Access Token First

    headers = {
        "Authorization": f"Bearer {traincheck_config.request_token}"
    }

    request = requests.get(rtt_baseaddress + "/api/get_access_token", headers = headers)

    access_token = ""

    if request.status_code == 200:
        data = request.json()
        if data['token'] is not None:
            access_token = data['token']

    if access_token == "":
        return

    #
    # Build API Call

    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    rtt_search = "/rtt/location?code=gb-nr:{}&filterTo=gb-nr:{}".format(station_from,station_to)

    #
    # Add Time Details

    rtt_time = "&timeFrom={}-{:0>2}-{:0>2}T{:0>2}:{:0>2}:00".format(time_search.year, time_search.month, time_search.day, time_search.hour, time_search.minute)
    rtt_other = f"&timeWindow={time_window}&timeTolerance=true&detailed=true"

    #
    # API Call to get all matching services

    services_list = []

    try:
        request = requests.get(rtt_baseaddress + rtt_search + rtt_time + rtt_other, headers = headers)
        if request.status_code == 200:
            data = request.json()
            if data is not None:
                start = data['query']['location']['description']
                end = data['query']['filterTo']['description']
            
                if 'services' in data:
                    services_list = services_list + data['services']

    except ConnectionError as E:
        print (f"Exception (requesting data): {E}")

    return_list = []

    #
    # Filter the services and set the return values

    try:
        for service in services_list:

            #print(f"Service: {service}")

            origin_name = ""
            origin_time = datetime.now()
            planned = datetime.now()
            departure = datetime.now()
            difference = 0
            type = ""

            origin_name = service['origin'][0]['location']['description']
            origin_time = datetime.strptime(service['origin'][0]['temporalData']['scheduleAdvertised'],"%Y-%m-%dT%H:%M:%S")
            planned = datetime.strptime(service['temporalData']['departure']['scheduleAdvertised'],"%Y-%m-%dT%H:%M:%S")
            
            if 'realtimeActual' in service['temporalData']['departure']:
                type = "A"
                departure = datetime.strptime(service['temporalData']['departure']['realtimeActual'],"%Y-%m-%dT%H:%M:%S")
                difference = (departure - planned).total_seconds() / 60

            if 'realtimeForecast' in service['temporalData']['departure']:
                type = "E"
                departure = datetime.strptime(service['temporalData']['departure']['realtimeForecast'],"%Y-%m-%dT%H:%M:%S")
                difference = (departure - planned).total_seconds() / 60

            return_list.append((origin_name, origin_time, planned, type, departure, difference, start, end))

    except Exception as E:
        print (f"Exception (converting data): {E}")
        return []

    #
    # Sort the services by the planned arrival time/date and remove duplicates
    # This was implemented for the earlier version of the API. Commented out while testing the new (2026) API version.

    #return_list = sorted(return_list, key=lambda x: x[2])

    # Remove duplicates

    #previous_date = datetime.min
    #for x in range(len(return_list)-1,-1,-1):
        #if return_list[x][1] != previous_date:
            #previous_date = return_list[x][1]
        #else:
            #return_list.pop(x)

    return return_list
