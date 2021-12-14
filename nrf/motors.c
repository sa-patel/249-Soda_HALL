#include "motors.h"
#include "display.h"
#include "buckler.h"
#include "kobukiActuator.h"
#include "kobukiSensorTypes.h"
#include "kobukiSensorPoll.h"
#include "kobukiUtilities.h"

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

#include <math.h>
#include <stdint.h>


// Motor speed constants
const int BASE_SPEED = 100;
const int MAX_SPEED = 150;

// PID constants
#define PERIOD (0.25) // Expected time between iterations
#define TURN_THRESHOLD (0.8) // Turn in place if the heading error exceeds this.
#define STRAIGHT_THRESHOLD (0.14) // Return to driving forward if heading error is below this.
const float kp_pos = 10;
const float kd_pos = 1 / PERIOD;
const float kdd_pos = 0; // Not implemented
const float kp_head = 100;
const float kd_head = 1 / PERIOD;
const float kp_dist = 100;
#define TICKS_PER_RAD (2637)
#define TICKS_PER_METER (11000)
const float kp_enc_turn = 300./TICKS_PER_RAD;
int g_desired_enc_diff = 0;
int g_remaining_enc = 0;
int g_orig_remaining_enc = 0;

volatile int left = 0;
volatile int right = 0;
int g_driving = true;

 // initialize state
typedef enum {
    STRAIGHT,
    TURN
} DriveState_t;

static DriveState_t drive_state = STRAIGHT;


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

// // Drive the kobuki motors
// void drive(void) {
//     int left_power = clamp(left, MAX_SPEED);
//     int right_power = clamp(right, MAX_SPEED);
//     //printf("getting drive: %d, %d \n", left_encoder, right_encoder);
//     kobukiDriveDirect(left_power, right_power);
// }

uint16_t g_left_enc = 0;
uint16_t g_right_enc = 0;

void motors_encoders_clear(uint16_t left_enc, uint16_t right_enc) {
    g_left_enc = left_enc;
    g_right_enc = right_enc;
    g_driving = true;
}

static inline int overflow_subtract(uint16_t a, uint16_t b) {
    int32_t diff = a - b;
    if (diff > UINT16_MAX>>1) {
        return -(b + (UINT16_MAX - a));
    }
    if (-diff > UINT16_MAX>>1) {
        return a + (UINT16_MAX - b);
    }
    return diff;
}

void drive(uint16_t left_enc, uint16_t right_enc) {
    if (!g_driving) return;
    // static uint16_t prev_left_enc = 0;
    // static uint16_t prev_right_enc = 0;
    int diff = overflow_subtract(right_enc, g_right_enc) - overflow_subtract(left_enc, g_left_enc);
    // int diff = (right_enc - g_right_enc) - (left_enc - g_left_enc);
    int error = g_desired_enc_diff - diff;
    // printf("error %d ",error);
    // int turn_speed = (int)(kp_enc_turn*error);
    int turn_speed = clamp((int)(kp_enc_turn*error), 80);
    int drive_speed = 0;
    if (drive_state == STRAIGHT && g_remaining_enc > 100) {
        drive_speed = BASE_SPEED;
    }
    g_remaining_enc = g_orig_remaining_enc - overflow_subtract(right_enc, g_right_enc);
    // printf("speeds %d %d\n", drive_speed+turn_speed, drive_speed-turn_speed);
    kobukiDriveDirect(clamp(drive_speed-turn_speed, MAX_SPEED), clamp(drive_speed+turn_speed, MAX_SPEED));

}

static inline void transition(float head_error) {
    if (fabs(head_error) > TURN_THRESHOLD) {
        drive_state = TURN;
    } else if (fabs(head_error) < STRAIGHT_THRESHOLD) {
        drive_state = STRAIGHT;
    }
}

// Control the motors 
void motors_drive_correction(float pos_error, float head_error, float remaining_dist) {
    // Local variables for previous error.
    static float prev_pos_error = 0;
    static float prev_head_error = 0;

    transition(head_error);
    g_desired_enc_diff = (int)(head_error*TICKS_PER_RAD);
    g_remaining_enc = (int)(remaining_dist*TICKS_PER_METER);
    g_orig_remaining_enc = (int)(remaining_dist*TICKS_PER_METER);


    // Calculate the correction terms.
    float delta_pos_error = pos_error - prev_pos_error;
    float delta_head_error = head_error - prev_head_error;
    int turn_speed = (int)(kp_pos * pos_error + kd_pos * delta_pos_error 
                     + kp_head * head_error + kd_head * delta_head_error);

    // Forward speed is zero if drive_state is turning. Nonzero otherwise.
    int forward_speed = 0;
    if (drive_state == STRAIGHT) {
        forward_speed = clamp(remaining_dist * kp_dist, BASE_SPEED);
    }

    // Drive the motors.
    left = forward_speed - turn_speed;
    right = forward_speed + turn_speed;
    // printf("left %d right %d\n", left, right);

    // Update prev variables.
    prev_pos_error = pos_error;
    prev_head_error = head_error;
}

void motors_stop(void) {
    left = 0; // deprecated
    right = 0;
    // g_desired_enc_diff = 0;
    // g_remaining_enc = 0;
    // g_orig_remaining_enc = 0;
    g_driving = false;
}
