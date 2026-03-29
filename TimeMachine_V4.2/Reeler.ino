/****************************************************************
  Function called when reeler diagnostics opcode sent
****************************************************************/
void RotateReelerMotor(uint8_t  SlaveSelect) //Use only in Diagnostics
{
  while (rMotor == HIGH)
  {
    ReelerSteps(SlaveSelect);
    rMotor = LOW;
  }
   SerialUSB.println(Reeler_int_done);
}

void ReelerMotorSpeedMultplier() //Use only in Diagnostics
{
  while (Relermotorflag == HIGH)
  {
    if (SerialUSB.available()) {
      Multiplicationfactor = SerialUSB.parseInt();
      Relermotorflag = LOW;
    }
  }
}

void ReelerMotorSpeed1() //Use only in Diagnostics
{
   Debugstate && Serial.println("TPRSP_exe");
  while (rSpeed1 == HIGH)
  {
    if (SerialUSB.available()) {
      float RPM  = SerialUSB.parseInt();  
   SetSpeed1 = (RPM * 51200) / 60;  // Pulse per second
    Debugstate && Serial.println(SetSpeed1);
      rSpeed1 = LOW;
    }
  }
}

void ReelerMotorSpeed2() //Use only in Diagnostics
{
  Debugstate && Serial.println("BMRSP_exe");
  while (rSpeed2 == HIGH)
  {
    if (SerialUSB.available()) {
      float RPM  = SerialUSB.parseInt();  
     SetSpeed2 = (RPM * 51200) / 60;  // Pulse per second
   Debugstate && Serial.println(SetSpeed2);
    rSpeed2 = LOW;
    }
  
  }
}

void ReelerTeethCount()
{
  Debugstate && Serial.println("R_T_fun_exe");
  reelerTeethCountFlag = HIGH;
  while (reelerTeethCountFlag == HIGH)
  {
    if (SerialUSB.available())
    {
      NoOfTeeth= SerialUSB.parseInt();
    Debugstate && Serial.println(NoOfTeeth );
      reelerTeethCountFlag = LOW;
    }
  }
}

void SkipTrigger()
{
  
  SkipTriggerCountFlag = HIGH;
  while (SkipTriggerCountFlag == HIGH)
  {
    if (SerialUSB.available())
    {
      Skiptriggervalue= SerialUSB.parseInt();
   
      SkipTriggerCountFlag = LOW;
    }
  }
}
