from computerVision.CV_positioning_system import CV_positioning_system
import timeit

pos_sys = CV_positioning_system()
count = 0
start = timeit.timeit()

for i in range(0,5):
    end = timeit.timeit()
    ids_to_coords = pos_sys.get_stationary_positions()
    count = count + 1

end = timeit.timeit()
speed = (end-start)/count
frequency = 1/speed
print("speed [seconds/loop]", speed)
print("frequency [Hz]", frequency)