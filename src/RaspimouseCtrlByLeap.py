import os, sys, inspect, thread, time, math, paramiko, argparse
src_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
arch_dir = os.path.abspath(os.path.join(src_dir, '../lib'))
sys.path.insert(0, os.path.abspath(os.path.join(src_dir, arch_dir)))

import Leap

DEBUG = False

class MotionListener(Leap.Listener):
    def on_connect(self, controller):
        print "Connected"
        
        # Argument parser
        parser = argparse.ArgumentParser()
        parser.add_argument("ip", help="IP addresse to be connected via SSH")
        parser.add_argument("user", help="User name to connect via SSH")
        parser.add_argument("password", help="Password to connect via SSH")
        self.args = parser.parse_args()
        
        # Kep Tap Motion
        controller.enable_gesture(Leap.Gesture.TYPE_KEY_TAP);
        controller.config.set("Gesture.KeyTap.MinDownVelocity", 40.0)
        controller.config.set("Gesture.KeyTap.HistorySeconds", .2)
        controller.config.set("Gesture.KeyTap.MinDistance", 1.0)
        # controller.config.save()

        # Swipe
        controller.enable_gesture(Leap.Gesture.TYPE_SWIPE);
        controller.config.set("Gesture.Swipe.MinLength", 120.0)
        controller.config.set("Gesture.Swipe.MinVelocity", 750)
        controller.config.save()

        self.moving = False

    def on_disconnect(self, controller):
        print "Disconnected"

    # SSH connection
    def ssh_connection(self):
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(self.args.ip, username=self.args.user, password=self.args.password)
        ssh_session = client.get_transport().open_session()
        if ssh_session.active:
            # print "SSH connection establihsed to RaspiMouse"
            self.ssh = ssh_session
        return

    def ssh_command(self, opval):
        self.ssh_connection()
        if self.ssh.active:
            cmd = 'rm /tmp/opval; echo ' + str(opval) + ' > /tmp/opval'
            self.ssh.exec_command(cmd)
            print(self.ssh.recv(1024))
        return

    # Private Functions
    def move(self):
        if not self.moving: 
            print "Start moving."
            self.moving = True
            self.ssh_command(1)

    def stop(self):
        if self.moving:
            print "Stop."
            self.moving = False
            self.ssh_command(0)

    def turnRight(self):
        if self.moving:
            print "Turn Right."
            self.ssh_command(2)
            
    def turnLeft(self):
        if self.moving:
            print "Turn Left."
            self.ssh_command(3)

    def on_frame(self, controller):
        frame = controller.frame()
        hands = frame.hands
        if DEBUG:
            print "Frame id: %d, timestamp: %d, hands: %d, fingers: %d" % (frame.id, frame.timestamp, len(frame.hands), len(frame.fingers))
            hand = hands[0] # first hand
            print(hand.palm_position)

        if hands.is_empty:
            if DEBUG:
                print "no hands. Raspimouse should be stopped."
            self.stop()
        else:
            self.move()
            for gesture in frame.gestures():
                # start to move by <Key Taps>
                # https://developer-archive.leapmotion.com/documentation/v2/python/api/Leap.KeyTapGesture.html
                # if gesture.type is Leap.Gesture.TYPE_KEY_TAP:                        
                #     key_tap = Leap.KeyTapGesture(gesture)
                #     if DEBUG:
                #         print "keytap detected. Raspimouse will start to move."
                #     self.move()
                
                # Turn Left/Right <Swipe>
                # https://developer-archive.leapmotion.com/documentation/v2/python/api/Leap.SwipeGesture.html
                if gesture.type is Leap.Gesture.TYPE_SWIPE:
                    swipe = Leap.SwipeGesture(gesture)
                    direction = swipe.direction
                    if abs(direction[0]) > abs(direction[1]): # horizontal movement
                        if direction[0] > 0:
                            swipeDirection = "right"
                            self.turnRight()
                        else:
                            swipeDirection = "left"
                            self.turnLeft()
                    else: # vertical movement, nothing to do
                        swipeDirection = "ignore"
                    if DEBUG:
                        print direction
                        print swipeDirection
                        print "Swipe gesture detected"
 

def main():
    # Create a sample listener and controller
    listener = MotionListener()
    controller = Leap.Controller()

    # Have the sample listener receive events from the controller
    controller.add_listener(listener)

    # Keep this process running until Enter is pressed
    print "Press Enter to quit..."
    try:
        sys.stdin.readline()
    except KeyboardInterrupt:
        pass
    finally:
        # Remove the sample listener when done
        controller.remove_listener(listener)

if __name__ == "__main__":
    main()
