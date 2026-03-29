void sendData(unsigned long address, unsigned long datagram, uint8_t chipCS)
{
    Debugstate && Serial.println("send_D_exe");
    unsigned long i_datagram;
    digitalWrite(chipCS, LOW);
    SPI.transfer(address);
    i_datagram |= SPI.transfer((datagram >> 24) & 0xff);
    i_datagram <<= 8;
    i_datagram |= SPI.transfer((datagram >> 16) & 0xff);
    i_datagram <<= 8;
    i_datagram |= SPI.transfer((datagram >> 8) & 0xff);
    i_datagram <<= 8;
    i_datagram |= SPI.transfer((datagram) & 0xff);
    digitalWrite(chipCS, HIGH);
    SPI.endTransaction();
    //  SerialUSB.println(i_datagram,HEX);
}

unsigned long int  receiveData(  uint32_t address, uint8_t chipCS) {
    // request the read for the address
    Debugstate && Serial.println("receive_D_exe");
    digitalWrite(chipCS, LOW);
    delayMicroseconds(10);
    SPI.transfer(address);
    SPI.transfer(0x00);
    SPI.transfer(0x00);
    SPI.transfer(0x00);
    SPI.transfer(0x00);
    SPI.endTransaction();
    digitalWrite(chipCS, HIGH);
  
  
    // read it in the second cycle
    digitalWrite(chipCS, LOW);
    SPI.transfer(0x2D);
    uint32_t value = 0;
    value |= SPI.transfer(0x00) << 24;
    value <<= 8;
    value |= SPI.transfer(0x00) << 16;
    value <<= 8;
    value |= SPI.transfer(0x00) << 8;
    value <<= 8;
    value |= SPI.transfer(0x00);
    SPI.endTransaction();
    digitalWrite(chipCS, HIGH);
    return value;
}

void StepperInitial(uint8_t  SlaveSelect)
{
    Debugstate && Serial.println("STPR_I_fun_exe");
    sendData(0x80, 0x00000008, SlaveSelect);    //GCONF
    sendData(0xEC, 0x000100C5, SlaveSelect);    // CHOPCONF: TOFF=5, HSTRT=4, HEND=1, TBL=2, CHM=0 (spreadCycle)
    sendData(0xB0, 0x00011F05, SlaveSelect);    //IHOLD_IRUN: IHOLD=5, IRUN=31 (max.current), IHOLDDELAY=1
    sendData(0xAC, 0x00002710, SlaveSelect);    // TZEROWAIT=10000
    sendData(0x90, 0x00000000, SlaveSelect);    // PWMCONF PWM_CONF: AUTO=1, 2/1024 Fclk, Switch amp limit=200, grad=1
    sendData(0xB2, 0x00061A80, SlaveSelect);    // VHIGH=400 000: Set VHIGH to a high value to allow stealthChop
    sendData(0xB1, 0x00007530, SlaveSelect);    // VCOOLTHRS=30000: Set upper limit for stealthChop to about 30RPM
    sendData(0xED, 0x00008701, SlaveSelect);    // COOLCONF
    sendData(0xA4, 0x000003E8, SlaveSelect);    //A1=1000
    sendData(0xA5, 0x000186A0, SlaveSelect);    //V1=100000
    sendData(0xA6, 0x0000C350, SlaveSelect);    //AMAX=60000
    sendData(0xA7, 0x00000000, SlaveSelect);    //VMAX=256000
    sendData(0xAA, 0x00000578, SlaveSelect);    //D1=1400
    sendData(0xAB, 0x0000000A, SlaveSelect);    //VSTOP=10
    sendData(0xB4, 0x0000000C, SlaveSelect);    //pol_stop
    sendData(0xA0, 0x00000000, SlaveSelect);    //RAMPMODE=0
  
    sendData(0xFC, 0x000100C5, SlaveSelect);   //CHOP CONF
    sendData(0xD0, 0x00011F05, SlaveSelect);   //CURRENT SETTING
    sendData(0xC0, 0x00000001, SlaveSelect);   //RAMPMODE=1
    sendData(0xC4, 0x000003E8, SlaveSelect);   //A1=1000
    sendData(0xC5, 0x000003E8, SlaveSelect);   //V1=100000
    sendData(0xC6, 0x0000EA60, SlaveSelect);   //AMAX=60000
    sendData(0xC7, 0x00000000, SlaveSelect);   //VMAX=0
    sendData(0xCA, 0x00000578, SlaveSelect);   //D1=1400
    sendData(0xCB, 0x0000000A, SlaveSelect);   //VSTOP=10
    sendData(0xC7, 0x00000000, SlaveSelect);   //VMAX=0
    sendData(0xC0, 0x00000000, SlaveSelect);   //RAMPMODE=0


}

void StepperRotateCW(uint8_t  SlaveSelect) {
    Debugstate && Serial.println("SRCW_exe");
    //    LimitSwitchCheck=true;
    sendData(0x80, 0x00000008, SlaveSelect);    //GCONF
    sendData(0xEC, 0x000100C5, SlaveSelect);   //CHOP CONF
    sendData(0xB0, 0x00011F05, SlaveSelect);   //CURRENT SETTING
    sendData(0xA0, 0x00000001, SlaveSelect);   //RAMPMODE=1
    sendData(0xA4, 0x000003E8, SlaveSelect);   //A1=1000
    sendData(0xA5, 0x000003E8, SlaveSelect);   //V1=100000
    sendData(0xA6, 0x0000EA60, SlaveSelect);   //AMAX=60000
    sendData(0xA7, 0x0003E800, SlaveSelect);   //VMAX=256000
    sendData(0xAA, 0x00000578, SlaveSelect);   //D1=1400
    sendData(0xAB, 0x0000000A, SlaveSelect);   //VSTOP=10
}


void StepperRotateCCW(uint8_t  SlaveSelect) {
    Debugstate && Serial.println("SRCCW_exe");
    sendData(0x80, 0x00000108, SlaveSelect);    //GCONF
    sendData(0xEC, 0x000100C5, SlaveSelect);   //CHOP CONF
    sendData(0xB0, 0x00011F05, SlaveSelect);   //CURRENT SETTING
    sendData(0xA0, 0x00000001, SlaveSelect);   //RAMPMODE=1
    sendData(0xA4, 0x000003E8, SlaveSelect);   //A1=1000
    sendData(0xA5, 0x000003E8, SlaveSelect);   //V1=100000
    sendData(0xA6, 0x0000EA60, SlaveSelect);   //AMAX=60000
    sendData(0xA7, 0x0003E800, SlaveSelect);   //VMAX=256000
    sendData(0xAA, 0x00000578, SlaveSelect);   //D1=1400
    sendData(0xAB, 0x0000000A, SlaveSelect);   //VSTOP=10
}


void StopStepperCW(uint8_t  SlaveSelect) {
    Debugstate && Serial.println("SSCW_exe");
    sendData(0xA7, 0x00000000, SlaveSelect);   //VMAX=0
}

void StepstoRotateTop(uint8_t  SlaveSelect) {
    Debugstate && Serial.println("SRT_exe");
    sendData(0x80, 0x00000108, SlaveSelect);   //GCONF
    sendData(0xEC, 0x000100C5, SlaveSelect);   //CHOP CONF
    sendData(0xB0, 0x00011F05, SlaveSelect);   //CURRENT SETTING
    sendData(0xA0, 0x00000000, SlaveSelect);   //RAMPMODE=0
    sendData(0xA4, 0x000003E8, SlaveSelect);   //A1=1000
    sendData(0xA5, 0x0000C350, SlaveSelect);   //V1=100000
    sendData(0xA6, 0x000001F4, SlaveSelect);   //AMAX=60000
    sendData(0xA7, 0x0003E800, SlaveSelect);   //VMAX=256000
    sendData(0xA8, 0x000002BC, SlaveSelect);   //DMAX=256000
    sendData(0xAA, 0x00000578, SlaveSelect);   //D1=1400
    sendData(0xAB, 0x0000000A, SlaveSelect);   //VSTOP=10
    sendData(0xA1, 0X00000000, SlaveSelect);   //XACTUAL=0
    sendData(0xAD, Steps, SlaveSelect);    //XTARGET=0
    sendData(0x85, Steps, SlaveSelect);    //X_Compare
}
void StepstoRotateBtm(uint8_t  SlaveSelect) {
    Debugstate && Serial.println("SRB_exe");
    sendData(0x80, 0x00000008, SlaveSelect);   //GCONF
    sendData(0xEC, 0x000100C5, SlaveSelect);   //CHOP CONF
    sendData(0xB0, 0x00011F05, SlaveSelect);   //CURRENT SETTING
    sendData(0xA0, 0x00000000, SlaveSelect);   //RAMPMODE=0
    sendData(0xA4, 0x000003E8, SlaveSelect);   //A1=1000
    sendData(0xA5, 0x0000C350, SlaveSelect);   //V1=100000
    sendData(0xA6, 0x000001F4, SlaveSelect);   //AMAX=60000
    sendData(0xA7, 0x0003E800, SlaveSelect);   //VMAX=256000
    sendData(0xA8, 0x000002BC, SlaveSelect);   //DMAX=256000
    sendData(0xAA, 0x00000578, SlaveSelect);   //D1=1400
    sendData(0xAB, 0x0000000A, SlaveSelect);   //VSTOP=10
    sendData(0xA1, 0X00000000, SlaveSelect);   //XACTUAL=0
    sendData(0xAD, Steps, SlaveSelect);    //XTARGET=0
    sendData(0x85, Steps, SlaveSelect);    //X_Compare
}

void ReelerInitial(uint8_t  SlaveSelect)
{
    Debugstate && Serial.println("RI_fun_exe");
    sendData(0x80, 0x00000008, SlaveSelect);    //GCONF
  //sendData(0xFC, 0x000100C5, SlaveSelect);   //CHOP CONF
  //sendData(0xD0, 0x00011F05, SlaveSelect);   //CURRENT SETTING
  //sendData(0xC0, 0x00000001, SlaveSelect);   //RAMPMODE=1
  //sendData(0xC4, 0x000003E8, SlaveSelect);   //A1=1000
  //sendData(0xC5, 0x000003E8, SlaveSelect);   //V1=100000
  //sendData(0xC6, 0x0000EA60, SlaveSelect);   //AMAX=60000
  //sendData(0xC7, 0x00000000, SlaveSelect);   //VMAX=0
  //sendData(0xCA, 0x00000578, SlaveSelect);   //D1=1400
  //sendData(0xCB, 0x0000000A, SlaveSelect);   //VSTOP=10
  //sendData(0xC7, 0x00000000, SlaveSelect);   //VMAX=0
  }

  void ReelerSteps(uint8_t  SlaveSelect) {
    Debugstate && Serial.println("R_STEP_exe");
    sendData(0x80, 0x00000008, SlaveSelect);    //GCONF
    sendData(0xEC, 0x000100C5, SlaveSelect);   //CHOP CONF
    sendData(0xB0, 0x00011F05, SlaveSelect);   //CURRENT SETTING
    sendData(0xC0, 0x00000000, SlaveSelect);   //RAMPMODE=0
    sendData(0xC4, 0x000003E8, SlaveSelect);   //A1=1000
    sendData(0xC5, 0x0000C350, SlaveSelect);   //V1=100000
    sendData(0xC6, 0x000001F4, SlaveSelect);   //AMAX=60000
    sendData(0xC7, 0x00004E20, SlaveSelect);   //VMAX=256000
    sendData(0xC8, 0x000002BC, SlaveSelect);   //DMAX=256000
    sendData(0xCA, 0x00000578, SlaveSelect);   //D1=1400
    sendData(0xCB, 0x0000000A, SlaveSelect);   //VSTOP=10
    sendData(0xCD, 0x000186A0, SlaveSelect);   //XTARGET=0
    sendData(0x85, 0x000186A0, SlaveSelect); //X_Compare
    sendData(0xC1, 0X00000000, SlaveSelect);   //XACTUAL=0
  }

  void StartReelerMotor1(uint8_t  SlaveSelect) {
    Debugstate && Serial.println("SRM1_fun_exe");
    //SerialUSB.println("start");
    sendData(0xC4, 0x0000FFFF, SlaveSelect);   //A1=65535 (max acceleration phase 1)
    sendData(0xC6, 0x0000FFFF, SlaveSelect);   //AMAX=65535 (max acceleration phase 2)
    sendData(0xC0, 0x00000001, SlaveSelect);   //RAMPMODE=1
    sendData(0xC7, SetSpeed1, SlaveSelect);    //VMAX
    reelerMotorFlag1 = HIGH;
    //Serial.println(SetSpeed1);
    
  }

  void StartReelerMotor2(uint8_t  SlaveSelect) {
    Debugstate && Serial.println("SRM2_fun_exe");
    sendData(0xC4, 0x0000FFFF, SlaveSelect);   //A1=65535 (max acceleration phase 1)
    sendData(0xC6, 0x0000FFFF, SlaveSelect);   //AMAX=65535 (max acceleration phase 2)
    sendData(0xC0, 0x00000001, SlaveSelect);   //RAMPMODE=1
    sendData(0xC7, SetSpeed2, SlaveSelect);    //VMAX
    reelerMotorFlag2 = HIGH;
    //Serial.println(SetSpeed2);
  }

  void StopReelerMotor1(uint8_t  SlaveSelect) {
    Debugstate && Serial.println("STRM1_fun_exe");
    TpMtr =1;
    sendData(0xCA, 0x0000FFFF, SlaveSelect);   //D1=65535 (max deceleration)
    sendData(0xC8, 0x0000FFFF, SlaveSelect);   //DMAX=65535 (max deceleration phase 2)
    sendData(0xCB, 0x000000FF, SlaveSelect);   //VSTOP=255 (higher stop velocity for abrupt stop)
    sendData(0xC7, 0x00000000, SlaveSelect);   //VMAX=0
    reelerMotorFlag1 = LOW;
    trigMillis1 = millis();
  }


  void StopReelerMotor2(uint8_t  SlaveSelect) {
    Debugstate && Serial.println("STRM2_fun_exe");
    BmMtr = 1;
    sendData(0xCA, 0x0000FFFF, SlaveSelect);   //D1=65535 (max deceleration)
    sendData(0xC8, 0x0000FFFF, SlaveSelect);   //DMAX=65535 (max deceleration phase 2)
    sendData(0xCB, 0x000000FF, SlaveSelect);   //VSTOP=255 (higher stop velocity for abrupt stop)
    sendData(0xC7, 0x00000000, SlaveSelect);   //VMAX=0
    reelerMotorFlag2 = LOW;
    trigMillis1 = millis();
  }
