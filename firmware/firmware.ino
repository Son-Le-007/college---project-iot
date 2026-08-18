#include <Arduino.h>
#include <WiFi.h>
#include <WiFiClient.h>
#include <PubSubClient.h>
#include "secrets.h"
#include "config.h"
#include "sensor_manager.h"
#include "storage_manager.h"

#define LDRPIN 1

const char *ssid = WIFI_SSID;
const char *pass = WIFI_PASSWORD;

const char *mqtt_topic = "sensors";

WiFiClient espClient;
PubSubClient client(espClient);

// Automation Pump Config
float currentTherehold;
bool pumpState = false;

void runTuoiCayTuDong(float currentSoilMoisturePercent) {
    if (currentSoilMoisturePercent < currentTherehold) {
        if (pumpState == false) {
            digitalWrite(RELAY_PIN, HIGH);
            pumpState = true;
        }
    } else {
        if (pumpState == true) {
            digitalWrite(RELAY_PIN, LOW);
            pumpState = false;
        }
    }
}

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

void mqttCallBack(char* topic, byte* payload, unsigned int length) {
    String message;
    for (int i = 0; i < length; i++) {
        message += (char)payload[i];
    }

    if (String(topic) == "/threshold/set") {
        float newThrehold = message.toFloat();

        if (newThrehold > 0 && newnewThrehold <= 100) {
            if (newThrehold != currentTherehold) {
                currentTherehold = newThrehold;
                saveMoistureThrehold();
                Serial.println("Da cap nhat nguong moi thanh cong!");
            }
        }
    }
    
}

void setup()
{
    Serial.begin(115200);

    initSensor();
    currentTherehold = loadMoistureThrehold();

    setup_wifi();
    Serial.println(MQTT_HOST);
    client.setServer(MQTT_HOST, MQTT_PORT);
    client.setCallback(mqttCallback);
}

void loop()
{
    if (!client.connected())
    {
        reconnect();
    }

    client.loop();
    
    DHTData dhtData = readDHTData();
    float soilMoisturePercent = readSoilMoisturePercent();
    float ambient_light = readAmbientLightPercent();
    
    runTuoiCayTuDong(soilMoisturePercent);

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
