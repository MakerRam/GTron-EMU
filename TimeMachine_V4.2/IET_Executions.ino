/*****************************************************************************************************
  Name  :  Select
  Type  :  IET (Inspection Event) - Events which functions during inspection process
  Desc  :  Changes the state of all Hardware buttons, Towerlamp, Stamping and Winding.
*****************************************************************************************************/
void ietSelect()
{   
  run_FLAG =                HIGH;
  pause_FLAG =              LOW;
  stop_FLAG =               LOW;
  buzzeroff_FLAG =          LOW;
  Trig_Count = 0;
  D_Trig_Count = 0;
  i2cLOW(3, 3); //TL_RED
  digitalWrite(TL_YELLOW, LOW);
  digitalWrite(TL_GREEN,  LOW);
  i2cHGH(3, 1); //RUN_LAMP
  i2cLOW(3, 0); //PAUSE_LAMP
  i2cLOW(3, 7); //STOP_LAMP
  i2cLOW(3, 6); //BUZZEROFF_LAMP
  i2cLOW(3, 2); //TL_Buzzer
  
  
  digitalWrite(STAMPING_RELAY,    LOW);
  //Stamping and winding should be working in this state
}

/*****************************************************************************************************
  Name  :  Run
  Type  :  IET (Inspection Event) - Events which functions during inspection process
  Desc  :  Changes the state of all Hardware buttons, Towerlamp, Stamping and Winding.
*****************************************************************************************************/
void ietRun()
{
 
  run_FLAG =                LOW;
  pause_FLAG =              HIGH;
  stop_FLAG =               HIGH;
  buzzeroff_FLAG =          LOW;


  i2cLOW(3, 3); //TL_RED
  digitalWrite(TL_YELLOW, LOW);
  digitalWrite(TL_GREEN,  HIGH);

  i2cLOW(3, 1); //RUN_LAMP
  i2cHGH(3, 0); //PAUSE_LAMP
  i2cHGH(3, 7); //STOP_LAMP
  i2cLOW(3, 6); //BUZZEROFF_LAMP
  i2cLOW(3, 2); //TL_Buzzer

  digitalWrite(STAMPING_RELAY,    LOW);
  digitalWrite(TOP_SOLENOID_VALVE ,               LOW);
  //  digitalWrite(WINDING,     LOW); //Stamping and winding should be working in this state
}

/*****************************************************************************************************
  Name  :  PASS
  Type  :  IET (Inspection Event) - Events which functions during inspection process
  Desc  :  Changes the state of all Hardware buttons, Towerlamp, Stamping and Winding.
*****************************************************************************************************/
void ietPass()
{
  run_FLAG =                LOW;
  pause_FLAG =              HIGH;
  stop_FLAG =               HIGH;
  buzzeroff_FLAG =          LOW;


  i2cLOW(3, 3); //TL_RED
  digitalWrite(TL_YELLOW, LOW);
  digitalWrite(TL_GREEN,  HIGH);

  i2cLOW(3, 1); //RUN_LAMP
  i2cHGH(3, 0); //PAUSE_LAMP
  i2cHGH(3, 7); //STOP_LAMP
  i2cLOW(3, 6); //BUZZEROFF_LAMP
  i2cLOW(3, 2); //TL_Buzzer

  digitalWrite(STAMPING_RELAY,    LOW);
  digitalWrite(TOP_SOLENOID_VALVE ,               LOW);
  //  digitalWrite(WINDING,     LOW); //Stamping and winding should be working in this state
}

/*****************************************************************************************************
  Name  :  PAUSE
  Type  :  IET (Inspection Event) - Events which functions during inspection process
  Desc  :  Changes the state of all Hardware buttons, Towerlamp, Stamping and Winding.
*****************************************************************************************************/
void ietPause()
{
  run_FLAG =                HIGH;
  pause_FLAG =              LOW;
  stop_FLAG =               HIGH;
  buzzeroff_FLAG =          LOW;


  i2cLOW(3, 3); //TL_RED
  digitalWrite(TL_YELLOW, HIGH);
  digitalWrite(TL_GREEN,  LOW);

  i2cHGH(3, 1); //RUN_LAMP
  i2cLOW(3, 0); //PAUSE_LAMP
  i2cHGH(3, 7); //STOP_LAMP
  i2cLOW(3, 6); //BUZZEROFF_LAMP
  i2cLOW(3, 2); //TL_Buzzer

  
  digitalWrite(STAMPING_RELAY,    HIGH);
  digitalWrite(TOP_SOLENOID_VALVE ,   HIGH);
  //  digitalWrite(WINDING,     HIGH); //Stamping and winding should be working in this state
}

/*****************************************************************************************************
  Name  :  FAIL
  Type  :  IET (Inspection Event) - Events which functions during inspection process
  Desc  :  Changes the state of all Hardware buttons, Towerlamp, Stamping and Winding.
*****************************************************************************************************/
void ietFail()
{
  run_FLAG =                LOW;
  pause_FLAG =              LOW;
  stop_FLAG =               LOW;
  buzzeroff_FLAG =          HIGH;


  i2cHGH(3, 3); //TL_RED
  digitalWrite(TL_YELLOW, LOW);
  digitalWrite(TL_GREEN,  LOW);

  i2cLOW(3, 1); //RUN_LAMP
  i2cLOW(3, 0); //PAUSE_LAMP
  i2cLOW(3, 7); //STOP_LAMP
  i2cHGH(3, 6); //BUZZEROFF_LAMP
  i2cHGH(3, 2); //TL_Buzzer

  digitalWrite(STAMPING_RELAY,    HIGH);
  digitalWrite(TOP_SOLENOID_VALVE ,               HIGH);
  //  digitalWrite(WINDING,     HIGH); //Stamping and winding should be working in this state
}
/*****************************************************************************************************
  Name  :  E-STOP PRESSED
  Type  :  IET (Inspection Event) - Events which functions during inspection process
  Desc  :  Changes the state of all Hardware buttons, Towerlamp, Stamping and Winding.
*****************************************************************************************************/
void ietEstoppressed()
{
  i2cLOW(3, 1); //RUN_LAMP
  i2cLOW(3, 0); //PAUSE_LAMP
  i2cLOW(3, 7); //STOP_LAMP
  i2cLOW(3, 6);    //BUZZEROFF_LAMP
  i2cHGH(3, 2); //TL_Buzzer
  i2cHGH(3, 3); //TL_RED
  gMotor = LOW;
  digitalWrite(STAMPING_RELAY,    HIGH);                  //Stamping and winding should be working in this state
  digitalWrite(TOP_SOLENOID_VALVE ,  HIGH);
 
}
/*****************************************************************************************************
  Name  :  E-STOP RELEASED
  Type  :  IET (Inspection Event) - Events which functions during inspection process
  Desc  :  Changes the state of all Hardware buttons, Towerlamp, Stamping and Winding.
*****************************************************************************************************/
void ietEstopreleased()
{

  i2cLOW(3, 3); //TL_RED
  digitalWrite(TL_YELLOW, HIGH);
  digitalWrite(TL_GREEN,  LOW);

  i2cHGH(3, 1); //RUN_LAMP
  i2cLOW(3, 0); //PAUSE_LAMP
  i2cHGH(3, 7); //STOP_LAMP
  i2cLOW(3, 6); //BUZZEROFF_LAMP
  i2cLOW(3, 2); //TL_Buzzer
  digitalWrite(STAMPING_RELAY,    LOW);                     //Stamping and winding should be working in this state
  digitalWrite(TOP_SOLENOID_VALVE ,   LOW);
   
}
/*****************************************************************************************************
  Name  :  BuzzerOff
  Type  :  IET (Inspection Event) - Events which functions during inspection process
  Desc  :  Changes the state of all Hardware buttons, Towerlamp, Stamping and Winding.
*****************************************************************************************************/
void ietBuzzeroffER()
{
  run_FLAG =                HIGH;
  stop_FLAG =               HIGH;
  i2cHGH(3, 1); //RUN_LAMP
  i2cLOW(3, 0); //PAUSE_LAMP
  i2cHGH(3, 7); //STOP_LAMP
  i2cLOW(3, 6); //BUZZEROFF_LAMP
  i2cLOW(3, 2); //TL_Buzzer
}

void ietBuzzeroffDR()
{
  run_FLAG =                LOW;
  stop_FLAG =               HIGH;
  i2cLOW(3, 1); //RUN_LAMP
  i2cLOW(3, 0); //PAUSE_LAMP
  i2cHGH(3, 7); //STOP_LAMP
  i2cHGH(3, 6); //BUZZEROFF_LAMP
  i2cLOW(3, 2); //TL_Buzzer
}

/*****************************************************************************************************
  Name  :  DOOR POKA YOKE
  Type  :  IET (Inspection Event) - Events which functions during inspection process
  Desc  :  Changes the state of all Hardware buttons, Towerlamp, Stamping and Winding.
*****************************************************************************************************/
void ietDoorLock()
{
  run_FLAG =                HIGH;
  pause_FLAG =              HIGH;
  stop_FLAG =               HIGH;
  buzzeroff_FLAG =          HIGH;


  i2cLOW(3, 3); //TL_RED
  digitalWrite(TL_YELLOW, LOW);
  digitalWrite(TL_GREEN,  LOW);

  i2cHGH(3, 1); //RUN_LAMP
  i2cHGH(3, 0); //PAUSE_LAMP
  i2cHGH(3, 7); //STOP_LAMP
  i2cHGH(3, 6); //BUZZEROFF_LAMP
  i2cLOW(3, 2); //TL_Buzzer
  digitalWrite(STAMPING_RELAY,    HIGH);
  digitalWrite(TOP_SOLENOID_VALVE ,               HIGH);
  //  digitalWrite(WINDING,     HIGH); //Stamping and winding should be working in this state
}

/*****************************************************************************************************
  Name  :  Disable Hardware buttons.
  Type  :  IET (Inspection Event) - Events which functions during inspection process
  Desc  :  Changes the state of all Hardware buttons.
*****************************************************************************************************/

void hwbdb()
{
  run_FLAG =                LOW;
  pause_FLAG =              LOW;
  stop_FLAG =               LOW;
  buzzeroff_FLAG =          LOW;
  doorlock_FLAG  =          LOW;

  i2cLOW(3, 1); //RUN_LAMP
  i2cLOW(3, 0); //PAUSE_LAMP
  i2cLOW(3, 7); //STOP_LAMP
  i2cLOW(3, 6); //BUZZEROFF_LAMP
}

/*****************************************************************************************************
  Name  :  Disable All
  Type  :  IET (Inspection Event) - Events which functions during inspection process
  Desc  :  Changes the state of all Hardware buttons, Towerlamp, Stamping and Winding.
*****************************************************************************************************/
void dhbls()
{
   Timer2.stop();
  Timer2.detachInterrupt();
  run_FLAG =                LOW;
  pause_FLAG =              LOW;
  stop_FLAG =               LOW;
  buzzeroff_FLAG =          LOW;
  doorlock_FLAG =           LOW;
  Trig_Count = 0;
  rMotor = LOW;
  rMotor1 = LOW;
  rMotor2 = LOW;

  ENABLE_R1_LCS = false;
  ENABLE_R2_LCS = false;

  i2cLOW(3, 3); //TL_RED
  digitalWrite(TL_YELLOW, LOW);
  digitalWrite(TL_GREEN,  LOW);


  i2cLOW(3, 1); //RUN_LAMP
  i2cLOW(3, 0); //PAUSE_LAMP
  i2cLOW(3, 7); //STOP_LAMP
  i2cLOW(3, 6); //BUZZEROFF_LAMP
  i2cLOW(3, 2); //TL_Buzzer

  digitalWrite(STAMPING_RELAY,    HIGH);
  StopReelerMotor1(TOP_MOTOR_SS);
  StopReelerMotor2(BOTTOM_MOTOR_SS);
  //  digitalWrite(WINDING,     HIGH);

  detachInterrupt(digitalPinToInterrupt(TOP_SENSOR_TRIGGER_INPUT));
  detachInterrupt(digitalPinToInterrupt(BOTTOM_SENSOR_TRIGGER_INPUT));
  //  detachInterrupt(digitalPinToInterrupt (EncoderIntPin));

  i2cLOW(2, 0); //TOP_SENSOR_POWER_1
  i2cLOW(2, 1); //TOP_SENSOR_POWER_2
  i2cLOW(2, 2); //TOP_SENSOR_POWER_3
  i2cLOW(2, 3); //TOP_SENSOR_POWER_4
  i2cLOW(2, 4); //BOTTOM_SENSOR_POWER_5
  i2cLOW(2, 5); //BOTTOM_SENSOR_POWER_6
  i2cLOW(2, 6); //BOTTOM_SENSOR_POWER_7
  i2cLOW(2, 7); //BOTTOM_SENSOR_POWER_8
  
   LightCameraSequenceFlag_0 = false;
   LightCameraSequenceFlag_1 = false;
   LightCameraSequenceFlag_2 = false;
   LightCameraSequenceFlag_3 = false;
   LightCameraSequenceFlag_4 = false;
   LightCameraSequenceFlag_5 = false;
   LightCameraSequenceFlag_6 = false;

   TSFlag =false;
   
  digitalWrite(TOP_SOLENOID_VALVE ,  HIGH);
  digitalWrite(BOTTOM_SOLENOID_VALVE, LOW);
  i2cLOW(2, 7);

  //  ClearInterrupt(TOP_ENCODER_SS);
}
