// Load Wi-Fi library
#include <WiFi.h>
#include <ESPAsyncWebServer.h>

// Network credentials Here
const char* ssid     = "Can't connect to this network ";
const char* password = "hehehehe";

// Set web server port number to 80
WiFiServer server(80);
// AsyncWebServer server(80);

// Variable to store the HTTP request
String header;

//variables to store the current LED states
String statePin12 = "off";
String statePin13 = "off";
String statePin14 = "off";
String statePin27 = "off";
//Output variable to GPIO pins
const int ledPin12 = 12;
const int ledPin13 = 13;
const int ledPin14 = 14;
const int ledPin27 = 27;

// Current time
unsigned long currentTime = millis();
// Previous time
unsigned long previousTime = 0;
// Define timeout time in milliseconds
const long timeoutTime = 2000;

void setup() {
  Serial.begin(115200);
  
  pinMode(ledPin13, OUTPUT);      // set the LED pin mode
  digitalWrite(ledPin13, 0);      // turn LED off by default
  pinMode(ledPin12, OUTPUT);      // set the LED pin mode
  digitalWrite(ledPin12, 0);      // turn LED off by default
  pinMode(ledPin14, OUTPUT);      // set the LED pin mode
  digitalWrite(ledPin14, 0);      // turn LED off by default
  pinMode(ledPin27, OUTPUT);      // set the LED pin mode
  digitalWrite(ledPin27, 0);      // turn LED off by default

  WiFi.softAP(ssid,password);
  
  // Print IP address and start web server
  Serial.println("");
  Serial.println("IP address: ");
  Serial.println(WiFi.softAPIP());
  server.begin();
}

void loop() {
  WiFiClient client = server.available();   // Listen for incoming clients

  if (client) {                             // If a new client connects,
    currentTime = millis();
    previousTime = currentTime;
    Serial.println("New Client.");          // print a message out in the serial port
    String currentLine = "";                // make a String to hold incoming data from the client

    while (client.connected() && currentTime - previousTime <= timeoutTime) {
      // loop while the client's connected
      currentTime = millis();
      if (client.available()) {             // if there's bytes to read from the client,
        char c = client.read();             // read a byte, then
        Serial.write(c);                    // print it out the serial monitor
        header += c;
        if (c == '\n') {                    // if the byte is a newline character
          // if the current line is blank, you got two newline characters in a row.
          // that's the end of the client HTTP request, so send a response:
          if (currentLine.length() == 0) {
            // HTTP headers always start with a response code (e.g. HTTP/1.1 200 OK)
            // and a content-type so the client knows what's coming, then a blank line:
            client.println("HTTP/1.1 200 OK");
            client.println("Content-type:text/html");
            client.println("Connection: close");
            client.println();

            // turns the GPIOs on and off
            if (header.indexOf("GET /12/on") >= 0) {
              statePin12 = "on";
              digitalWrite(ledPin12, HIGH);               // turns the LED on
            } else if (header.indexOf("GET /12/off") >= 0) {
              statePin12 = "off";
              digitalWrite(ledPin12, LOW);                //turns the LED off
            }

            if (header.indexOf("GET /13/on") >= 0) {
              statePin13 = "on";
              digitalWrite(ledPin13, HIGH);               // turns the LED on
            } else if (header.indexOf("GET /13/off") >= 0) {
              statePin13 = "off";
              digitalWrite(ledPin13, LOW);                //turns the LED off
            }
            
            if (header.indexOf("GET /14/on") >= 0) {
              statePin14 = "on";
              digitalWrite(ledPin14, HIGH);               // turns the LED on
            } else if (header.indexOf("GET /14/off") >= 0) {
              statePin14 = "off";
              digitalWrite(ledPin14, LOW);               // turns the LED off
            }
            
            if (header.indexOf("GET /27/on") >= 0) {
              statePin27 = "on";
              digitalWrite(ledPin27, HIGH);               // turns the LED on
            } else if (header.indexOf("GET /27/off") >= 0) {
              statePin27 = "off";
              digitalWrite(ledPin27, LOW);               // turns the LED off
            }

            // Display the HTML web page
            client.println("<!DOCTYPE html><html>");
            client.println("<head><meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">");
            client.println("<link rel=\"icon\" href=\"data:,\">");
            // CSS to style the on/off buttons
            client.println("<style>body { font-family: monospace; margin: 0; }");
            client.println(".container { display: grid; grid-template-columns: 1fr 1fr; grid-template-rows: 1fr 1fr; height: 100vh; }");
            client.println(".button { border: none; color: white; text-decoration: none; font-size: 32px; text-align: center; cursor: pointer; transition-duration: 0.4s; width: calc(100% - 20px); height: calc(100% - 20px); display: flex; justify-content: center; align-items: center; background-size: contain; background-repeat: no-repeat; background-position: center; }"); // Adjusted width and height to include spacing
            client.println(".button.off { background-color: rgb(40,38,51); }");
            client.println(".button2 { background-color: rgb(12,141,1); }</style></head>");

            // client.println("<body><h1>ESP32 Web Server</h1>");
            client.println("<body>");
            client.println("<div class=\"container\">");

            if (statePin12 == "on") {
              client.println("<a href=\"/12/off\" class=\"button button2\"><img src=\"light.png\"></a>");
            } else {
              client.println("<a href=\"/12/on\" class=\"button off\"><img src=\"light.png\"></a>");
            }
            if (statePin13 == "on") {
              client.println("<a href=\"/13/off\" class=\"button button2\"><img src=\"fan\"></a>");
            } else {
              client.println("<a href=\"/13/on\" class=\"button off\"><img src=\"fan\"></a>");
            }
            if (statePin14 == "on") {
              client.println("<a href=\"/14/off\" class=\"button button2\"><img src=\"tv\"></a>");
            } else {
              client.println("<a href=\"/14/on\" class=\"button off\"><img src=\"tv\"></a>");
            }
            if (statePin27 == "on") {
              client.println("<a href=\"/27/off\" class=\"button button2\"><img src=\"ac\"></a>");
            } else {
              client.println("<a href=\"/27/on\" class=\"button off\"><img src=\"ac\"></a>");
            }
            client.println("</div>");
            client.println("</body></html>");

            // The HTTP response ends with another blank line
            client.println();
            // Break out of the while loop
            break;
          } else { // if you got a newline, then clear currentLine
            currentLine = "";
          }
        } else if (c != '\r') {  // if you got anything else but a carriage return character,
          currentLine += c;      // add it to the end of the currentLine
        }
      }
    }
    // Clear the header variable
    header = "";
    // Close the connection
    client.stop();
    Serial.println("Client disconnected.");
    Serial.println("");
  }
}