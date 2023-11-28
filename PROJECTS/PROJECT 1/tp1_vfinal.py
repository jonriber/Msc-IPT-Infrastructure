import network
import socket
from time import sleep
from picozero import pico_temp_sensor, pico_led
import machine
from umqtt.simple import MQTTClient

ssid = 'CasaDCF'
password = 'naotempassword2020'

mqtt_broker = 'broker.mqttdashboard.com'
mqtt_client_id = 'clientId-fred'
mqtt_topic_led = b'melhorgrupoled'

def connect():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    while not wlan.isconnected():
        print('A tentar ligar...')
        sleep(1)
    ip = wlan.ifconfig()[0]
    print(f'Conectado com o ip {ip}')
    return ip

def open_socket(ip):
    address = (ip, 80)
    connection = socket.socket()
    connection.bind(address)
    connection.listen(1)
    return connection

def connect_mqtt():
    client = MQTTClient(mqtt_client_id, mqtt_broker, keepalive=60)
    client.connect()
    print(f'Conectado ao broker MQTT: {mqtt_broker}')
    return client

def publish_led_state(client, state):
    client.publish(mqtt_topic_led, state.encode())

def publish_temperature(client, temperature):
    client.publish(b'/temperature', str(temperature).encode())

def control_led(state):
    if state == 'ON':
        print('Ligando LED...')
        pico_led.on()
    elif state == 'OFF':
        print('Desligando LED...')
        pico_led.off()

def webpage(temperature, state):
    html = """
        <!DOCTYPE html>
        <html lang="en">

        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Controle de LED e Temperatura</title>
            <style>
                body {
                    font-family: 'Arial', sans-serif;
                    background-color: #f5f5f5;
                    text-align: center;
                    margin: 20px;
                    color: #333;
                }

                h1 {
                    color: #008CBA;
                }

                form {
                    margin-top: 20px;
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                }

                input[type="submit"] {
                    padding: 15px 25px;
                    font-size: 18px;
                    border: none;
                    border-radius: 5px;
                    cursor: pointer;
                    margin-top: 15px;
                    transition: background-color 0.3s ease;
                }

                input[type="submit"][value="Ligar LED"] {
                    background-color: #4CAF50;
                    color: white;
                }

                input[type="submit"][value="Desligar LED"] {
                    background-color: #FF6347;
                    color: white;
                }

                p {
                    font-size: 18px;
                    margin-top: 20px;
                    color: #333;
                }
            </style>
        </head>

        <body>
            <h1>Controle de LED e Temperatura</h1>

            <form action="/lighton" method="post">
                <input type="submit" name="led" value="Ligar LED" />
            </form>

            <form action="/lightoff" method="post">
                <input type="submit" name="led" value="Desligar LED" />
            </form>
            <br><br><br>
    """

    if state == "ON":
        print('LED está ON...')
        html += '<img src="http://a2o3.com/images/aceso.gif?{time.ticks_ms()}" alt="LED ligado">'
    elif state == "OFF":
        print('LED está OFF...')
        html += '<img src="http://a2o3.com/images/apagado.gif?{time.ticks_ms()}" alt="LED desligado">'
    
    temperature_formatted = "{:.1f}".format(temperature)
    html += f'<p><strong>Temperatura Atual:</strong> {temperature_formatted} °C</p></body></html>'
    
    return html

def serve(connection, mqtt_client):
    state = 'OFF'
    pico_led.off()

    while True:
        client = connection.accept()[0]
        request = client.recv(1024).decode('utf-8')
        request_lines = request.split('\r\n')

        try:
            path = request_lines[0].split()[1].split('?')[0]
        except IndexError:
            path = ""

        if path == '/lighton':
            print('Recebido comando para ligar o LED...')
            publish_led_state(mqtt_client, 'ON')
            control_led('ON')
            state = 'ON'
        elif path == '/lightoff':
            print('Recebido comando para desligar o LED...')
            publish_led_state(mqtt_client, 'OFF')
            control_led('OFF')
            state = 'OFF'

        temperature = pico_temp_sensor.temp
        publish_temperature(mqtt_client, temperature)

        html = webpage(temperature, state)
        response = f"HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n{html}"
        client.send(response.encode())
        client.close()

try:
    ip = connect()
    connection = open_socket(ip)
    mqtt_client = connect_mqtt()
    serve(connection, mqtt_client)
except KeyboardInterrupt:
    machine.reset()
