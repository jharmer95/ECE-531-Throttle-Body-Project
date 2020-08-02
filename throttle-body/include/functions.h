/*---------------------------------------------------------------------------------------------
 *  Copyright (c) Jackson Harmer. All rights reserved.
 *  Licensed under the MIT License. See LICENSE.md in the project root for license information.
 *--------------------------------------------------------------------------------------------*/

#pragma once

float Saturate(float val);
void UpdateServo();
int GetServoPosition();
void SetServoPosition(int pos);
void receiveEvent(int howMany);
void requestEvent();
