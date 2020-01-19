#!/usr/bin/env python

import pygame
import rospy
import os
import subprocess
import time
import sys
from geometry_msgs.msg import Twist
from std_msgs.msg import String

class ConsoleControl:
    def __init__(self):
        self.process = subprocess.Popen("ds4drv", stdout=subprocess.DEVNULL)
        pygame.init()
        #Initialize the joysticks
        pygame.joystick.init()
        self.joystick = None
        while pygame.joystick.get_count()<1:
            #print("number of joystick %d" % pygame.joystick.get_count())
            pygame.joystick.quit()
            pygame.joystick.init()
           
        print("number of joystick %d" % pygame.joystick.get_count())
        self.joystick = pygame.joystick.Joystick(0)
        print(pygame.joystick.Joystick(0).get_name())
        #Initialize the selected joystick
        self.joystick.init()
        rospy.init_node('console_control')
        self.cmd_pub = rospy.Publisher('ps4_drv', Twist, queue_size=1)
        self.mode_pub = rospy.Publisher('ps4_mode', String, queue_size=1)
        self.mode = 'manual'
        self.record = False
        self.throttle = 0.0
        self.steering = 0.0
        self.forwardscale = 0.4
        self.msg = Twist()
        rospy.loginfo("Initialization completed")
        
    def listen(self):
        while not rospy.is_shutdown():
            for event in pygame.event.get(): #user did something
                if event.type == pygame.JOYBUTTONDOWN:
                    #button square: manual driving
                    if (event.button == 0 and self.mode != 'manual'):
                        self.mode = 'manual'
                    #button X: E-stop
                    elif (event.button == 1):
                        self.mode = 'E-stop'
                        self.throttle = 0.0
                        self.steering = 0.0
                    #button circle: Record
                    elif (event.button == 2):
                        #record
                        self.record = True
                    elif (event.button == 9):
                        self.record = False
                    #button triangle: Auto
                    elif (event.button == 3):
                        self.mode = 'auto'
                        #Auto
                    #button R1:
                    elif (event.button == 5):
                        self.forwardscale -= 0.01
                        rospy.loginfo("forwardscale = %f" % self.forwardscale)
                    #button L1:
                    elif (event.button == 4):
                        self.forwardscale += 0.01
                        rospy.loginfo("forwardscale = %f" % self.forwardscale)
                elif (event.type == pygame.JOYAXISMOTION and self.mode=='manual'):
                    #vertical axis on right stick
                    self.throttle=round(self.joystick.get_axis(5)*(-1.0),2)
                    #horizontal axis on left stick
                    self.steering=round(self.joystick.get_axis(0)*(-1),2)
                elif event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit(0)
                
                #rospy.loginfo("throttle=%3.2f, steering=%3.2f" % (self.throttle, self.steering))
                #rospy.loginfo("mode is %s" % self.mode)
                if(self.throttle>0):
                    self.msg.linear.x = self.throttle*self.forwardscale
                else:
                    self.msg.linear.x = self.throttle
                self.msg.angular.z = self.steering
                self.msg.linear.z = self.record
                self.cmd_pub.publish(self.msg)
                self.mode_pub.publish(self.mode)       
                

if __name__ == "__main__":
    console_control = ConsoleControl()
    console_control.listen()
