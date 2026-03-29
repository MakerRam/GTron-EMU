/*****************************************************************************************************
  Name  :  HardwareButton Polling
  Desc  :  Polls the pushbutton press through out the process with debounce.
           Debounce specified at Global variables
*****************************************************************************************************/

void PushButtons()
{

  /*===============================================
                        RUN
    =============================================*/
  if (run_FLAG == HIGH)
  {
    i2cObj.i2caddr = 1;
    int run_VAL = i2cObj.digitalRead(3);
    //    SerialUSB.println(run_VAL);
    if (run_VAL != lastRun_FLAG)
    {
      pbLastMillis = millis();
    }
    if ((millis() - pbLastMillis) > pbDebounceDelay)
    {
      if (run_VAL != runState)
      {
        runState = run_VAL;
        if (runState == LOW)
        {
          SerialUSB.println(RUN_PRESS);
        }
      }
    }
    lastRun_FLAG = run_VAL;
  }

  /*===============================================
                        PAUSE
    =============================================*/
  if (pause_FLAG == HIGH)
  {
    int pause_VAL = digitalRead(PAUSE_BUTTON);
    if (pause_VAL != lastPause_FLAG)
    {
      pbLastMillis = millis();
    }
    if ((millis() - pbLastMillis) > pbDebounceDelay)
    {
      if (pause_VAL != pauseState)
      {
        pauseState = pause_VAL;
        if (pauseState == LOW)
        {
          SerialUSB.println(PAUSE_PRESS);
        }
      }
    }
    lastPause_FLAG = pause_VAL;
  }

  /*===============================================
                       STOP
    =============================================*/
  if (stop_FLAG == HIGH)
  {
    int stop_VAL = digitalRead(STOP_BUTTON);
    if (stop_VAL != lastStop_FLAG)
    {
      pbLastMillis = millis();
    }
    if ((millis() - pbLastMillis) > pbDebounceDelay)
    {
      if (stop_VAL != stopState)
      {
        stopState = stop_VAL;
        if (stopState == LOW)
        {
          SerialUSB.println(STOP_PRESS);
        }
      }
    }
    lastStop_FLAG = stop_VAL;
  }

  /*===============================================
                      BUZZER OFF
    =============================================*/
  if (buzzeroff_FLAG == HIGH)
  {
    i2cObj.i2caddr = 1;
    int buzzeroff_VAL = i2cObj.digitalRead(7);
    if (buzzeroff_VAL != lastBuzzeroff_FLAG)
    {
      pbLastMillis = millis();
    }
    if ((millis() - pbLastMillis) > pbDebounceDelay)
    {
      if (buzzeroff_VAL != buzzeroffState)
      {
        buzzeroffState = buzzeroff_VAL;
        if (buzzeroffState == LOW)
        {
          SerialUSB.println(BUZZEROFF_PRESS);
        }
      }
    }
    lastBuzzeroff_FLAG = buzzeroff_VAL;
  }


  /*===============================================
                  ESTOP INDICATION
    =============================================*/

  if (EstopFlag == HIGH)
  {
    int Estop_VAL = digitalRead(ESTOP_BUTTON);
    if (Estop_VAL != lastEStop_FLAG)
    {
      pbLastMillis = millis();
    }
    if ((millis() - pbLastMillis) > pbDebounceDelay)
    {
      if (Estop_VAL != EstopState)
      {
        EstopState = Estop_VAL;
        if (EstopState == LOW)
        {
          SerialUSB.println(EMERGENCY_STOP_NOTPRESSED);
         ietEstopreleased();
        }
        else
        {
          SerialUSB.println(EMERGENCY_STOP_PRESSED);
          ietEstoppressed();
         }
      }
    }
    lastEStop_FLAG = Estop_VAL;
  }

  /*===============================================
           TOP&BOTTOM RACK DOOR POKA YOKE
    =============================================*/
  if (doorlock_FLAG == HIGH)
  {
    i2cObj.i2caddr = 1;
    int doorlock_VAL = ((i2cObj.digitalRead(1)) && (i2cObj.digitalRead(2))) ;
    if (doorlock_VAL != lastdoorlock_FLAG)
    {
      pbLastMillis = millis();
    }
    if ((millis() - pbLastMillis) > pbDebounceDelay)
    {
      if (doorlock_VAL != doorlockState)
      {
        doorlockState = doorlock_VAL;
        if (doorlockState == LOW)
        {
          SerialUSB.println(DOORUNLOCK_PRESS);
        }
      }
    }
    lastdoorlock_FLAG = doorlock_VAL;
  }

/*===============================================
           Pressure switch check
    =============================================*/
  if (PressureSwitch_FLAG == HIGH)
  {
    i2cObj.i2caddr = 1;
    int Pressure_Val = (i2cObj.digitalRead(4)) ;
    
    if (Pressure_Val != lastPressure_Val)
    {
      pbLastMillis = millis();
    }
    if ((millis() - pbLastMillis) > pbDebounceDelay)
    {
      if (Pressure_Val != Pressure_State)
      {
        Pressure_State = Pressure_Val;
        if (Pressure_State == LOW)
        {
          SerialUSB.println(PRESSURESWITCH_OFF);
        }
        else {
          SerialUSB.println(PRESSURESWITCH_ON);
          }
      }
    }
    lastPressure_Val = Pressure_Val;
  }
}
