import os
import requests
import socket
import datetime
import time
import logging

# Configuration from environment variables with defaults
file_path = os.path.dirname(os.path.realpath(__file__))

# Use /app/logs in Docker, current directory otherwise
log_dir = os.getenv('LOG_DIR', file_path)
if not os.path.exists(log_dir) and log_dir != file_path:
    os.makedirs(log_dir, exist_ok=True)

logging.basicConfig(filename=f'{log_dir}/networkinfo.log', format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')

# Home Assistant Configuration
HA_HOST = os.getenv('HA_HOST', '192.168.1.116')
HA_PORT = os.getenv('HA_PORT', '8123')
HA_WEBHOOK_ID = os.getenv('HA_WEBHOOK_ID', '-1r22edZi_iswfPBM0u1XVnf6')
HA_USE_HTTPS = os.getenv('HA_USE_HTTPS', 'true').lower() == 'true'

# Build webhook URL
protocol = 'https' if HA_USE_HTTPS else 'http'
URL_FOR_WEBHOOK = f'{protocol}://{HA_HOST}:{HA_PORT}/api/webhook/{HA_WEBHOOK_ID}'

# Timing configuration (in seconds)
SLEEP_WHILE_OFFLINE = int(os.getenv('SLEEP_WHILE_OFFLINE', '60'))
SLEEP_WHILE_ONLINE = int(os.getenv('SLEEP_WHILE_ONLINE', '30'))
SLEEP_AFTER_RESET = int(os.getenv('SLEEP_AFTER_RESET', '120'))

NUMBER_OF_FAILED_PINGS_TO_RESET = int(os.getenv('NUMBER_OF_FAILED_PINGS_TO_RESET', '3'))
NUMBER_OF_ATTEMPTS_TO_LOG_ALIVE = int(os.getenv('NUMBER_OF_ATTEMPTS_TO_LOG_ALIVE', '20'))  # ~10 minutes if always online

MAX_NUMBER_OF_RESETS = int(os.getenv('MAX_NUMBER_OF_RESETS', '3'))

# Log configuration on startup
logging.warning("=== RouterDown Monitor Starting ===")
logging.warning(f"Webhook URL: {URL_FOR_WEBHOOK}")
logging.warning(f"Sleep while offline: {SLEEP_WHILE_OFFLINE}s")
logging.warning(f"Sleep while online: {SLEEP_WHILE_ONLINE}s")
logging.warning(f"Sleep after reset: {SLEEP_AFTER_RESET}s")
logging.warning(f"Failed pings to reset: {NUMBER_OF_FAILED_PINGS_TO_RESET}")
logging.warning(f"Max resets per outage: {MAX_NUMBER_OF_RESETS}")

# creating log file in the currenty directory
# ??getcwd?? get current directory,
# os function, ??path?? to specify path

def ping():
    # to ping a particular IP
    try:
        socket.setdefaulttimeout(3)
        
        # if data interruption occurs for 3
        # seconds, <except> part will be executed

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # AF_INET: address family
        # SOCK_STREAM: type for TCP

        host = "8.8.8.8"
        port = 53

        server_address = (host, port)
        s.connect(server_address)

    except OSError as error:
        return False
        # function returns false value
        # after data interruption

    else:
        s.close()
        # closing the connection after the
        # communication with the server is completed
        return True


def calculate_time(start, stop):

    # calculating unavailability
    # time and converting it in seconds
    difference = stop - start
    seconds = float(str(difference.total_seconds()))
    return str(datetime.timedelta(seconds=seconds)).split(".")[0]


def first_check():
    # to check if the system was already
    # connected to an internet connection

    if ping():
        # if ping returns true
        live = "CONNECTION ACQUIRED"
        print(live)
        connection_acquired_time = datetime.datetime.now()
        acquiring_message = "connection acquired at: " + \
            str(connection_acquired_time).split(".")[0]
        print(acquiring_message)

        logging.warning(live)
        logging.warning(acquiring_message)

        return True

    else:
        # if ping returns false
        not_live = "CONNECTION NOT ACQUIRED"
        print(not_live)
        logging.warning(not_live)

        return False


def main():

    # main function to call functions
    monitor_start_time = datetime.datetime.now()
    monitoring_date_time = "monitoring started at: " + \
        str(monitor_start_time).split(".")[0]

    if first_check():
        # if true
        print(monitoring_date_time)
        # monitoring will only start when
        # the connection will be acquired

    else:
        # if false
        while True:
        
            # infinite loop to see if the connection is acquired
            if not ping():
                # if connection not acquired
                time.sleep(SLEEP_WHILE_ONLINE)
            else:
                
                # if connection is acquired
                first_check()
                print(monitoring_date_time)
                break


    logging.warning(monitoring_date_time)

    alive_check = 0
    while True:
        if alive_check >= NUMBER_OF_ATTEMPTS_TO_LOG_ALIVE:
            logging.warning("I am alive and kicking! Number of attemps: %s", str(alive_check))
            alive_check = 0
        # infinite loop, as we are monitoring
        # the network connection till the machine runs
        alive_check += 1

        if ping():
            # if true: the loop will execute after every 5 seconds
            time.sleep(SLEEP_WHILE_ONLINE)

        else:
            # if false: fail message will be displayed
            down_time = datetime.datetime.now()
            fail_msg = "disconnected at: " + str(down_time).split(".")[0]
            print(fail_msg)
            continuos_failed_pings = 1 
            number_of_resets = 0
    
            logging.warning(fail_msg)

            while not ping():
                logging.warning("continuos_failed_pings ="+str(continuos_failed_pings))
                logging.warning("number_of_resets ="+str(number_of_resets))

                if continuos_failed_pings % NUMBER_OF_FAILED_PINGS_TO_RESET == 0 and number_of_resets <= MAX_NUMBER_OF_RESETS:
                    #reset the router using a home assistant web hook :)
                    logging.warning("ATTEMPTING RESET!")

                    x = requests.post(URL_FOR_WEBHOOK, verify=False)

                    if x.status_code != 200:
                        logging.warning("Web hook failed: %s", str(x.reason))
                    else: 
                        number_of_resets += 1
                        logging.warning("RESETTING ROUTER NOW")

                    time.sleep(SLEEP_AFTER_RESET)
                    continuos_failed_pings = 0

                # infinite loop, will run till ping() return true
                continuos_failed_pings += 1
                time.sleep(SLEEP_WHILE_OFFLINE)
                
            up_time = datetime.datetime.now()
            
            # after loop breaks, connection restored
            uptime_message = "connected again: " + str(up_time).split(".")[0]

            down_time = calculate_time(down_time, up_time)
            unavailablity_time = "connection was unavailable for: " + down_time

            print(uptime_message)
            print(unavailablity_time)

            logging.warning("%s", uptime_message)
            logging.warning("%s", unavailablity_time)

main()
