/**
* Communicates float data over serial without loss of precision
*/

int state = LOW;

void setup() {
  Serial.begin(1000000); // setup serial connection speed
}

void loop() {
  int vr = 0;
  int vd = 0;
  int angle = 0;
  //a = 0.174387;
  
  Serial.write(0x40);
  Serial.print(vr);
  Serial.write(0xA8);
  Serial.print(vd);
  Serial.write(0xB9);
  Serial.print(angle);
  Serial.write(0x0C);
  Serial.flush();
  delay(1000);
  
}


void serialFloatPrint(float f) {
  byte * b = (byte *) &f;
  Serial.print("f:");
  Serial.print(f);
  Serial.write(b[0]);
  Serial.write(b[1]);
  Serial.write(b[2]);
  Serial.write(b[3]);
  /* DEBUG */
  Serial.println();
  Serial.print(b[0],BIN);
  Serial.print(b[1], BIN);
  Serial.print(b[2], BIN);
  Serial.println(b[3], BIN);
  //*/
}
