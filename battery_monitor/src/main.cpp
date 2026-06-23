#include <Arduino.h>
#include <VescUart.h>
#include <WiFi.h>
#include <PubSubClient.h>
#include <cstdint>
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
hw_timer_t *sendTimer = NULL;
bool sendNow;


void setupWifi(){
    WiFi.begin(Params::ssid, Params::pass);
    while(WiFi.status() != WL_CONNECTED){
        delay(500);
    }
}

void setupMqtt(){
    mqttClient.setServer(Params::broker_ip, Params::broker_port);
    while (!mqttClient.connected()) {
        mqttClient.connect(Params::mqttId);
        Serial.printf("connecting to %s:%d\n", Params::broker_ip, Params::broker_port);
        delay(100);
    }
    Serial.println("connected to mqtt");
}

void sendMessage(char* value_string, float value){
    char message[32];
    char topic[32];
    snprintf(message, sizeof(message), "%.4f", value);
    snprintf(topic, sizeof(topic), "%s/%s", Params::mqttId, value_string);
    Serial.printf("%s: %s", topic, message);
    mqttClient.publish(topic, message);
}

void IRAM_ATTR sendTimerCallback() {
    sendNow = true;
}

void setupTimer(){
    sendTimer = timerBegin(0, 80, true);
    timerAttachInterrupt(sendTimer, &sendTimerCallback, true);
    uint64_t timer_time = (uint64_t) 1e6 / Params::mqtt_send_rate;
    timerAlarmWrite(sendTimer, timer_time, true);
    timerAlarmEnable(sendTimer);
    sendNow = false;
}

void setup(){
    Serial.begin(115200);
    Serial.println("helloooo");
    vescSerial.begin(115200, SERIAL_8N1, Params::uart_rx, Params::uart_tx);
    pinMode(LED_BUILTIN, OUTPUT);
    vescUart.setSerialPort(&vescSerial);
    setupWifi();
    setupMqtt();
    setupTimer();
}

void loop(){
    mqttClient.loop();
    if(sendNow){
        sendNow = false;
        if (vescUart.getVescValues()) {
            sendMessage("dutyCycleNow", vescUart.data.dutyCycleNow);
            sendMessage("wattHoursCharged", vescUart.data.wattHoursCharged);
            sendMessage("tachometerAbs", vescUart.data.tachometerAbs);
            sendMessage("tempMosfet", vescUart.data.tempMosfet);
            sendMessage("pidPos", vescUart.data.pidPos);
            sendMessage("id", vescUart.data.id);
            sendMessage("error", vescUart.data.error); 
            sendMessage("voltage", vescUart.data.inpVoltage);
            sendMessage("current", vescUart.data.avgInputCurrent);
            sendMessage("rpm", vescUart.data.rpm);
            sendMessage("avgMotorCurrent", vescUart.data.avgMotorCurrent);
            sendMessage("ampHours", vescUart.data.ampHours);
            sendMessage("ampHoursCharged", vescUart.data.ampHoursCharged);
            sendMessage("wattHours", vescUart.data.wattHours);
            sendMessage("tachometer", vescUart.data.tachometer);
            sendMessage("tempMotor", vescUart.data.tempMotor);
        } else {
            Serial.println("Failed to read VESC");
        }
    }
}
