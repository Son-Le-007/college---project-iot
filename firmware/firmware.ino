#include <Arduino.h>
#include <WiFi.h>
#include <WiFiClient.h>
#include <PubSubClient.h>
#include <DHT.h>
#include "secrets.h"

// Pin Configurations
#define DHTPIN 10
#define DHTTYPE DHT22
#define LDRPIN 1

DHT dht(DHTPIN, DHTTYPE);

const char *ssid = "Wokwi-GUEST";
const char *pass = "";

const char *mqtt_topic = "sensors";

WiFiClient espClient;
PubSubClient client(espClient);

void setup_wifi()
{
    Serial.print("Connecting to WiFi");

    WiFi.begin(ssid, pass);

    while (WiFi.status() != WL_CONNECTED)
    {
        delay(500);
        Serial.print(".");
    }

    Serial.println();
    Serial.println("WiFi connected");
    Serial.println(WiFi.localIP());
}

void reconnect()
{
    while (!client.connected())
    {
        Serial.print("Connecting to MQTT...");

        if (client.connect("esp32-s3-cam"))
        {
            Serial.println(" connected");
        }
        else
        {
            Serial.print(" failed, rc=");
            Serial.println(client.state());
            delay(3000);
        }
    }
}

void setup()
{
    Serial.begin(115200);

    dht.begin();

    setup_wifi();

    client.setServer(MQTT_HOST, MQTT_PORT);
}

void loop()
{
    if (!client.connected())
    {
        reconnect();
    }

    client.loop();

    float temperature = dht.readTemperature();
    float humidity = dht.readHumidity();
    float ambient_light = analogRead(LDRPIN);

    if (isnan(temperature) || isnan(humidity))
    {
        Serial.println("DHT read failed");
        delay(2000);
        return;
    }

    String payload = "{";
    payload += "\"temperature\":" + String(temperature, 1) + ",";
    payload += "\"humidity\":" + String(humidity, 1) + ",";
    payload += "\"ambient_light\":" + String(ambient_light, 1);
    payload += "}";

    Serial.println(payload);

    if (client.publish(mqtt_topic, payload.c_str()))
    {
        Serial.println("Publish OK");
    }
    else
    {
        Serial.println("Publish FAILED");
    }

    delay(5000);
}