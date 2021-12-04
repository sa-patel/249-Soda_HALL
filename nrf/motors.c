#include "motors.h"
#include "display.h"
#include "buckler.h"
#include "kobukiActuator.h"
#include "kobukiSensorTypes.h"
#include "kobukiSensorPoll.h"
#include "kobukiUtilities.h"
/*
#include "app_error.h"
#include "nrf.h"
#include "nrf_delay.h"
#include "nrfx_gpiote.h"
#include "nrf_gpio.h"
#include "nrf_log.h"
#include "nrf_log_ctrl.h"
#include "nrf_log_default_backends.h"
#include "nrf_pwr_mgmt.h"
#include "nrf_serial.h"
*/

// Positional and heading error
volatile float g_pos_error = 0;
volatile float g_head_error = 0;

// Motor speed constants
const int BASE_SPEED = 100;
const int MAX_SPEED = 150;

// PID constants
#define PERIOD (0.25) // Expected time between iterations
const float kp_pos = 10;
const float kd_pos = 1 / PERIOD;
const float kdd_pos = 0; // Not implemented
const float kp_head = 1;
const float kd_head = 1 / PERIOD;
const float kp_dist = 1;

void initKobuki(void) {
  kobukiInit();

  //NRF_LOG_INIT(NULL);
  //NRF_LOG_DEFAULT_BACKENDS_INIT();

  KobukiSensors_t initial_sensors;
  
  kobukiSensorPoll(&initial_sensors);
}

// Clamp a value between -max and max.
int clamp(int value, int max) {
    if (value > max) {
        return max;
    }
    if (value < -max) {
        return -max;
    }
    return value;
}

// Drive the kobuki motors
void drive(int left, int right) {
    int left_encoder = clamp(left, MAX_SPEED);
    int right_encoder = clamp(right, MAX_SPEED);
    printf("getting drive: %d, %d \n", left_encoder, right_encoder);
    kobukiDriveDirect(left_encoder, right_encoder);
}

// Control the motors 
void motors_drive_correction(float pos_error, float head_error, float remaining_dist) {
    // Local variables for previous error.
    static float prev_pos_error = 0;
    static float prev_head_error = 0;

    // Calculate the correction terms.
    float delta_pos_error = pos_error - prev_pos_error;
    float delta_head_error = head_error - prev_head_error;
    int turn_speed = (int)(kp_pos * pos_error + kd_pos * delta_pos_error 
                     + kp_head * head_error + kd_head * delta_head_error);
    int forward_speed = clamp(remaining_dist * kp_dist, BASE_SPEED);

    // Drive the motors.
    drive(forward_speed - turn_speed, forward_speed + turn_speed);

    // Update prev variables.
    prev_pos_error = pos_error;
    prev_head_error = head_error;
}
