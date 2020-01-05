import os, sys, inspect, thread, time, math
src_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
arch_dir = os.path.abspath(os.path.join(src_dir, '../lib'))
sys.path.insert(0, os.path.abspath(os.path.join(src_dir, arch_dir)))

import Leap

class MotionListener(Leap.Listener):
    def on_connect(self, controller):
        print "Connected"
        # Kep Tap Motion
        controller.enable_gesture(Leap.Gesture.TYPE_KEY_TAP);
        controller.config.set("Gesture.KeyTap.MinDownVelocity", 40.0)
        controller.config.set("Gesture.KeyTap.HistorySeconds", .2)
        controller.config.set("Gesture.KeyTap.MinDistance", 1.0)
        # controller.config.save()

        # Swipe
        controller.enable_gesture(Leap.Gesture.TYPE_SWIPE);
        controller.config.set("Gesture.Swipe.MinLength", 100.0)
        controller.config.set("Gesture.Swipe.MinVelocity", 750)
        controller.config.save()

    def on_disconnect(self,controller):
        print "Disconnected"

    def on_frame(self, controller):
        frame = controller.frame()
        # print "Frame id: %d, timestamp: %d, hands: %d, fingers: %d" % (
        #    frame.id, frame.timestamp, len(frame.hands), len(frame.fingers))
        # displaying the position of hand palm
        hands = frame.hands
        hand = hands[0] # first hand
        # print(hand.palm_position)

        if hands.is_empty:
            print "no hands. Raspimouse should be stopped."

        for gesture in frame.gestures():
            # start/stop to move by <Key Taps> or <No hand>
            # https://developer-archive.leapmotion.com/documentation/v2/python/api/Leap.KeyTapGesture.html
            if gesture.type is Leap.Gesture.TYPE_KEY_TAP:                        
                key_tap = Leap.KeyTapGesture(gesture)
                print "keytap detected. Raspimouse will start to move."
            # Turn Left/Right <Swipe>
            # https://developer-archive.leapmotion.com/documentation/v2/python/api/Leap.SwipeGesture.html
            if gesture.type is Leap.Gesture.TYPE_SWIPE:
                swipe = Leap.SwipeGesture(gesture)
                direction = swipe.direction
                if abs(direction[0]) > abs(direction[1]): # horizontal move
                    if direction[0] > 0:
                        swipeDirection = "right"
                    else:
                        swipeDirection = "left"
                else: # vertical
                    swipeDirection = "ignore"    
                print direction
                print swipeDirection
                print "Swipe detected"

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
