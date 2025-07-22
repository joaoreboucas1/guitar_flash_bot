from time import sleep, time
from datetime import datetime
from enum import Enum
import logging
import threading
import queue
import sys
from math import floor, ceil
import pyautogui as pg
import PIL.Image as Image
import PIL.ImageGrab as ImageGrab
import pynput

logging.basicConfig(stream=sys.stdout, format='%(asctime)s.%(msecs)03d: %(message)s',
                    datefmt='%d/%m/%Y %H:%M:%S', level=logging.INFO)

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
unheld_button_color = (51, 51, 51)

next_button = (1094, 641)
next_color = (201,9,9)

class Action(Enum):
    PRESS = 1
    HOLD = 2
    RELEASE = 3

def click_play():
    """
    Description: clicks on the specifies (x_play, y_play) coordinates
    """
    x_play = 675
    y_play = 455
    x_play, y_play = scale_menu((x_play, y_play))
    pg.click(x_play, y_play)
    logging.info(f"Clicking at ({x_play}, {y_play})")

def play_song(play_area):
    (left, top), (right, bottom) = play_area
    width = right - left
    height = bottom - top

    # Chord check coordinates
    chord_green  = (left + 248, bottom - 100)
    chord_red    = (left + 326, bottom - 100)
    chord_yellow = (left + 408, bottom - 100)
    chord_blue   = (left + 485, bottom - 100)
    chord_orange = (left + 565, bottom - 100)

    # Hold check coordinates
    hold_green  = (left + 268, bottom - 143)
    hold_red    = (left + 335, bottom - 143)
    hold_yellow = (left + 406, bottom - 143)
    hold_blue   = (left + 480, bottom - 143)
    hold_orange = (left + 545, bottom - 143)
    
    logging.info(f"Starting song...")
    pg.click(left + width/2, top + height/2)
    sleep(0.1)
    pg.press("a")

    frame = 0
    start_time = time()
    
    held_buttons = []
    holding = False
    interval = 0.2
    scheduled_hold = False
    scheduled_release = False

    im = ImageGrab.grab()
    bg_green = im.getpixel(chord_green)
    bg_red = im.getpixel(chord_red)
    bg_yellow = im.getpixel(chord_yellow)
    bg_blue = im.getpixel(chord_blue)
    bg_orange = im.getpixel(chord_orange)
    logging.info(f"Background colors: {bg_green}, {bg_red}, {bg_yellow}, {bg_blue}, {bg_orange}")
    
    def watch_actions(action_queue):
        """
        Description: continuously gets frames and processes them into actions, inserting into a queue.
        """
        nonlocal frame, held_buttons, holding, interval, bg_green, bg_red, bg_yellow, bg_blue, bg_orange, scheduled_hold, scheduled_release
        logging.info(f"Thread 1 starting to watch actions...")
        idle_frames = 0
        previous_pressed = []

        while idle_frames < 500:
            frame = frame + 1
            im = ImageGrab.grab()
            frame_time = time()
            
            color_green = im.getpixel(chord_green)
            color_red = im.getpixel(chord_red)
            color_yellow = im.getpixel(chord_yellow)
            color_blue = im.getpixel(chord_blue)
            color_orange = im.getpixel(chord_orange)

            # Processing frame info
            if not holding:
                buttons_to_press = []
                should_hold = False
                if color_green != bg_green and color_green != unheld_button_color:
                    buttons_to_press.append('a')
                    should_hold = im.getpixel(hold_green) == green_hold_color
                if color_red != bg_red and color_red != unheld_button_color:
                    buttons_to_press.append('s')
                    should_hold = should_hold or (im.getpixel(hold_red) == red_hold_color)
                if color_yellow != bg_yellow and color_yellow != unheld_button_color:
                    buttons_to_press.append('j')
                    should_hold = should_hold or (im.getpixel(hold_yellow) == yellow_hold_color)
                if color_blue != bg_blue and bg_blue != unheld_button_color:
                    buttons_to_press.append('k')
                    should_hold = should_hold or (im.getpixel(hold_blue) == blue_hold_color)
                if color_orange != bg_orange and bg_orange != unheld_button_color:
                    buttons_to_press.append('l')
                    should_hold = should_hold or (im.getpixel(hold_orange) == orange_hold_color)
                
                if buttons_to_press == [] or len(buttons_to_press) > 3 or buttons_to_press == previous_pressed:
                    idle_frames += 1
                    previous_pressed = []
                    continue
                if not scheduled_hold:
                    if should_hold:
                        idle_frames = 0
                        scheduled_hold = True
                        action_queue.put({'action': Action.HOLD, 'buttons': buttons_to_press, 'when': frame_time + interval})
                    else:
                        idle_frames = 0
                        action_queue.put({'action': Action.PRESS, 'buttons': buttons_to_press, 'when': frame_time + interval})
                    previous_pressed = buttons_to_press
            else:                
                should_release = (
                    ('a' in held_buttons and color_green != green_hold_color and color_green != (255, 255, 255)) or
                    ('s' in held_buttons and color_red != red_hold_color and color_red != (255, 255, 255)) or
                    ('j' in held_buttons and color_yellow != yellow_hold_color and color_yellow != (255, 255, 255)) or
                    ('k' in held_buttons and color_blue != blue_hold_color and color_blue != (255, 255, 255)) or 
                    ('l' in held_buttons and color_orange != orange_hold_color and color_orange != (255, 255, 255))
                )
                if should_release and not scheduled_release:
                    scheduled_release = True
                    action_queue.put({'action': Action.RELEASE, 'buttons': held_buttons, 'when': frame_time + interval})
        action_queue.put({'action': 'shutdown'})

    def execute_actions(action_queue):
        """
        Description: performs actions in the action queue.
        """
        nonlocal holding, held_buttons, scheduled_hold, scheduled_release
        threshold = 0.08
        logging.info(f"Thread 2 ready for actions to perform...")
        while True:
            last_action = action_queue.get()
            current_time = time()
            if last_action['action'] == 'shutdown':
                break
            if abs(last_action['when'] - current_time) < threshold:
                if last_action['action'] == Action.PRESS:
                    logging.info(f"Pressing {last_action['buttons']}")
                    pg.press(last_action['buttons']) 
                elif last_action['action'] == Action.HOLD and not holding:
                    holding = True
                    scheduled_hold = False
                    held_buttons = last_action['buttons']
                    logging.info(f"Holding {held_buttons}")
                    for button in held_buttons:
                        pg.platformModule._keyDown(button)
                elif last_action['action'] == Action.RELEASE:
                    holding = False
                    scheduled_release = False
                    logging.info(f"Releasing {held_buttons}")
                    for button in held_buttons:
                        pg.platformModule._keyUp(button)
                    held_buttons = []
            elif current_time > last_action['when'] and last_action['action'] == Action.RELEASE:
                holding = False
                scheduled_release = False
                logging.info(f"Releasing {held_buttons}")
                for button in held_buttons:
                    pg.platformModule._keyUp(button)
                held_buttons = []
            elif current_time < last_action['when']:
                action_queue.put(last_action)

    action_queue = queue.Queue()
    action_queue.put({'action': None, 'when': -1})
    watch_thread = threading.Thread(target=watch_actions, args=(action_queue,))
    exec_thread = threading.Thread(target=execute_actions, args=(action_queue,))
    watch_thread.daemon = True
    exec_thread.daemon = True

    watch_thread.start()
    exec_thread.start()

    while watch_thread.is_alive() and exec_thread.is_alive():
        try:
            sleep(1)
        except KeyboardInterrupt:
            logging.info("Interrupting bot...")
            sys.exit(1)

    watch_thread.join()
    exec_thread.join()
    
    im = ImageGrab.grab()
    im_name = f'./statistics/{song.replace(" ", "_")}_{datetime.now().strftime("%d-%m-%Y_%H-%M-%S")}.png'
    im.save(im_name, "PNG")
    logging.info(f"Song finished! Saved statistics screenshot in {im_name}.")


play_area = []
def on_click(x, y, button, pressed):
    if pressed:
        logging.info(f"Registered play area corner at ({x}, {y})")
        play_area.append([x, y])
        if len(play_area) >= 2: return False

def main():
    logging.info("Starting bot!")
    logging.info("Choose the song and wait for it to load")
    logging.info("Click on the top left and bottom right corners of the play area")
    with pynput.mouse.Listener(on_click=on_click) as listener:
        listener.join()
    logging.info(f"Play area corners: {play_area}")
    play_song(play_area)

if __name__=='__main__':
    main()