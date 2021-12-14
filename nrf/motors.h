#include <stdint.h>
void motors_drive_correction(float pos_error, float head_error, float remaining_dist);

// void drive(void);

void drive(uint16_t left_enc, uint16_t right_enc);

void motors_encoders_clear(uint16_t left_enc, uint16_t right_enc);

void motors_stop(void);

void initKobuki(void);

// extern int kp_pos;
// extern int kd_pos;
// extern int kp_head;
// extern int kd_head;
