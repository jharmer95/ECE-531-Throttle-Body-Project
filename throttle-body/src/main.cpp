/*---------------------------------------------------------------------------------------------
 *  Copyright (c) Jackson Harmer. All rights reserved.
 *  Licensed under the MIT License. See LICENSE.md in the project root for license information.
 *--------------------------------------------------------------------------------------------*/

#include "functions.h"
#include "i2c_buffer.hpp"
#include "calibrations.hpp"

#include <Arduino.h>
#include <Servo.h>
#include <Wire.h>

#include <stdint.h>

#ifdef _DEBUG
#   define PRINT(...) Serial.print(__VA_ARGS__)
#   define PRINTLN(...) Serial.println(__VA_ARGS__)
#else
#   define PRINT(...)
#   define PRINTLN(...)
#endif

static_assert(LOW == 0x0, "Expecting LOW to be 0");

constexpr int SERVO_PWM_PIN = 3;
constexpr unsigned long BAUD_RATE = 9600UL;
constexpr int I2C_ADDRESS = 8;

i2c_buffer g_buf;
volatile int g_servo_position = 45;
Servo g_servo;

void setup()
{
    Wire.begin(I2C_ADDRESS);
    Wire.onReceive(receiveEvent);
    Wire.onRequest(requestEvent);
    g_servo.attach(SERVO_PWM_PIN);
    Serial.begin(BAUD_RATE);
    PRINTLN("DEBUG Enabled!\n");
}

void loop()
{
    delay(calibration::LOOP_DELAY);
    UpdateServo();
}

float Saturate(float val)
{
    if (val < -1.00f * calibration::SATURATION_CUTOFF)
    {
        return -1.00f;
    }

    if (val > calibration::SATURATION_CUTOFF)
    {
        return 1.00f;
    }

    return atan(calibration::SATURATION_STEEPNESS * val) * (2.00f / PI);
}

void UpdateServo()
{
    g_servo.write(g_servo_position);
    delay(calibration::SERVO_READ_DELAY);
}

int GetServoPosition()
{
    g_buf.clear_error();
    return g_servo_position;
}

void SetServoPosition(int pos)
{
    g_servo_position = map(pos, 0, 90, calibration::SERVO_MIN_POSITION, calibration::SERVO_MAX_POSITION);
    PRINT("Setting servo to ");
    PRINTLN(g_servo_position);
    g_buf.clear_error();
}

void receiveEvent(int howMany)
{
    PRINT("Received call, size: ");
    PRINTLN(howMany, DEC);

    while (Wire.available())
    {
        memset(&g_buf, 0, sizeof(g_buf));

        Wire.readBytes(reinterpret_cast<uint8_t*>(&g_buf), sizeof(g_buf));

        switch (g_buf.cmd)
        {
            case command::GetServoPosition:
                g_buf.params.p[0].i = GetServoPosition();
                break;

            case command::SetServoPosition:
                SetServoPosition(g_buf.params.p[0].i);
                break;

            default:
                break;
        }
    }
}

void requestEvent()
{
    Wire.write(reinterpret_cast<uint8_t*>(&g_buf), sizeof(g_buf));
}
