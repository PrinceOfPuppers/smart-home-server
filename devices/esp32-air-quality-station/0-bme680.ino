#include "bsec.h"
#include "bme680_type.h"

Bsec iaqSensor;
String output;

int checkIaqSensorStatus(void)
{
  if (iaqSensor.bsecStatus != BSEC_OK) {
    if (iaqSensor.bsecStatus < BSEC_OK) {
      debugln("BSEC error code : " + String(iaqSensor.bsecStatus));
      return AQS_STATUS_ERR;
    } else {
      debugln("BSEC warning code : " + String(iaqSensor.bsecStatus));
      return AQS_STATUS_WARN;
    }
  }

  if (iaqSensor.bme68xStatus != BME68X_OK) {
    if (iaqSensor.bme68xStatus < BME68X_OK) {
      debugln("BME68X error code : " + String(iaqSensor.bme68xStatus));
      return AQS_STATUS_ERR;
    } else {
      debugln("BME68X warning code : " + String(iaqSensor.bme68xStatus));
      return AQS_STATUS_WARN;
    }
  }

  return AQS_STATUS_OK;
}



// Entry point for the example
int setup_bme680(void)
{
  /* Initializes the Serial communication */
  Serial.begin(115200);
  delay(1000);
  iaqSensor.begin(BME68X_I2C_ADDR_HIGH, Wire);

  int status;
  status = checkIaqSensorStatus();
  if(status != AQS_STATUS_OK){
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
  if(status != AQS_STATUS_OK){
      return status;
  }

  return AQS_STATUS_OK;
}



int update_bme(BMEData *out){
    if (iaqSensor.run()) { // If new data is available
        out->iaq = iaqSensor.iaq;
        out->pressure = iaqSensor.pressure;
        out->temperature = iaqSensor.temperature;
        out->humidity = iaqSensor.humidity;
        out->co2Equivalent = iaqSensor.co2Equivalent;
        out->breathVocEquivalent = iaqSensor.breathVocEquivalent;
        debugln("BME Data:");
        debugln("IQA: " + String(out->iaq));
        debugln("Pressure: " + String(out->iaq) + " Pa");
        debugln("Temp: " + String(out->temperature) + " *C");
        debugln("Humid: " + String(out->humidity) + " %");
        debugln("Co2 eq: " + String(out->humidity) + " ppm");
        debugln("VOC: " + String(out->breathVocEquivalent) + " ppm");
        return AQS_STATUS_OK;
    } else {
        return checkIaqSensorStatus();
    }
    debugln("BME no Update");
    return AQS_STATUS_NO_UPDATE;
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
