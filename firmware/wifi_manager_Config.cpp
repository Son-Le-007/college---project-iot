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
  <html lang="vi">
  <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cấu hình Wi-Fi</title>
  </head>
  <body style="font-family: Arial; margin: 20px;">
    <center><h2 style="color: #007bff; margin: 0;">TVS</h2></center>
    

    <center style="margin-top: 50px;">
            <h3>Cài đặt wifi cho thiết bị</h3>
            <form action="/save" method="POST" style="display: inline-block; background: #f0f0f0; text-align: left; padding: 20px;">
                <label>Tên Wifi (SSID):</label><br>
                <input type="text" name="ssid" required ><br><br>

                <label>Mật khẩu:</label><br>
                <input type="password" name="password"><br><br>
                <center>
                    <input type="submit" value="Lưu và kết nối">
                </center>
            </form>
            <center>
                <p style="color: #666;">Thank you for purchasing our product!</p>
            </center>
    </center>
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

void handleCaptiveRedirect() {
  server.sendHeader("Location", String("http://") + WiFi.softAPIP().toString(), true);
  server.send(302, "text/plain", "");
}

void startAPMode() {
  WiFi.mode(WIFI_AP);
  WiFi.softAP("ESP32_Config_Network");

  dnsServer.start(DNS_PORT, "*", WiFi.softAPIP());

  server.on("/", HTTP_GET, []() {
    server.send(200, "text/html", HTML_FORMAT);
  });

  server.on("/generate_204", handleCaptiveRedirect);

  server.onNotFound([]() {
    server.send(200, "text/html", HTML_FORMAT);
  });

  server.on("/save", HTTP_POST, handleSave);

  server.begin();
  Serial.print("IP Address: ");
  Serial.println(WiFi.softAPIP());
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
  if (WiFi.getMode() == WIFI_AP) {
    dnsServer.processNextRequest();
    server.handleClient();
  }
}