from time import sleep, time
from datetime import datetime
import threading
import queue
import sys
from math import floor, ceil
import pyautogui as pg
import PIL.Image as Image
import PIL.ImageGrab as ImageGrab

# Mouse scroll constant
MOUSE_SCROLL = 120

RESIZE_SCREEN = False
if len(sys.argv) > 1 and sys.argv[1] == '--resize':
    RESIZE_SCREEN = True

def scale_menu(coords):
    if RESIZE_SCREEN:
        return (x,y)
    x = coords[0]
    y = coords[1]
    A = 427/341
    B = -83044/341
    C = 103/82
    D = -133/82
    return (floor((x - B)/A), ceil((y - D)/C))

def scale_play_area(coords):
    if RESIZE_SCREEN:
        return (x,y)
    x = coords[0]
    y = coords[1]
    A = 1027/822
    B = -99121/411
    C = 1.25
    D = -1119/4
    return (floor((x - B)/A), ceil((y - D)/C))

# Chord check coordinates:
chord_green = scale_play_area((782, 790))
chord_red = scale_play_area((864, 790))
chord_yellow = scale_play_area((947, 790))
chord_blue = scale_play_area((1027, 790))
chord_orange = scale_play_area((1106, 790))

# Hold check coordinates
hold_green = scale_play_area((804, 750))
hold_red = scale_play_area((872, 750))
hold_yellow = scale_play_area((947, 750))
hold_blue = scale_play_area((1019, 750))
hold_orange = scale_play_area((1090, 750))

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

next_button = scale_play_area((1094, 641))
next_color = scale_play_area((201,9,9))

def scroll_down(num):
    pg.scroll(-num*MOUSE_SCROLL)
    if num < 0:
        print(f"{datetime.now()}: Scrolling up {-num} times")
    else:
        print(f"{datetime.now()}: Scrolling down {num} times")

def click_play():
    """
    Description: clicks on the specifies (x_play, y_play) coordinates
    """
    x_play = 675
    y_play = 455
    x_play, y_play = scale_menu((x_play, y_play))
    pg.click(x_play, y_play)
    print(f"{datetime.now()}: Clicking at ({x_play}, {y_play})")

def choose_song_from_input():
    query = input("Choose a song: ")
    click_play()
    sleep(3)
    print(f"{datetime.now()}: ctrl-f searching for user query...")
    pg.hotkey('ctrl', 'f')
    sleep(0.5)
    pg.write(query)
    sleep(0.5)
    print(f"{datetime.now()}: User query result is centralized, clicking screen center")
    pg.click(715, 551)
    pg.sleep(10)
    print(f"{datetime.now()}: Pressing 'a'")
    pg.press('a')
    sleep(3)
    print(f"{datetime.now()}: Starting game! Song: {query}")

def play_song():
    print(f"{datetime.now()}: Starting song...")
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
    print(f"{datetime.now()}: Background colors", bg_green, bg_red, bg_yellow, bg_blue, bg_orange)
    
    def watch_actions(action_queue):
        """
        Description: continuously gets frames and processes them into actions, inserting into a queue.
        """
        nonlocal frame, held_buttons, holding, interval, bg_green, bg_red, bg_yellow, bg_blue, bg_orange, scheduled_hold, scheduled_release
        print(f"{datetime.now()}: Thread 1 starting to watch actions...")
        idle_frames = 0
        previous_pressed = []

        while idle_frames < 500:
            frame = frame + 1
            im = ImageGrab.grab()
            frame_time = time()

            # Processing frame info
            if not holding:
                color_green = im.getpixel(chord_green)
                color_red = im.getpixel(chord_red)
                color_yellow = im.getpixel(chord_yellow)
                color_blue = im.getpixel(chord_blue)
                color_orange = im.getpixel(chord_orange)
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
                        action_queue.put({'action': 'hold', 'buttons': buttons_to_press, 'when': frame_time + interval})
                    else:
                        idle_frames = 0
                        action_queue.put({'action': 'press', 'buttons': buttons_to_press, 'when': frame_time + interval})
                    previous_pressed = buttons_to_press
            else:
                # TODO: change release check location to match press check location
                color_green = im.getpixel(hold_green)
                color_red = im.getpixel(hold_red)
                color_yellow = im.getpixel(hold_yellow)
                color_blue = im.getpixel(hold_blue)
                color_orange = im.getpixel(hold_orange)
                
                should_release = (
                    ('a' in held_buttons and color_green != green_hold_color and color_green != (255, 255, 255)) or
                    ('s' in held_buttons and color_red != red_hold_color and color_red != (255, 255, 255)) or
                    ('j' in held_buttons and color_yellow != yellow_hold_color and color_yellow != (255, 255, 255)) or
                    ('k' in held_buttons and color_blue != blue_hold_color and color_blue != (255, 255, 255)) or 
                    ('l' in held_buttons and color_orange != orange_hold_color and color_orange != (255, 255, 255))
                )
                if should_release and not scheduled_release:
                    scheduled_release = True
                    action_queue.put({'action': 'release', 'buttons': held_buttons, 'when': frame_time + interval})
        action_queue.put({'action': 'shutdown'})

    def execute_actions(action_queue):
        """
        Description: performs actions in the action queue.
        """
        nonlocal holding, held_buttons, scheduled_hold, scheduled_release
        threshold = 0.08
        print(f"{datetime.now()}: Thread 2 ready for actions to perform...")
        while True:
            last_action = action_queue.get()
            current_time = time()
            if last_action['action'] == 'shutdown':
                break
            if abs(last_action['when'] - current_time) < threshold:
                if last_action['action'] == 'press':
                    print(f"{datetime.now()}: Pressing", last_action['buttons'])
                    pg.press(last_action['buttons']) 
                elif last_action['action'] == 'hold' and not holding:
                    holding = True
                    scheduled_hold = False
                    held_buttons = last_action['buttons']
                    print(f"{datetime.now()}: Holding", held_buttons)
                    for button in held_buttons:
                        pg.platformModule._keyDown(button)
                elif last_action['action'] == 'release':
                    holding = False
                    scheduled_release = False
                    print(f"{datetime.now()}: Releasing", held_buttons)
                    for button in held_buttons:
                        pg.platformModule._keyUp(button)
                    held_buttons = []
            elif current_time > last_action['when'] and last_action['action'] == 'release':
                holding = False
                scheduled_release = False
                print(f"{datetime.now()}: Releasing", held_buttons)
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
            print(f"{datetime.now()}: Interrupting bot...")
            sys.exit(1)

    watch_thread.join()
    exec_thread.join()
    
    im = ImageGrab.grab()
    im_name = f'./statistics/{datetime.now().strftime("%d-%m-%Y_%H-%M-%S")}.png'
    im.save(im_name, "PNG")
    print(f"{datetime.now()}: Song finished! Saved statistics screenshot in {im_name}.")

def main():
    print(f"{datetime.now()}: Starting bot!")
    choose_song_from_input()
    play_song()

if __name__=='__main__':
    main()