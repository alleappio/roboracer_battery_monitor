import paho.mqtt.client as mqtt

class MqttClient:
    last_message = {}
    received_value = {}
    def __init__(self, ip, port, id, wildcard):
        self.received_value = {
            "voltage": False,
            "current": False,
            "rpm": False,
            "avgMotorCurrent": False,
            "ampHours": False,
            "wattHours": False,
            "tachometer": False,
            "tempMotor": False,
        }

        self.ip = ip
        self.port = port
        self.id = id
        self.wildcard = wildcard

        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

        self.client.connect(self.ip, self.port, 60)
        self.client.loop_forever()

    def on_connect(self, client, userdata, flags, rc):
        print("Connected with result code:", rc)
        client.subscribe(self.wildcard)
        print(f"subscribed to topic: {self.wildcard}")

    def on_message(self, client, userdata, msg):
        self.process_message(msg.topic, msg.payload.decode())

    def process_message(self, topic, message):
        splitted = topic.split("/")
        namespaces = splitted[:len(splitted)-2]
        value_name = splitted[-1]
        self.last_message[value_name] = message
        self.received_value[value_name] = True
        all_received_flag = True
        for i in self.received_value:
            if self.received_value[i] == False:
                all_received_flag = False

        if all_received_flag:
            print("{")
            for i in self.received_value:
                self.received_value[i] = False
                print(f"{i}: {self.last_message[i]}")
            print("}")

    def get_last_message(self, value_name):
        return self.last_message.get(value_name, None)
