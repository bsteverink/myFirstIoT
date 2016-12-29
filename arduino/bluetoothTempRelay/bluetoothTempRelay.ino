#include <SoftwareSerial.h>
#include <dht.h>

#define RxD 10    //receive data on digital 0
#define TxD 11 //transmit on digital 1
#define DHT11_PIN 5 //Set DHT temp/hum sensor data pin to input 5 on arduino

SoftwareSerial blueToothSerial(RxD, TxD);

unsigned long time;
unsigned long last_check = 0;
dht DHT;

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  setupBlueToothConnection();
}

void setupBlueToothConnection(){
  blueToothSerial.begin(9600);
  blueToothSerial.print("AT+NAMEARDUINO");
  delay(1000); // This delay is required.
  blueToothSerial.write("Welcome to the Arduino\r\n");
  blueToothSerial.flush();
}

void loop() {
  checkTemp();
  if (blueToothSerial.available())
    Serial.write(blueToothSerial.read());

  if (Serial.available())
    blueToothSerial.write(Serial.read());
}

void checkTemp(){
  time = millis();
  if (time - last_check > 2000) {
    last_check = millis();
    
    int chk = DHT.read11(DHT11_PIN);

    switch(chk) {
      case DHTLIB_OK:
        Serial.write("OK\r\n");
        break;
      case DHTLIB_ERROR_CHECKSUM:
        Serial.write("Checksum error\r\n");
        break;
    }

    blueToothSerial.print(DHT.humidity);
    blueToothSerial.print(",");
    blueToothSerial.print(DHT.temperature);
    blueToothSerial.print(",");
    blueToothSerial.println(time);      
  }


}

