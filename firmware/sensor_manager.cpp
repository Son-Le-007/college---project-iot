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

const int WET_SOIL_RAW = 1100;  // Represents 100% moisture
const int DRY_SOIL_RAW = 3200;  // Represents 0% moisture

float readSoilMoisturePercent() {
  // The higher moisture, the samller the DIEN TRO value (Analog value)
  float soil_moisture_raw_data = analogRead(SOLI_MOISTURE_PIN);
  float soil_moisture_percent = map(soil_moisture_raw_data, DRY_SOIL_RAW, WET_SOIL_RAW, 0, 100); 
  Serial.print("Raw data: ");
  // Serial.println(soil_moisture_raw_data);
  // Serial.println(soil_moisture_percent);
  return (float)constrain(soil_moisture_percent, 0, 100);
}


float readAmbientLightLux() {
  int raw_light = analogRead(LDRPIN);
  if (raw_light == 0 || raw_light == 4095) {
      return 0.0;
  }
  const float V_IN = 3.3;             // Điện áp cấp cho ESP32
  const float ADC_RES = 4095.0;       // Độ phân giải ADC 12-bit
  const float R_PULLDOWN = 10000.0;   // Trở kéo 10k Ohm trên module

  float voltage = (raw_light / ADC_RES) * V_IN;
  float ldr_resistance = R_PULLDOWN * voltage / (V_IN - voltage);
  const float GAMMA = 0.7;
  const float RL10 = 50.0; // Điện trở LDR ở 10 Lux (kOhm)
  
  float lux = pow(RL10 * 1000.0 * pow(10, GAMMA) / ldr_resistance, (1 / GAMMA));
  
  return lux;
}
