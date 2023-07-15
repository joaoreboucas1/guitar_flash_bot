# Guitar Flash Bot

## Description
A bot that plays [Guitar Flash](guitarflash.com) songs. The bot is written in Python using the [`pyautogui`](https://pyautogui.readthedocs.io/en/latest/) library. Using multithreading via the `threading` library to optimize action processing.

[The first 100%!](https://github.com/joaoreboucas1/guitar_flash_bot/blob/main/100_percent.png?raw=true)

## Setup
Currently, the bot works in 1980x1020 screens. The screen positions have beed adjusted for Micosoft Edge, assuming the root webpage is opened fullscreen without scrolling the page. Should also work for other Chromium-based browsers as long as there are no toolbars, only tabs and URL field. One can then proceed to run the script as long as there is no windows blocking the screen positions where the bot detects chords and clicks. After a song is finished, the bot saves a screenshot of the statistics in `statistics/`. 

## Point Records so far
- 25052 points on Tokio Hotel - Monsoon. Hit 1329 chords (99%), missed 5, wrong 2, 8/8 specials, max combo 455
- 4781 on MindFlow - Breakthrough. Hit 445 chords (87%), missed 63, wrong 12, 4/10 specials, max combo 134
- 23582 on Bloc Party - Helicopter. Hit 1269 chords (99%), missed 3, wrong 7, 9/9 specials, max combo 241
- 20457 on Foo Fighters - These Days. Hit 1670 (83%), missed 320, wrong 126, 6/11 specials, max combo 330*

## Notes
- The code implicitly assumes "simultaneous hold/release" actions: keys are always held and released together. Many songs don't operate like this.
- The bot does not perform well in a variety of situations. For instance, in the song These Days, the bot has trouble processing when there are quick sequences of hold/release/press actions.