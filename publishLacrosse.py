import argparse
import configparser
import json
import logging
import persistqueue


from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient


config = configparser.ConfigParser()
config.read('config.ini')

host = config['DEFAULT']['host']
topic = config['DEFAULT']['topic']
clientId = config['DEFAULT']['client']
certPath = config['DEFAULT']['certpath']
sensor_queue_path = config['DEFAULT']['sensorqueue']


def main():
    # Init AWSIoTMQTTClient
    myAWSIoTMQTTClient = None
    myAWSIoTMQTTClient = AWSIoTMQTTClient(clientId)
    myAWSIoTMQTTClient.configureEndpoint(host, 8883)
    myAWSIoTMQTTClient.configureCredentials("{}AmazonRootCA1.pem".format(certPath),
                                            "{}private.pem.key".format(certPath),
                                            "{}certificate.pem.crt".format(certPath))

    # AWSIoTMQTTClient connection configuration
    myAWSIoTMQTTClient.configureAutoReconnectBackoffTime(1, 32, 20)
    myAWSIoTMQTTClient.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
    myAWSIoTMQTTClient.configureDrainingFrequency(2)  # Draining: 2 Hz
    myAWSIoTMQTTClient.configureConnectDisconnectTimeout(10)  # 10 sec
    myAWSIoTMQTTClient.configureMQTTOperationTimeout(5)  # 5 sec
    myAWSIoTMQTTClient.connect()

    logging.debug('Open queue')
    sensor_queue = persistqueue.SQLiteAckQueue(sensor_queue_path)
    logging.debug('Opened queue')
    while True:
        try:
            logging.debug('Try to get next item')
            item = sensor_queue.get()
            if myAWSIoTMQTTClient.publish(topic, json.dumps(item), 1):
                logging.debug('Published message to topic %s: %s\n' % (topic, json.dumps(item)))
                sensor_queue.ack(item)
            else:
                logging.error('Failed to published message to topic %s: %s\n' % (topic, json.dumps(item)))
                sensor_queue.nack(item)

        except KeyboardInterrupt:
            break

        except Exception:
            sensor_queue.nack(item)

    print("Disconnecting...")
    myAWSIoTMQTTClient.disconnect()


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
