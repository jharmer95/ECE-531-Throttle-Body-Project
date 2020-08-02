/*---------------------------------------------------------------------------------------------
 *  Copyright (c) Jackson Harmer. All rights reserved.
 *  Licensed under the MIT License. See LICENSE.md in the project root for license information.
 *--------------------------------------------------------------------------------------------*/

#pragma once

namespace calibration
{
    constexpr int SERVO_MIN_POSITION = 16;
    constexpr int SERVO_MAX_POSITION = 118;
    constexpr unsigned long LOOP_DELAY = 100UL;
    constexpr unsigned long SERVO_READ_DELAY = 15UL;
    constexpr float SATURATION_CUTOFF = 20.00f;
    constexpr float SATURATION_STEEPNESS = 10.00f;
} // namespace calibration
