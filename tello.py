import cv2
from turtle import Turtle
from djitellopy import Tello
from time import sleep
from threading import Thread
from ultralytics import YOLO

"""
********************************** INFORMATION ************************************************************************
According to the drone's docs, the speed is 15 cm/s.

The distance is in pixels, so we need to create a conversion rate. You can create yours as your convenience

Each iteration will have a time.sleep(seg) to wait the instruction be done.

*********************************************************************************************************************
"""

model = YOLO('yolov8_house_items.pt')

class Fly(Turtle):

    def __init__(self, exported_path):
        super().__init__()

        self.hideturtle()

        self.start = False

        self.keep_recording = True

        self.exported_path = exported_path

        self.tello = Tello()


    def start_flying(self, start, path):

        if start:

            self.tello.connect()
            self.tello.get_battery()
            self.showturtle()
            self.shapesize(2)
            self.left(90)

            recorder = Thread(target=self.video_recorder, daemon=True)
            recorder.start()



            self.path_to_commands(path)

    def draw_turtle(self, path_list):

        for l in path_list:
            x = l[0]
            y = l[1]
            path_list.pop(0)

            return x, y


    def to_travel(self, dist_px):
        """
        speed = 15cm/s
        1px -> 1 cm

        return the seconds that will be used to know the time interval between commands.
        Feel free to use as you want
        """

        if dist_px < 0:
            if dist_px < -100:  # I put this condition min value because testing at home. Outside max value is -500

                cm = 50
            else:
                cm = abs(dist_px)

        elif dist_px > 100:  # I put this max value because testing at home. Outside max value is 500

            cm = 50

        else:
            cm = dist_px

        return round((cm / 15), 2)


    def path_to_commands(self,full_path):

        print("******** START THE PATH ********")
        sleep(2)  # wait to initialize the video_recorder
        self.tello.takeoff()

        speed = 20
        path_list = full_path[-1]
        path = full_path[:-1]

        for item in path:

            if item["motion"] == "forward":

                seconds = self.to_travel(item["distance"])

                self.tello.send_rc_control(0, speed, 0, 0)

                print("SENCONDS: ############", seconds)
                sleep(seconds)

            elif item["motion"] == "backward":

                seconds = self.to_travel(item["distance"])

                self.tello.send_rc_control(0, -speed, 0, 0)

                print("SENCONDS: ############", seconds)
                sleep(seconds)

            elif item["motion"] == "left":

                seconds = self.to_travel(item["distance"])

                self.tello.send_rc_control(speed, 0, 0, 0)

                print("SENCONDS: ############", seconds)
                sleep(seconds)

            elif item["motion"] == "right":

                seconds = self.to_travel(item["distance"])

                self.tello.send_rc_control(-speed, 0, 0, 0)

                print("SENCONDS: ############", seconds)
                sleep(seconds)

            elif item["motion"] == "rotate_right":

                yw = 90
                seconds = 1

                self.tello.send_rc_control(0, 0, 0, yw)

                print("SENCONDS: ############", seconds)
                self.right(90)
                sleep(seconds)

            elif item["motion"] == "rotate_left":

                yw = 90
                seconds = 1

                self.tello.send_rc_control(0, 0, 0, yw)
                print("SENCONDS: ############", seconds)
                self.left(90)
                sleep(seconds)  # As it is in other thread it keeps flying

            elif item["motion"] == "up":

                self.tello.send_rc_control(0, 0, speed, 0)
                seconds = 1
                sleep(seconds)

            elif item["down"] == "down":

                self.tello.send_rc_control(0, 0, -speed, 0)
                seconds = 1
                sleep(seconds)


            self.tello.send_rc_control(0, 0, 0, 0)

            try:

                x, y = self.draw_turtle(path_list)
                self.goto(x, y)
            except TypeError:
                pass

        print("*************** LAND ********************")

        self.keep_recording = False

        self.tello.land()


    def abort_mission(self):
        if self.tello:  # Check if tello is initialized
            return self.tello.emergency()

    def video_recorder(self):

        self.tello.streamon()

        while self.keep_recording:

            frame_read = self.tello.get_frame_read().frame
            frame_read = cv2.resize(frame_read, (640, 640))

            results = model(frame_read)

            annotated_frame = results[0].plot()

            cv2.imshow("DRONE DETECTIONS", annotated_frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
                self.tello.land()
        self.tello.streamoff()












