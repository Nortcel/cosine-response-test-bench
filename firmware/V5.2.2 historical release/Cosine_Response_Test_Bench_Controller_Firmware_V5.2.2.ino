
#include <dht.h>

// Firmware info
const char* FW_VERSION = "V5.2.2";
const char* BOARD_NAME = "Arduino Uno R3";
const char* BUILD_INFO = __DATE__ " " __TIME__;


dht DHT;

enum ModeState
{
  MODE_STANDBY,
  MODE_MEASURING,
  MODE_FREE,
  MODE_HOMING
};

const int StartPin = 2;
const int StopPin = 3;
const int FreePin = 4;
const int LeftPIRPin = 5;
const int RightPIRPin = 6;
const int LaserPin = 7;
const int DirCtrlPin = 8;
const int StepCtrlPin = 9;
const int DHTPin = 10;
const int EnablePin = 12;
const int UVSensorPin = A1;

const int MeasureSteps = 800;
const int MeasureSamples = 101;

unsigned int scanDelayUs = 9400;
unsigned int returnDelayUs = 6000;

ModeState mode = MODE_STANDBY;
bool stopRequested = false;
bool atNullpoint = false;
String commandBuffer = "";

const unsigned long DebounceMs = 40;
const unsigned long IgnoreStopAfterStartMs = 250;
const unsigned long AlignReportIntervalMs = 100;

bool startStableState = HIGH;
bool stopStableState = HIGH;
bool freeStableState = HIGH;

bool lastStartReading = HIGH;
bool lastStopReading = HIGH;
bool lastFreeReading = HIGH;

unsigned long startLastChangeMs = 0;
unsigned long stopLastChangeMs = 0;
unsigned long freeLastChangeMs = 0;

unsigned long measurementStartMs = 0;
unsigned long lastAlignReportMs = 0;
unsigned long lastSerialCharMs = 0;

// Forward declarations
void serviceSerial();
void processCommand(const String &command);
void goToNullpoint();
void runFreeMode();
void startMeasurement();
void printStatus(const char *message);
void printDHTReading();
void printVoltageSample(int sampleIndex, float angleDeg, float voltage);
void printSettings();
void turnLaserOnCommand();
void goToEndPosition();
void enableMotor();
void disableMotor();
void laserOn();
void laserOff();
void stepMotorOnce(unsigned int pulseDelayUs);
bool leftActive();
bool rightActive();
bool startPressedEvent();
bool stopPressedEvent();
bool freePressedEvent();
void sendFirmwareInfo();

bool leftActive()
{
  return digitalRead(LeftPIRPin) == HIGH;
}

bool rightActive()
{
  return digitalRead(RightPIRPin) == HIGH;
}

void laserOn()
{
  digitalWrite(LaserPin, HIGH);
}

void laserOff()
{
  digitalWrite(LaserPin, LOW);
}

void enableMotor()
{
  digitalWrite(EnablePin, LOW);
}

void disableMotor()
{
  digitalWrite(EnablePin, HIGH);
}

void stepMotorOnce(unsigned int pulseDelayUs)
{
  digitalWrite(StepCtrlPin, HIGH);
  delayMicroseconds(pulseDelayUs);
  digitalWrite(StepCtrlPin, LOW);
  delayMicroseconds(pulseDelayUs);
}

void printStatus(const char *message)
{
  Serial.println(message);
}

void printDHTReading()
{
  DHT.read11(DHTPin);
  Serial.print("Humidity=");
  Serial.println(DHT.humidity, 2);
  Serial.print("Temperature=");
  Serial.println(DHT.temperature, 2);
}

void printVoltageSample(int sampleIndex, float angleDeg, float voltage)
{
  Serial.print("Sample=");
  Serial.println(sampleIndex + 1);
  Serial.print("Angle=");
  Serial.println(angleDeg, 4);
  Serial.print("Voltage=");
  Serial.println(voltage, 6);
}

void printSettings()
{
  Serial.print("Config: SCAN_US=");
  Serial.println(scanDelayUs);
  Serial.print("RETURN_US=");
  Serial.println(returnDelayUs);
}

bool readDebouncedPress(int pin, bool &stableState, bool &lastReading, unsigned long &lastChangeMs)
{
  bool reading = digitalRead(pin);
  bool event = false;

  if (reading != lastReading)
  {
    lastChangeMs = millis();
    lastReading = reading;
  }

  if ((millis() - lastChangeMs) > DebounceMs)
  {
    if (reading != stableState)
    {
      stableState = reading;
      if (stableState == LOW)
      {
        event = true;
      }
    }
  }

  return event;
}

bool startPressedEvent()
{
  return readDebouncedPress(StartPin, startStableState, lastStartReading, startLastChangeMs);
}

bool stopPressedEvent()
{
  return readDebouncedPress(StopPin, stopStableState, lastStopReading, stopLastChangeMs);
}

bool freePressedEvent()
{
  return readDebouncedPress(FreePin, freeStableState, lastFreeReading, freeLastChangeMs);
}

void goToNullpoint()
{
  mode = MODE_HOMING;
  printStatus("Returning to nullpoint");
  laserOff();
  enableMotor();
  digitalWrite(DirCtrlPin, HIGH);

  unsigned long startedMs = millis();

  while (!leftActive())
  {
    serviceSerial();

    if (millis() - startedMs > 15000UL)
    {
      printStatus("Nullpoint timeout");
      break;
    }

    stepMotorOnce(returnDelayUs);
  }

  atNullpoint = leftActive();
  mode = MODE_STANDBY;
  printStatus(atNullpoint ? "Nullpoint reached" : "Nullpoint not confirmed");
}

void runFreeMode()
{
  mode = MODE_FREE;
  stopRequested = false;

  printStatus("Free mode active");
  disableMotor();
  laserOn();
  lastAlignReportMs = 0;

  while (true)
  {
    serviceSerial();

    unsigned long now = millis();
    if (now - lastAlignReportMs >= AlignReportIntervalMs)
    {
      lastAlignReportMs = now;
      int raw = analogRead(UVSensorPin);
      float voltage = raw * (5.0 / 1023.0);
      Serial.print("AlignVoltage=");
      Serial.println(voltage, 6);
    }

    if (stopPressedEvent() || stopRequested)
    {
      printStatus("Free mode stopped");
      enableMotor();
      laserOff();
      goToNullpoint();
      return;
    }
  }
}

void startMeasurement()
{
  mode = MODE_MEASURING;
  atNullpoint = false;
  stopRequested = false;

  printStatus("Measurement started");
  printDHTReading();
  printSettings();

  laserOn();
  delay(1000);

  enableMotor();
  digitalWrite(DirCtrlPin, LOW);

  const int measurementIntervals = MeasureSamples - 1;
  const int stepsPerInterval = MeasureSteps / measurementIntervals;

  if (measurementIntervals <= 0 || (MeasureSteps % measurementIntervals != 0))
  {
    printStatus("Invalid sampling configuration");
    laserOff();
    goToNullpoint();
    return;
  }

  measurementStartMs = millis();

  int sampleCount = 0;
  int raw0 = analogRead(UVSensorPin);
  float voltage0 = raw0 * (5.0 / 1023.0);
  printVoltageSample(sampleCount, -90.0, voltage0);
  sampleCount++;

  for (int i = 0; i < MeasureSteps; i++)
  {
    serviceSerial();

    if ((millis() - measurementStartMs) > IgnoreStopAfterStartMs)
    {
      if (stopPressedEvent() || stopRequested)
      {
        printStatus("Measurement stopped");
        laserOff();
        goToNullpoint();
        return;
      }
    }

    if (rightActive())
    {
      printStatus("Right end sensor triggered");
      laserOff();
      goToNullpoint();
      return;
    }

    stepMotorOnce(scanDelayUs);

    if (((i + 1) % stepsPerInterval) == 0 && sampleCount < MeasureSamples)
    {
      int raw = analogRead(UVSensorPin);
      float voltage = raw * (5.0 / 1023.0);
      float angleDeg = -90.0 + (180.0 * sampleCount / (MeasureSamples - 1));
      printVoltageSample(sampleCount, angleDeg, voltage);
      sampleCount++;
    }
  }

  printStatus("Measurement complete");
  laserOff();
  delay(500);
  goToNullpoint();
}


void turnLaserOnCommand()
{
  if (mode != MODE_STANDBY)
  {
    printStatus("Busy");
    return;
  }

  enableMotor();
  laserOn();
  printStatus("Laser on");
}

void goToEndPosition()
{
  if (mode != MODE_STANDBY)
  {
    printStatus("Busy");
    return;
  }

  mode = MODE_HOMING;
  stopRequested = false;
  printStatus("Moving to end position");
  laserOff();
  enableMotor();
  digitalWrite(DirCtrlPin, LOW);

  unsigned long startedMs = millis();

  while (!rightActive())
  {
    serviceSerial();

    if (stopRequested || stopPressedEvent())
    {
      printStatus("Move to end stopped");
      mode = MODE_STANDBY;
      laserOff();
      return;
    }

    if (millis() - startedMs > 15000UL)
    {
      printStatus("End position timeout");
      mode = MODE_STANDBY;
      laserOff();
      return;
    }

    stepMotorOnce(returnDelayUs);
  }

  mode = MODE_STANDBY;
  atNullpoint = false;
  printStatus("End position reached");
}


void processCommand(const String &command)
{
  String cmd = command;
  cmd.trim();
  cmd.toUpperCase();

  if (cmd.indexOf("STOP") >= 0)
  {
    stopRequested = true;
    laserOff();
    printStatus("Command accepted: STOP");
  }
  else if (cmd == "VERSION" || cmd == "INFO")
  {
    printStatus("Command accepted: VERSION");
    sendFirmwareInfo();
    printSettings();
  }
  else if (cmd == "START")
  {
    if (mode == MODE_STANDBY && atNullpoint)
    {
      startMeasurement();
    }
    else if (mode == MODE_STANDBY && !atNullpoint)
    {
      printStatus("Already at nullpoint");
      goToNullpoint();
    }
    else
    {
      printStatus("Busy");
    }
  }
  else if (cmd == "FREE")
  {
    if (mode == MODE_STANDBY)
    {
      printStatus("Command accepted: FREE");
      runFreeMode();
    }
    else
    {
      printStatus("Busy");
    }
  }
  else if (cmd == "HOME")
  {
    printStatus("Command accepted: HOME");
    goToNullpoint();
  }
  else if (cmd == "LASER ON" || cmd == "LASERON")
  {
    printStatus("Command accepted: LASER ON");
    turnLaserOnCommand();
  }
  else if (cmd == "LASER OFF" || cmd == "LASEROFF")
  {
    printStatus("Command accepted: LASER OFF");
    laserOff();
    mode = MODE_STANDBY;
  }
  else if (cmd == "GO END" || cmd == "GOEND")
  {
    printStatus("Command accepted: GO END");
    goToEndPosition();
  }
  else if (cmd == "STATUS")
  {
    if (mode == MODE_STANDBY)
      printStatus("Mode=STANDBY");
    else if (mode == MODE_MEASURING)
      printStatus("Mode=MEASURING");
    else if (mode == MODE_FREE)
      printStatus("Mode=FREE");
    else
      printStatus("Mode=HOMING");

    printStatus(atNullpoint ? "AtNullpoint=1" : "AtNullpoint=0");
    printSettings();
  }
  else if (cmd.startsWith("SET SCAN_US "))
  {
    unsigned long value = cmd.substring(12).toInt();
    if (value >= 150 && value <= 20000)
    {
      scanDelayUs = (unsigned int)value;
      printStatus("Command accepted: SET SCAN_US");
      printSettings();
    }
    else
    {
      printStatus("Invalid SCAN_US range");
    }
  }
  else if (cmd.startsWith("SET RETURN_US "))
  {
    unsigned long value = cmd.substring(14).toInt();
    if (value >= 100 && value <= 20000)
    {
      returnDelayUs = (unsigned int)value;
      printStatus("Command accepted: SET RETURN_US");
      printSettings();
    }
    else
    {
      printStatus("Invalid RETURN_US range");
    }
  }
  else if (cmd == "GET SETTINGS")
  {
    printStatus("Command accepted: GET SETTINGS");
    printSettings();
  }
  else
  {
    printStatus("Unknown command");
  }
}

void serviceSerial()
{
  while (Serial.available() > 0)
  {
    char c = (char)Serial.read();
    unsigned long now = millis();

    if (now - lastSerialCharMs > 100)
    {
      commandBuffer = "";
    }
    lastSerialCharMs = now;

    if (c == '\r')
    {
      continue;
    }

    if (c == '\n')
    {
      if (commandBuffer.length() > 0)
      {
        processCommand(commandBuffer);
        commandBuffer = "";
      }
    }
    else
    {
      commandBuffer += c;
      if (commandBuffer.length() > 96)
      {
        commandBuffer = "";
      }
    }
  }
}

void setup()
{
  pinMode(StartPin, INPUT_PULLUP);
  pinMode(StopPin, INPUT_PULLUP);
  pinMode(FreePin, INPUT_PULLUP);
  pinMode(LeftPIRPin, INPUT);
  pinMode(RightPIRPin, INPUT);
  pinMode(LaserPin, OUTPUT);
  pinMode(DirCtrlPin, OUTPUT);
  pinMode(StepCtrlPin, OUTPUT);
  pinMode(DHTPin, INPUT);
  pinMode(EnablePin, OUTPUT);

  digitalWrite(DirCtrlPin, LOW);
  digitalWrite(StepCtrlPin, LOW);
  disableMotor();
  laserOff();

  Serial.begin(9600);
  delay(300);

  startStableState = digitalRead(StartPin);
  stopStableState = digitalRead(StopPin);
  freeStableState = digitalRead(FreePin);

  lastStartReading = startStableState;
  lastStopReading = stopStableState;
  lastFreeReading = freeStableState;

  atNullpoint = leftActive();
  if (atNullpoint)
  {
    printStatus("Already at nullpoint");
  }
  else
  {
    goToNullpoint();
  }
}

void loop()
{
  serviceSerial();

  if (mode == MODE_STANDBY)
  {
    if (stopPressedEvent())
    {
      printStatus("Stop ignored in standby");
    }

    if (startPressedEvent())
    {
      startMeasurement();
      return;
    }

    if (freePressedEvent())
    {
      runFreeMode();
      return;
    }
  }
}

void sendFirmwareInfo() {
  Serial.print("FIRMWARE=");
  Serial.println(FW_VERSION);
  Serial.print("BOARD=");
  Serial.println(BOARD_NAME);
  Serial.print("BUILD=");
  Serial.println(BUILD_INFO);
}
