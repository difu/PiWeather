import argparse
import configparser
import datetime
import time
import socket
import os
import persistqueue
import json
import logging
from multiprocessing import Process
import requests


config = configparser.ConfigParser()
config.read('config.ini')
sensor_queue_path = config['DAVIS']['sensorqueue']
weatherlink_ip_port = config['DAVIS']['weatherlink_ip_port']
scrape_interval_sec = int(config['DAVIS']['scrapeintervalsec'])


sensor_queue = persistqueue.SQLiteAckQueue(sensor_queue_path)

current_conditions_url = 'http://' + weatherlink_ip_port + '/v1/current_conditions'

""" {
  "payload": {
    "value": [
      19.5,
      "C"
    ]
  },
  "Sensor": "Sensor/lacrosse/44/T",
  "Timestamp": "2019-05-17T17:04:39"
} """


def make_request_using_socket(url):
    try:
        resp = requests.get(url)
        json_data = json.loads(resp.text)
        if json_data["data"] is None:
            logging.error(json_data["error"])
        else:
            logging.debug("Raw Davis Sensor Data: " + json.dumps(json_data["data"]))
            return json_data
    except ConnectionRefusedError:
        print("Encountered 'ConnectionRefusedError'. Please Retry")
    except TimeoutError:
        print("Encountered 'TimeoutError'. Please Retry")


def get_sensor_json_items(davis_json, sensor_id, metrics):
    all_conditions = davis_json["data"]["conditions"]

    for conditions in all_conditions:
        the_sensor_id = conditions['txid']
        if the_sensor_id == sensor_id:
            the_items = []
            for metric in metrics:
                davis_metric = ""
                unit = ""
                if metric == "T":
                    davis_metric = "temp"
                    unit = "C"
                elif metric == "RH":
                    davis_metric = "hum"
                    unit = "%"
                else:
                    logging.error("Unknown metric " + metric)
                    continue
                value = conditions[davis_metric]
                if unit == "C":
                    # (75 °F − 32) × 5/9 = 24,333 °C
                    value = (value-32) * (5/9)
                logging.debug("Sensordata: ID: " + str(sensor_id) + ", Metric:" + metric + ", Value:" + str(value))
                the_item = {"Sensor": "Sensor/Davis/"+str(sensor_id)+"/" + metric,
                            "Timestamp": datetime.datetime.now().replace(microsecond=0).isoformat(),
                            "value": [
                                         value, unit
                                    ]
                            }

                the_items.append(the_item)
            return the_items
    return False


def main():
    global current_conditions_url
    global sensor_queue

    while True:
        try:
            raw_json = make_request_using_socket(current_conditions_url)
            items = get_sensor_json_items(raw_json, 1, {"T", "RH"})
            if items is not False:
                for item in items:
                    logging.debug("Item: " + str(item))
                    #item = str(item).replace("'", '"')
                    sensor_queue.put(item)
                    # item_json = json.loads(str(item))
            logging.debug("Put item(s) in queue, sleeping.")
            time.sleep(scrape_interval_sec)

        except ConnectionRefusedError:
            logging.error("Encountered 'ConnectionRefusedError'. Aborting")
            break
        except TimeoutError:
            logging.error("Encountered 'TimeoutError'. Aborting")
            break
        except KeyboardInterrupt:
            break

    logging.debug('Finished')


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', action='store_true', default=False,
                        dest='enable_debug',
                        help='Enable debug output')
    parser.add_argument('-dry', action='store_true', default=False,
                        dest='dry_run',
                        help='only print output and run once')

    parsed_args = parser.parse_args()

    log_level=logging.INFO
    if parsed_args.enable_debug:
        log_level = logging.DEBUG

    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S', level=log_level)

    main()

