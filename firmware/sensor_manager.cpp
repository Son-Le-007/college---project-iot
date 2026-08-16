#include <DHT.h>
#include "config.h"
#include "sensor_manager.h"

static DHT dht(DHTPIN, DHTTYPE);

void initSensor() {
  pinMode(SOLI_MOISTURE_PIN, INPUT);
  dht.begin();
}

DHTData readDHTData() {
  DHTData dhtData;
  dhtData.temperature = dht.readTemperature();
  dhtData.humidity = dht.readHumidity();
  
  if (isnan(dhtData.temperature) || isnan(dhtData.humidity)) {
    dhtData.isValid = false;
    Serial.println("[Sensor] Error: Failed to read from DHT sensor!");
  } else {
    dhtData.isValid = true;
  }
  return dhtData;
}

float readSoilMoisturePercent() {
  float soil_moisture_raw_data = analogRead(SOLI_MOISTURE_PIN);
  float soil_moisture_percent = map(soil_moisture_raw_data, 0, 1024, 0, 100); 
  return soil_moisture_percent;
}