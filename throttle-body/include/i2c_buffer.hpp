/*---------------------------------------------------------------------------------------------
 *  Copyright (c) 2020 Jackson Harmer. All rights reserved.
 *  Licensed under the MIT License. See LICENSE.md in the project root for license information.
 *--------------------------------------------------------------------------------------------*/

#pragma once

#include <stdint.h>
#include <string.h>

union param_t
{
    float f;
    int32_t i{};
    uint32_t u;
};

union params_t
{
    param_t p[7]{};
    char str[28];
};

enum class command : int8_t
{
    // Values between -127 and 0 are reserved for error codes
    Error_Generic = -1, // Indicates a non-specific error occurred
    Error_None = 0,     // Indicate no error on return

    // Value between 1 and 128 are reserved for function calls
    GetServoPosition = 1,
    SetServoPosition = 2
};

struct i2c_buffer
{
    command cmd;
    params_t params;

    void clear_error()
    {
        cmd = command::Error_None;
        memset(params.str, '\0', 28);
    }

    void set_error(command error_code, const char* error_mesg)
    {
        cmd = error_code;
        memset(params.str, '\0', 28);
        strncpy(params.str, error_mesg, 27);
    }
};

static_assert(sizeof(i2c_buffer) <= 32UL, "Buffer size must be less than 32 bytes");
