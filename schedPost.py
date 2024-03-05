from datetime import datetime, timedelta
import os
import re
import json
import csv
import sys
import requests
import argparse
import logging

# Initializing argparser and setting commonly used timestamps
argparser=argparse.ArgumentParser()
argparser.add_argument('-c','--config', required=False, type=str,help="Optionally provide a path to a JSON file containing configuration options. If not provided, options must be supplied using command line flags.")
argparser.add_argument('--file', required=True, type=open, help="The comma-delimited csv file you want to use as a source.")
dateStamp = datetime.now().strftime("%Y-%m-%d")
timeStamp = datetime.now().strftime("%Y-%m-%d %H_%M_%S")

def post_statuses(server,access_token,data):
    # Function for looping through all of the entries and posting them
    successes = 0
    failures = 0
    url = f"https://{server}/api/v1/statuses"
    for post in data:
        schedule = datetime.strftime(datetime.combine(datetime.strptime(post["post_date"],"%Y-%m-%d"), datetime.strptime("15:00:00","%H:%M:%S").time()),"%Y-%m-%dT%H:%M:%S.%fZ")
        
        # This is only here for testing, setting the scheduling time for 5 minutes from runtime
        # td = timedelta(minutes=5)
        # schedule = datetime.strftime(datetime.utcnow() + td,"%Y-%m-%dT%H:%M:%S.%fZ")
        # pl("debug",f"Schedule: {schedule}")

        # Start forming the json to send with the request
        requestJson = {
            "status": post["status"],
            "scheduled_at": schedule,
            "visibility": post["visibility"]
        }
        # Some attributes that might not always be filled out
        if (post["sensitive"] == "Y"):
            requestJson["sensitive"] = "true"
            requestJson["spoiler_text"] = post["spoiler_text"]
        else:
            requestJson["sensitive"] = "false"
        pl("deubg", f"Request JSON: {requestJson}")

        # Send the request and check the response
        resp = requests.post(url,headers={"Authorization": f"Bearer {access_token}"},json=requestJson,timeout=5)
        respJson = resp.json()
        match resp.status_code:
            case 200:
                pl("info", f"Status scheduled: {respJson}")
                successes += 1
            case 401:
                pl("error", f"{server} : Request unauthorized. {respJson}")
                pl("error", f"Failed post: {requestJson}")
                failures += 1
            case 422:
                pl("error", f"{server} : Unprocessable entity. {respJson}")
                pl("error", f"Failed post: {requestJson}")
                failures += 1

    # Print the numbers
    pl("info", f"    {len(data)} entries submitted.")
    pl("info", f"    {successes} successfully scheduled.")
    pl("info", f"    {failures} failed to schedule.")

def pl(level,message):
    # This is a function to make logging + writing to the console simultaneous
    match level:
        case "debug":
            logging.debug(message)
        case "info":
            logging.info(message)
        case "error":
            logging.error(message)
        case _:
            logging.info(message)
    print(message)

if __name__ == "__main__":
    # Getting arguments and pulling from the config file
    arguments = argparser.parse_args()
    if(arguments.config != None):
        if os.path.exists(arguments.config):
            with open(arguments.config, "r", encoding="utf-8") as f:
                config = json.load(f)
            for key in config:
                setattr(arguments, key.lower().replace('-','_'), config[key])
        else:
            print(f"Config file {arguments.config} doesn't exist")
            sys.exit(1)
    
    # If no server or access token are specified, quit
    if(arguments.server == None or arguments.access_token == None):
        print("You must supply at least a server name and access token")
        sys.exit(1)
    
    # In case someone provided the server name as url instead,
    setattr(arguments, 'server', re.sub(r"^(https://)?([^/]*)/?$", "\\2", arguments.server))

    # Logging
    log_file = arguments.log_directory + "\log_" + dateStamp + ".txt"
    def switch(loglevel):
        if loglevel == "info":
            return logging.INFO
        if loglevel == "debug":
            return logging.DEBUG
        if loglevel == "error":
            return logging.ERROR
        else:
            return logging.INFO
    logging.basicConfig(format='%(asctime)s %(levelname)-8s %(message)s',filename=log_file, level=switch(arguments.log_level), datefmt='%Y-%m-%d %H:%M:%S')

    # First bit of logging
    pl("debug", f"Server: {arguments.server}")
    pl("debug", f"Log level: {arguments.log_level}")
    pl("debug", f"Log directory: {arguments.log_directory}")
    pl("debug", f"File: {arguments.file}")

    # Pulling in the specified file and turning it into a Dict list
    data = list(csv.DictReader(arguments.file, delimiter=","))
    pl("info", f"Provided file read. {arguments.file}")
    pl("info", f"Entries in file: {len(data)}")
    if(len(data) == 0):
        pl("error", "You must supply a file with one or more record")
        sys.exit(1)

    # Check for the necessary values
    sample = data[0]
    if (   ("post_date" not in sample.keys())
        or ("status" not in sample.keys())):
        pl("error", "The provided file does not contain the necessary headers: post_date, status")
        sys.exit(1)

    # Call the function to post statuses, passing along the needed bits
    post_statuses(arguments.server,arguments.access_token,data)

    pl("info", f"    Run completed")