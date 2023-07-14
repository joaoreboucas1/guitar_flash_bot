from time import sleep
from datetime import datetime
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
    if song == "Monsoon":
        y_song = 627
    elif song == "Technical Difficulties":
        y_song = 684
    elif song == "My Will Be Done":
        y_song = 742
    elif song == "Helicopter":
        y_song = 710
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
    idle_frames = 0
    previous_pressed = []
    held_buttons = []
    action_queue = [{'action': None, 'frame': -1}]
    holding = False
    interval = 3

    im = ImageGrab.grab()
    bg_green = im.getpixel(chord_green)
    bg_red = im.getpixel(chord_red)
    bg_yellow = im.getpixel(chord_yellow)
    bg_blue = im.getpixel(chord_blue)
    bg_orange = im.getpixel(chord_orange)
    print(f"{datetime.now()}: Background colors", bg_green, bg_red, bg_yellow, bg_blue, bg_orange)
    
    while idle_frames < 700:
        frame += 1

        # Check if bot needs to perform an action
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
                assert False, f"Unhandled action {last_action['action']}"
        
        # Capture the frame to read specific pixels
        im = ImageGrab.grab()

        # Processing frame info
        if not holding:
            color_green = im.getpixel(chord_green)
            color_red = im.getpixel(chord_red)
            color_yellow = im.getpixel(chord_yellow)
            color_blue = im.getpixel(chord_blue)
            color_orange = im.getpixel(chord_orange)
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
            
            if buttons_to_press == [] or len(buttons_to_press) == 5:
                idle_frames += 1
                continue
            if not (action_queue[-1]['action'] == 'hold'):
                if should_hold:
                    idle_frames = 0
                    action_queue.append({'action': 'hold', 'buttons': buttons_to_press, 'frame': frame + interval})
                else:
                    idle_frames = 0
                    action_queue.append({'action': 'press', 'buttons': buttons_to_press, 'frame': frame + interval})
        else:
            color_green = im.getpixel(hold_green)
            color_red = im.getpixel(hold_red)
            color_yellow = im.getpixel(hold_yellow)
            color_blue = im.getpixel(hold_blue)
            color_orange = im.getpixel(hold_orange)
            should_release = (
                ('a' in held_buttons and color_green != green_hold_color) or
                ('s' in held_buttons and color_red != red_hold_color) or
                ('j' in held_buttons and color_yellow != yellow_hold_color) or
                ('k' in held_buttons and color_blue != blue_hold_color) or 
                ('l' in held_buttons and color_orange != orange_hold_color)
            )
            if should_release and not (action_queue[-1]['action'] == 'release'):
                action_queue.append({'action': 'release', 'buttons': None, 'frame': frame + interval})        
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
    for _ in range(10):
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

    
    