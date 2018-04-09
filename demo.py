from utils import *
from darknet import Darknet
import cv2


from DroneVision import DroneVision
from Mambo import Mambo
import threading
import time
import shutil
from subprocess import check_output, CalledProcessError
import signal

# set this to true if you want to fly for the demo
testFlying = False

class UserVision:
    def __init__(self, vision):
        self.index = 0
        self.vision = vision

    def save_pictures(self, args):
        #print("in save pictures")
        img = self.vision.get_latest_valid_picture()

        filename = "test_image_%06d.png" % self.index
        cv2.imwrite(filename, img)
        self.index +=1
        #print(self.index)


def demo_cam(cfgfile, weightfile):
    m = Darknet(cfgfile)
    m.print_network()
    m.load_weights(weightfile)
    print('Loading weights from %s... Done!' % (weightfile))

    if m.num_classes == 20:
        namesfile = 'data/voc.names'
    elif m.num_classes == 80:
        namesfile = 'data/coco.names'
    else:
        namesfile = 'data/names'
    class_names = load_class_names(namesfile)

    use_cuda = 1
    if use_cuda:
        m.cuda()

    cap = cv2.VideoCapture("rtsp://192.168.10.36")
    if not cap.isOpened():
        print("Unable to open camera")
        exit(-1)

    cv2.namedWindow("YoloV2", cv2.WND_PROP_FULLSCREEN)
    cv2.setWindowProperty("YoloV2", cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN)

    while True:
        res, img = cap.read()
        if res:
            sized = cv2.resize(img, (m.width, m.height))
            bboxes = do_detect(m, sized, 0.5, 0.4, use_cuda)
            print('------')
            draw_img = plot_boxes_cv2(img, bboxes, None, class_names)
            cv2.imshow("YoloV2", draw_img)
            cv2.waitKey(1)
        else:
            print("Unable to read image")
            exit(-1)


def demo(cfgfile, weightfile):
    m = Darknet(cfgfile)
    m.print_network()
    m.load_weights(weightfile)
    print('Loading weights from %s... Done!' % (weightfile))

    if m.num_classes == 20:
        namesfile = 'data/voc.names'
    elif m.num_classes == 80:
        namesfile = 'data/coco.names'
    else:
        namesfile = 'data/names'
    class_names = load_class_names(namesfile)
 
    use_cuda = 1
    if use_cuda:
        m.cuda()

    # cap = cv2.VideoCapture("rtsp://192.168.10.1:554/onvif1")
    # cap = cv2.VideoCapture("rtsp://192.168.99.1/media/stream2")


#---------------------FOR Mambo------------------------------------
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

        # wait for next step
        nextstep = raw_input("Any key to continue:")

        print("Preparing to open vision")
        mamboVision = DroneVision(mambo, is_bebop=False, buffer_size=30)

        # userVision = UserVision(mamboVision)
        # mamboVision.set_user_callback_function(userVision.save_pictures, user_callback_args=None)
        success = mamboVision.open_video()
        #img = mamboVision.get_latest_valid_picture()

        print("Success in opening vision is %s" % success)
        cv2.namedWindow("YoloV2", cv2.WND_PROP_FULLSCREEN)
        cv2.setWindowProperty("YoloV2", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
# ------------------------------------------------------------------
        if (success):
            print("Vision successfully started!")
            mambo.smart_sleep(1)
            # removed the user call to this function (it now happens in open_video())
            # mamboVision.start_video_buffering()
            count = 30
            while True:
                imgName = "./images/image_" + str(count).zfill(5) + ".png"
                img = cv2.imread(imgName)
                # img = mamboVision.get_latest_valid_picture()
                if img is None:
                    print("Unable to read image")
                else:
                    sized = cv2.resize(img, (m.width, m.height))
                    bboxes = do_detect(m, sized, 0.5, 0.4, use_cuda)
                    print('------')
                    draw_img = plot_boxes_cv2(img, bboxes, None, class_names)
                    cv2.imshow("YoloV2", draw_img)
                    count = count + 1
                if cv2.waitKey(1) == ord('q'):
                    break
            # done doing vision demo
            print("Quiting...")
            mamboVision.close_video()
            mambo.smart_sleep(10)
            # grep the ffmpeg process
            try:
                pidlist = map(int, check_output(["pidof", "ffmpeg"]).split())
            except CalledProcessError:
                print("Cannot grep the pid")
                pidlist = []
            for pid in pidlist:
                os.kill(pid,signal.SIGTERM)
                print("Killing the ffmpeg process...")
                time.sleep(2)

            # print("disconnecting")
            # mambo.disconnect()
            print("Cleaning up...")
            for file in os.listdir('./images'):
                while True:
                    try:
                        if os.path.isfile(os.path.join('./images',file)):
                            os.unlink(os.path.join('./images',file))
                            break
                    except Exception:
                        print('Trying to delet images')

        print("disconnecting")
        mambo.disconnect()
            # print("Done!")
            # shutil.rmtree("./images",ignore_errors=True)
            # os.mkdir("./images")


            

        
    




    # cap = cv2.VideoCapture("rtsp://192.168.10.36")
    # if not cap.isOpened():
    #     print("Unable to open camera")
    #     exit(-1)

    # while True:
    #     res, img = cap.read()
    #     if res:
    #         sized = cv2.resize(img, (m.width, m.height))
    #         bboxes = do_detect(m, sized, 0.5, 0.4, use_cuda)
    #         print('------')
    #         draw_img = plot_boxes_cv2(img, bboxes, None, class_names)
    #         cv2.imshow(cfgfile, draw_img)
    #         cv2.waitKey(1)
    #     else:
    #          print("Unable to read image")
    #          exit(-1)

############################################
if __name__ == '__main__':
    demo("cfg/yolo.cfg", "yolo.weights")
    # demo_cam("cfg/yolov2.cfg", "yolov2.weights")
    # if sys.argv[1] == "Drone":
    #     demo("cfg/yolo.cfg", "yolo.weights")
    # elif sys.argv[1] == "Camera":
    #     demo_cam("cfg/yolo.cfg", "yolo.weights")


    # if len(sys.argv) == 3:
    #     cfgfile = sys.argv[1]
    #     weightfile = sys.argv[2]
    #     demo(cfgfile, weightfile)
    #     #demo('cfg/tiny-yolo-voc.cfg', 'tiny-yolo-voc.weights')
    # else:
    #     print('Usage:')
    #     print('    python demo.py cfgfile weightfile')
    #     print('')
    #     print('    perform detection on camera')
