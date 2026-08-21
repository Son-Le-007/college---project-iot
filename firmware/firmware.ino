#include <Arduino.h>
#include <ArduinoJson.h>
#include <WiFi.h>
#include <WiFiClient.h>
#include <PubSubClient.h>
#include "secrets.h"
#include "config.h"
#include "sensor_manager.h"
#include "storage_manager.h"
#include "wifi_manager_Config.h"

#define LDRPIN 1

const char *ssid = WIFI_SSID;
const char *pass = WIFI_PASSWORD;

const char *mqtt_topic = "sensors";

WiFiClient espClient;
PubSubClient client(espClient);

// Automation Pump Config
float currentTherehold;
bool pumpState = false;

unsigned long lastMqttReconnectAttempt = 0;
unsigned long lastSensorPublish = 0;

void runTuoiCayTuDong(float currentSoilMoisturePercent) {
    Serial.println(currentSoilMoisturePercent);
    Serial.println(currentTherehold);
    if (currentSoilMoisturePercent < currentTherehold) {
        if (pumpState == false) {
            Serial.println("RElay on");
            digitalWrite(RELAY_PIN, LOW);
            pumpState = true;
        }
    } else {
        if (pumpState == true) {
            digitalWrite(RELAY_PIN, HIGH);
            pumpState = false;
        }
    }
}

void setup_wifi_debug()
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

bool reconnect()
{
        Serial.print("Connecting to MQTT...");

        if (client.connect("esp32-s3-cam"))
        {
            Serial.println("MQTT connected");
            client.subscribe("/threshold/set"); 
            client.subscribe("garden/control/buzzer"); 
            return true;
        }
        else
        {
            Serial.print(" failed, rc=");
            Serial.println(client.state());
            return false;
        }
}

void mqttCallBack(char* topic, byte* payload, unsigned int length) {
    String message;
    for (int i = 0; i < length; i++) {
        message += (char)payload[i];
    }

    if (String(topic) == "/threshold/set") {
        float newThrehold = message.toFloat();

        if (newThrehold > 0 && newThrehold <= 100) {
            if (newThrehold != currentTherehold) {
                currentTherehold = newThrehold;
                saveMoistureThrehold(newThrehold);
                Serial.println("Da cap nhat nguong moi thanh cong!");
            }
        }
    }
    if (String(topic) == "garden/control/buzzer") {
        StaticJsonDocument<200> doc;
        DeserializationError error = deserializeJson(doc, message);
        
        if (!error) {
            String status = doc["status"];
            if (status == "ON") {
                digitalWrite(BUZZER_PIN, HIGH); // Cấp điện cho còi kêu
                Serial.println("🔔 WEB RA LỆNH: BẬT CÒI!");
            } else if (status == "OFF") {
                digitalWrite(BUZZER_PIN, LOW);  // Ngắt điện còi
                Serial.println("🔕 WEB RA LỆNH: TẮT CÒI!");
            }
        }
    }
}


void setup()
{
    Serial.begin(115200);

    initSensor();
    currentTherehold = loadMoistureThrehold();
    pinMode(RELAY_PIN, OUTPUT);
    digitalWrite(RELAY_PIN, HIGH); 

    pinMode(BUZZER_PIN, OUTPUT);
    digitalWrite(BUZZER_PIN, LOW); 
    pinMode(PIRPIN, INPUT);

    setup_wifi();

    // Serial.println(MQTT_HOST);
    client.setServer(MQTT_HOST, MQTT_PORT);
    client.setCallback(mqttCallBack);
}

void loop()
{
    wifi_loop();
    if (WiFi.status() != WL_CONNECTED) {
        return;
    }

    unsigned long now = millis();
    if (!client.connected())
    {
        if (now - lastMqttReconnectAttempt > 5000) {
            lastMqttReconnectAttempt = now;
            reconnect();
        }
    } else {
        client.loop();
    }

    if (now - lastSensorPublish >= 5000) {
        lastSensorPublish = now;

        DHTData dhtData = readDHTData();
        float soilMoisturePercent = readSoilMoisturePercent();
        float ambient_light = readAmbientLightLux();
        bool isMotion = (digitalRead(PIRPIN) == HIGH) ? 1 : 0;
        
        runTuoiCayTuDong(soilMoisturePercent);

        if (!dhtData.isValid)
        {
            Serial.println("DHT read failed");
            //delay(2000);
            return;
        }

        String payload = "{";
        payload += "\"temperature\":" + String(dhtData.temperature, 1) + ",";
        payload += "\"humidity\":" + String(dhtData.humidity, 1) + ",";
        payload += "\"soil_moisture\":" + String(soilMoisturePercent, 1) +",";
        payload += "\"ambient_light\":" + String(ambient_light, 1) +",";
        payload += "\"isMotion\":" + String(isMotion);
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

    }
}
