#!/bin/python3

# https://github.com/Aditya-Khadilkar/Face-tracking-with-Anime-characters
# borrowed source code is marked as 'copycat'

try:
    import pygame_sdl2
    pygame_sdl2.import_as_pygame()
except ImportError:
    pass
import sys
import pygame
from math import sin, cos, radians
from time import sleep
import random
import cv2

def fmap(num, smin, smax, tmin, tmax):
    source_range = (smax - smin)
    target_range = (tmax - tmin)
    return (((num - smin) * target_range) / source_range) + tmin

def clamp(num, min, max):
    if num > max:
        return max
    if num < min:
        return min
    return num

def rotate_image(image, angle): # copycat
    if angle == 0: return image
    height, width = image.shape[:2]
    rot_mat = cv2.getRotationMatrix2D((width/2, height/2), angle, 0.9)
    result = cv2.warpAffine(image, rot_mat, (width, height), flags=cv2.INTER_LINEAR)
    return result

def rotate_point(pos, img, angle): # copycat
    if angle == 0: return pos
    x = pos[0] - img.shape[1]*0.4
    y = pos[1] - img.shape[0]*0.4
    newx = x*cos(radians(angle)) + y*sin(radians(angle)) + img.shape[1]*0.4
    newy = -x*sin(radians(angle)) + y*cos(radians(angle)) + img.shape[0]*0.4
    return int(newx), int(newy), pos[2], pos[3]

# returns float <1; 1.05>
def beat_zoom():
    state = float(heartbeat_time) / heartbeat_limit
    t = 1
    for b in beats_f:
        if state > b and state < b + beat_duration_f:
            time = state - b
            tmp = fmap(time, 0, beat_duration_f, 1, 1.05)
            if tmp > t:
                t = tmp
    return t

# returns floats (<-1; 1>, <-1; 1>)
def eyeshift():
    global old_shift_x
    global old_shift_y

    print("\x1b[H")

    # copycat
    ret, img = cam.read()
    img = cv2.flip(img, +1)
    for angle in [0, -25, 25]:
        rotated_img = rotate_image(img, angle)
        detected = face.detectMultiScale(rotated_img, **settings)
        if len(detected):
            detected = [rotate_point(detected[-1], img, -angle)]
            break

    shift_x = old_shift_x
    shift_y = old_shift_y
    for x, y, w, h in detected[-1:]:
        cv2.rectangle(img, (x, y), (x+w, y+h), (255,0,0), 2)
        #shift_x = float(x) / float(w) * 2 - 1 #(x+w)/2
        #shift_y = float(y) / float(h) * 2 - 1 #2*(y+h)/3 # to look at the eyes
        shift_x = float(x) / float(w) * 2 - 2
        shift_y = float(y) / float(h) * 2 - 2
    # end of copycat

    old_shift_x = shift_x
    old_shift_y = shift_y

    print(str(shift_x) + "                ")
    print(str(shift_y) + "                ")

    # random shift
    delta = 0.03
    shift_x = shift_x + fmap(random.random(), 0, 1, -delta, delta)
    shift_y = shift_y + fmap(random.random(), 0, 1, -delta, delta)

    dampener = 0.3
    offset_x = -0.1
    offset_y = 0
    shift_x = clamp(shift_x * dampener + offset_x, -1, 1)
    shift_y = clamp(shift_y * dampener + offset_y, -1, 1)
    return (shift_x, shift_y)

def update_img(screen):
    #pygame.Surface.fill(screen, (0, 0, 0))

    scale = float(height) / img_height * beat_zoom()
    x = (width - img_width * scale) / 2
    y = height - img_height * scale + ((beat_zoom() - 1) * height)

    # img, degree, scale
    _bg = pygame.transform.rotozoom(bg, 0, scale)
    _body = pygame.transform.rotozoom(body, 0, scale)
    _eyes = pygame.transform.rotozoom(eyes, 0, scale)
    shift = eyeshift()
    sx = shift[0] * allowed_x_shift * scale
    sy = shift[1] * allowed_y_shift * scale
    ex = x + sx + eye_x_offset * scale
    ey = y + sy + eye_y_offset * scale

    screen.blit(_bg, (x, y))
    screen.blit(_body, (x, y))
    screen.blit(_eyes, (ex, ey))
    pygame.draw.rect(screen, color_overlay, (0, 0, width, height))

def loop():
    screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
    update_img(screen)
    pygame.display.flip()

if __name__ != '__main__':
    quit()

cam = cv2.VideoCapture(0)
face = cv2.CascadeClassifier('haarcascade_frontalface_alt2.xml')
settings = {
    'scaleFactor': 1.3,
    'minNeighbors': 3,
    'minSize': (50, 50),
}

pygame.init()
pygame.mixer.init()
clock = pygame.time.Clock()

target_fps = 60

# source image w,h
img_width = 1280
img_height = 720
allowed_x_shift = 16 # delta
allowed_y_shift = 3  # delta
eye_x_offset = -6
eye_y_offset = 2
# any
width = 800
height = 600
old_shift_x = 0
old_shift_y = 0

eyes = pygame.image.load('eyes2.png')
body = pygame.image.load('eyes1.png')
icon = pygame.image.load('icon.png')
pygame.display.set_icon(icon)
pygame.display.set_caption("Yuri is watching...")

heartbeat_limit = 20
heartbeat_time = 0
beat_duration_f = 0.1
beats_f = (0.75, 0.9)


pygame.mixer.music.set_volume(1)

if sys.argv[1:]: # any argument calls the 1.
    bg = pygame.image.load('club.png')
    color_overlay = (20, 0, 0, 200) # R G B alpha
    sound = pygame.mixer.music.load('5_yuri2.ogg')
else: # no argument
    bg = pygame.image.load('closet.png')
    color_overlay = (0, 0, 0, 200) # R G B alpha
    sound = pygame.mixer.music.load('heartbeat.ogg')

pygame.mixer.music.play(-1)

print("\x1b[2J")
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYUP and event.key == pygame.K_ESCAPE:
           running = False
        elif event.type == pygame.KEYUP and event.key == pygame.K_q:
           running = False
        elif event.type == pygame.VIDEORESIZE:
            width = event.w
            height = event.h

    loop()
    heartbeat_time = heartbeat_time + 1
    if heartbeat_time > heartbeat_limit:
        heartbeat_time = 0

    used_ms = clock.tick(target_fps) / 10
    total_ms = 1000 / target_fps
    print(total_ms)
    print(used_ms)
    if (total_ms > used_ms):
        t = (total_ms - used_ms) / 100
        print("good - sleeping for: " + str(t))
        sleep(t)
    else:
        print("slow                                             ")
    clock.tick(target_fps)

cv2.destroyAllWindows()
pygame.mixer.quit()
pygame.quit()
quit()
