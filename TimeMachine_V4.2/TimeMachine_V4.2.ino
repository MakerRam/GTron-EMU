/**************************************************HEADER*********************************************
  PROJECT NAME :  TIME MACHINE 4.2.0
  DESCRIPTION  :  GTRON specific machine code for 2 Rack systems which handle all the sequence oprtations of GTRON comes from MI JSON.
  PRIVACY      :  Encrypted to use only for Zentron Projects.
  AUTHOR       :  SANTHOSH SEKAR             START DATE :    06 Jan 2021
  REVISED BY   :  RAMKUMAR                   DATE       :    21 August 2025

  CHECK RELEASE NOTES FOR CHANGES AND UPDATES

  [ BELOW ARE THE PROTOCOLS TO PREVENT TIME MACHINE,RECOMMENDED TO AVOID THE FOLLOWING ]
  
  * Print statements inside ISR functions.
  * Not to use pin number 0 and 1 for interrupts.
  * Communication over the serialUSB getting overflown(basically when more than 64bytes).
  * Touching base board while machine is running.
 
                              
******************************************************************************************************/
#include "Adafruit_MCP23008.h"
#include <String.h>
#include <Wire.h>
#include <SPI.h>                            // SPI Header
#include <LS7366.h>                         // Encoder IC Header
#include <DueTimer.h>
#include <SD.h>
Adafruit_MCP23008 i2cObj;
File myFile;
int pinCS = 41;                             // Pin 41 on Arduino Uno
volatile bool Debugstate = false;           // To debug flow through Programming port
volatile bool Guidetest = false;           // To test guide relaibility in long run 

/*****************************************************************************************************
  Name  :  I/O Pin Mapping
  Param@:  None
  Brief :  Initializes all DIOS as INPUT/OUTPUT.
*****************************************************************************************************/

/*____________________________________INPUTS_______________________________________________________*/
//Limit Switches
#define TOP_CLOSE_LIMIT_SWITCH          27
#define TOP_OPEN_LIMIT_SWITCH           28
#define BOTTOM_CLOSE_LIMIT_SWITCH       2
#define BOTTOM_OPEN_LIMIT_SWITCH        3

//Trigger Sensors
#define TOP_SENSOR_TRIGGER_INPUT        29 // All the 4 sensor's output is connected in single IO
#define BOTTOM_SENSOR_TRIGGER_INPUT     4

//Hardware Buttons
#define ESTOP_BUTTON                    30
#define RUN_BUTTON                      3 //I2C1_3: Slot I2C1 Expander Pin No 3
#define PAUSE_BUTTON                    20
#define STOP_BUTTON                     21
//#define BUZZEROFF_BUTTON              107 //I2C1_7
//#define SPARE_BUTTON                  100 //I2C1_0
//#define TOP_DOOR_LIMIT_SWITCH         101 //I2C1_1
//#define BOTTOM_DOOR_LIMIT_SWITCH      102 //I2C1_2
//#define PRESSURE_SWITCH               104 //I2C1_4
//#define SPARE_INPUT_1_I2C             105 //I2C_5
//#define SPARE_INPUT_2_I2C             106 //I2C_6

//Sag Sensors
#define TOP_UPPER_SAG_SENSOR            22
#define TOP_LOWER_SAG_SENSOR            24
//#define TOP_EXIT_SENSOR               41
#define BOTTOM_UPPER_SAG_SENSOR         39
#define BOTTOM_LOWER_SAG_SENSOR         40
#define BOTTOM_EXIT_SAG_SENSOR          42


/*____________________________________OUTPUTS_____________________________________________________*/

////Trigger Sensor Power
//#define TOP_SENSOR_POWER_1             0 //I2C2_0
//#define TOP_SENSOR_POWER_2             1 //I2C2_1
//#define TOP_SENSOR_POWER_3             2 //I2C2_2
//#define TOP_SENSOR_POWER_4             3 //I2C2_3
//#define BOTTOM_SENSOR_POWER_5          4 //I2C2_4
//#define BOTTOM_SENSOR_POWER_6          5 //I2C2_5
//#define BOTTOM_SENSOR_POWER_7          6 //I2C2_6
//#define BOTTOM_SENSOR_POWER_8          7 //I2C2_7

//Cameras and Lights
#define TOP_CAMERA_1                     5
#define TOP_CAMERA_2                     6
#define TOP_CAMERA_3                     7
#define TOP_LIGHT_1                      18
#define TOP_LIGHT_2                      19
#define TOP_LIGHT_3                      A2
#define BOTTOM_CAMERA_4                  8
#define BOTTOM_CAMERA_5                  9
#define BOTTOM_CAMERA_6                  10
#define BOTTOM_LIGHT_4                   A3
#define BOTTOM_LIGHT_5                   A0
#define BOTTOM_LIGHT_6                   A1

//Lamps, Indicators and Misc
//#define RUN_LAMP                       2 //I2C3_2
//#define PAUSE_LAMP                     3 //I2C3_3
//#define STOP_LAMP                      4 //I2C3_4
//#define BUZZEROFF_LAMP                 5 //I2C3_5
//#define SPARE_LAMP                     6 //I2C3_6
//#define TL_RED                         0 //I2C3_0
#define TL_YELLOW                       50
#define TL_GREEN                        51
//#define TL_BUZZER                      1 //I2C3_1
#define TOP_SOLENOID_VALVE              49
#define BOTTOM_SOLENOID_VALVE           52
#define STAMPING_RELAY                  11
//#define SPARE_OUT1_I2C                 7 //I2C3_7
#define SPARE_OUT2_HS                   12

//SPI SSs and INTs
#define TOP_MOTOR_SS                    A9
#define TOP_MOTOR_INT                   A8
#define TOP_ENCODER_SS                  25
#define TOP_ENCODER_INT                 26

#define BOTTOM_MOTOR_SS                 47
#define BOTTOM_MOTOR_INT                48
#define BOTTOM_ENCODER_SS               14
#define BOTTOM_ENCODER_INT              15

#define Resolution                      1600 //ENCODER RESOLUTION



/*****************************************************************************************************
  Name  :  OPCODE Mapping
  Param@:  None
  Brief :  Labelling all OPCODES which communicates from and to Machine Interface of ZenGage
*****************************************************************************************************/

// Communication Check
#define PING                                      "QUERY"                               
#define PING_RESPONSE                             "YES"
/*************************Front Pannel***************************/
// Emergency Button status check (Machine Power status check)
#define EMERGENCY_STOP_CHECK                      "EMSTP"
#define MACHINE_POWER_ON                          "MP1"
#define MACHINE_POWER_OFF                         "MP0"
// Push Button Check
#define ATTACH_RUN                                "ATRUN"
#define DETACH_RUN                                "DTRUN"
#define ATTACH_PAUSE                              "ATPAU"
#define DETACH_PAUSE                              "DTPAU"
#define ATTACH_STOP                               "ATSTP"
#define DETACH_STOP                               "DTSTP"
#define ATTACH_BUZZEROFF                          "ATBOF"
#define DETACH_BUZZEROFF                          "DTBOF"
// Push Button Indicator check                                               //NEED TO CODE
#define RUN_LAMP_ON                               "RUNON"               
#define PAUSE_LAMP_ON                             "PAUON"
#define STOP_LAMP_ON                              "STPON"
#define BUZZER_LAMP_ON                            "BZRON"
#define RUN_LAMP_OFF                              "RUNOF"
#define PAUSE_LAMP_OFF                            "PAUOF"
#define STOP_LAMP_OFF                             "STPOF"
#define BUZZER_LAMP_OFF                           "BZROF"
/***********************Pheripherals check*************************/
//Tower Lamp check
#define TOWERLAMP_RED_ON                          "TRED1"
#define TOWERLAMP_RED_OFF                         "TRED0"
#define TOWERLAMP_YELLOW_ON                       "TYEL1"
#define TOWERLAMP_YELLOW_OFF                      "TYEL0"
#define TOWERLAMP_GREEN_ON                        "TGRN1"
#define TOWERLAMP_GREEN_OFF                       "TGRN0"
#define TOWERLAMP_BUZZER_ON                       "TBZR1"
#define TOWERLAMP_BUZZER_OFF                      "TBZR0"
//Stamping & Winding check
#define STAMPING_RELAY_ON                         "STMP1"
#define STAMPING_RELAY_OFF                        "STMP0"
#define WINDING_RELAY_ON                          "WIND1"
#define WINDING_RELAY_OFF                         "WIND0"
//Door Limit switch
#define DOOR_LOCK_CHECK                           "DOORC"
//#define BTM_DOOR_LOCK_CHECK                     "bmDRC"
#define DOOR_LIMIT_SWITCH_PRESSED                 "DL1"
#define DOOR_LIMIT_SWITCH_NOTPRESSED              "DL0"
//Solenoid Check
#define SOLENOID_ON                              "SOLON"
#define SOLENOID_OFF                             "SOLOF"
// Sag Sensor Check
#define TOP_SAG_SENSOR_CHECK                     "TPSAG"
#define BOTTOM_SAG_SENSOR_CHECK                  "BMSAG"
// Sag Sensor response
#define TOP_U_SAG_SENSOR_PASS                     "TU1"
#define TOP_U_SAG_SENSOR_FAIL                     "TU0"
#define TOP_L_SAG_SENSOR_PASS                     "TL1"
#define TOP_L_SAG_SENSOR_FAIL                     "TL0"

#define BOTTOM_U_SAG_SENSOR_PASS                  "BU1"
#define BOTTOM_U_SAG_SENSOR_FAIL                  "BU0"
#define BOTTOM_L_SAG_SENSOR_PASS                  "BL1"
#define BOTTOM_L_SAG_SENSOR_FAIL                  "BL0"

/************************Rack test ********************************/

// Top Guide Limit switch check
#define TOP_LIMIT_SWITCH_CHECK                    "tpLSC"
#define TOP_LIMIT_SWITCH_PRESSED                  "tpOL1"
#define TOP_LIMIT_SWITCH_NOTPRESSED               "tpOL0"

// Bottom Guide Limit switch check
#define BTM_LIMIT_SWITCH_CHECK                    "bmLSC"
#define BTM_LIMIT_SWITCH_PRESSED                  "bmOL1"
#define BTM_LIMIT_SWITCH_NOTPRESSED               "bmOL0"

// Top Reeler check
#define STEPPER_INITIALIZATION                    "SMINI"
#define REELER_INITIALIZATION                     "RMINI"
#define TOP_ROTATE_REELER                         "tpRTR"

// Bottom Reeler check

#define BTM_ROTATE_REELER                         "bmRTR"

// Top Guide check

#define TOP_GUIDE_OPEN                            "tpGOP"
#define TOP_GUIDE_CLOSE                           "tpGCL"
#define TOP_GUIDE_OPEN_RESPONSE                   "tpGOR"
#define TOP_GUIDE_CLOSE_RESPONSE                  "tpGCR"

// Bottom Guide check
#define BTM_GUIDE_OPEN                            "bmGOP"
#define BTM_GUIDE_CLOSE                           "bmGCL"
#define BTM_GUIDE_OPEN_RESPONSE                   "bmGOR"
#define BTM_GUIDE_CLOSE_RESPONSE                  "bmGCR"

// Top Guide Long run test
#define TOP_GUIDE_TEST                            "tpGTS"

// Bottom Guide Long run test
#define BOTTOM_GUIDE_TEST                         "bmGTS"

// Top Trigger Sensor check
#define POWERON_SENSOR_1                          "POS01"
#define POWERON_SENSOR_2                          "POS02"
#define POWERON_SENSOR_3                          "POS03"
#define POWERON_SENSOR_4                          "POS04"
#define POWEROFF_SENSOR_1                         "PFS01"
#define POWEROFF_SENSOR_2                         "PFS02"
#define POWEROFF_SENSOR_3                         "PFS03"
#define POWEROFF_SENSOR_4                         "PFS04"

// Bottom Trigger Sensor check
#define POWERON_SENSOR_5                          "POS05"
#define POWERON_SENSOR_6                          "POS06"
#define POWERON_SENSOR_7                          "POS07"
#define POWERON_SENSOR_8                          "POS08"
#define POWEROFF_SENSOR_5                         "PFS05"
#define POWEROFF_SENSOR_6                         "PFS06"
#define POWEROFF_SENSOR_7                         "PFS07"
#define POWEROFF_SENSOR_8                         "PFS08"

// Sensor Trigger check
#define TOP_SENSOR_CHECK                         "TPSCK"
#define TOP_SENSOR_ON                            "TS1"
#define TOP_SENSOR_OFF                           "TS0"

#define BOTTOM_SENSOR_CHECK                      "BPSCK"
#define BOTTOM_SENSOR_ON                         "BS1"
#define BOTTOM_SENSOR_OFF                        "BS0"

// Light Camera Individual Sequence check
#define LIGHT_CAMERA_SEQUENCE_1                   "LCS01"   //Rack 1_Top_Cam = ON 
#define LIGHT_CAMERA_SEQUENCE_2                   "LCS02"   //Rack 1_Side_Cam = ON
#define LIGHT_CAMERA_SEQUENCE_3                   "LCS03"   //Rack 1_Front_Cam = ON
#define LIGHT_CAMERA_SEQUENCE_4                   "LCS04"   //Rack 1_Top_Light_Cam = ON
#define LIGHT_CAMERA_SEQUENCE_5                   "LCS05"   //Rack 2_Top_Cam = ON
#define LIGHT_CAMERA_SEQUENCE_6                   "LCS06"   //Rack 2_Side_Cam = ON
#define LIGHT_CAMERA_SEQUENCE_7                   "LCS07"   //Rack 2_Front_Cam = ON

// Top Light Camera Sequence check
#define LIGHT_CAMERA_SEQUENCE_TOP                 "LCStp" //Rack_1 Top_Cam = ON; Side_Cam = ON; Front_Cam = ON

// Bottom Light Camera Sequence check
#define LIGHT_CAMERA_SEQUENCE_BTM                 "LCSbm" //Rack_2 Top_Cam = ON; Side_Cam = ON; Front_Cam = ON

/*****************************************************************************************************************/

//Emergency status
#define EMERGENCY_STOP_PRESSED                    "ES1"
#define EMERGENCY_STOP_NOTPRESSED                 "ES0"

#define ATTACH_DOORLOCK                           "ATDRL"
#define DETACH_DOORLOCK                           "DTDRL"

#define LIGHT_CAMERA_SEQUENCE_I0                  "LCSI0"   //Rack_1 Top_Cam_Flag
#define LIGHT_CAMERA_SEQUENCE_I1                  "LCSI1"   //Rack_1 Side_Cam_Flag
#define LIGHT_CAMERA_SEQUENCE_I2                  "LCSI2"   //Rack_1 Front_Cam_Flag
#define LIGHT_CAMERA_SEQUENCE_I3                  "LCSI3"   //Rack_1 Top_ Light_Cam_Flag 
#define LIGHT_CAMERA_SEQUENCE_I4                  "LCSI4"   //Rack_2 Top_Cam_Flag
#define LIGHT_CAMERA_SEQUENCE_I5                  "LCSI5"   //Rack_2 Side_Cam_Flag
#define LIGHT_CAMERA_SEQUENCE_I6                  "LCSI6"   //Rack_2 Front_Cam_Flag

// ON_OFF TIMING CONFIGURABLE THROUGH MI - NEED TO CODE
#define LIGHT_ON_DELAY_TIMING                     "LONDT"   //
#define CAMERA_ON_DELAY_TIMING                    "CONDT"   //
#define CAMERA_OFF_DELAY_TIMING                   "COFDT"   //
#define LIGHT_OFF_DELAY_TIMING                    "LOFDT"   //

#define TOP_LIGHT_ON_DELAY_TIMING                 "TLOND"   //
#define TOP_CAMERA_ON_DELAY_TIMING                "TCOND"   //
#define TOP_CAMERA_OFF_DELAY_TIMING               "TCOFD"   //
#define TOP_LIGHT_OFF_DELAY_TIMING                "TLOFD"   //

#define ATTACH_SENSOR_TOP                         "tpATS"
#define ATTACH_SENSOR_BTM                         "bmATS"
#define DETACH_SENSOR_TOP                         "tpDTS"
#define DETACH_SENSOR_BTM                         "bmDTS"

#define IET_SELECT_PRESS                          "IESEL"
#define IET_RUN_PRESS                             "IERUN"
#define IET_PASS_PRESS                            "IEPAS"
#define IET_PAUSE_PRESS                           "IEPAU"
#define IET_FAIL_PRESS                            "IEFAI"
#define IET_BUZZEROFFDR_PRESS                     "BOFDR"
#define IET_BUZZEROFFER_PRESS                     "BOFER"
#define IET_DOORLOCKSWITCH_PRESS                  "IEDRL"
#define IET_DHBLS                                 "DHBLS"
#define IET_HARDWARE_BUTTON_DISABLE               "HWBDB"

#define TOP_GUIDE_INSERT                          "tpGDI"
#define BTM_GUIDE_INSERT                          "bmGDI"

#define TOP_REELER_SPEED                          "tpRSP"
#define BTM_REELER_SPEED                          "bmRSP"

#define TOP_REELER_TEETH                          "tpRTH"
#define BTM_REELER_TEETH                          "bmRTH"

#define REELER_MULTIPLICATION_FACTOR              "RMSMF"

#define TOP_START_REELER                          "tpSTR"
#define TOP_STOP_REELER                           "tpSTP"
#define BTM_START_REELER                          "bmSTR"
#define BTM_STOP_REELER                           "bmSTP"

#define RUN_PRESS                                 "RUN"
#define PAUSE_PRESS                               "PAU"
#define STOP_PRESS                                "STP"
#define BUZZEROFF_PRESS                           "BOF"
#define DOORUNLOCK_PRESS                          "DUL"
#define PRESSURESWITCH_ENABLE                    "PSWEN"
#define PRESSURESWITCH_DISABLE                   "PSWDB"
#define PRESSURESWITCH_CHECK                     "PSWCK"
#define PRESSURESWITCH_ON                        "PSWON"
#define PRESSURESWITCH_OFF                       "PSWOF"

#define GUIDE_REACHED                             "GRD"
#define INCORRECTOPCODE                           "FLS"

#define ENCODER_INITIALIZATION_TOP                "tpENI"//ENCODER INITILIZATION
#define ENCODER_INITIAL_ANGLE_TOP                 "tpINA"//ENCODER INITIAL ANGLE SET
#define ENCODER_ENABLE_TOP                        "tpEEN"//
#define ENCODER_DISABLE_TOP                       "tpEDB"
#define ENCODER_INITIALIZATION_BOTTOM             "bmENI"//ENCODER INITILIZATION
#define ENCODER_INITIAL_ANGLE_BOTTOM              "bmINA"//ENCODER INITIAL ANGLE SET
#define ENCODER_ENABLE_BOTTOM                     "bmEEN"//
#define ENCODER_DISABLE_BOTTOM                    "bmEDB"
#define I2C1_INITIALIZATION                       "I2C1"
#define I2C2_INITIALIZATION                       "I2C2"
#define I2C3_INITIALIZATION                       "I2C3"

// Reference Search
#define Top_Camera_Reference_search              "RFS01"
#define Bottom_Camera_Reference_search           "RFS02"
#define Top_Reference_Search_Response            "TRD01"
#define Bottom_Reference_Search_Response         "TRD02"
#define Top_SPM_Delay                            "SPM01"
#define Bottom_SPM_Delay                         "SPM02"


#define TRIGGER_SIGNAL                            "D"
#define MI_RESPONSE                               "MIRSP"

//Time stample enable/disable
#define TIMESTAMP_ENABLE                          "TSENB"

#define SKIP_TRIGGER_COUNT                        "SKTRG"

#define Reeler_int_done                            "RHD"

// Rejection Logic opcode

#define Rejection_Done                           "RJDNE"
#define Rejectionlogic_Enable                    "RJENB"

/*****************************************************************************************************
  Name  :  Global Variables
  Param@:  None
  Brief :  Labelling all OPCODES which communicates from and to Machine Interface of ZenGage
*****************************************************************************************************/
//HARDWARE VARIABLES//
/********************************************For Diagnostic only**********************************/
short LightOnDelay            = 1000;  /*Specify the time in MicroSeconds here for light ON/OFF functions*/
short CameraTriggerDelay      = 500;   /*Pulse delay for camera trigger signal*/
short LightOffDelay           = 5;
short LightCamInterval        = 20;    /*Delay between previous and next Light Cam Sequence MilliSeconds*/

/********************************************For Light Camera Inspection only**********************************/
//TOP RACK TOP CAMERA
short LIGHT_ONDELAY           = 1000;  /*Specify the time in MicroSeconds here for light ON/OFF functions*/
short CAMERA_ONDELAY          = 500;   /*Pulse delay for camera trigger signal*/
short CAMERA_OFFDELAY         = 100;
short LIGHT_OFFDELAY          = 5;    /*Delay between previous and next Light Cam Sequence MilliSeconds*/

// TOP RACK TOP CAMERA WITH BACKLIGHT
short TOP_LIGHT_ONDELAY      = 5000;  /*Specify the time in MicroSeconds here for light ON/OFF functions*/
short TOP_CAMERA_ONDELAY     = 500;   /*Pulse delay for camera trigger signal*/
short TOP_CAMERA_OFFDELAY    = 100;
short TOP_LIGHT_OFFDELAY     = 5;    /*Delay between previous and next Light Cam Sequence MilliSeconds*/


int EffectiveTeeth = 0;
int Skiptriggervalue = 1;

short pbDebounceDelay         = 50;  /*Debounce delay of Hardware Buttons - in millis*/

bool ENABLE_R1_LCS = false;
bool ENABLE_R2_LCS = false;
bool estop;


//HARDWARE FLAGS//
bool LCtp_FLAG = LOW; /*Flags get set in "ISR_Executions" tab, when the sensor interupt occurs*/
bool LCbm_FLAG = LOW;

bool run_FLAG             = LOW; /*Used in "Opcode_Polling" and "Push_Buttons" tab to poll the Push button press*/
bool lastRun_FLAG         = LOW;
bool runState;

bool pause_FLAG           = LOW;
bool lastPause_FLAG       = LOW;
bool pauseState;

bool stop_FLAG            = LOW;
bool lastStop_FLAG        = LOW;
bool stopState;

bool buzzeroff_FLAG       = LOW;
bool lastBuzzeroff_FLAG   = LOW;
bool buzzeroffState;


bool doorlock_FLAG       = LOW;
bool lastdoorlock_FLAG   = LOW;
bool doorlockState;

bool PressureSwitch_FLAG = LOW;
bool Pressure_State = LOW;
bool lastPressure_Val = LOW;


bool EstopState;
bool EstopFlag            = HIGH;
bool lastEStop_FLAG       = LOW;

bool gMotor = LOW;                                  /*Used in "Opcode_Polling" and "Guide" tab. Gets set when guide needs to rotate*/
bool rMotor = LOW;                                  /*Used in "Opcode_Polling" and "Sag_logic" tab. Gets set when reeler needs to rotate*/
bool rMotor1 = LOW;                                 /*Used in "Opcode_Polling" and "Sag_logic" tab. Gets set when reeler needs to rotate*/
bool rMotor2 = LOW;                                 /*Used in "Opcode_Polling" and "Sag_logic" tab. Gets set when reeler needs to rotate*/
int  TpMtr = 1;                                     /*Used in "Opcode_Polling" and "Sag_logic" tab. Gets set when reeler needs to rotate*/
int  BmMtr = 1;                                     /*Used in "Opcode_Polling" and "Sag_logic" tab. Gets set when reeler needs to rotate*/
bool rSpeed1 = LOW;                                 /*Used in "Opcode_Polling" and "Sag_logic" tab. Gets set when reeler needs to rotate*/
bool rSpeed2 = LOW;                                 /*Used in "Opcode_Polling" and "Sag_logic" tab. Gets set when reeler needs to rotate*/
bool reelerMotorFlag1 = LOW, reelerMotorFlag2 = LOW;
bool prevTrig1, prevTrig2;
volatile unsigned long trigMillis1, trigMillis2;
unsigned long trigDebounceDelay1 = 4000, trigDebounceDelay2 = 2000;



//POLLING BUFFERS
volatile unsigned long pbLastMillis;                /*For Push button*/
volatile unsigned long estopMillis;                 /*For Push button*/
volatile unsigned long estopLastMillis;             /*For Push button*/
volatile unsigned long Inspec_last_sec;             /*Run flag is set high , only after motor initialization*/
int T_Gcounter = 0;
int B_Gcounter = 0;
unsigned int InitialAngle = 0;
double  NoOfTeeth = 0;

int saginc=1;
bool firstsag = HIGH;
char Buffer[10] = {'\0'};                           /*Buffer variable where the incoming Opcodes will be stored*/
int Array [70] = {'\0'};                            // Maximum no. of teeth


volatile bool gISRFlag = HIGH, TriggerAngleFlag = HIGH, TrigFlag = LOW, ReelerStepState = LOW;
bool ISRFlag = LOW, T_FirstCall = HIGH, B_FirstCall = HIGH, SecondCall = HIGH, ENC_FLAG_Top = LOW, ENC_FLAG_Bottom = LOW, reelerTeethCountFlag = LOW, SkipTriggerCountFlag = LOW;
unsigned long int PresentCounterValue = 0L, PreviousCounterValue = 0L;

volatile int pin;
int Steps;
int SetSpeed1 = 20000;
int SetSpeed2 = 20000;
int ActSpeed1;
int ActSpeed2;
float Multiplicationfactor=68.4;
//char Buffer[10] = {'\0'};                           /*Buffer variable where the incoming Opcodes will be stored*/

uint32_t previousticktp = 0;
uint32_t presentticktp = 0;
uint32_t debounce_delaytp = 30000;

uint32_t previoustickbt = 0;
uint32_t presenttickbt = 0;
uint32_t debounce_delaybt = 50000;
uint32_t Trig_Count = 0;
uint32_t D_Trig_Count = 0;
String S3;


uint32_t gspmdelay_Top = 0;
uint32_t gspmdelay_Bottom = 0;

//LS7366 enc(BOTTOM_ENCODER_SS);                          //Setting Object & assigning Chip Select Pin
//LS7366 enc();                                           //Setting Object & assigning Chip Select Pin
uint32_t MILLIS = 0;
uint32_t D_MILLIS = 0;

uint32_t Time = 0;

char buffer1[50];
char buffer2[50];
volatile bool insync=true; 

bool LightCameraSequenceFlag_0 = false;                //LCS_TOP_FLAG
bool LightCameraSequenceFlag_1 = false;
bool LightCameraSequenceFlag_2 = false;
bool LightCameraSequenceFlag_3 = false;
bool LightCameraSequenceFlag_4 = false;
bool LightCameraSequenceFlag_5 = false;
bool LightCameraSequenceFlag_6 = false;

bool Lightondelayflag =LOW;
bool Lightoffdelayflag =LOW;
bool Cameraondelayflag =LOW;
bool Cameraoffdelayflag =LOW; 

bool TSFlag =false;

volatile bool rejectionDoneISR = false;
volatile unsigned long lastISRTime = 0;

bool Rejectionlogic_Flag = false;
bool interruptAttached = false;

bool Relermotorflag = LOW;

 bool falsetrigger = true;
void setup() {
//INITIALISATION
  digitalWrite(TOP_CAMERA_1,                  HIGH);
  digitalWrite(TOP_CAMERA_2,                  HIGH);
  digitalWrite(TOP_CAMERA_3,                  HIGH);
  digitalWrite(BOTTOM_CAMERA_4,               HIGH);
  digitalWrite(BOTTOM_CAMERA_5,               HIGH);
  digitalWrite(BOTTOM_CAMERA_6,               HIGH);
  digitalWrite(TOP_LIGHT_1,                   HIGH);
  digitalWrite(TOP_LIGHT_2,                   HIGH);
  digitalWrite(TOP_LIGHT_3,                   HIGH);
  digitalWrite(BOTTOM_LIGHT_4,                HIGH);
  digitalWrite(BOTTOM_LIGHT_5,                HIGH);
  digitalWrite(BOTTOM_LIGHT_6,                HIGH);
  digitalWrite(TL_YELLOW,                     LOW);
  digitalWrite(TL_GREEN,                      LOW);
  digitalWrite(BOTTOM_SOLENOID_VALVE, LOW);
  digitalWrite(TOP_MOTOR_SS,                  HIGH);
  digitalWrite(BOTTOM_MOTOR_SS,               HIGH);
  digitalWrite(TOP_ENCODER_SS,                HIGH);
  digitalWrite(BOTTOM_ENCODER_SS,             HIGH);
 
  
//INPUTS

  pinMode(TOP_CLOSE_LIMIT_SWITCH,            INPUT);
  pinMode(TOP_OPEN_LIMIT_SWITCH,             INPUT);
  pinMode(BOTTOM_CLOSE_LIMIT_SWITCH,         INPUT);
  pinMode(BOTTOM_OPEN_LIMIT_SWITCH,          INPUT);
  pinMode(TOP_SENSOR_TRIGGER_INPUT,          INPUT);
  pinMode(BOTTOM_SENSOR_TRIGGER_INPUT,       INPUT);
  pinMode(ESTOP_BUTTON,                      INPUT);
  pinMode(PAUSE_BUTTON,                      INPUT);
  pinMode(STOP_BUTTON,                       INPUT);
  pinMode(TOP_UPPER_SAG_SENSOR,              INPUT);
  pinMode(TOP_LOWER_SAG_SENSOR,              INPUT);
//  pinMode(TOP_EXIT_SENSOR,                   INPUT);
  pinMode(BOTTOM_UPPER_SAG_SENSOR,           INPUT);
  pinMode(BOTTOM_LOWER_SAG_SENSOR,           INPUT);
  pinMode(BOTTOM_EXIT_SAG_SENSOR,            INPUT);
  pinMode(TOP_ENCODER_INT,                   INPUT_PULLUP);
  pinMode(BOTTOM_ENCODER_INT,                INPUT_PULLUP);
  pinMode(pinCS, OUTPUT);

  //OUTPUTS

  pinMode(TOP_CAMERA_1,                     OUTPUT);
  pinMode(TOP_CAMERA_2,                     OUTPUT);
  pinMode(TOP_CAMERA_3,                     OUTPUT);
  pinMode(TOP_LIGHT_1,                      OUTPUT);
  pinMode(TOP_LIGHT_2,                      OUTPUT);
  pinMode(TOP_LIGHT_3,                      OUTPUT);
  pinMode(BOTTOM_CAMERA_4,                  OUTPUT);
  pinMode(BOTTOM_CAMERA_5,                  OUTPUT);
  pinMode(BOTTOM_CAMERA_6,                  OUTPUT);
  pinMode(BOTTOM_LIGHT_4,                   OUTPUT);
  pinMode(BOTTOM_LIGHT_5,                   OUTPUT);
  pinMode(BOTTOM_LIGHT_6,                   OUTPUT);
  pinMode(TL_YELLOW,                        OUTPUT);
  pinMode(TL_GREEN,                         OUTPUT);
  pinMode(TOP_SOLENOID_VALVE,               OUTPUT);
  pinMode(BOTTOM_SOLENOID_VALVE,            OUTPUT);
  pinMode(STAMPING_RELAY,                   OUTPUT);
  pinMode(TOP_ENCODER_SS,                   OUTPUT);
  pinMode(TOP_MOTOR_SS,                     OUTPUT);
  pinMode(BOTTOM_ENCODER_SS,                OUTPUT);
  pinMode(BOTTOM_MOTOR_SS,                  OUTPUT);

  
  i2cLOW(3, 3); //TL_RED
  i2cLOW(3, 2); //TL_Buzzer

  //commmunication
  SerialUSB.begin(115200);
  Serial.begin(115200);
  SerialUSB.setTimeout(100);
  SPI.begin();
  SPI.setBitOrder(MSBFIRST);
  SPI.setClockDivider(SPI_CLOCK_DIV8);
  i2cInit(1);
  i2cInit(2);
  i2cInit(3);
  i2cpinInput(1);
  i2cpinOutput(2);
  i2cpinOutput(3);
 /***************************For Sdcard based log***************************/
 if (SD.begin())
{
//SerialUSB.println("SD card is ready to use.");
digitalWrite(pinCS, HIGH);
} 
else
{
//SerialUSB.println("SD card initialization failed");
return;
} 

}

void loop()
{
  ISR_Executions();
  OpcodePolling();
  PushButtons(); 
  SagLogic();
  RejectionLogic();
  
//  LightCameraSequence_1();
//  delay(50);
//  LightCameraSequence_2();
//  delay(50);
//  LightCameraSequence_3();
//  delay(50);
//  LightCameraSequence_5();
//  delay(50);
//  LightCameraSequence_6();
//  delay(50);
//  LightCameraSequence_7();
//  delay(50);
}
