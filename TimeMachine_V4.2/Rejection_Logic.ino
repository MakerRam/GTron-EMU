/*****************************************************************************************************
  Name  :  Rejection Logic
  Desc  :  Based on the below Sensor logic confirmation, Next Run will be
          executed during the inspection process
*****************************************************************************************************/

void RejectionLogic() {
  if (Rejectionlogic_Flag && !interruptAttached) {
       
      //Serial.println("Rejection Enabled");
    attachInterrupt(digitalPinToInterrupt(BOTTOM_SENSOR_TRIGGER_INPUT), check, RISING);
    interruptAttached = true;
  }

   if (rejectionDoneISR) {
    noInterrupts();
    rejectionDoneISR = false;
    interrupts();

    detachInterrupt(digitalPinToInterrupt(BOTTOM_SENSOR_TRIGGER_INPUT));
    //Serial.println("ISR detached");
    interruptAttached = false;
    Rejectionlogic_Flag = false;
    falsetrigger = true;
    SerialUSB.println(Rejection_Done);
   //Serial.println(Rejection_Done);
  }
}


void check() {

  unsigned long now = micros();

  // Debounce
  if ((now - lastISRTime) > debounce_delaybt) {
    if (falsetrigger){
     // SerialUSB.println("false trigger");
     //Serial.println("false trigger");
      falsetrigger = false;
      }else
      {
    rejectionDoneISR = true;
    //Serial.println("trigger received");
    lastISRTime = now;}
  }
}





         
