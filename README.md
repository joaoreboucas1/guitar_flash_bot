# Guitar Flash Bot

## Description
A bot that plays [Guitar Flash](guitarflash.com) songs. The bot is written in Python using the [`pyautogui`](https://pyautogui.readthedocs.io/en/latest/) library. Using multithreading via the `threading` library to optimize action processing.

![The first 100%!](https://github.com/joaoreboucas1/guitar_flash_bot/blob/main/100_percent.png?raw=true)

## Setup
Currently, the bot works in 1980x1020 screens if the display zoom is set to 100%. The screen positions have beed adjusted for Micosoft Edge, assuming the root webpage is opened fullscreen without scrolling the page. Should also work for other Chromium-based browsers as long as there are no toolbars, only tabs and URL field. One can then proceed to run the script in a shell (using the command `python bot.py`) as long as there is no windows blocking the screen positions where the bot detects chords and clicks. I use a terminal running on my second screen and the browser fullscreen in the first screen. After a song is finished, the bot saves a screenshot of the statistics in `statistics/`. 

If your screen scale is set to 125%, run the bot with the `--resize` flag.

## Point Records so far
- 26531 points on Tokio Hotel - Monsoon. Hit 1334 chords (100%!), missed 0, wrong 0, 8/8 specials, max combo 1334
- 4781 on MindFlow - Breakthrough. Hit 445 chords (87%), missed 63, wrong 12, 4/10 specials, max combo 134
- 23582 on Bloc Party - Helicopter. Hit 1269 chords (99%), missed 3, wrong 7, 9/9 specials, max combo 241
- 20457 on Foo Fighters - These Days. Hit 1670 (83%), missed 320, wrong 126, 6/11 specials, max combo 330*

## Notes
- This bot has only been tested on my own computer: it might not work properly in other computers.
- The code implicitly assumes "simultaneous hold/release" actions: keys are always held and released together. Many songs don't operate like this.
- The bot does not perform well in a variety of situations. For instance, in the song These Days, the bot has trouble processing when there are quick sequences of hold/release/press actions.