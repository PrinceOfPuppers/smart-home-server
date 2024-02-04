#include "bsec.h"

Bsec iaqSensor;
String output;

typedef struct BME{
    float iaq;
    float pressure;
    float temperature;
    float humidity;
    float co2Equivalent;
    float breathVocEquivalent;
} BME;


int checkIaqSensorStatus(void)
{
  if (iaqSensor.bsecStatus != BSEC_OK) {
    if (iaqSensor.bsecStatus < BSEC_OK) {
      debugln("BSEC error code : " + String(iaqSensor.bsecStatus));
      return STATUS_ERR;
    } else {
      debugln("BSEC warning code : " + String(iaqSensor.bsecStatus));
      return STATUS_WARN;
    }
  }

  if (iaqSensor.bme68xStatus != BME68X_OK) {
    if (iaqSensor.bme68xStatus < BME68X_OK) {
      debugln("BME68X error code : " + String(iaqSensor.bme68xStatus));
      return STATUS_ERR;
    } else {
      debugln("BME68X warning code : " + String(iaqSensor.bme68xStatus));
      return STATUS_WARN;
    }
  }

  return STATUS_OK;
}



// Entry point for the example
int setup_bme680(void)
{
  /* Initializes the Serial communication */
  Serial.begin(115200);
  delay(1000);
  pinMode(LED_BUILTIN, OUTPUT);
  iaqSensor.begin(BME68X_I2C_ADDR_HIGH, Wire);

  int status;
  status = checkIaqSensorStatus();
  if(status != STATUS_OK){
      return status;
  }

  bsec_virtual_sensor_t sensorList[7] = {
    BSEC_OUTPUT_IAQ,
    BSEC_OUTPUT_CO2_EQUIVALENT,
    BSEC_OUTPUT_BREATH_VOC_EQUIVALENT,
    BSEC_OUTPUT_STABILIZATION_STATUS,
    BSEC_OUTPUT_RUN_IN_STATUS,
    BSEC_OUTPUT_SENSOR_HEAT_COMPENSATED_TEMPERATURE,
    BSEC_OUTPUT_SENSOR_HEAT_COMPENSATED_HUMIDITY,
  };

  iaqSensor.updateSubscription(sensorList, 7, BSEC_SAMPLE_RATE_LP);
  status = checkIaqSensorStatus();
  if(status != STATUS_OK){
      return status;
  }

  return STATUS_OK;
}



int update_bme(BME *out){
    if (iaqSensor.run()) { // If new data is available
        bme->iqa = iaqSensor.iqa;
        bme->pressure = iaqSensor.pressure;
        bme->temperature = iaqSensor.temperature;
        bme->humidity = iaqSensor.humidity;
        bme->co2Equivalent = iaqSensor.co2Equivalent;
        bme->breathVocEquivalent = iaqSensor.breathVocEquivalent;
        debugln("BME Data:");
        debugln("IQA: " + String(bme->iqa));
        debugln("Pressure: " + String(bme->iqa) + " Pa");
        debugln("Temp: " + String(bme->temperature) + " *C");
        debugln("Humid: " + String(bme->humidity) + " %");
        debugln("Co2 eq: " + String(bme->humidity) + " ppm");
        debugln("VOC: " + String(bme->breathVocEquivalent) + " ppm");
        return STATUS_OK;
    } else {
        return checkIaqSensorStatus();
    }
    debugln("BME no Update")
    return STATUS_NO_UPDATE;
}

/*
void print_bme680(void)
{
  unsigned long time_trigger = millis();
  if (iaqSensor.run()) { // If new data is available
    digitalWrite(LED_BUILTIN, LOW);
    output = String(time_trigger);
    output += ", " + String(iaqSensor.iaq);
    output += ", " + String(iaqSensor.iaqAccuracy);
    output += ", " + String(iaqSensor.staticIaq);
    output += ", " + String(iaqSensor.co2Equivalent);
    output += ", " + String(iaqSensor.breathVocEquivalent);
    output += ", " + String(iaqSensor.rawTemperature);
    output += ", " + String(iaqSensor.pressure);
    output += ", " + String(iaqSensor.rawHumidity);
    output += ", " + String(iaqSensor.gasResistance);
    output += ", " + String(iaqSensor.stabStatus);
    output += ", " + String(iaqSensor.runInStatus);
    output += ", " + String(iaqSensor.temperature);
    output += ", " + String(iaqSensor.humidity);
    output += ", " + String(iaqSensor.gasPercentage);
    Serial.println(output);
    digitalWrite(LED_BUILTIN, HIGH);
  } else {
    checkIaqSensorStatus();
  }
}

*/
