#ifndef BME680_TYPE_H_
#define BME680_TYPE_H_

typedef struct BMEData{
    float iaq;
    float pressure;
    float temperature;
    float humidity;
    float co2Equivalent;
    float breathVocEquivalent;
} BMEData;

#endif
