void OpcodePolling()
{
  if (SerialUSB.available()) {
    SerialUSB.readBytes(Buffer, 5);
    /******************************************************************
      Timing Unit Diagnostica - Checks the connection helth between
      PC and Controller
    ******************************************************************/
    if (strcmp(Buffer, PING) == 0) {
     
      SerialUSB.println(PING_RESPONSE);
     //LightCameraSequence_Top();
    }
    /****************************************************************
      Syncronous Feedback response
    ***************************************************************/
    else if (strcmp(Buffer, MI_RESPONSE) == 0)

    {
     insync=true;
     
      }
      /****************************************************************
     Rejection logic response
    ***************************************************************/
    else if (strcmp(Buffer, Rejectionlogic_Enable) == 0) {
      i2cHGH(2, 7); //RejectionEnable
      Rejectionlogic_Flag = true;
    }


      
    /******************************************************************
      Emergency Stop status check - Checks whether the Estop is
      pressed initailly when software launches
      (Currently not implemented properly. Specified in the
      place of Machine power status check)
    ******************************************************************/
    else if (strcmp(Buffer, EMERGENCY_STOP_CHECK) == 0)
    {
      if (EstopState == LOW) {
        SerialUSB.println(MACHINE_POWER_ON);
      }
      else if (EstopState == HIGH) {
        SerialUSB.println(MACHINE_POWER_OFF);
      }
    }

    /******************************************************************
      Top Rack Limit Switch status check - Called initially before
      Motor Diagnostics starts
    ******************************************************************/
    else if (strcmp(Buffer, TOP_LIMIT_SWITCH_CHECK) == 0)
    {
      if (digitalRead(TOP_OPEN_LIMIT_SWITCH) == LOW) {
        SerialUSB.println(TOP_LIMIT_SWITCH_NOTPRESSED);
      }
      else if (digitalRead(TOP_OPEN_LIMIT_SWITCH) == HIGH) {
        SerialUSB.println(TOP_LIMIT_SWITCH_PRESSED);
      }
    }

    /******************************************************************
      Bottom Rack Limit Switch status check - Called initially before
      Motor Diagnostics starts
    ******************************************************************/
    else if (strcmp(Buffer, BTM_LIMIT_SWITCH_CHECK) == 0)
    {
      if (digitalRead(BOTTOM_OPEN_LIMIT_SWITCH) == LOW) {
        SerialUSB.println(BTM_LIMIT_SWITCH_NOTPRESSED);
      }
      else if (digitalRead(BOTTOM_OPEN_LIMIT_SWITCH) == HIGH) {
        SerialUSB.println(BTM_LIMIT_SWITCH_PRESSED);
      }
    }

    /******************************************************************
      Top Rack Door Lock status check - Called initially before
      Inspection starts
    ******************************************************************/
    else if (strcmp(Buffer, DOOR_LOCK_CHECK) == 0)
    {
      i2cObj.i2caddr = 1;
      if (i2cObj.digitalRead(1) == HIGH && i2cObj.digitalRead(2) == HIGH ) {
        SerialUSB.println(DOOR_LIMIT_SWITCH_PRESSED);
//        SerialUSB.println("pressed");
      }
      else if (i2cObj.digitalRead(1) == LOW || i2cObj.digitalRead(2) == LOW ) {
        SerialUSB.println(DOOR_LIMIT_SWITCH_NOTPRESSED);
//        SerialUSB.println("notpressed");
      }
    }

else if (strcmp(Buffer, PRESSURESWITCH_ENABLE) == 0)
    {
     PressureSwitch_FLAG =HIGH;
      }
else if (strcmp(Buffer, PRESSURESWITCH_DISABLE) == 0)
    {
     PressureSwitch_FLAG =LOW;
      } 
else if (strcmp(Buffer, PRESSURESWITCH_CHECK) == 0)
    {
      i2cObj.i2caddr = 1;
      if (i2cObj.digitalRead(4)==HIGH){
     SerialUSB.println(PRESSURESWITCH_ON);
      } else{
        SerialUSB.println(PRESSURESWITCH_OFF);
        }
      }


//    /******************************************************************
//      Bottom Rack Door Lock status check - Called initially before
//      Inspection starts
//    ******************************************************************/
//    else if (strcmp(Buffer, BTM_DOOR_LOCK_CHECK) == 0)
//    {
//      i2cObj.i2caddr = 1;
//      if (i2cObj.digitalRead(2) == HIGH) {
//        SerialUSB.println(DOOR_LIMIT_SWITCH_PRESSED);
//      }
//      else if (i2cObj.digitalRead(2) == LOW) {
//        SerialUSB.println(DOOR_LIMIT_SWITCH_NOTPRESSED);
//      }
//    }



    /******************************************************************
       Guide and Reeler motor functions - Called during Diagnostics
    ******************************************************************/
    if (strcmp(Buffer, TOP_GUIDE_OPEN) == 0) {
      GuideTopOpen(TOP_MOTOR_SS, TOP_OPEN_LIMIT_SWITCH);
    }
    if (strcmp(Buffer, TOP_GUIDE_CLOSE) == 0) {
      GuideTopClose(TOP_MOTOR_SS, TOP_CLOSE_LIMIT_SWITCH);
    }
    if (strcmp(Buffer, BTM_GUIDE_OPEN) == 0) {
      GuideBtmOpen(BOTTOM_MOTOR_SS, BOTTOM_OPEN_LIMIT_SWITCH);
    }
    if (strcmp(Buffer, BTM_GUIDE_CLOSE) == 0) {
      GuideBtmClose(BOTTOM_MOTOR_SS, BOTTOM_CLOSE_LIMIT_SWITCH);
    }
    if (strcmp(Buffer, TOP_ROTATE_REELER) == 0) {
      rMotor = HIGH;
      RotateReelerMotor(TOP_MOTOR_SS);
//ReelerSteps(TOP_MOTOR_SS);
    }
    if (strcmp(Buffer, BTM_ROTATE_REELER) == 0) {
      rMotor = HIGH;
      RotateReelerMotor(BOTTOM_MOTOR_SS);
    }
    if (strcmp(Buffer, STEPPER_INITIALIZATION) == 0) {
      StepperInitial(TOP_MOTOR_SS);
      StepperInitial(BOTTOM_MOTOR_SS);

    }
    if (strcmp(Buffer, REELER_INITIALIZATION) == 0) {
      ReelerInitial(TOP_MOTOR_SS);
      ReelerInitial(BOTTOM_MOTOR_SS);
    }
    if (strcmp(Buffer, TOP_GUIDE_TEST) == 0) {
      GuideTopOpen(TOP_MOTOR_SS, TOP_OPEN_LIMIT_SWITCH);
      
      GuideTopClose(TOP_MOTOR_SS, TOP_CLOSE_LIMIT_SWITCH);
      
    }
    if (strcmp(Buffer, BOTTOM_GUIDE_TEST) == 0) {
      GuideBtmOpen(BOTTOM_MOTOR_SS, BOTTOM_OPEN_LIMIT_SWITCH);
      
      GuideBtmClose(BOTTOM_MOTOR_SS, BOTTOM_CLOSE_LIMIT_SWITCH);
      
    }
    /******************************************************************
      Hardware button Enable & Disable functions - Called in multiple
      places. Refer MI JSON
     ******************************************************************/
    else if (strcmp(Buffer, ATTACH_RUN) == 0) {
      run_FLAG = HIGH;
    }
    else if (strcmp(Buffer, DETACH_RUN) == 0) {
      run_FLAG = LOW;
    }

    else if (strcmp(Buffer, ATTACH_PAUSE) == 0) {
      pause_FLAG = HIGH;
    }

    else if (strcmp(Buffer, DETACH_PAUSE) == 0) {
      pause_FLAG = LOW;
    }

    else if (strcmp(Buffer, ATTACH_STOP) == 0) {
      stop_FLAG = HIGH;
    }
    else if (strcmp(Buffer, DETACH_STOP) == 0) {
      stop_FLAG = LOW;
    }

    else if (strcmp(Buffer, ATTACH_BUZZEROFF) == 0) {
      buzzeroff_FLAG = HIGH;
    }
    else if (strcmp(Buffer, DETACH_BUZZEROFF) == 0) {
      buzzeroff_FLAG = LOW;
    }

    else if (strcmp(Buffer, ATTACH_DOORLOCK) == 0) {
      doorlock_FLAG = HIGH;
    }
    else if (strcmp(Buffer, RUN_LAMP_ON) == 0) {
      i2cHGH(3, 1); //RUN_LAMP
    }
    else if (strcmp(Buffer, PAUSE_LAMP_ON) == 0) {
      i2cHGH(3, 0); //PAUSE_LAMP
    }
    else if (strcmp(Buffer, STOP_LAMP_ON) == 0) {
      i2cHGH(3, 7); //STOP_LAMP
    }
    else if (strcmp(Buffer, BUZZER_LAMP_ON) == 0) {
      i2cHGH(3, 6); //BUZZEROFF_LAMP
    }
    else if (strcmp(Buffer, RUN_LAMP_OFF) == 0) {
      i2cLOW(3, 1); //RUN_LAMP
    }
    else if (strcmp(Buffer, PAUSE_LAMP_OFF) == 0) {
      i2cLOW(3, 0); //PAUSE_LAMP
    }
    else if (strcmp(Buffer, STOP_LAMP_OFF) == 0) {
      i2cLOW(3, 7); //STOP_LAMP
    }
    else if (strcmp(Buffer, BUZZER_LAMP_OFF) == 0) {
      i2cLOW(3, 6); //BUZZEROFF_LAMP
    }
 

    /******************************************************************
      Light Camera Sequences - Called during Diagnostics
    ******************************************************************/
    else if (strcmp(Buffer, LIGHT_CAMERA_SEQUENCE_1) == 0) {
      LightCameraSequence_1();
    }
    else if (strcmp(Buffer, LIGHT_CAMERA_SEQUENCE_2) == 0) {
      LightCameraSequence_2();
    }
    else if (strcmp(Buffer, LIGHT_CAMERA_SEQUENCE_3) == 0) {
      LightCameraSequence_3();
    }
    else if (strcmp(Buffer, LIGHT_CAMERA_SEQUENCE_4) == 0) {
      LightCameraSequence_4();
    }
    else if (strcmp(Buffer, LIGHT_CAMERA_SEQUENCE_5) == 0) {
      LightCameraSequence_5();
    }
    else if (strcmp(Buffer, LIGHT_CAMERA_SEQUENCE_6) == 0) {
      LightCameraSequence_6();
    }
    else if (strcmp(Buffer, LIGHT_CAMERA_SEQUENCE_7) == 0) {
      LightCameraSequence_7();
    }
    else if (strcmp(Buffer, LIGHT_CAMERA_SEQUENCE_TOP) == 0) {
      LightCameraSequence_Top();
    }
    else if (strcmp(Buffer, LIGHT_CAMERA_SEQUENCE_BTM) == 0) {
      LightCameraSequence_Btm();
    }
     /******************************************************************
         Enabling and Disableing Light camera
         sequence for inspection 
    ******************************************************************/
    else if (strcmp(Buffer, LIGHT_CAMERA_SEQUENCE_I0) == 0) {
      LightCameraSequenceFlag_0 =true;
    }
    else if (strcmp(Buffer, LIGHT_CAMERA_SEQUENCE_I1) == 0) {
      LightCameraSequenceFlag_1 =true;
    }
    else if (strcmp(Buffer, LIGHT_CAMERA_SEQUENCE_I2) == 0) {
      LightCameraSequenceFlag_2 =true;
    }
    else if (strcmp(Buffer, LIGHT_CAMERA_SEQUENCE_I3) == 0) {
      LightCameraSequenceFlag_3 =true;
    }
     else if (strcmp(Buffer, LIGHT_CAMERA_SEQUENCE_I4) == 0) {
      LightCameraSequenceFlag_4 =true;
    }
    else if (strcmp(Buffer, LIGHT_CAMERA_SEQUENCE_I5) == 0) {
      LightCameraSequenceFlag_5 =true;
    }
    else if (strcmp(Buffer, LIGHT_CAMERA_SEQUENCE_I6) == 0) {
      LightCameraSequenceFlag_6 =true;
    }
/******************************************************************
         Enabling and Disableing Timestamp for inspection 
    ******************************************************************/
    else if (strcmp(Buffer, TIMESTAMP_ENABLE) == 0) {
      TSFlag =true;
    }
   


    
    /******************************************************************
         Get Light camera sequence delay time for Standard 
         & Top Light Sequence for inspection 
    ******************************************************************
     else if (strcmp(Buffer, LIGHT_ON_DELAY_TIMING) == 0) {
      Lightondelayflag =HIGH;
      Lightondelay();
    }
    else if (strcmp(Buffer, CAMERA_ON_DELAY_TIMING) == 0) {
      Cameraondelayflag =HIGH;
      Cameraondelay();
    }
    else if (strcmp(Buffer, CAMERA_OFF_DELAY_TIMING) == 0) {
      Cameraoffdelayflag =HIGH;
      Cameraoffdelay();
    }
    else if (strcmp(Buffer, LIGHT_OFF_DELAY_TIMING) == 0) {
      Lightoffdelayflag =HIGH;
      Lightoffdelay();
    }
     else if (strcmp(Buffer, TOP_LIGHT_ON_DELAY_TIMING) == 0) {
      Lightondelayflag =HIGH;
       TopLightondelay();
    }
    else if (strcmp(Buffer, TOP_CAMERA_ON_DELAY_TIMING) == 0) {
      Cameraondelayflag =HIGH;
      TopCameraondelay();
    }
    else if (strcmp(Buffer, TOP_CAMERA_OFF_DELAY_TIMING) == 0) {
      Cameraoffdelayflag =HIGH;
      TopCameraoffdelay();
    }
    else if (strcmp(Buffer, TOP_LIGHT_OFF_DELAY_TIMING) == 0) {
      Lightoffdelayflag =HIGH;
      TopLightoffdelay();
    }*/




    
    /******************************************************************
         Enabling and Disableing Trigger sensors for Light camera
         sequence during inspection - Called during inspection
    ******************************************************************/
    //SENSOR - 1
    else if (strcmp(Buffer, ATTACH_SENSOR_TOP) == 0) {
      attachInterrupt(digitalPinToInterrupt(TOP_SENSOR_TRIGGER_INPUT), SetLCtp, RISING);
    }
    else if (strcmp(Buffer, DETACH_SENSOR_TOP) == 0) {
      detachInterrupt(digitalPinToInterrupt(TOP_SENSOR_TRIGGER_INPUT));
    }
    else if (strcmp(Buffer, POWERON_SENSOR_1) == 0) {
      //      SerialUSB.println("power on");
      i2cHGH(2, 3); //TOP_SENSOR_POWER_1
    }
    else if (strcmp(Buffer, POWEROFF_SENSOR_1) == 0) {
      i2cLOW(2, 3); //TOP_SENSOR_POWER_1
    }

    //SENSOR - 2
    //    else if (strcmp(Buffer, ATTACH_SENSOR_TOP) == 0) {
    //      attachInterrupt(digitalPinToInterrupt(TOP_SENSOR_TRIGGER_INPUT), SetLCtp, RISING);
    //    }
    //    else if (strcmp(Buffer, DETACH_SENSOR_TOP) == 0) {
    //      detachInterrupt(digitalPinToInterrupt(TOP_SENSOR_TRIGGER_INPUT));
    //    }
    else if (strcmp(Buffer, POWERON_SENSOR_2) == 0) {
      i2cHGH(2, 2); //TOP_SENSOR_POWER_2
    }
    else if (strcmp(Buffer, POWEROFF_SENSOR_2) == 0) {
      i2cLOW(2, 2); //TOP_SENSOR_POWER_2
    }


    //SENSOR - 3
    //    else if (strcmp(Buffer, ATTACH_SENSOR_TOP) == 0) {
    //      attachInterrupt(digitalPinToInterrupt(TOP_SENSOR_TRIGGER_INPUT), SetLCtp, RISING);
    //    }
    //    else if (strcmp(Buffer, DETACH_SENSOR_TOP) == 0) {
    //      detachInterrupt(digitalPinToInterrupt(TOP_SENSOR_TRIGGER_INPUT));
    //    }
    else if (strcmp(Buffer, POWERON_SENSOR_3) == 0) {
      i2cHGH(2, 1); //TOP_SENSOR_POWER_3
    }
    else if (strcmp(Buffer, POWEROFF_SENSOR_3) == 0) {
      i2cLOW(2, 1); //TOP_SENSOR_POWER_3
    }


    //SENSOR - 4
    //    else if (strcmp(Buffer, ATTACH_SENSOR_TOP) == 0) {
    //      attachInterrupt(digitalPinToInterrupt(TOP_SENSOR_TRIGGER_INPUT), SetLCtp, RISING);
    //    }
    //    else if (strcmp(Buffer, DETACH_SENSOR_TOP) == 0) {
    //      detachInterrupt(digitalPinToInterrupt(TOP_SENSOR_TRIGGER_INPUT));
    //    }
    else if (strcmp(Buffer, POWERON_SENSOR_4) == 0) {
      i2cHGH(2, 0); //TOP_SENSOR_POWER_4
    }
    else if (strcmp(Buffer, POWEROFF_SENSOR_4) == 0) {
      i2cLOW(2, 0); //TOP_SENSOR_POWER_4
    }


    //SENSOR - 5
    else if (strcmp(Buffer, ATTACH_SENSOR_BTM) == 0) {
      attachInterrupt(digitalPinToInterrupt(BOTTOM_SENSOR_TRIGGER_INPUT), SetLCbm, RISING);
    }
    else if (strcmp(Buffer, DETACH_SENSOR_BTM) == 0) {
      detachInterrupt(digitalPinToInterrupt(BOTTOM_SENSOR_TRIGGER_INPUT));
    }
    else if (strcmp(Buffer, POWERON_SENSOR_5) == 0) {
      i2cHGH(2, 7); //BOTTOM_SENSOR_POWER_5
    }
    else if (strcmp(Buffer, POWEROFF_SENSOR_5) == 0) {
      i2cLOW(2, 7); //BOTTOM_SENSOR_POWER_5
    }


    //SENSOR - 6
    //    else if (strcmp(Buffer, ATTACH_SENSOR_BTM) == 0) {
    //      attachInterrupt(digitalPinToInterrupt(BOTTOM_SENSOR_TRIGGER_INPUT), SetLCbm, RISING);
    //    }
    //    else if (strcmp(Buffer, DETACH_SENSOR_BTM) == 0) {
    //      detachInterrupt(digitalPinToInterrupt(BOTTOM_SENSOR_TRIGGER_INPUT));
    //    }
    else if (strcmp(Buffer, POWERON_SENSOR_6) == 0) {
      i2cHGH(2, 6); //BOTTOM_SENSOR_POWER_6
    }
    else if (strcmp(Buffer, POWEROFF_SENSOR_6) == 0) {
      i2cLOW(2, 6); //BOTTOM_SENSOR_POWER_6
    }



    //SENSOR - 7
    //    else if (strcmp(Buffer, ATTACH_SENSOR_BTM) == 0) {
    //      attachInterrupt(digitalPinToInterrupt(BOTTOM_SENSOR_TRIGGER_INPUT), SetLCbm, RISING);
    //    }
    //    else if (strcmp(Buffer, DETACH_SENSOR_BTM) == 0) {
    //      detachInterrupt(digitalPinToInterrupt(BOTTOM_SENSOR_TRIGGER_INPUT));
    //    }
    else if (strcmp(Buffer, POWERON_SENSOR_7) == 0) {
      i2cHGH(2, 5); //BOTTOM_SENSOR_POWER_7
    }
    else if (strcmp(Buffer, POWEROFF_SENSOR_7) == 0) {
      i2cLOW(2, 5); //BOTTOM_SENSOR_POWER_7
    }


    //SENSOR - 8
    //    else if (strcmp(Buffer, ATTACH_SENSOR_BTM) == 0) {
    //      attachInterrupt(digitalPinToInterrupt(BOTTOM_SENSOR_TRIGGER_INPUT), SetLCbm, RISING);
    //    }
    //    else if (strcmp(Buffer, DETACH_SENSOR_BTM) == 0) {
    //      detachInterrupt(digitalPinToInterrupt(BOTTOM_SENSOR_TRIGGER_INPUT));
    //    }
    else if (strcmp(Buffer, POWERON_SENSOR_8) == 0) {
      i2cHGH(2, 4); //BOTTOM_SENSOR_POWER_8
    }
    else if (strcmp(Buffer, POWEROFF_SENSOR_8) == 0) {
      i2cLOW(2, 4); //BOTTOM_SENSOR_POWER_8
    }
    else if (strcmp(Buffer, TOP_SENSOR_CHECK) == 0)
    {
      if (digitalRead(TOP_SENSOR_TRIGGER_INPUT) == LOW) {
        SerialUSB.println(TOP_SENSOR_ON);
      }
      if (digitalRead(TOP_SENSOR_TRIGGER_INPUT) == HIGH) {
        SerialUSB.println(TOP_SENSOR_OFF);
      }
    }
     else if (strcmp(Buffer, BOTTOM_SENSOR_CHECK) == 0)
    {
      if (digitalRead(BOTTOM_SENSOR_TRIGGER_INPUT) == LOW) {
        SerialUSB.println(BOTTOM_SENSOR_ON);
      }
      if (digitalRead(BOTTOM_SENSOR_TRIGGER_INPUT) == HIGH) {
        SerialUSB.println(BOTTOM_SENSOR_OFF);
      }
    }
    /******************************************************************
      Tower Lamp ON/OFF Sequence - Called during diagnostics.
      Works throughout JSON
    ******************************************************************/
    else if (strcmp(Buffer, TOWERLAMP_RED_ON) == 0) {
      i2cHGH(3, 3); //TL_RED
    }
    else if (strcmp(Buffer, TOWERLAMP_RED_OFF) == 0) {
      i2cLOW(3, 3); //TL_RED
    }

    else if (strcmp(Buffer, TOWERLAMP_YELLOW_ON) == 0) {
      digitalWrite(TL_YELLOW, HIGH);
    }
    else if (strcmp(Buffer, TOWERLAMP_YELLOW_OFF) == 0) {
      digitalWrite(TL_YELLOW, LOW);
    }

    else if (strcmp(Buffer, TOWERLAMP_GREEN_ON) == 0) {
      digitalWrite(TL_GREEN, HIGH);
    }
    else if (strcmp(Buffer, TOWERLAMP_GREEN_OFF) == 0) {
      digitalWrite(TL_GREEN, LOW);
    }

    else if (strcmp(Buffer, TOWERLAMP_BUZZER_ON) == 0) {
      i2cHGH(3, 2); //TL_Buzzer
    }
    else if (strcmp(Buffer, TOWERLAMP_BUZZER_OFF) == 0) {
      i2cLOW(3, 2); //TL_Buzzer
    }
     else if (strcmp(Buffer, TOP_SAG_SENSOR_CHECK) == 0)
    {
      if (digitalRead (TOP_LOWER_SAG_SENSOR) == LOW) {
        SerialUSB.println(TOP_L_SAG_SENSOR_PASS);
      }
      if (digitalRead (TOP_UPPER_SAG_SENSOR) == LOW) {
        SerialUSB.println(TOP_U_SAG_SENSOR_PASS);
      }
      if (digitalRead (TOP_LOWER_SAG_SENSOR) == HIGH) {
        SerialUSB.println(TOP_L_SAG_SENSOR_FAIL);
      }
      if (digitalRead (TOP_UPPER_SAG_SENSOR) == HIGH) {
        SerialUSB.println(TOP_U_SAG_SENSOR_FAIL);
      }
    }
    else if (strcmp(Buffer, BOTTOM_SAG_SENSOR_CHECK) == 0)
    {
      if (digitalRead (BOTTOM_LOWER_SAG_SENSOR) == LOW) {
        SerialUSB.println(BOTTOM_L_SAG_SENSOR_PASS);
      }
      if (digitalRead (BOTTOM_UPPER_SAG_SENSOR) == LOW) {
        SerialUSB.println(BOTTOM_U_SAG_SENSOR_PASS);
      }
      if (digitalRead (BOTTOM_LOWER_SAG_SENSOR) == HIGH) {
        SerialUSB.println(BOTTOM_L_SAG_SENSOR_FAIL);
      }
      if (digitalRead (BOTTOM_UPPER_SAG_SENSOR) == HIGH) {
        SerialUSB.println(BOTTOM_U_SAG_SENSOR_FAIL);
      }
    }
    /******************************************************************
      IET call functions - Called before and during inspection process
    ******************************************************************/

    else if (strcmp(Buffer, IET_SELECT_PRESS) == 0) {
      ietSelect();
    }
    else if (strcmp(Buffer, IET_RUN_PRESS) == 0) {
      ietRun();
    }
    else if (strcmp(Buffer, IET_PASS_PRESS) == 0) {
      ietPass();
    }
    else if (strcmp(Buffer, IET_PAUSE_PRESS) == 0) {
      ietPause();
    }
    else if (strcmp(Buffer, IET_FAIL_PRESS) == 0) {
      ietFail();
    }
    else if (strcmp(Buffer, IET_BUZZEROFFDR_PRESS) == 0) {
      ietBuzzeroffDR();
    }
    else if (strcmp(Buffer, IET_BUZZEROFFER_PRESS) == 0) {
      ietBuzzeroffER();
    }
    else if (strcmp(Buffer, IET_DHBLS) == 0) {
      dhbls();
    }
    else if (strcmp(Buffer, IET_HARDWARE_BUTTON_DISABLE) == 0) {
      hwbdb();
    }


    /******************************************************************
      Sag based Reeler function - Called during inspection process
    ******************************************************************/
    if (strcmp(Buffer, TOP_START_REELER) == 0) {
      rMotor1 = HIGH;
      
       D_Trig_Count = 0;
    }
    if (strcmp(Buffer, BTM_START_REELER) == 0) {
      rMotor2 = HIGH;
    }
    if (strcmp(Buffer, TOP_STOP_REELER) == 0) {
      rMotor1 = LOW;
      StopReelerMotor1(TOP_MOTOR_SS);
    }
    if (strcmp(Buffer, BTM_STOP_REELER) == 0) {
      rMotor2 = LOW;
      StopReelerMotor2(BOTTOM_MOTOR_SS);
    }
    if (strcmp(Buffer, REELER_MULTIPLICATION_FACTOR) == 0) {
      Relermotorflag = HIGH;
      ReelerMotorSpeedMultplier();}

    if (strcmp(Buffer, TOP_REELER_SPEED) == 0) {
      Debugstate && Serial.println("TPRSP_REC");
      rSpeed1 = HIGH;
      ReelerMotorSpeed1();
    }
    if (strcmp(Buffer, BTM_REELER_SPEED) == 0) {
       Debugstate && Serial.println("BMRSP_REC");
      rSpeed2 = HIGH;
      ReelerMotorSpeed2();
    }
    /******************************************************************
       Guide steps function - Called after selecting part.Guide moves
       upto given steps according to part. Specify the steps in JSON
    ******************************************************************/

    if (strcmp(Buffer, TOP_GUIDE_INSERT) == 0) {
      gMotor = HIGH;
      GuideStepsTop(TOP_MOTOR_SS);
    }
    if (strcmp(Buffer, BTM_GUIDE_INSERT) == 0) {
      gMotor = HIGH;
      GuideStepsBottom(BOTTOM_MOTOR_SS);
    }

    /******************************************************************
      Stamping and Winding Relay ON/OFF Sequence - Called multiple
      places. Works throughout JSON
    ******************************************************************/
    else if (strcmp(Buffer, STAMPING_RELAY_ON) == 0) {
      digitalWrite(STAMPING_RELAY, HIGH);
    }
    else if (strcmp(Buffer, STAMPING_RELAY_OFF) == 0) {
      digitalWrite(STAMPING_RELAY, LOW);
    }

    else if (strcmp(Buffer, WINDING_RELAY_ON) == 0) {
      digitalWrite(STAMPING_RELAY, HIGH);
    }
    else if (strcmp(Buffer, WINDING_RELAY_OFF) == 0) {
      digitalWrite(STAMPING_RELAY, LOW);
    }
    else if (strcmp(Buffer, SOLENOID_ON) == 0) {
      digitalWrite(TOP_SOLENOID_VALVE , LOW);
    }
    else if (strcmp(Buffer, SOLENOID_OFF) == 0) {
     digitalWrite(TOP_SOLENOID_VALVE , HIGH);
    }
        /******************************************************************
          Encoder function - Called after selecting part.
        ******************************************************************/
    
        else if (strcmp(Buffer, ENCODER_INITIALIZATION_TOP) == 0) {
          Debugstate && Serial.println("EI_cmd_rd");
          TOP_EncoderInitial();
        }
    
        else if (strcmp(Buffer, ENCODER_INITIAL_ANGLE_TOP) == 0) {
        Debugstate && Serial.println("EIA_cmd_rd");
          EncoderInitialAngle(TOP_ENCODER_SS);
        }
    
        else if (strcmp(Buffer, TOP_REELER_TEETH) == 0) {
          Debugstate && Serial.println("RT_Cmd_rd");
          ReelerTeethCount();
        }

         else if (strcmp(Buffer, SKIP_TRIGGER_COUNT) == 0) {
       
          SkipTrigger();
        }
    
        else if (strcmp(Buffer, ENCODER_ENABLE_TOP) == 0) {
          Debugstate && Serial.println("EET_cmd_rd");
          attachInterrupt(digitalPinToInterrupt(TOP_ENCODER_INT), ISRTrigger_Top, FALLING);
        }
        else if (strcmp(Buffer, ENCODER_DISABLE_TOP) == 0) {
          Debugstate && Serial.println("EDT_cmd_rd");
          detachInterrupt(TOP_ENCODER_INT);
        }
    /*********************Bottom Rack encoder trigger************************/
        else if (strcmp(Buffer, ENCODER_INITIALIZATION_BOTTOM) == 0) {
           Debugstate && Serial.println("EIB_cmd_rd");
          BOTTOM_EncoderInitial();
        }
    
        else if (strcmp(Buffer, ENCODER_INITIAL_ANGLE_BOTTOM) == 0) {
          Debugstate && Serial.println("EIAB_cmd_rd");
          EncoderInitialAngle(BOTTOM_ENCODER_SS);
        }
    
        else if (strcmp(Buffer, BTM_REELER_TEETH) == 0) {
           Debugstate && Serial.println("RT_Cmd_rd");
          ReelerTeethCount();
        }
    
        else if (strcmp(Buffer, ENCODER_ENABLE_BOTTOM) == 0) {
          Debugstate && Serial.println("EEB_cmd_rd");
          attachInterrupt(digitalPinToInterrupt(BOTTOM_ENCODER_INT), ISRTrigger_Bottom, FALLING);
        }
        else if (strcmp(Buffer, ENCODER_DISABLE_BOTTOM) == 0) {
          Debugstate && Serial.println("EDB_cmd_rd");
          detachInterrupt(digitalPinToInterrupt (BOTTOM_ENCODER_INT));
        }

    else if (strcmp(Buffer, I2C1_INITIALIZATION) == 0) {
      i2cpinInput(1);
    }
    else if (strcmp(Buffer, I2C2_INITIALIZATION) == 0) {
      i2cpinOutput(2);
    }
    else if (strcmp(Buffer, I2C3_INITIALIZATION) == 0) {
      i2cpinOutput(3);
    }
    
//Reference Search Opcodes
    else if (strcmp(Buffer, Top_Camera_Reference_search) == 0) {
      LightCameraSequence_Top();
      delayMicroseconds(gspmdelay_Top);
      SerialUSB.println(Top_Reference_Search_Response);      
    }
    else if (strcmp(Buffer, Bottom_Camera_Reference_search) == 0) {
      LightCameraSequence_Btm();
      delayMicroseconds(gspmdelay_Bottom);
      SerialUSB.println(Bottom_Reference_Search_Response);      
    }
    else if (strcmp(Buffer, Top_SPM_Delay) == 0) {
      if(SerialUSB.available())
      {
        gspmdelay_Top = SerialUSB.parseInt(); 
      }   
    }
    else if (strcmp(Buffer, Bottom_SPM_Delay) == 0) {
      if(SerialUSB.available())
      {
        gspmdelay_Bottom = SerialUSB.parseInt(); 
      }   
    }
  }
}
