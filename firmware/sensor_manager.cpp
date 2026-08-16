#include <DHT.h>
#include "config.h"
#include "sensor_manager.h"

static DHT dht(DHTPIN, DHTTYPE);

void initSensor() {
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