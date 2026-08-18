#include "wifi_manager_Config.h"

#include <WiFi.h>
#include <WebServer.h>
#include <Preferences.h>

#include <DNSServer.h>

WebServer server(80);
Preferences preferences;
DNSServer dnsServer;

const byte DNS_PORT = 53;

const char* HTML_FORMAT = R"rawliteral(
  <!DOCTYPE html>
  <head>
  <meta charset="UTF-8">
  <title>Cấu hình Wi-Fi</title></head>
  <body>
    <h2>Cài đặt wifi cho thiết bị</h2>
    <form action="/save" method="POST">
        <label>Tên Wifi (SSID):</label>
        <input type="text" name="ssid" required><br><br>
        <label>Mật khẩu:</label>
        <input type="password" name="password"><br><br>
        <input type="submit" value="Lưu và kết nối">
    </form>
  </body>
  </html>
)rawliteral";

void handleSave() {
  if (server.hasArg("ssid")) {
    String q_ssid = server.arg("ssid");
    String q_pass = server.arg("password");

    preferences.begin("wifi-config", false);
    preferences.putString("ssid", q_ssid);
    preferences.putString("password", q_pass);
    preferences.end();
    
    server.send(200, "text/html", "<h3> Luu thanh cong! ESP dang khoi dong lai...</h3>");
    delay(2000);

    ESP.restart();
  }
}

void startAPMode() {
  WiFi.mode(WIFI_AP);
  WiFi.softAP("ESP32_Config_Network", "12345678");

  dnsServer.start(DNS_PORT, "*", WiFi.softAPIP());

  server.on("/", HTTP_GET, []() {
    server.send(200, "text/html", HTML_FORMAT);
  });

  server.onNotFound([]() {
    server.send(200, "text/html", HTML_FORMAT);
  });

  server.on("/save", HTTP_POST, handleSave);

  server.begin();
}

void setup_wifi() {
  preferences.begin("wifi-config", true);
  String saved_ssid = preferences.getString("ssid", "");
  String saved_pass = preferences.getString("password", "");
  preferences.end();

  if (saved_ssid != "") {
    WiFi.begin(saved_ssid.c_str(), saved_pass.c_str());
    int timeout = 0;
    while (WiFi.status() != WL_CONNECTED && timeout < 20) {// wait for 10 second
      delay(500);
      timeout++;
    }
  }

  if (WiFi.status() != WL_CONNECTED) {
    startAPMode();
  } else {
    Serial.println(WiFi.localIP());
    Serial.println("Wifi connected");
  }
}

void wifi_loop() {
  while (WiFi.getMode() == WIFI_AP) {
    dnsServer.processNextRequest();
    server.handleClient();
  }
}