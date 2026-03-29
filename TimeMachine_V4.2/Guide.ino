/*****************************************************************************************************
  Name  :  GuideOpen
  Desc  :  Opens the guide until it reaches the full open limit(sensed by Open Limit switch)
  Remark:  Need to implement the "Fail to Open case"
*****************************************************************************************************/
void GuideTopOpen(uint8_t SlaveSelect, uint8_t LimitSwitch)
{
  
  if (digitalRead(LimitSwitch) == LOW) {
    StepperRotateCW(SlaveSelect);
  }
  while (digitalRead(LimitSwitch) == LOW && digitalRead(ESTOP_BUTTON)==LOW)
  {
  }
  
  StopStepperCW(SlaveSelect);
  if (digitalRead(LimitSwitch) == HIGH){
    Time=millis();
  Guidetest && SerialUSB.println(Time);
  SerialUSB.println(TOP_GUIDE_OPEN_RESPONSE);
  }
}
/*****************************************************************************************************
  Name  :  GuideClose
  Desc  :  Closes the guide until it reaches the full close limit(sensed by Open Limit switch)
  Remark:  Need to implement the "Fail to Close case"
*****************************************************************************************************/
void GuideTopClose(uint8_t SlaveSelect, uint8_t LimitSwitch)
{
  if (digitalRead(LimitSwitch) == LOW) {
    StepperRotateCCW(SlaveSelect);
  }
  while (digitalRead(LimitSwitch) == LOW && digitalRead(ESTOP_BUTTON)==LOW)
  {}
  StopStepperCW(SlaveSelect);
   if (digitalRead(LimitSwitch) == HIGH){
    Time=millis();
    Guidetest && SerialUSB.println(Time);
  SerialUSB.println(TOP_GUIDE_CLOSE_RESPONSE);
  }

}


/*****************************************************************************************************
  Name  :  GuideOpen
  Desc  :  Opens the guide until it reaches the full open limit(sensed by Open Limit switch)
  Remark:  Need to implement the "Fail to Open case"
*****************************************************************************************************/
void GuideBtmOpen(uint8_t SlaveSelect, uint8_t LimitSwitch)
{
  if (digitalRead(LimitSwitch) == LOW) {
    StepperRotateCCW(SlaveSelect);
  }
  while (digitalRead(LimitSwitch) == LOW && digitalRead(ESTOP_BUTTON)==LOW)
  {
  }
  StopStepperCW(SlaveSelect);
  if (digitalRead(LimitSwitch) == HIGH){
    Time=millis();
  Guidetest && SerialUSB.println(Time);
  SerialUSB.println(BTM_GUIDE_OPEN_RESPONSE);
  }
  

}
/*****************************************************************************************************
  Name  :  GuideClose
  Desc  :  Closes the guide until it reaches the full close limit(sensed by Open Limit switch)
  Remark:  Need to implement the "Fail to Close case"
*****************************************************************************************************/
void GuideBtmClose(uint8_t SlaveSelect, uint8_t LimitSwitch)
{
  if (digitalRead(LimitSwitch) == LOW) {
    StepperRotateCW(SlaveSelect);
  }
  while (digitalRead(LimitSwitch) == LOW && digitalRead(ESTOP_BUTTON)==LOW)
  {}
  StopStepperCW(SlaveSelect);
  if (digitalRead(LimitSwitch) == HIGH){
    Time=millis();
  Guidetest && SerialUSB.println(Time);
  SerialUSB.println(BTM_GUIDE_CLOSE_RESPONSE);
  }
}
/*******************************************************************************************************
Guide 
********************************************************************************************************/


















/*****************************************************************************************************
  Name  :  GuideSteps
  Desc  :  Closes to the steps specified in MI JSON.
*****************************************************************************************************/
void GuideStepsTop(uint8_t SlaveSelect)
{
  
  while (gMotor == HIGH)
  {
    if (SerialUSB.available())
    {
      bool GRD_flag=true;
      Steps = SerialUSB.parseInt();
      StepstoRotateTop(SlaveSelect);
      while(GRD_flag )
      {
        if(receiveData(0x35,TOP_MOTOR_SS) & 0x80)
        {
        SerialUSB.println(GUIDE_REACHED);
        GRD_flag=false;
        gMotor = LOW;
        }
      }
      
    }
  }
  
}
/*****************************************************************************************************
  Name  :  GuideSteps
  Desc  :  Closes to the steps specified in MI JSON.
*****************************************************************************************************/
void GuideStepsBottom(uint8_t SlaveSelect)
{
  while (gMotor == HIGH)
  {
    if (SerialUSB.available())
    {
      bool GRD_flag=true;
      Steps = SerialUSB.parseInt();
      StepstoRotateBtm(SlaveSelect);
      while(GRD_flag )
      {
        if(receiveData(0x35,BOTTOM_MOTOR_SS) & 0x80)
        {
        SerialUSB.println(GUIDE_REACHED);
        GRD_flag=false;
        gMotor = LOW;
        }
    }
  }
}}
