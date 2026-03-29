/*****************************************************************************************************
  ISR for Light Camera sequence.
  Sets only the flag when interrupt occurs
*****************************************************************************************************/

void SetLCtp() {
  presentticktp = micros();
  if ((presentticktp - previousticktp) > debounce_delaytp)
  {
    if (!ENABLE_R1_LCS){
      ENABLE_R1_LCS = true;                     //To avoid first trigger
      }
      else
      {
   LCtp_FLAG = HIGH;
   previousticktp = micros();
  }
  }
}

void SetLCbm() {
  presenttickbt = micros();
  if ((presenttickbt - previoustickbt) > debounce_delaybt)
  {
    if (!ENABLE_R2_LCS){
      ENABLE_R2_LCS = true;
      }
      else 
      {
       LCbm_FLAG = HIGH;
       previoustickbt = micros();
        }
  }
}


/*****************************************************************************************************
  ISR Executions.
  Executes the defined set of functions when the ISR Flags are Set.
*****************************************************************************************************/
void ISR_Executions()
{
  if (LCtp_FLAG == HIGH) {
    LightCameraSequence_Top();
    //SerialUSB.println(TRIGGER_SIGNAL);
  }

  if (LCbm_FLAG == HIGH) {
    LightCameraSequence_Btm();
  }
  if (ENC_FLAG_Top == HIGH) {
    LS7366 enc(TOP_ENCODER_SS);
    Debugstate && Serial.println("ISRT_exe");
    
    // --- Debug: trigger#, encoder pulse, and time gap ---
//    static unsigned long T_prevUs = 0;
//    unsigned long T_nowUs = micros();
//    Serial.print("T#");
//    Serial.print(T_Gcounter);
//    Serial.print(" enc=");
//    Serial.print(enc.read_counter());
//    Serial.print(" us=");
//    Serial.println(T_nowUs - T_prevUs);
//    T_prevUs = T_nowUs;
    // --- End Debug ---
     LightCameraSequence_Top(); //call the light cam seq
    //SerialUSB.println(TRIGGER_SIGNAL);
    ENC_FLAG_Top = LOW;
    T_Gcounter += 1;
    enc.clear_status_register();
    if (T_Gcounter >= EffectiveTeeth) {  // CHANGED: >= effectiveTeeth instead of == NoOfTeeth
  T_Gcounter = 0;
  enc.write_data_register(Array[0]);
} else {
  enc.write_data_register(Array[T_Gcounter]);  // MOVED: Inside else block
}
  }
  if (ENC_FLAG_Bottom == HIGH) {
    LS7366 enc(BOTTOM_ENCODER_SS);
    Debugstate && Serial.println("ISRB_exe");
    
    // --- Debug: trigger#, encoder pulse, and time gap ---
//    static unsigned long B_prevUs = 0;
//    unsigned long B_nowUs = micros();
//    SerialUSB.print("B#");
//    SerialUSB.print(B_Gcounter);
//    SerialUSB.print(" enc=");
//    SerialUSB.print(enc.read_counter());
//    SerialUSB.print(" us=");
//    SerialUSB.println(B_nowUs - B_prevUs);
//    B_prevUs = B_nowUs;
    // --- End Debug ---
    //SerialUSB.println(TRIGGER_SIGNAL);
    LightCameraSequence_Btm(); //call the light cam seq
    ENC_FLAG_Bottom = LOW;
    B_Gcounter += 1;
    enc.clear_status_register();
   if (B_Gcounter >= EffectiveTeeth) { // CHANGED: >= effectiveTeeth instead of == NoOfTeeth
B_Gcounter = 0;
enc.write_data_register(Array[0]);
} else {
enc.write_data_register(Array[B_Gcounter]); // MOVED: Inside else block
}
  }
}


void TOP_ISRFunction()
{
  LS7366 enc(TOP_ENCODER_SS);
 Debugstate && Serial.println("TISR_fun_exe");
  if (T_FirstCall) {
    T_FirstCall = LOW;                       // Code should not run on first call, which is when interrupt is attached
    enc.clear_status_register();          // Clearing Status Register
    Debugstate && Serial.println("FC");
  }

  else
  {
    Debugstate && Serial.println("FC_not");
    T_FirstCall = HIGH;
    gISRFlag = LOW;
    StopReelerMotor1(TOP_MOTOR_SS);
    SerialUSB.println(Reeler_int_done);
    enc.clear_status_register();          // Clearing Status Register
    detachInterrupt(TOP_ENCODER_INT);
  }
}
void BOTTOM_ISRFunction()
{
  LS7366 enc(BOTTOM_ENCODER_SS);
 Debugstate && Serial.println("BISR_fun_exe");
  if (B_FirstCall) {
    B_FirstCall = LOW;                       // Code should not run on first call, which is when interrupt is attached
    enc.clear_status_register();          // Clearing Status Register
    Debugstate && Serial.println("FC");
  }

  else
  {
    Debugstate && Serial.println("FC_not");
    B_FirstCall = HIGH;
    gISRFlag = LOW;
    StopReelerMotor2(BOTTOM_MOTOR_SS);
      SerialUSB.println(Reeler_int_done);
    enc.clear_status_register();          // Clearing Status Register
   detachInterrupt(BOTTOM_ENCODER_INT);
  }
}
void ISRTrigger_Top()
{  
   Debugstate && Serial.println("ISRT");
  ENC_FLAG_Top = HIGH;
}
void ISRTrigger_Bottom()
{
  Debugstate && Serial.println("ISRB");
   ENC_FLAG_Bottom = HIGH;
}
