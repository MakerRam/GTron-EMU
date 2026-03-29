/**********************SPI BASED DATA LOG*****************************/
//UNDER DEVELOPMENT

void data(const char *str){
   digitalWrite(pinCS, LOW);
   myFile = SD.open("test.txt", FILE_WRITE);
  if (myFile) {
    Debugstate && myFile.println(str);
    myFile.close(); 
  }
  else {
    Debugstate && SerialUSB.println("error opening test.txt while write");
  }
  /*************to read data**************/
myFile = SD.open("test.txt");
  
   if (myFile) {
        Debugstate && SerialUSB.println("Read:");

   while (myFile.available()) 
    {
    Debugstate && SerialUSB.write(myFile.read());
     }
      SD.remove("test.txt");
    myFile.close();
    digitalWrite(pinCS, HIGH);
    }
  else {
    Debugstate && SerialUSB.println("error opening test.txt while read");
    }
  
  }
