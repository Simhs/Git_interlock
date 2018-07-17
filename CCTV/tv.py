
# -*- coding: utf-8 -*-
import time

import cv2
import pygame

import HomeTV
import sys
'''
if len(sys.argv) >= 2:
    server_ip = sys.argv[1]
else:
    server_ip = 'localhost'
    print "sys.argv[1] has no data"
    print "you have to put ip after file"
    print "lkie : python tv.py <serv ip> "
    print "Now excute : python tv.py localhost"
'''
def cvimage_to_pygame(image):
    try:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        cvimg = pygame.image.frombuffer(image.tostring(), image.shape[1::-1], "RGB")
    except:
        return False
    return cvimg



stv = HomeTV.SimTV("64.137.189.244",19200)

w_size = 800
h_size = 480

pygame.init()
# screen = pygame.display.set_mode((self.w, self.h),pygame.FULLSCREEN)
screen = pygame.display.set_mode((w_size,h_size))


serverDownImage = pygame.image.load("rsc/serverDown.png").convert_alpha()
serverDownImage = pygame.transform.scale(serverDownImage, (800, 480))

ch0 = pygame.image.load("rsc/ch1.png").convert_alpha()
ch1 = pygame.image.load("rsc/ch2.png").convert_alpha()
ch2 = pygame.image.load("rsc/ch3.png").convert_alpha()
ch3 = pygame.image.load("rsc/ch4.png").convert_alpha()
ch4 = pygame.image.load("rsc/ch5.png").convert_alpha()

ch = [ch0,ch1,ch2,ch3,ch4]


channel = 0
while 1:
    screen.fill((0, 0, 0))
    try:
        nosize, frame = stv.run(channel%3)
    except:
        screen.fill((0, 0, 0))
        frame = serverDownImage
        screen.blit(frame, [0, 0, 0, 0])
        pygame.display.flip()
        continue
    if nosize == '0':
        screen.fill((0, 0, 0))
    else:
        frame = cvimage_to_pygame(frame)
        frame = pygame.transform.scale(frame, (800, 480))
        screen.blit(frame, [0, 0, 0, 0])
        screen.blit(ch[channel % 3], [0, 0, 0, 0])

    for evt in pygame.event.get():
        if evt.type == pygame.KEYDOWN:
            if evt.key == pygame.K_SPACE:
                channel += 1

    pygame.display.flip()

pygame.quit()
