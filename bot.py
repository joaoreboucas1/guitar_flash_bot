from time import time, sleep
from datetime import datetime
import os
import numpy as np
import pyautogui as pg
import PIL.Image as Image
import PIL.ImageOps as ImageOps
import PIL.ImageGrab as ImageGrab

# Play area coordinates
MOUSE_SCROLL = 120
x_pad = 0
y_pad = 0

# Chord check coordinates:
# Worked very well on first try but these coordinates overlap with the fire that pops up when a chord is hit.
chord_green = (758, 836)
chord_red = (854, 836)
chord_yellow = (947, 836)
chord_blue = (1040, 836)
chord_orange = (1134, 836)

# Chord check coordinates:
chord_green = (782, 790)
chord_red = (864, 790)
chord_yellow = (947, 790)
chord_blue = (1027, 790)
chord_orange = (1106, 790)

# Hold check coordinates
hold_green = (804, 750)
hold_red = (872, 750)
hold_yellow = (947, 750)
hold_blue = (1019, 750)
hold_orange = (1090, 750)


# Color RGB values
green = (0, 152, 0)
red = (255, 0, 0)
yellow = (244, 244, 2)
blue = (0, 152, 255)
orange = (255, 101, 0)
white = (255, 255, 255)
orange_hold_color = (255, 102, 0)
blue_hold_color = (51, 153, 204)
red_hold_color = (204, 0, 0)
yellow_hold_color = (255, 255, 0)
green_hold_color = (0, 255, 0)

next_button = (1094, 641)
next_color = (201,9,9)

def screen_grab():
    """
    Description: takes a screenshot and saves to a location.
    """
    # box = ()
    img = ImageGrab.grab()
    # img.save(rf"{os.getcwd()}/full_snap_{int(time())}.png", "PNG")
    return img

def click_play():
    """
    Description: clicks on the specifies (x_play, y_play) coordinates
    """
    x_play = 675
    y_play = 455
    pg.click(x_play, y_play)
    print(f"{datetime.now()}: Click at ({x_play}, {y_play})")

def choose_song(song):
    """
    Description: chooses a song from the Guitar Flash list
    """
    x_song = 677
    if song == 'Monsoon':
        y_song = 627
    elif song == 'Technical Difficulties':
        y_song = 684
    elif song == 'My Will Be Done':
        y_song = 742
    else:
        assert False, "Other songs not implemented"
    pg.click(x_song, y_song)
    print(f"{datetime.now()}: Click at ({x_song}, {y_song})")

def start_game(song):
    click_play()
    sleep(3) # Takes a while for the song list to load
    choose_song(song)
    sleep(10) # Takes a while for the song to load
    pg.scroll(-2*MOUSE_SCROLL) # Adjusts the screen to fit play area
    print(f"{datetime.now()}: Scroll twice down")
    pg.press('a') # Presses any button to start the song
    print(f"{datetime.now()}: Press a")

def play_song():
    print(f"{datetime.now()}: Starting song...")
    previous_pressed = []
    action_queue = []
    frame = 0
    idle_frames = 0
    im = screen_grab()
    bg_green = im.getpixel(chord_green)
    bg_red = im.getpixel(chord_red)
    bg_yellow = im.getpixel(chord_yellow)
    bg_blue = im.getpixel(chord_blue)
    bg_orange = im.getpixel(chord_orange)
    print("Background colors:", bg_green, bg_red, bg_yellow, bg_blue, bg_orange)
    holding = False
    interval = 3
    while idle_frames < 3600:
        frame += 1
        if len(action_queue) > 0:
            last_action = action_queue[-1]
            if last_action['frame'] == frame:
                if last_action['action'] == 'press':
                    print(f"{datetime.now()}: Pressing", last_action['buttons'])
                    pg.press(last_action['buttons']) 
                elif last_action['action'] == 'hold' and not holding:
                    holding = True
                    held_buttons = last_action['buttons']
                    print(f"{datetime.now()}: Holding", held_buttons)
                    for button in held_buttons:
                        pg.keyDown(button)                    
                elif last_action['action'] == 'release':
                    holding = False
                    print(f"{datetime.now()}: Releasing", held_buttons)
                    for button in held_buttons:
                        pg.keyUp(button)
                    held_buttons = []
                else:
                    assert False, f"Unknown action {last_action['action']}"
        
        im = screen_grab()
        color_green = im.getpixel(chord_green)
        color_red = im.getpixel(chord_red)
        color_yellow = im.getpixel(chord_yellow)
        color_blue = im.getpixel(chord_blue)
        color_orange = im.getpixel(chord_orange)

        pressed_buttons = []
        should_hold = False
        if color_green != bg_green:
            pressed_buttons.append('a')
            should_hold = im.getpixel(hold_green) == green_hold_color
        if color_red != bg_red:
            pressed_buttons.append('s')
            should_hold = should_hold or (im.getpixel(hold_red) == red_hold_color)
        if color_yellow != bg_yellow:
            pressed_buttons.append('j')
            should_hold = should_hold or (im.getpixel(hold_yellow) == yellow_hold_color)
        if color_blue != bg_blue:
            pressed_buttons.append('k')
            should_hold = should_hold or (im.getpixel(hold_blue) == blue_hold_color)
        if color_orange != bg_orange:
            pressed_buttons.append('l')
            should_hold = should_hold or (im.getpixel(hold_orange) == orange_hold_color)
        
        if holding:
            if pressed_buttons == held_buttons:
                # print(f"Must release {pressed_buttons} in 3 frames")
                if action_queue[-1]['action'] == 'release':
                    pass
                action_queue.append({'action': 'release', 'buttons': None, 'frame': frame + interval})

        if pressed_buttons == previous_pressed or pressed_buttons == [] or len(pressed_buttons) == 5:
            pressed_buttons = []
            idle_frames += 1
        else:
            if should_hold and not holding:
                # print(f"Must hold {pressed_buttons} in 3 frames")
                if action_queue[-1]['action'] == 'hold':
                    pass
                else:
                    action_queue.append({'action': 'hold', 'buttons': pressed_buttons, 'frame': frame + interval})
            else: 
                # print(f"Must press {pressed_buttons} in 3 frames")
                if not holding:
                    action_queue.append({'action': 'press', 'buttons': pressed_buttons, 'frame': frame + interval})
        
        previous_pressed = pressed_buttons


def main():
    print(f"{datetime.now()}: Starting bot!")
    # song = 'Technical Difficulties'
    song = "Monsoon"
    # song = "My Will Be Done"
    start_game(song)
    print(f"{datetime.now()}: Starting game! Song: {song}")
    sleep(3) # Waiting 3 seconds to start song
    for _ in range(10):
        play_song()
        print(f"{datetime.now()}: Song finished! Starting next...")
        pg.click(next_button)
        sleep(20)
        pg.scroll(-2*MOUSE_SCROLL) # Adjusts the screen to fit play area
        pg.press('a')
        
        
            

def get_rgb_values():
    with Image.open("frame.png") as im:
        #print(im.getpixel(next_button))
        print(im.getpixel((782,655)))
        print(im.getpixel(hold_blue))
        print(im.getpixel(hold_red))
        #print(im.getpixel((1078,727)))


if __name__=='__main__':
    main()
    # get_rgb_values()