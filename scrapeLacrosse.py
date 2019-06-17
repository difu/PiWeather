import argparse
import configparser
import dateutil.parser as dparser
import json
import logging
import persistqueue
import time

from RaspyRFM.rfm69 import FSK
from RaspyRFM.rfm69 import Rfm69
from RaspyRFM.sensors import lacross


config = configparser.ConfigParser()
config.read('config.ini')

host = config['DEFAULT']['host']
topic = config['DEFAULT']['topic']
clientId = config['DEFAULT']['client']
certPath = config['DEFAULT']['certpath']
sensor_queue_path = config['DEFAULT']['sensorqueue']
scrape_interval_sec = int(config['DEFAULT']['scrapeintervalsec'])
valid_sensor_ids = config['DEFAULT']['valid_sensor_ids']

last_published_sensor_timestamps = {}


def get_json_from_sensor(the_rfm):
    """ Returns a json representation of the sensor data

    :param the_rfm: Raspberry RFM Module connection
    :returns: json object, if valid message, None otherwise
    """

    data = the_rfm.ReceivePacket(7)
    sensor_obj = lacross.Create(data)
    if sensor_obj:
        return sensor_obj.GetData()
    else:
        return None


def check_publish(sensor_id, timestamp):
    """ Returns True, if sensor data is old enough to be publish, False otherwise

    :param sensor_id: the id of the sensor
    :param timestamp: the timestamp of the measured value
    :return: True, if timestamp is older than last timestamp plus scrape interval
    """
    parsed_t = dparser.parse(timestamp)
    t_in_seconds = int(parsed_t.strftime('%s'))
    logging.debug('measured ts %s, actual ts %s ' % (str(t_in_seconds), str(time.time())))
    if sensor_id in last_published_sensor_timestamps:
        last_published_ts = int(last_published_sensor_timestamps[sensor_id])
        if last_published_ts < t_in_seconds-scrape_interval_sec:
            logging.debug('measured ts %s, last_published_ts %s ' % (str(t_in_seconds), str(last_published_ts)))
            last_published_sensor_timestamps[sensor_id] = t_in_seconds
            return True
    else:
        last_published_sensor_timestamps[sensor_id] = t_in_seconds
        return True
    return False


def main():
    # Publish to the same topic in a loop forever

    if Rfm69.Test(1):
        rfm = Rfm69(1, 24)  # when using the RaspyRFM twin
    elif Rfm69.Test(0):
        rfm = Rfm69()  # when using a single single 868 MHz RaspyRFM
    else:
        print("No RFM69 module found!")
        exit()

    rfm.SetParams(
        Freq=868.312,  # MHz center frequency
        Datarate=9.579,  # 17.241, #kbit/s baudrate
        ModulationType=FSK,  # modulation
        Deviation=90,  # 90 kHz frequency deviation
        SyncPattern=[0x2d, 0xd4],  # syncword
        Bandwidth=200,  # kHz bandwidth
        RssiThresh=-100  # -100 dB RSSI threshold
    )

    sensor_queue = persistqueue.SQLiteAckQueue(sensor_queue_path)

    while True:
        try:
            sensor_obj = get_json_from_sensor(rfm)
            logging.debug('Raw sensor :%s ' % sensor_obj)
            if sensor_obj is None:
                continue

            for key in {'T', 'RH'}:
                if key in sensor_obj:
                    sensor_id = "Sensor/lacrosse/" + sensor_obj["ID"] + "/" + key
                    if sensor_obj["ID"] in valid_sensor_ids.split(','):
                        pass
                    else:
                        logging.error('Wrong sensor id %s ' % (str(sensor_id)))
                        continue

                    if check_publish(sensor_id, sensor_obj["timestamp"]):

                        sensor_message = {'Sensor': sensor_id,
                                          'Timestamp': sensor_obj["timestamp"], 'value': sensor_obj[key]}

                        sensor_queue.put(sensor_message)
                        logging.debug('Wrote message to queue with topic %s: %s\n' % (topic, json.dumps(sensor_message)))
                    else:
                        logging.debug('Actual message too new. Skipping')

        except KeyboardInterrupt:
            break

    logging.debug('Finished')


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', action='store_true', default=False,
                        dest='enable_debug',
                        help='Enable debug output')

    parsed_args = parser.parse_args()

    log_level=logging.INFO
    if parsed_args.enable_debug:
        log_level = logging.DEBUG

    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S', level=log_level)

    main()
