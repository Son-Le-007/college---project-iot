#include "storage_manager.h"
#include <Arduino.h>
#include <Preferences.h>

const float DEFAULT_THREHOLD = 30.0;

static const char* PREF_NAMESPACE = "irrigation";
static const char* KEY_THREHOLD = "moisture_threshold";

void saveMoistureThrehold(float threhold) {
    Preferences preferences;
    preferences.begin(PREF_NAMESPACE, false);
    preferences.putFloat(KEY_THREHOLD, threhold);
    preferences.end();
}
float loadMoistureThrehold() {
    Preferences preferences;
    preferences.begin(PREF_NAMESPACE, true);

    float threhold = DEFAULT_THREHOLD;
    if (preferences.isKey(KEY_THREHOLD)) {
        threhold = preferences.getFloat(KEY_THREHOLD, DEFAULT_THREHOLD);
        Serial.print("[Storage] Loaded threshold from NVS: ");
        Serial.println(threhold);
    } else {
        Serial.println("[Storage] Failed to load threhold");
    }
    preferences.end();
    return threhold;
}
