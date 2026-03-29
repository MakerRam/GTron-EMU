
/************2 rack compatible******************/
void TOP_EncoderInitial()
{
  LS7366 enc(TOP_ENCODER_SS);
   Debugstate && Serial.println("TEI_fun_exe");
  enc.clear_mode_register_0();          // Clearing MDR0
  enc.clear_mode_register_1();          // Clearing MDR1
  enc.clear_counter();                  // Clearing Counter
  enc.clear_status_register();          // Clearing Status Register
  enc.write_mode_register_0(QUADRX4 | FREE_RUN | INDX_LOADO | SYNCH_INDX | FILTER_2); // Set MDR0 to load CNTR to OTR on Z pulse
  enc.write_mode_register_1(IDX_FLAG | EN_CNTR | BYTE_4); // Set MDR1 to give interrupt on Z pulse
  
  attachInterrupt(digitalPinToInterrupt(TOP_ENCODER_INT), TOP_ISRFunction, FALLING);  //Attaching Interrupt
   StartReelerMotor1(TOP_MOTOR_SS);
   T_Gcounter=0;
    
}
void BOTTOM_EncoderInitial()
{
  LS7366 enc(BOTTOM_ENCODER_SS);
   Debugstate && Serial.println("BEI_fun_exe");
  enc.clear_mode_register_0();          // Clearing MDR0
  enc.clear_mode_register_1();          // Clearing MDR1
  enc.clear_counter();                  // Clearing Counter
  enc.clear_status_register();          // Clearing Status Register
  enc.write_mode_register_0(QUADRX4 | FREE_RUN | INDX_LOADO | SYNCH_INDX | FILTER_2); // Set MDR0 to load CNTR to OTR on Z pulse
  enc.write_mode_register_1(IDX_FLAG | EN_CNTR | BYTE_4); // Set MDR1 to give interrupt on Z pulse

  attachInterrupt(digitalPinToInterrupt(BOTTOM_ENCODER_INT), BOTTOM_ISRFunction, FALLING);  //Attaching Interrupt
  StartReelerMotor2(BOTTOM_MOTOR_SS);
 
    B_Gcounter=0;
}


void Setforcomparison( uint8_t  E_SlaveSelect)
{
  LS7366 enc(E_SlaveSelect);
  Debugstate && Serial.println("SFR_fun_exe");
  enc.write_mode_register_0(QUADRX4 | FREE_RUN | INDX_RESETC | SYNCH_INDX | FILTER_2);
  enc.write_mode_register_1(CMP_FLAG | EN_CNTR | BYTE_4);      //Enabling Interrupt for Comparison
}

void EncoderInitialAngle(uint8_t E_SlaveSelect) {
  Debugstate && Serial.println("EIA_fun_exe");
  Setforcomparison(E_SlaveSelect);
  TriggerAngleFlag = HIGH;
  
  while (TriggerAngleFlag == HIGH) {
    if (SerialUSB.available()) {
      InitialAngle = SerialUSB.parseInt();
      
      // Approach B: Calculate NoOfTeeth from TriggerAngle input
      // NoOfTeeth is now treated as TriggerAngle input
      double InputTriggerAngle = NoOfTeeth;  // Input from ReelerTeethCount() function
      
      // Calculate actual number of teeth by rounding
      double CalculatedTeeth = (double) Resolution / InputTriggerAngle;
      int ActualTeeth = round(CalculatedTeeth);
      
      // Recalculate actual TriggerAngle for consistent spacing
      double TriggerAngle = (double) Resolution / (double) ActualTeeth;
      double CurrentAngle = InitialAngle;
      
      // For alternate triggering, double the step size
      double AlternateTriggerAngle = TriggerAngle * Skiptriggervalue;  // Every 1st or 2nd terminal trigger based on skip trigger value set in MI Json 
      EffectiveTeeth = ActualTeeth / Skiptriggervalue;  
      
      for (int i = 0; i < EffectiveTeeth; i++) {
        Array[i] = round(CurrentAngle);
        CurrentAngle += AlternateTriggerAngle;
      }
      
      // Mark unused positions
      for (int i = EffectiveTeeth; i < ActualTeeth; i++) {
        Array[i] = -1;
      }
      
      writeDataValue(Array[0], E_SlaveSelect);
      TriggerAngleFlag = LOW;
      
      // Update NoOfTeeth with actual calculated teeth for reference
      NoOfTeeth = ActualTeeth;
    }
  }
}



void writeDataValue( int value, uint8_t  E_SlaveSelect)
{       
  LS7366 enc(E_SlaveSelect);
  Debugstate && Serial.println("WDV_exe");  
                 
  enc.write_data_register(value);    //Writting value to Compare
}








/*
void ClearInterrupt(uint8_t  SlaveSelect)
{              
  enc.clear_status_register();                          //Clearing Status Register
  enc.clear_counter();                                   //Clearing Counter
}

void ReadCounter(uint8_t  SlaveSelect)
{
  int readCounter = enc.read_counter();
}*/
