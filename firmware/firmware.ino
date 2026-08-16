#include <Arduino.h>
#include <WiFi.h>
#include <WiFiClient.h>
#include <PubSubClient.h>
#include "secrets.h"
#include "config.h"
#include "sensor_manager.h"

#define LDRPIN 1

const char *ssid = WIFI_SSID;
const char *pass = WIFI_PASSWORD;

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

    initSensor();

    setup_wifi();
    Serial.println(MQTT_HOST);
    client.setServer(MQTT_HOST, MQTT_PORT);
}

void loop()
{
    if (!client.connected())
    {
        reconnect();
    }

    client.loop();
    
    DHTData dhtData = readDHTData();
    float ambient_light = analogRead(LDRPIN);
    float soilMoisturePercent = readSoilMoisturePercent();

    if (!dhtData.isValid)
    {
        Serial.println("DHT read failed");
        delay(2000);
        return;
    }

    String payload = "{";
    payload += "\"temperature\":" + String(dhtData.temperature, 1) + ",";
    payload += "\"humidity\":" + String(dhtData.humidity, 1) + ",";
    payload += "\"soil_moisture\":" + String(soilMoisturePercent, 1) +",";
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