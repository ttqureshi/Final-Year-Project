#include <WiFi.h>
#include <AsyncTCP.h>
#include <ESPAsyncWebServer.h>

// Network credentials Here
const char* ssid     = "Can't connect to this network ";
const char* password = "hehehehe";

// Variable to store the HTTP request
String header;

//variables to store the current LED states
String statePin12 = "off";
String statePin13 = "off";
String statePin14 = "off";
String statePin27 = "off";

//Output variable to GPIO pins
const int ledPin12 = 33;
const int ledPin13 = 26;
const int ledPin14 = 14;
const int ledPin27 = 27;

AsyncWebServer server(80);

void setup() {
  Serial.begin(115200);

  pinMode(ledPin13, OUTPUT);
  digitalWrite(ledPin13, HIGH);
  pinMode(ledPin12, OUTPUT);
  digitalWrite(ledPin12, HIGH);
  pinMode(ledPin14, OUTPUT);
  digitalWrite(ledPin14, HIGH);
  pinMode(ledPin27, OUTPUT);
  digitalWrite(ledPin27, HIGH);

  WiFi.begin(ssid, password);
  
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi...");
  }
  
  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());

  server.on("/", HTTP_GET, [](AsyncWebServerRequest *request){
    request->send(200, "text/html", getPage());
  });

  server.on("/12/on", HTTP_GET, [](AsyncWebServerRequest *request){
    statePin12 = "on";
    digitalWrite(ledPin12, LOW);
    request->send(200, "text/html", getPage());
  });

  server.on("/12/off", HTTP_GET, [](AsyncWebServerRequest *request){
    statePin12 = "off";
    digitalWrite(ledPin12, HIGH);
    request->send(200, "text/html", getPage());
  });

  server.on("/13/on", HTTP_GET, [](AsyncWebServerRequest *request){
    statePin13 = "on";
    digitalWrite(ledPin13, LOW);
    request->send(200, "text/html", getPage());
  });

  server.on("/13/off", HTTP_GET, [](AsyncWebServerRequest *request){
    statePin13 = "off";
    digitalWrite(ledPin13, HIGH);
    request->send(200, "text/html", getPage());
  });

  server.on("/14/on", HTTP_GET, [](AsyncWebServerRequest *request){
    statePin14 = "on";
    digitalWrite(ledPin14, LOW);
    request->send(200, "text/html", getPage());
  });

  server.on("/14/off", HTTP_GET, [](AsyncWebServerRequest *request){
    statePin14 = "off";
    digitalWrite(ledPin14, HIGH);
    request->send(200, "text/html", getPage());
  });

  server.on("/27/on", HTTP_GET, [](AsyncWebServerRequest *request){
    statePin27 = "on";
    digitalWrite(ledPin27, LOW);
    request->send(200, "text/html", getPage());
  });

  server.on("/27/off", HTTP_GET, [](AsyncWebServerRequest *request){
    statePin27 = "off";
    digitalWrite(ledPin27, HIGH);
    request->send(200, "text/html", getPage());
  });

  server.begin();
}

void loop() {
}

String getPage() {
  String page = "<!DOCTYPE html><html>";
  page += "<head><meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">";
  page += "<link rel=\"icon\" href=\"data:,\">";
  page += "<style>";
  page += "body { font-family: 'Arial', sans-serif; margin: 0; background: #f4f4f9; overflow: hidden; }";
  page += "h1 { text-align: center; color: #333; margin-top: 20px; margin-bottom: 10px; }";
  page += ".container { display: flex; flex-wrap: wrap; justify-content: space-around; align-items: center; height: calc(100vh - 70px); }"; // Reduced container height
  page += ".button { border: none; color: white; padding: 15px; font-size: 24px; text-align: center; cursor: pointer; transition: transform 0.3s, box-shadow 0.3s; width: 45%; height: 40%; border-radius: 10px; display: flex; justify-content: center; align-items: center; }";
  page += ".button:hover { transform: scale(1.05); box-shadow: 0 5px 15px rgba(0,0,0,0.3); }";
  page += ".off { background-color: #778beb; }";
  page += ".on { background-color: #f3a683; }";
  page += "footer { text-align: center; font-size: 12px; color: black; padding: 10px 0; position: absolute; bottom: 0; width: 100%; background: #f4f4f9; }";
  page += "</style></head>";
  page += "<body>";
  page += "<h1>Welcome to Your Assistant</h1>";
  page += "<div class=\"container\">";

  // Button for Pin 12
  page += "<a href=\"/12/" + String(statePin12 == "on" ? "off" : "on") + "\" class=\"button " + (statePin12 == "on" ? "on" : "off") + "\">Light " + (statePin12 == "on" ? "Off" : "On") + "</a>";
  // Button for Pin 13
  page += "<a href=\"/13/" + String(statePin13 == "on" ? "off" : "on") + "\" class=\"button " + (statePin13 == "on" ? "on" : "off") + "\">Fan " + (statePin13 == "on" ? "Off" : "On") + "</a>";
  // Button for Pin 14
  page += "<a href=\"/14/" + String(statePin14 == "on" ? "off" : "on") + "\" class=\"button " + (statePin14 == "on" ? "on" : "off") + "\">TV " + (statePin14 == "on" ? "Off" : "On") + "</a>";
  // Button for Pin 27
  page += "<a href=\"/27/" + String(statePin27 == "on" ? "off" : "on") + "\" class=\"button " + (statePin27 == "on" ? "on" : "off") + "\">AC " + (statePin27 == "on" ? "Off" : "On") + "</a>";

  page += "</div>";
  page += "<footer>Powered by ESP32 &ndash; Automating Your World</footer>";
  page += "</body></html>";

  return page;
}