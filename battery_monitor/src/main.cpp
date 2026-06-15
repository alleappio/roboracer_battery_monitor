#include <Arduino.h>
#include <VescUart.h>
#include <WiFi.h>

#include "HardwareSerial.h"
#include "WiFiType.h"
#include "esp32-hal-gpio.h"
#include "parameters.hpp"

WiFiClient wifiClient;
HardwareSerial vescSerial(1);
VescUart vescUart;

void setupWifi(){
    WiFi.begin(ssid, pass);
    while(WiFi.status() != WL_CONNECTED){
        delay(500);
    }
}

void setup(){
    Serial.begin(115200);
    vescSerial.begin(115200, SERIAL_8N1, uart_rx, uart_tx);
    pinMode(LED_BUILTIN, OUTPUT);
    vescUart.setSerialPort(&vescSerial);
    setupWifi();    
}

void loop(){
    digitalWrite(LED_BUILTIN, HIGH);
    delay(1000);

    digitalWrite(LED_BUILTIN, LOW);
    delay(1000);
}
