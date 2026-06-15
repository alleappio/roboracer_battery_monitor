#include <Arduino.h>
#include <VescUart.h>
#include <WiFi.h>
#include <PubSubClient.h>
#include <cstdio>
#include <string.h>

#include "HardwareSerial.h"
#include "WiFiType.h"
#include "esp32-hal-gpio.h"
#include "parameters.hpp"

WiFiClient wifiClient;
HardwareSerial vescSerial(1);
VescUart vescUart;
PubSubClient mqttClient(wifiClient);

void setupWifi(){
    WiFi.begin(ssid, pass);
    while(WiFi.status() != WL_CONNECTED){
        delay(500);
    }
}

void setupMqtt(){
    mqttClient.setServer(broker_ip, broker_port);
    while (!mqttClient.connected()) {
        mqttClient.connect(mqttId);
        Serial.printf("connecting to %s:%d\n", broker_ip, broker_port);
        delay(100);
    }
    Serial.println("connected to mqtt");
}

void sendMessage(char* value_string, float value){
    char message[32];
    char topic[32];
    snprintf(message, sizeof(message), "%.2f", value);
    snprintf(topic, sizeof(topic), "/%s/%s", mqttId, value_string);
    Serial.printf("%s: %s", topic, message);
    mqttClient.publish(topic, message);
}

void setup(){
    Serial.begin(115200);
    Serial.println("helloooo");
    vescSerial.begin(115200, SERIAL_8N1, uart_rx, uart_tx);
    pinMode(LED_BUILTIN, OUTPUT);
    vescUart.setSerialPort(&vescSerial);
    setupWifi();
    setupMqtt();
}

void loop(){
    mqttClient.loop();

    if (vescUart.getVescValues()) {
        sendMessage("voltage", vescUart.data.inpVoltage);
        sendMessage("current", vescUart.data.avgInputCurrent);
        sendMessage("rpm", vescUart.data.rpm);
        sendMessage("avgMotorCurrent", vescUart.data.avgMotorCurrent);
        sendMessage("ampHours", vescUart.data.ampHours);
        sendMessage("wattHours", vescUart.data.wattHours);
        sendMessage("tachometer", vescUart.data.tachometer);
        sendMessage("tempMotor", vescUart.data.tempMotor);
    } else {
        Serial.println("Failed to read VESC");
    }

    // delay(1000);
}
