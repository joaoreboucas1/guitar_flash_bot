from time import sleep, time
from datetime import datetime
import threading
import queue
import pyautogui as pg
import PIL.Image as Image
import PIL.ImageGrab as ImageGrab

# Mouse scroll constant
MOUSE_SCROLL = 120

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

def click_play():
    """
    Description: clicks on the specifies (x_play, y_play) coordinates
    """
    x_play = 675
    y_play = 455
    pg.click(x_play, y_play)
    print(f"{datetime.now()}: Clicking at ({x_play}, {y_play})")

def choose_song(song):
    """
    Description: chooses a song from the Guitar Flash list
    """
    x_song = 677
    if song == "The Lead Sprinkler":
        y_song = 627
    elif song == "Monsoon":
        y_song = 684
    elif song == "Technical Difficulties":
        y_song = 742
    elif song == "Helicopter":
        y_song = 770
        scroll_down(30)
        sleep(1)
    elif song == "Breakthrough":
        y_song = 880
        scroll_down(600)
        sleep(1)
        scroll_down(50)
        sleep(1)
        scroll_down(-8)
        sleep(1)
    else:
        assert False, "Other songs not implemented"
    pg.click(x_song, y_song)
    print(f"{datetime.now()}: Click at ({x_song}, {y_song})")

def start_game(song):
    click_play()
    sleep(3) # Takes a while for the song list to load
    choose_song(song)
    sleep(10) # Takes a while for the song to load
    scroll_down(2)
    sleep(1)
    pg.press('a') # Presses any button to start the song
    print(f"{datetime.now()}: Pressing 'a'")


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
        # Capture the frame to read specific pixels
        nonlocal frame, held_buttons, holding, interval, bg_green, bg_red, bg_yellow, bg_blue, bg_orange, scheduled_hold, scheduled_release
        print(f"Starting to watch actions...")
        idle_frames = 0
        previous_pressed = []

        while idle_frames < 350:
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
                # print(color_yellow, color_blue)
                buttons_to_press = []
                should_hold = False
                if color_green != bg_green:
                    buttons_to_press.append('a')
                    should_hold = im.getpixel(hold_green) == green_hold_color
                if color_red != bg_red:
                    buttons_to_press.append('s')
                    should_hold = should_hold or (im.getpixel(hold_red) == red_hold_color)
                if color_yellow != bg_yellow:
                    buttons_to_press.append('j')
                    should_hold = should_hold or (im.getpixel(hold_yellow) == yellow_hold_color)
                if color_blue != bg_blue:
                    buttons_to_press.append('k')
                    should_hold = should_hold or (im.getpixel(hold_blue) == blue_hold_color)
                if color_orange != bg_orange:
                    buttons_to_press.append('l')
                    should_hold = should_hold or (im.getpixel(hold_orange) == orange_hold_color)
                
                if buttons_to_press == [] or len(buttons_to_press) == 5 or buttons_to_press == previous_pressed:
                    idle_frames += 1
                    previous_pressed = []
                    continue
                if not scheduled_hold:
                    if should_hold:
                        idle_frames = 0
                        print(f"Adding action to queue: hold {buttons_to_press}")
                        scheduled_hold = True
                        action_queue.put({'action': 'hold', 'buttons': buttons_to_press, 'when': frame_time + interval})
                    else:
                        idle_frames = 0
                        print(f"Adding action to queue: press {buttons_to_press}")
                        action_queue.put({'action': 'press', 'buttons': buttons_to_press, 'when': frame_time + interval})
                    previous_pressed = buttons_to_press
            else:
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
        while True:
            last_action = action_queue.get()
            current_time = time()
            if last_action['action'] == 'shutdown':
                break
            if last_action['when'] - current_time < threshold:
                if last_action['action'] == 'press':
                    print(f"{datetime.now()}: Pressing", last_action['buttons'])
                    pg.press(last_action['buttons']) 
                elif last_action['action'] == 'hold' and not holding:
                    holding = True
                    scheduled_hold = False
                    held_buttons = last_action['buttons']
                    print(f"{datetime.now()}: Holding", held_buttons)
                    for button in held_buttons:
                        pg.keyDown(button)
                elif last_action['action'] == 'release':
                    holding = False
                    scheduled_release = False
                    print(f"{datetime.now()}: Releasing", held_buttons)
                    for button in held_buttons:
                        pg.keyUp(button)
                    held_buttons = []
                else:
                    continue
            else:
                action_queue.put(last_action)
    
    action_queue = queue.Queue()
    action_queue.put({'action': None, 'when': -1})
    watch_thread = threading.Thread(target=watch_actions, args=(action_queue,))
    exec_thread = threading.Thread(target=execute_actions, args=(action_queue,))

    watch_thread.start()
    exec_thread.start()

    watch_thread.join()
    exec_thread.join()
    
    im = ImageGrab.grab()
    im_name = f'./statistics/{datetime.now().strftime("%d-%m-%Y_%H-%M-%S")}.png'
    im.save(im_name, "PNG")
    print(f"{datetime.now()}: Song finished! Saved statistics screenshot in {im_name}.")


def main():
    print(f"{datetime.now()}: Starting bot!")
    # song = "Helicopter"
    song = "Monsoon"
    # song = "Technical Difficulties"
    # song = "My Will Be Done"
    # song = "Breakthrough"
    start_game(song)
    print(f"{datetime.now()}: Starting game! Song: {song}")
    sleep(3) # Waiting 3 seconds to start song
    for _ in range(1):
        play_song()
        print(f"{datetime.now()}: Starting next song...")
        pg.click(next_button)
        sleep(12)
        scroll_down(2)
        sleep(1)
        pg.press('a')
        print(f"{datetime.now()}: Pressing 'a'")

        
        
def scroll_down(num):
    pg.scroll(-num*MOUSE_SCROLL)
    if num < 0:
        print(f"{datetime.now()}: Scrolling up {-num} times")
    else:
        print(f"{datetime.now()}: Scrolling down {num} times")

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

    
    