// BLE Service Template
//
// Creates a service for changing LED state over BLE

#include <stdint.h>
#include "nrf_twi_mngr.h"
#include "app_util.h"
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
#include "display.h"
#include "lsm9ds1.h"
#include "nrf_drv_spi.h"

#include "buckler.h"
#include "kobukiActuator.h"
#include "kobukiSensorTypes.h"
#include "kobukiSensorPoll.h"
#include "kobukiUtilities.h"

#include "simple_ble.h"

#include "max44009.h"

// Project modules
#include "motors.h"


typedef enum {
    IDLE, //At base station
    RETURNING, //Going to the base station to wait for next order
    DELIVERING_ORDER, // Bringing order to customer
    UNLOADING, // Order is being loaded onto or unloaded from robot
    LOADING,
    PLAN_PATH_TO_BASE,
    PLAN_PATH_TO_TABLE,
    UNDEFINED
} KobukiState_t;

KobukiState_t current_state = IDLE; 

//NRF_TWI_MNGR_DEF(twi_mngr_instance, 5, 0);

#define SCALE_FACTOR 100.00
// Intervals for advertising and connections
static simple_ble_config_t ble_config = {
        // c0:98:e5:49:xx:xx
        .platform_id       = 0x49,    // used as 4th octect in device BLE address
        .device_id         = 0x0001, // TODO: replace with your lab bench number
        .adv_name          = "EE149 LED", // used in advertisements if there is room
        .adv_interval      = MSEC_TO_UNITS(1000, UNIT_0_625_MS),
        .min_conn_interval = MSEC_TO_UNITS(500, UNIT_1_25_MS),
        .max_conn_interval = MSEC_TO_UNITS(1000, UNIT_1_25_MS),
};

// 32e61089-2b22-4db5-a914-43ce41986c70
static simple_ble_service_t generic_service = {{
    .uuid128 = {0x70,0x6C,0x98,0x41,0xCE,0x43,0x14,0xA9,
                0xB5,0x4D,0x22,0x2B,0x89,0x10,0xE6,0x32}
}};

// 32e61059-2b22-4db5-a914-43ce41986c70
static simple_ble_service_t state_service= {{
    .uuid128 = {0x70,0x6C,0x98,0x41,0xCE,0x43,0x14,0xA9,
                0xB5,0x4D,0x22,0x2B,0x59,0x10,0xE6,0x32}
}};



static simple_ble_char_t test_error_data = {.uuid16 = 0x108c};
static simple_ble_char_t display_string_data = {.uuid16 = 0x108d};
static simple_ble_char_t get_button_press = {.uuid16 = 0x108e};

static simple_ble_char_t get_kobuki_state= {.uuid16 = 0x105c};
static simple_ble_char_t led1_state_char = {.uuid16 = 0x105d};



static int led_state = 1;
static uint8_t button_press;
static uint8_t error_data[6];
static volatile int g_button_pressed = 0;

static unsigned char buf_disp[64];
#define DISPLAY_WIDTH 15
volatile static char display_list[3][DISPLAY_WIDTH];
// volatile static char** display_list = {"               ", "               ", "               "};
static unsigned char buf_state[64];
KobukiSensors_t sensors = {0};

//snprintf(buf, 16, "%f", measure_distance(sensors.leftWheelEncoder, previous_encoder)); 
//display_write( buf, DISPLAY_LINE_1);

/*******************************************************************************
 *   State for this applications
 ******************************************************************************/
// Main application state
simple_ble_app_t* simple_ble_app;

void ble_evt_write(ble_evt_t const* p_ble_evt) {
    if (simple_ble_is_char_event(p_ble_evt, &test_error_data)) {
      //printf("Data is : %02x %02x \n",error_data[0],error_data[1]);
      float pos_error = ((error_data[0] << 8) | error_data[1])/SCALE_FACTOR;
      float head_error = ((error_data[2] << 8) | error_data[3])/SCALE_FACTOR;
      float remain_dist = ((error_data[4] << 8) | error_data[5])/SCALE_FACTOR;
      printf("Recovered positional error data: %f \n",pos_error);
      printf("Recovered heading error data: %f \n",head_error);
      motors_drive_correction(pos_error, head_error, remain_dist);
    }
    if (simple_ble_is_char_event(p_ble_evt, &display_string_data)) {
      //printf("Data is : %02x %02x \n",error_data[0],error_data[1]);
      //snprintf(buf, 16, "%f", measure_distance(sensors.leftWheelEncoder, previous_encoder)); 
	    char delim[] = ",";
      char *p = strtok((char*)buf_disp, delim);
      int i = 0;
      while (p != NULL){
        if (i >= 3) {
          break;
        }
        strncpy(display_list[i], p, DISPLAY_WIDTH);
        printf("%d %s\n", i, p);
        i++;
        p = strtok(NULL, delim);
      }
        
        char line_1[16];
        if (i > 1) {
          snprintf(line_1, DISPLAY_WIDTH, "%s %s", display_list[0], display_list[1]);
          display_write(line_1, DISPLAY_LINE_0);
        }
        else if (i == 1) {
          // display_write("               ", DISPLAY_LINE_0);
          display_write(display_list[0], DISPLAY_LINE_0);
        }
        else {
          // display_write("               ", DISPLAY_LINE_0);
        }
        if (i > 2) {
          // display_write("               ", DISPLAY_LINE_1);
          display_write(display_list[2], DISPLAY_LINE_1);
        }
        else {
          // display_write("               ", DISPLAY_LINE_1);
        }
        //nrf_delay_ms(2500);
      
    }
    if (simple_ble_is_char_event(p_ble_evt, &get_button_press)) {
      //printf("Data is : %02x %02x \n",error_data[0],error_data[1]);
      //snprintf(buf, 16, "%f", measure_distance(sensors.leftWheelEncoder, previous_encoder)); 
      //char send_buf[16];
      button_press = g_button_pressed;
      printf("button pressed %d \n",button_press);
      g_button_pressed = 0;
    }
    if (simple_ble_is_char_event(p_ble_evt, &led1_state_char)) {
      printf("Got write to LED characteristic!\n");
      if (led_state) {
        printf("Turning on LED!\n");
        nrf_gpio_pin_clear(BUCKLER_LED0);
      } else {
        printf("Turning off LED!\n");
        nrf_gpio_pin_set(BUCKLER_LED0);
      }
    }
    if (simple_ble_is_char_event(p_ble_evt, &get_kobuki_state)) {
      if (strcmp((char*)buf_state, "IDLE") == 0) { 
        current_state = IDLE;
      } else if (strcmp((char*)buf_state,"RETURNING") == 0){ 
        current_state = RETURNING;
      }else if (strcmp((char*)buf_state,"DELIVERING_ORDER") == 0){ 
        current_state = DELIVERING_ORDER;
      }else if (strcmp((char*)buf_state,"UNLOADING") == 0){ 
        current_state = UNLOADING;
      }else if (strcmp((char*)buf_state,"LOADING") == 0){ 
        current_state = LOADING;
      }else if (strcmp((char*)buf_state,"PLAN_PATH_TO_BASE") == 0){ 
        current_state = PLAN_PATH_TO_BASE;
      }else if (strcmp((char*)buf_state,"PLAN_PATH_TO_TABLE") == 0){ 
        current_state = PLAN_PATH_TO_TABLE;
      }else { 
        current_state = UNDEFINED;
      }
    } 
}

static int display_index = 0;
static void advance_drink(void) {
  display_write(display_list[display_index], DISPLAY_LINE_1);
  //printf("%s\n", display_list[display_index]);
  display_index++;
  display_index%=3;
}

int main(void) {

  // Initialize

  // initialize RTT library
  NRF_LOG_INIT(NULL);
  NRF_LOG_DEFAULT_BACKENDS_INIT();
  printf("Initialized RTT!\n");

  //kobukiSensorPoll(&initial_sensors);  

  // initialize display
  nrf_drv_spi_t spi_instance = NRF_DRV_SPI_INSTANCE(1);
  nrf_drv_spi_config_t spi_config = {
    .sck_pin = BUCKLER_LCD_SCLK,
    .mosi_pin = BUCKLER_LCD_MOSI,
    .miso_pin = BUCKLER_LCD_MISO,
    .ss_pin = BUCKLER_LCD_CS,
    .irq_priority = NRFX_SPI_DEFAULT_CONFIG_IRQ_PRIORITY,
    .orc = 0,
    .frequency = NRF_DRV_SPI_FREQ_4M,
    .mode = NRF_DRV_SPI_MODE_2,
    .bit_order = NRF_DRV_SPI_BIT_ORDER_MSB_FIRST
  };

  ret_code_t error_code = nrf_drv_spi_init(&spi_instance, &spi_config, NULL, NULL);
  APP_ERROR_CHECK(error_code);
  display_init(&spi_instance);
  display_write("Waiter 1", DISPLAY_LINE_0);
  printf("Display initialized!\n");

  // Setup LED GPIO
  nrf_gpio_cfg_output(BUCKLER_LED0);

  // Setup BLE
  simple_ble_app = simple_ble_init(&ble_config);

  simple_ble_add_service(&generic_service);
 

  simple_ble_add_characteristic(1, 1, 0, 0,
    sizeof(uint8_t),&button_press,
    &generic_service, &get_button_press);
  
  simple_ble_add_characteristic(1, 1, 0, 0,
      sizeof(uint8_t)*6, error_data,
      &generic_service, &test_error_data); ///send 6 bytes, 2 bytes for each error 

  simple_ble_add_characteristic(1, 1, 0, 0,
      sizeof(char)*64, buf_disp,
      &generic_service, &display_string_data);

  // simple_ble_add_service(&state_service);

  // simple_ble_add_characteristic(1, 1, 0, 0,
  //     sizeof(char)*64, buf_state,
  //     &state_service, &get_kobuki_state);
  
  // simple_ble_add_characteristic(1, 1, 0, 0,
  //     sizeof(led_state), (uint8_t*)&led_state,
  //     &state_service, &led1_state_char);

  // initialize i2c master (two wire interface)
  /*nrf_drv_twi_config_t i2c_config = NRF_DRV_TWI_DEFAULT_CONFIG;
  i2c_config.scl = BUCKLER_SENSORS_SCL;
  i2c_config.sda = BUCKLER_SENSORS_SDA;
  i2c_config.frequency = NRF_TWIM_FREQ_100K;
  error_code = nrf_twi_mngr_init(&twi_mngr_instance, &i2c_config);
  APP_ERROR_CHECK(error_code);
  lsm9ds1_init(&twi_mngr_instance);
  printf("IMU initialized!\n");*/
  kobukiInit();

  // Start Advertising
  simple_ble_adv_only_name();
  
  while(1) {
      kobukiSensorPoll(&sensors);
      int check_button = is_button_pressed(&sensors);
      if (check_button) { 
        g_button_pressed = 1;
      }
      drive();

    // switch (current_state){         if (check_button) { 
    //      g_button_pressed = 1;
    //    }
    //   case LOADING:
    //   case UNLOADING: {
    //     kobukiSensorPoll(&sensors);
    //     int check_button = is_button_pressed(&sensors);
    //     if (check_button) { 
    //       g_button_pressed = 1;
    //     }
    //     break;
    //   } 
    //   case DELIVERING_ORDER: 
    //   case RETURNING:
    //     g_button_pressed = 0;
    //     drive();
    //     break;
    //   case PLAN_PATH_TO_BASE:
    //   case PLAN_PATH_TO_TABLE: 
    //   case IDLE:
    //     g_button_pressed = 0; 
    //   default:
    //     g_button_pressed = 0;
    //     //nrf_delay_ms(250);somehow this f**ks up everthing
    //     break; 
    // }
  }
}

