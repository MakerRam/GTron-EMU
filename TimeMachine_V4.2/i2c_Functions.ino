#define IODIR                     0x00  // IO Direction Register 
#define IPOL                      0x01  // Input Polarity Register
#define GPINTEN                   0x02  // GPIO Interrupt-on-Change
#define DEFVAL                    0x03  // Default Compare Register for Interrupt-on-Change
#define INTCON                    0x04  // Interrupt Control Register 
#define IOCON                     0x05  // IOCON register is located 
#define GPPU                      0x06  // PULL-UP resistor configuration register 
#define INTF                      0x07  // Interrupt Flag Register
#define INTCAP                    0x08  // Interrupt(Value@GPIO) Capture Register

// Configurations for IOCON Register
#define ENABLE_SEQUENTIAL_OP      0xFF     // Enable sequential read
#define DISABLE_SEQUENTIAL_OP     0x20     // Disable   sequential read#define INTPOL_HIGH               
#define ENABLE_SLEW_RATE          0        // Slew Rate Enabled
#define DISABLE_SLEW_RATE         0x10     // Disable Slew Rate                
#define SET_HAEN                  0x08     // Enable Address Pins
#define RESET_HAEN                0        // Disable Address Pins#define SET_ODR             
#define SET_ODR                   0x04     // Active drain output 
#define RESET_ODR                 0x00     // Active drain output 
#define INTPOL_HIGH               0x02
#define INTPOL_LOW                0x00

#define ALLPINS_AS_INOROUT        0xFF
#define ALL_INPUTS_PULLEDUP       0x00
#define INPUT_POLARITY            0xFF     //Configure the polarity of Input GPIO's       :0x00 (GPIO register bit will reflect the same logic state of the input pin)
#define IODIR                     0x00  // IO Direction Register is located at 0x00
#define IOCON                     0x05  // IOCON register is located at address 0x05
#define GPPU                      0x06  // PULL-UP resistor configuration register address 0x06

//int ioDir = ALLPINS_AS_INOROUT;
int ipol = INPUT_POLARITY;
int pullup = ALL_INPUTS_PULLEDUP;
//int defval = DEF_REG_VALUE;
//int prevPinValue = PREV_PIN_VALUE;
int  gpioPin = 0;
byte readInterruptFlag = 0;
byte PrevintEnable = 0;
unsigned char readIntCapRegister = 0;
volatile int switchState;
byte PreviousIntcap = 0;
byte readGPINTEN = 0;
byte BINTCAP = 0;
byte BGPINTEN = 0;
byte BPreviousINTCAP = 0;

void i2cInit(uint8_t Slot)
{
//  pinMode(SlaveSelect[Slot], OUTPUT);
//  digitalWrite(SlaveSelect[Slot], LOW);
//  delay(100);
//  digitalWrite(SlaveSelect[Slot], HIGH);
  i2cObj.begin(Slot);
  i2cObj.i2caddr = Slot;
  Wire1.setClock(100000);
  int iocon_set = DISABLE_SEQUENTIAL_OP | ENABLE_SLEW_RATE |
                  SET_HAEN | RESET_ODR | INTPOL_HIGH;  // Must be 0x2A
  i2cObj.write8(IOCON, iocon_set);
}

void i2cHGH(uint8_t Slot, uint8_t PiNumber)
{
//  SerialUSB.println("HIGH");
  i2cObj.i2caddr = Slot;
  i2cObj.digitalWrite(PiNumber, HIGH);
}

void i2cLOW(uint8_t Slot, uint8_t PiNumber)
{
//  SerialUSB.println("low");
  i2cObj.i2caddr = Slot;
  i2cObj.digitalWrite(PiNumber, LOW);
}

void i2cpinInput(uint8_t Slot)
{
//  detachInterrupt(BoardInterrupt[Slot]);
  i2cObj.i2caddr = Slot;
  i2cObj.write8(IODIR, 0xFF);
  i2cObj.write8(GPPU, 0x00);
//  i2cpatch = true;
}

void i2cpinOutput(uint8_t Slot)
{
  i2cObj.i2caddr = Slot;
  i2cObj.write8(IODIR, 0x00);
}

void i2cRead(uint8_t Slot, uint8_t PiNumber)
{
  volatile int switchState;
  i2cObj.i2caddr = Slot;
  switchState = i2cObj.digitalRead(PiNumber);
}
