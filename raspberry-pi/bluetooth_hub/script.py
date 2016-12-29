if __name__=="__main__":

    import logging
    import time
    import os

    from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
    import bluetooth


    # Custom MQTT message callback
    def customCallback(client, userdata, message):
        print("Received a new message: ")
        print(message.payload)
        print("from topic: ")
        print(message.topic)
        print("--------------\n\n")


    bd_address = "98:D3:31:B1:7A:90"
    port = 1
    BASE_DIR = os.path.join("/home", "pi", "aws_iot")

    # Set params
    useWebsocket = False
    host = "a14d54zsock0vu.iot.eu-west-1.amazonaws.com"
    rootCAPath = os.path.join(BASE_DIR, "root-CA.crt")
    certificatePath = os.path.join(BASE_DIR, "RaspberryPi3b.cert.pem")
    privateKeyPath = os.path.join(BASE_DIR, "RaspberryPi3b.private.key")

    # Configure logging
    logger = logging.getLogger("AWSIoTPythonSDK.core")
    logger.setLevel(logging.DEBUG)
    streamHandler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    streamHandler.setFormatter(formatter)
    logger.addHandler(streamHandler)

    # Init AWSIoTMQTTClient
    myAWSIoTMQTTClient = None
    if useWebsocket:
        myAWSIoTMQTTClient = AWSIoTMQTTClient("basicPubSub", useWebsocket=True)
        myAWSIoTMQTTClient.configureEndpoint(host, 443)
        myAWSIoTMQTTClient.configureCredentials(rootCAPath)
    else:
        myAWSIoTMQTTClient = AWSIoTMQTTClient("basicPubSub")
        myAWSIoTMQTTClient.configureEndpoint(host, 8883)
        myAWSIoTMQTTClient.configureCredentials(rootCAPath, privateKeyPath, certificatePath)

    # AWSIoTMQTTClient connection configuration
    myAWSIoTMQTTClient.configureAutoReconnectBackoffTime(1, 32, 20)
    myAWSIoTMQTTClient.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
    myAWSIoTMQTTClient.configureDrainingFrequency(2)  # Draining: 2 Hz
    myAWSIoTMQTTClient.configureConnectDisconnectTimeout(10)  # 10 sec
    myAWSIoTMQTTClient.configureMQTTOperationTimeout(5)  # 5 sec

    # Connect and subscribe to AWS IoT
    myAWSIoTMQTTClient.connect()
    myAWSIoTMQTTClient.subscribe("cornelisoutshoornplaats/bedroom/temphum", 1, customCallback)
    time.sleep(2)

    # Set up the socket
    sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    sock.connect((bd_address, port))
    print "connected"
    sock.settimeout(5.0)
    sock.send("Hello from the raspberry")
    print "send data"


    # Start the listening loop
    sock.setblocking(0)
    total_data = []
    data = ''
    begin = time.time()
    print "listening for data"
    while True:
        try:
            data = sock.recv(255)
            if data:
                if "\r\n" in data:
                    split_data = data.split("\r\n")
                    last_part = split_data[0]
                    first_part = split_data[-1]
                    total_data.append(last_part)
                    print "received %s" % "".join(total_data)
                    myAWSIoTMQTTClient.publish("cornelisoutshoornplaats/bedroom/temphum", "".join(total_data), 1)
                    total_data = [first_part]
                else:
                    total_data.append(data)
                begin = time.time()
            else:
                time.sleep(3)
        except Exception as e:
            print e
            time.sleep(2)
            pass
    sock.close()
