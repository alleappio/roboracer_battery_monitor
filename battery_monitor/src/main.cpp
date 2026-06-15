#include <Arduino.h>
#include <VescUart.h>
#include <WiFi.h>
#include <PubSubClient.h>

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
        Serial.printf("Voltage: %.2f V\n", vescUart.data.inpVoltage);
        Serial.printf("Current: %.2f A\n", vescUart.data.avgInputCurrent);
        Serial.printf("RPM: %d\n", vescUart.data.rpm);
    } else {
        Serial.println("Failed to read VESC");
    }

    delay(1000);

    // digitalWrite(LED_BUILTIN, HIGH);
    // mqttClient.publish("/test", "On");
    // Serial.println("On");
    // delay(1000);
    //
    // digitalWrite(LED_BUILTIN, LOW);
    // mqttClient.publish("/test", "Off");
    // Serial.println("Off");
    // delay(1000);
}
