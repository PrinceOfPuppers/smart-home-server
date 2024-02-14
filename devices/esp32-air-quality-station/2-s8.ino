#include "s8_uart.h"

S8_UART *sensor_S8;
S8_sensor sensor;

int diagnose_s8(){
    // Check the health of the sensor
    debugln("Checking the health of s8...");
    sensor.meter_status = sensor_S8->get_meter_status();

    if (sensor.meter_status & S8_MASK_METER_ANY_ERROR) {
        debugln("One or more errors detected!");

        if (sensor.meter_status & S8_MASK_METER_FATAL_ERROR) {
            debugln("Fatal error in sensor!");
        }

        if (sensor.meter_status & S8_MASK_METER_OFFSET_REGULATION_ERROR) {
            debugln("Offset regulation error in sensor!");
        }

        if (sensor.meter_status & S8_MASK_METER_ALGORITHM_ERROR) {
            debugln("Algorithm error in sensor!");
        }

        if (sensor.meter_status & S8_MASK_METER_OUTPUT_ERROR) {
            debugln("Output error in sensor!");
        }

        if (sensor.meter_status & S8_MASK_METER_SELF_DIAG_ERROR) {
            debugln("Self diagnostics error in sensor!");
        }

        if (sensor.meter_status & S8_MASK_METER_OUT_OF_RANGE) {
            debugln("Out of range in sensor!");
        }

        if (sensor.meter_status & S8_MASK_METER_MEMORY_ERROR) {
            debugln("Memory error in sensor!");
        }
        return AQS_STATUS_ERR;
    }

    debugln("The sensor is OK.");
    return AQS_STATUS_OK;
}


int setup_s8() {
  debugln(">>> Setting Up SenseAir S8 <<<");

  // Initialize S8 sensor
  Serial2.begin(S8_BAUDRATE);
  sensor_S8 = new S8_UART(Serial2);

  // Check if S8 is available
  sensor_S8->get_firmware_version(sensor.firm_version);
  int len = strlen(sensor.firm_version);
  if (len == 0) {
      debugln("SenseAir S8 CO2 sensor not found!");
      return AQS_STATUS_ERR;
  }

  // Show basic S8 sensor info
  debug("Firmware version: "); debugln(sensor.firm_version);
  sensor.sensor_id = sensor_S8->get_sensor_ID();
  debug("Sensor ID: "); debug(sensor.sensor_id); debugln("");

  // Disabling ABC
  debugln("Disabling S8 ABC");
  sensor_S8->set_ABC_period(0);
  delay(1000);
  sensor.abc_period = sensor_S8->get_ABC_period();
  if (sensor.abc_period != 0) {
    debug("Error Disabling S8 ABC Period: ");
    debugln(sensor.abc_period);
    return AQS_STATUS_ERR;
  }
  debugln("S8 ABC Disabled Succesfully");

  // check health
  int status = diagnose_s8();
  if(status != AQS_STATUS_OK){
      return status;
  }
  debugln("S8 Setup Complete!");
  return AQS_STATUS_OK;
}

int calibrate_s8(){
    uint32_t elapsed = 0;
    uint32_t timeout = 30;

    debug("Starting Manual Calibration of S8... (Timeout: ");
    debug(timeout);
    debugln(" seconds)");

    if (!sensor_S8->manual_calibration()) {
        debugln("Error setting manual calibration!");
        return AQS_STATUS_ERR;
    }


    while(1){
        delay(2000);
        elapsed += 2;

        sensor.ack = sensor_S8->get_acknowledgement();
        if (sensor.ack & S8_MASK_CO2_BACKGROUND_CALIBRATION) {
            debug("Manual calibration is finished! (Elapsed: ");
            debug(elapsed);
            debugln(" seconds)");

            return AQS_STATUS_OK;
        }
        if(elapsed >= timeout){
            return AQS_STATUS_ERR;
        }
    }


    return AQS_STATUS_OK;
}

int update_s8(uint16_t *co2_out){
    sensor.co2 = sensor_S8->get_co2();
    debugln("S8 Data:");
    debug("  CO2 value: ");
    debug(sensor.co2);
    debugln(" ppm");

    *co2_out = sensor.co2;
    return AQS_STATUS_OK;
}

