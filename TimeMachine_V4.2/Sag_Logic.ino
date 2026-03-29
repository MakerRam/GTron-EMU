/*****************************************************************************************************
  Name  :  Sag Sensor Logic
  Desc  :  Based on the below logic of sag sensors, Reeler motor will be
           actuated during the inspection process
*****************************************************************************************************/
void SagLogic()
{
  if (EstopState == LOW)
  {
    
   if((rMotor1 == HIGH)){
      /*For NPN:- LOW = Terminal present; HIGH = Terminal not present*/
      if (digitalRead (TOP_LOWER_SAG_SENSOR) == LOW)
      {
        if (TpMtr == 1) {
          TpMtr = 0;
          //SerialUSB.println("yes");
          StartReelerMotor1(TOP_MOTOR_SS);
        }
      }
      if (digitalRead (TOP_UPPER_SAG_SENSOR) == LOW)
      {
        if (TpMtr == 0) {
          TpMtr = 1;
          // SerialUSB.println("no");
          StopReelerMotor1(TOP_MOTOR_SS);
        }
      }
    }}
  
    
    
    else
    {StopReelerMotor1(TOP_MOTOR_SS);
      
      }
    
   
  
  if (EstopState == LOW)
  {
    /*For NPN:- LOW = Terminal present; HIGH = Terminal not present*/
     if (rMotor2 == HIGH)  {
      if (digitalRead (BOTTOM_LOWER_SAG_SENSOR) == LOW)
      {
        if (BmMtr == 1) {
          BmMtr = 0;
          StartReelerMotor2(BOTTOM_MOTOR_SS);
        }
      }
      if (digitalRead(BOTTOM_UPPER_SAG_SENSOR) == LOW)
      {
        if (BmMtr == 0) {
          BmMtr = 1;
          StopReelerMotor2(BOTTOM_MOTOR_SS);
        }
      }
    }}
     else
    {StopReelerMotor2(BOTTOM_MOTOR_SS);
      
      }
   
  }
