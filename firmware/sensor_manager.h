#ifndef SENSOR_MANAGER_H
#define SENSOR_MANAGER_H

struct DHTData{
    float temperature;
    float humidity;
    bool isValid;
};

void initSensor();
DHTData readDHTData();
float readSoilMoisturePercent();

float readAmbientLightPercent(); 

#endif
