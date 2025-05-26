int xposPin = A0; //X軸Pin腳
int yposPin = A1; //Y軸Pin腳
int Xpos = 0; //X軸數值0~1023
int Ypos = 1; //Y軸數值0~1023
int buttonPin = 7; //搖桿上的按鈕Z軸
int buttonPress =0; // Z軸狀態

//int LEDPin = 9;  //設定X軸要控制的燈
//int LEDPin = 10; //設定Y軸要控制的燈


void setup() {
  // put your setup code here, to run once:
  // 設置上拉電阻
  pinMode(buttonPin,INPUT_PULLUP);
  // 未按下的時候電壓為高電壓
  digitalWrite(buttonPin,HIGH);
  Serial.begin(9600);
  //pinMode(LEDPin,OUTPUT); //設定LED燈為輸出裝置
  //pinMode(LEDPin2,OUTPUT);
}

void loop() {
  // put your main code here, to run repeatedly:
  // 偵測Z軸狀態
  buttonPress = digitalRead(buttonPin);
//  if(buttonPress == LOW){
//    Serial.println("Button Pressed");
//  }
  // 讀取X軸的值
  Xpos = analogRead(xposPin);
  // 讀取Y軸的值
  Ypos = analogRead(yposPin);
  // 將X軸轉換成-100到100
   int Xpct;
  if(Xpos<528){
    Xpct = map(Xpos, 0,527,-100,0);
  }
  else{
    Xpct = map(Xpos, 528,1023,0,100);
  }
  
  // 將Y軸轉換成-100到100
  int Ypct = map(Ypos,0,1023,100,-100);
  // 顯示出搖桿所有數值
  Serial.print("X:");
  Serial.print(Xpct);
  Serial.print(",Y:");
  Serial.print(Ypct);
  Serial.print(",Z:");
  Serial.println(buttonPress);

  ////這邊用搖桿控制LED燈亮暗
  //int LEDLight = map(Xpos,0,1023,0,255);
  //int LEDLight2 = map(Xpos,0,1023,0,255);
  //analogWrite(LEDPin,LEDLight);
  //analogWrite(LEDPin2,LEDLight2);

  delay(10);
}
