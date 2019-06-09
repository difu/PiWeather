import json
import configparser

from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient

from RaspyRFM.rfm69 import FSK
from RaspyRFM.rfm69 import Rfm69
from RaspyRFM.sensors import lacross

import persistqueue

import argparse

import logging

config = configparser.ConfigParser()
config.read('config.ini')

host = config['DEFAULT']['host']
topic = config['DEFAULT']['topic']
clientId = config['DEFAULT']['client']
certPath = config['DEFAULT']['certpath']
sensor_queue_path = config['DEFAULT']['sensorqueue']


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


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', action='store_true', default=False,
                        dest='enable_debug',
                        help='Enable debug output')

    parsed_args = parser.parse_args()

    if parsed_args.enable_debug:
        logging.basicConfig(level=logging.DEBUG)

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
            if sensor_obj is None:
                continue

            for key in {'T', 'RH'}:
                if key in sensor_obj:
                    sensor_message = {'Sensor': "Sensor/lacrosse/" + sensor_obj["ID"] + "/" + key,
                                      'Timestamp': sensor_obj["timestamp"], 'value': sensor_obj[key]}

                    sensor_queue.put(sensor_message)
                    logging.debug('Published message to topic %s: %s\n' % (topic, json.dumps(sensor_message)))
                    # print('Published message to topic %s: %s\n' % (topic, json.dumps(sensor_message)))
                    # myAWSIoTMQTTClient.publish(topic, json.dumps(sensor_message), 1)
                    # print('Published message to topic %s: %s\n' % (topic, json.dumps(sensor_message)))
                    # print('Sensor Obj %s: %s\n' % (topic, json.dumps(sensor_obj)))
        except KeyboardInterrupt:
            break

    print("Disconnecting...")
    myAWSIoTMQTTClient.disconnect()


if __name__ == "__main__":
    main()