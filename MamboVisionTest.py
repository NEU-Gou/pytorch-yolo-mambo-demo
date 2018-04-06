from DroneVision import DroneVision
from Mambo import Mambo
import threading
import cv2
import time


class UserVision:
    def __init__(self, vision):
        self.index = 0
        self.vision = vision

    def save_pictures(self, args):
        print("in save pictures on image %d " % self.index)

        img = self.vision.get_latest_valid_picture()

        if (img is not None):
            filename = "test_image_%06d.png" % self.index
            cv2.imwrite(filename, img)
            self.index +=1
            #print(self.index)

testFlying = False

# you will need to change this to the address of YOUR mambo; For BLE use only
mamboAddr = "C8:3A:35:CE:87:B2"

# make my mambo object
# remember to set True/False for the wifi depending on if you are using the wifi or the BLE to connect
mambo = Mambo(mamboAddr, use_wifi=True)
print("trying to connect to mambo now")
success = mambo.connect(num_retries=3)
print("connected: %s" % success)

if (success):
    # get the state information
    print("sleeping")
    mambo.smart_sleep(1)
    mambo.ask_for_state_update()
    mambo.smart_sleep(1)

    print("Preparing to open vision")
    mamboVision = DroneVision(mambo, is_bebop=False, buffer_size=30)


    # userVision = UserVision(mamboVision)
    # mamboVision.set_user_callback_function(userVision.save_pictures, user_callback_args=None)
    success = mamboVision.open_video()
    # img = mamboVision.get_latest_valid_picture()


    print("Success in opening vision is %s" % success)

    if (success):
        print("Vision successfully started!")
        #removed the user call to this function (it now happens in open_video())
        #mamboVision.start_video_buffering()

        while True:
            1
        # done doing vision demo
        print("Ending the sleep and vision")
        mamboVision.close_video()

        mambo.smart_sleep(5)

    print("disconnecting")
    mambo.disconnect()
