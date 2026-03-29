  /*****************************************************************************************************
  Light Camera Sequence 1
  Executes the TOP camera/Camera 1 sequence
*****************************************************************************************************/
void LightCameraSequence_1()
{
  D_MILLIS= millis();
  D_Trig_Count++;
  
  digitalWrite(TOP_LIGHT_1, LOW);// light on
  delayMicroseconds(LightOnDelay); //500 micro
  digitalWrite(TOP_CAMERA_1, LOW);
  delayMicroseconds(CameraTriggerDelay);
  digitalWrite(TOP_CAMERA_1, HIGH); //
  delayMicroseconds(LightOffDelay);
  digitalWrite(TOP_LIGHT_1, HIGH); //light off
  //delayMicroseconds(LightCamInterval);
   
  sprintf( buffer1, "%d", D_MILLIS );
  sprintf( buffer2, "%d", D_Trig_Count );
  String S1(buffer1);
  String S2(buffer2);
  S3 = "I1_" + S1 + "_" + S2;
  SerialUSB.println(S3);
}

/*****************************************************************************************************
  Light Camera Sequence 2
  Executes the SIDE camera/Camera 2 sequence
*****************************************************************************************************/
void LightCameraSequence_2()
{
  digitalWrite(TOP_LIGHT_2, LOW);
  delayMicroseconds(LightOnDelay);
  digitalWrite(TOP_CAMERA_2, LOW);
  delayMicroseconds(CameraTriggerDelay);
  digitalWrite(TOP_CAMERA_2, HIGH);
  delayMicroseconds(LightOffDelay);
  digitalWrite(TOP_LIGHT_2, HIGH);
  //delayMicroseconds(LightCamInterval);
  D_MILLIS= millis();
  sprintf( buffer1, "%d", D_MILLIS );
  sprintf( buffer2, "%d", D_Trig_Count );
  String S1(buffer1);
  String S2(buffer2);
  S3 = "I2_" + S1 + "_" + S2;
  SerialUSB.println(S3);
}
/*****************************************************************************************************
  Light Camera Sequence 2
  Executes the Back camera/Camera 2 sequence
*****************************************************************************************************/
void LightCameraSequence_3()
{  
  digitalWrite(TOP_LIGHT_3, LOW);
  delayMicroseconds(LightOnDelay);
  digitalWrite(TOP_CAMERA_3, LOW);
  delayMicroseconds(CameraTriggerDelay);
  digitalWrite(TOP_CAMERA_3, HIGH);
  delayMicroseconds(LightOffDelay);
  digitalWrite(TOP_LIGHT_3, HIGH);
  //delayMicroseconds(LightCamInterval);
  D_MILLIS= millis();
  sprintf( buffer1, "%d", D_MILLIS );
  sprintf( buffer2, "%d", D_Trig_Count );
  String S1(buffer1);
  String S2(buffer2);
  S3 = "I3_" + S1 + "_" + S2;
  SerialUSB.println(S3);
}
/*****************************************************************************************************
  Light Camera Sequence 4
  Executes the FRONT camera/Camera 3 sequence
*****************************************************************************************************/
void LightCameraSequence_4()
{
 digitalWrite(BOTTOM_SOLENOID_VALVE, HIGH);
  delayMicroseconds(LightOnDelay);
  digitalWrite(TOP_CAMERA_1, LOW);
  delayMicroseconds(CameraTriggerDelay);
  digitalWrite(TOP_CAMERA_1, HIGH);
  delayMicroseconds(LightOffDelay);  
  digitalWrite(BOTTOM_SOLENOID_VALVE, LOW);
  //delayMicroseconds(LightCamInterval);
  D_MILLIS= millis();
  sprintf( buffer1, "%d", D_MILLIS );
  sprintf( buffer2, "%d", D_Trig_Count );
  String S1(buffer1);
  String S2(buffer2);
  S3 = "I1_" + S1 + "_" + S2;
  SerialUSB.println(S3);
}


/*****************************************************************************************************
  Light Camera Sequence 5
  Executes the FRONT camera/Camera 4 sequence
*****************************************************************************************************/
void LightCameraSequence_5()
{
  digitalWrite(BOTTOM_LIGHT_4, LOW);
  delayMicroseconds(LightOnDelay);
  digitalWrite(BOTTOM_CAMERA_4, LOW);
  delayMicroseconds(CameraTriggerDelay);
  digitalWrite(BOTTOM_CAMERA_4, HIGH);
  delayMicroseconds(LightOffDelay);
  digitalWrite(BOTTOM_LIGHT_4, HIGH);
  //delayMicroseconds(LightCamInterval);
  D_MILLIS= millis();
  sprintf( buffer1, "%d", D_MILLIS );
  sprintf( buffer2, "%d", D_Trig_Count );
  String S1(buffer1);
  String S2(buffer2);
  S3 = "I4_" + S1 + "_" + S2;
  SerialUSB.println(S3);
}

/*****************************************************************************************************
  Light Camera Sequence 6
  Executes the FRONT camera/Camera 5 sequence
*****************************************************************************************************/

void LightCameraSequence_6()
{
  digitalWrite(BOTTOM_LIGHT_5, LOW);
  delayMicroseconds(LightOnDelay);
  digitalWrite(BOTTOM_CAMERA_5, LOW);
  delayMicroseconds(CameraTriggerDelay);
  digitalWrite(BOTTOM_CAMERA_5, HIGH);
  delayMicroseconds(LightOffDelay);
  digitalWrite(BOTTOM_LIGHT_5, HIGH);
  //delayMicroseconds(LightCamInterval);
  D_MILLIS= millis();
  sprintf( buffer1, "%d", D_MILLIS );
  sprintf( buffer2, "%d", D_Trig_Count );
  String S1(buffer1);
  String S2(buffer2);
  S3 = "I5_" + S1 + "_" + S2;
  SerialUSB.println(S3);
}

/*****************************************************************************************************
  Light Camera Sequence 7
  Executes the FRONT camera/Camera 6 sequence
*****************************************************************************************************/

void LightCameraSequence_7()
{
  digitalWrite(BOTTOM_LIGHT_6, LOW);
  delayMicroseconds(LightOnDelay);
  digitalWrite(BOTTOM_CAMERA_6, LOW);
  delayMicroseconds(CameraTriggerDelay);
  digitalWrite(BOTTOM_CAMERA_6, HIGH);
  delayMicroseconds(LightOffDelay);
  digitalWrite(BOTTOM_LIGHT_6, HIGH);
  //delayMicroseconds(LightCamInterval);
  D_MILLIS= millis();
  sprintf( buffer1, "%d", D_MILLIS );
  sprintf( buffer2, "%d", D_Trig_Count );
  String S1(buffer1);
  String S2(buffer2);
  S3 = "I6_" + S1 + "_" + S2;
  SerialUSB.println(S3);
}

/*****************************************************************************************************
  Light Camera Sequence Top Rack During Inspection
  Executes sequence of all the avilable cameras in the machine (Top Rack :-TOP T/B-SIDE-FRONT-Top T/B)
*****************************************************************************************************/
void LightCameraSequence_Top()
{
  if(insync){
  insync=true;               //change it to false for enable reconnect
  Trig_Count++;
  LCtp_FLAG = LOW;
  if(LightCameraSequenceFlag_0){
  Timer1.attachInterrupt(Light_0_On).start(LIGHT_ONDELAY);
  }
  }
  else
  {
  StopReelerMotor1(TOP_MOTOR_SS);
  rMotor1=LOW;
  rMotor1=LOW;
  insync=true;
  }}

  /**********************Light Sequence 0*********************/
void Light_0_On()
{
  Timer1.stop();
  Timer1.detachInterrupt();
  MILLIS = millis();
  digitalWrite(TOP_LIGHT_1, LOW);
  Timer1.attachInterrupt(Cam_0_On).start(CAMERA_ONDELAY);
}
void Cam_0_On()
{
  Timer1.stop();
  Timer1.detachInterrupt();
  digitalWrite(TOP_CAMERA_1, LOW);
  Timer1.attachInterrupt(Cam_0_Off).start(CAMERA_OFFDELAY);
}
void Cam_0_Off()
{
  Timer1.stop();
  Timer1.detachInterrupt();
  digitalWrite(TOP_CAMERA_1, HIGH);
  Timer1.attachInterrupt(Light_0_Off).start(LIGHT_OFFDELAY);
}
void Light_0_Off()
{
  Timer1.stop();
  Timer1.detachInterrupt();
  digitalWrite(TOP_LIGHT_1, HIGH); 
  sprintf( buffer1, "%d", MILLIS );
  sprintf( buffer2, "%d", Trig_Count );
  String S1(buffer1);
  String S2(buffer2);
  S3 = "I1_" + S1 + "_" + S2;
  TSFlag && SerialUSB.println(S3);                //TimeStamp
  if (LightCameraSequenceFlag_1){
  Timer1.attachInterrupt(Light_1_On).start(LIGHT_ONDELAY);
  }
}

 /**********************Light Sequence 1*********************/
void Light_1_On()
{
  Timer1.stop();
  Timer1.detachInterrupt();
  MILLIS = millis();
  digitalWrite(TOP_LIGHT_2, LOW);
  Timer1.attachInterrupt(Cam_1_On).start(CAMERA_ONDELAY);
}
void Cam_1_On()
{
  Timer1.stop();
  Timer1.detachInterrupt();
  digitalWrite(TOP_CAMERA_2, LOW);
  Timer1.attachInterrupt(Cam_1_Off).start(CAMERA_OFFDELAY);
}
void Cam_1_Off()
{
  Timer1.stop();
  Timer1.detachInterrupt();
  digitalWrite(TOP_CAMERA_2, HIGH);
  Timer1.attachInterrupt(Light_1_Off).start(LIGHT_OFFDELAY);
}
void Light_1_Off()
{
  Timer1.stop();
  Timer1.detachInterrupt();
  digitalWrite(TOP_LIGHT_2, HIGH);
  sprintf( buffer1, "%d", MILLIS );
  sprintf( buffer2, "%d", Trig_Count );
  String S1(buffer1);
  String S2(buffer2);
  S3 = "I2_" + S1 + "_" + S2;
  TSFlag && SerialUSB.println(S3);                        //TimeStamp
 if (LightCameraSequenceFlag_2){
  Timer1.attachInterrupt(Light_2_On).start(LIGHT_ONDELAY);
  }
}

/**********************Light Sequence 2*********************/

void Light_2_On()
{
  Timer1.stop();
  Timer1.detachInterrupt();
  MILLIS = millis();
  digitalWrite(TOP_LIGHT_3, LOW);
  Timer1.attachInterrupt(Cam_2_On).start(CAMERA_ONDELAY);
}
void Cam_2_On()
{
  Timer1.stop();
  Timer1.detachInterrupt();
  digitalWrite(TOP_CAMERA_3, LOW);
  Timer1.attachInterrupt(Cam_2_Off).start(CAMERA_OFFDELAY);
}
void Cam_2_Off()
{
  Timer1.stop();
  Timer1.detachInterrupt();
  digitalWrite(TOP_CAMERA_3, HIGH);
  Timer1.attachInterrupt(Light_2_Off).start(LIGHT_OFFDELAY);
}
void Light_2_Off()
{
  Timer1.stop();
  Timer1.detachInterrupt();
  digitalWrite(TOP_LIGHT_3, HIGH);
  sprintf( buffer1, "%d", MILLIS );
  sprintf( buffer2, "%d", Trig_Count );
  String S1(buffer1);
  String S2(buffer2);
  S3 = "I3_" + S1 + "_" + S2;
  TSFlag && SerialUSB.println(S3);                            //TimeStamp
  if (LightCameraSequenceFlag_3){
  Timer1.attachInterrupt(Light_3_On).start(TOP_LIGHT_ONDELAY);
  }
}
/**********************Light Sequence 3*********************/
void Light_3_On()
{
  Timer1.stop();
  Timer1.detachInterrupt();
  MILLIS = millis();
  digitalWrite(BOTTOM_SOLENOID_VALVE, HIGH);
  Timer1.attachInterrupt(Cam_3_On).start(TOP_CAMERA_ONDELAY);
}
void Cam_3_On()
{
  Timer1.stop();
  Timer1.detachInterrupt();
  digitalWrite(TOP_CAMERA_1, LOW);
  Timer1.attachInterrupt(Cam_3_Off).start(TOP_CAMERA_OFFDELAY);
}
void Cam_3_Off()
{
  Timer1.stop();
  Timer1.detachInterrupt();
  digitalWrite(TOP_CAMERA_1, HIGH);
  Timer1.attachInterrupt(Light_3_Off).start(TOP_LIGHT_OFFDELAY);
}
void Light_3_Off()
{
  Timer1.stop();
  Timer1.detachInterrupt();
  digitalWrite(BOTTOM_SOLENOID_VALVE, LOW);
  sprintf( buffer1, "%d", MILLIS );
  sprintf( buffer2, "%d", Trig_Count );
  String S1(buffer1);
  String S2(buffer2);
  S3 = "I1_" + S1 + "_" + S2;
  TSFlag && SerialUSB.println(S3);                                        //TimeStamp                                         
}

/*****************************************************************************************************
  Light Camera Sequence Bottom Rack
  Executes sequence of all the avilable cameras in the machine (Bottom Rack :-TOP-SIDE-FRONT)
*****************************************************************************************************/
void LightCameraSequence_Btm()
{
  LCbm_FLAG = LOW;
   if(LightCameraSequenceFlag_4){
  Timer2.attachInterrupt(Light_4_On).start(LIGHT_ONDELAY);
   }
}
/**********************Light Sequence 4************************/
void Light_4_On()
{
  Timer2.stop();
  Timer2.detachInterrupt();
  MILLIS = millis();
  digitalWrite(BOTTOM_LIGHT_4, LOW);
  Timer2.attachInterrupt(Cam_4_On).start(CAMERA_ONDELAY);
}

void Cam_4_On()
{
  Timer2.stop();
  Timer2.detachInterrupt();
  digitalWrite(BOTTOM_CAMERA_4, LOW);
  Timer2.attachInterrupt(Cam_4_Off).start(CAMERA_OFFDELAY);
}
void Cam_4_Off()
{
  Timer2.stop();
  Timer2.detachInterrupt();
  digitalWrite(BOTTOM_CAMERA_4, HIGH);
  Timer2.attachInterrupt(Light_4_Off).start(LIGHT_OFFDELAY);
}
void Light_4_Off()
{
  Timer2.stop();
  Timer2.detachInterrupt();
  digitalWrite(BOTTOM_LIGHT_4, HIGH);
  sprintf( buffer1, "%d", MILLIS );
  sprintf( buffer2, "%d", Trig_Count );
  String S1(buffer1);
  String S2(buffer2);
  S3 = "I4_" + S1 + "_" + S2;
  TSFlag && SerialUSB.println(S3);
  if(LightCameraSequenceFlag_5){
   Timer2.attachInterrupt(Light_5_On).start(LIGHT_ONDELAY);
}
}
/**********************Light Sequence 5************************/

void Light_5_On()
{
  Timer2.stop();
  Timer2.detachInterrupt();
  MILLIS = millis();
  digitalWrite(BOTTOM_LIGHT_5, LOW);
  Timer2.attachInterrupt(Cam_5_On).start(CAMERA_ONDELAY);
}
void Cam_5_On()
{
  Timer2.stop();
  Timer2.detachInterrupt();
  digitalWrite(BOTTOM_CAMERA_5, LOW);
  Timer2.attachInterrupt(Cam_5_Off).start(CAMERA_OFFDELAY);
}
void Cam_5_Off()
{
  Timer2.stop();
  Timer2.detachInterrupt();
  digitalWrite(BOTTOM_CAMERA_5, HIGH);
  Timer2.attachInterrupt(Light_5_Off).start(LIGHT_OFFDELAY);
}
void Light_5_Off()
{
  Timer2.stop();
  Timer2.detachInterrupt();
  digitalWrite(BOTTOM_LIGHT_5, HIGH);
  sprintf( buffer1, "%d", MILLIS );
  sprintf( buffer2, "%d", Trig_Count );
  String S1(buffer1);
  String S2(buffer2);
  S3 = "I5_" + S1 + "_" + S2;
  TSFlag && SerialUSB.println(S3);
  if (LightCameraSequenceFlag_6){
  Timer2.attachInterrupt(Light_6_On).start(LIGHT_ONDELAY);
  }
}

/**********************Light Sequence 6************************/
void Light_6_On()
{
  Timer2.stop();
  Timer2.detachInterrupt();
  MILLIS = millis();
  digitalWrite(BOTTOM_LIGHT_6, LOW);
  Timer2.attachInterrupt(Cam_6_On).start(CAMERA_ONDELAY);
}

void Cam_6_On()
{
  Timer2.stop();
  Timer2.detachInterrupt();
  digitalWrite(BOTTOM_CAMERA_6, LOW);
  Timer2.attachInterrupt(Cam_6_Off).start(CAMERA_OFFDELAY);
}
void Cam_6_Off()
{
  Timer2.stop();
  Timer2.detachInterrupt();
  digitalWrite(BOTTOM_CAMERA_6, HIGH);
  Timer2.attachInterrupt(Light_6_Off).start(LIGHT_OFFDELAY);
}

void Light_6_Off()
{
  Timer2.stop();
  Timer2.detachInterrupt();
  digitalWrite(BOTTOM_LIGHT_6, HIGH);
  sprintf( buffer1, "%d", MILLIS );
  sprintf( buffer2, "%d", Trig_Count );
  String S1(buffer1);
  String S2(buffer2);
  S3 = "I6_" + S1 + "_" + S2;
  TSFlag && SerialUSB.println(S3);                              //TimeStamp
}

/*******************************Get Standard Light camera delay*******************************/
void Lightondelay() 
{
  while (Lightondelayflag == HIGH)
  {
    if (SerialUSB.available()) {
      LIGHT_ONDELAY   = SerialUSB.parseInt();
      Lightondelayflag = LOW;
    }
  }
}
void Lightoffdelay() 
{
  while (Lightoffdelayflag == HIGH)
  {
    if (SerialUSB.available()) {
     LIGHT_OFFDELAY   = SerialUSB.parseInt();
     Lightoffdelayflag = LOW;
    }
  }
}
void Cameraondelay() 
{
  while (Cameraondelayflag == HIGH)
  {
    if (SerialUSB.available()) {
      CAMERA_ONDELAY     = SerialUSB.parseInt();
      Cameraondelayflag = LOW;
    }
  }
}
void Cameraoffdelay() 
{
  while (Cameraoffdelayflag == HIGH)
  {
    if (SerialUSB.available()) {
      CAMERA_OFFDELAY    = SerialUSB.parseInt();
      Cameraoffdelayflag = LOW;
    }
  }
}
/***************************Get Top Light camera delay*************************/
void TopLightondelay() 
{
  while (Lightondelayflag == HIGH)
  {
    if (SerialUSB.available()) {
      TOP_LIGHT_ONDELAY = SerialUSB.parseInt();
      Lightondelayflag = LOW;
    }
  }
}
void TopLightoffdelay() 
{
  while (Lightoffdelayflag == HIGH)
  {
    if (SerialUSB.available()) {
     TOP_LIGHT_OFFDELAY = SerialUSB.parseInt();
     Lightoffdelayflag = LOW;
    }
  }
}
void TopCameraondelay() 
{
  while (Cameraondelayflag == HIGH)
  {
    if (SerialUSB.available()) {
      TOP_CAMERA_ONDELAY = SerialUSB.parseInt();
      Cameraondelayflag = LOW;
    }
  }
}
void TopCameraoffdelay() 
{
  while (Cameraoffdelayflag == HIGH)
  {
    if (SerialUSB.available()) {
      TOP_CAMERA_OFFDELAY = SerialUSB.parseInt();
      Cameraoffdelayflag = LOW;
    }
  }
}
