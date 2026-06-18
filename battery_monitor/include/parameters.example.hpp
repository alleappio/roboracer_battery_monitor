#ifndef PARAMETERS_HPP
#define PARAMETERS_HPP
namespace Params {
    constexpr inline int uart_rx = 44;
    constexpr inline int uart_tx = 43;

    constexpr inline char* ssid = "";
    constexpr inline char* pass = "";

    constexpr inline char* broker_ip = "127.0.0.1";
    constexpr inline int broker_port = 1883;

    constexpr inline char* mqttId = "";

    constexpr inline float mqtt_send_rate = 20; // hz
}

#endif //PARAMETERS_HPP
