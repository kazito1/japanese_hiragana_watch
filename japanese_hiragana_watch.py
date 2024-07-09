#!/usr/bin/python

import logging
import pygame
import datetime
import locale
import sys
import os
import configparser
import time

# Configure logging
logging.basicConfig(filename='watch.log', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

# KAZ - add slideshow
from photo_manager import PhotoManager
from slideshow import Slideshow

# Delete token.json if it exists
if os.path.exists('token.json'):
    print("Removing old token file...")
    try:
        os.remove('token.json')
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)
    print("Old token file removed. A new one will be created during authentication.")

# Set the locale to Japanese
try:
    locale.setlocale(locale.LC_TIME, 'ja_JP.UTF-8')
except locale.Error:
    print("Error: Japanese locale not found. Please install Japanese language support.")
    sys.exit(1)

# Initialize Pygame
pygame.init()

# Read the configuration file
config = configparser.ConfigParser()
config.read('config.ini')

try:
    font_path = config.get('Font', 'font_file')
    screen_width = config.getint('Display', 'width')
    screen_height = config.getint('Display', 'height')
    fullscreen = config.getboolean('Display', 'fullscreen')
    slideshow_enabled = config.getboolean('Slideshow', 'enabled', fallback=False)
    transition_time = config.getint('Slideshow', 'transition_time', fallback=60)
    photo_months_range = config.getint('Photos', 'months_range', fallback=12)
except (configparser.NoSectionError, configparser.NoOptionError):
    print("Error: Configuration missing or invalid in config.ini")
    pygame.quit()
    sys.exit(1)

if not os.path.isfile(font_path):
    print(f"Error: Font file '{font_path}' not found")
    pygame.quit()
    sys.exit(1)

# Set up the display
if fullscreen:
    screen = pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN)
else:
    screen = pygame.display.set_mode((screen_width, screen_height))

pygame.display.set_caption("Japanese Watch")

# Define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

def get_japanese_number(number, category):
    if category == "minute":
        minute_exceptions = {
            1: "いっぷん", 2: "にふん", 3: "さんぷん", 4: "よんぷん", 5: "ごふん",
            6: "ろっぷん", 7: "ななふん", 8: "はっぷん", 9: "きゅうふん", 10: "じゅっぷん",
            11: "じゅういっぷん", 12: "じゅうにふん", 13: "じゅうさんぷん", 14: "じゅうよんぷん", 15: "じゅうごふん",
            16: "じゅうろっぷん", 17: "じゅうななふん", 18: "じゅうはっぷん", 19: "じゅうきゅうふん", 20: "にじゅっぷん",
            21: "にじゅういっぷん", 22: "にじゅうにふん", 23: "にじゅうさんぷん", 24: "にじゅうよんぷん", 25: "にじゅごふん",
            26: "にじゅうろっぷん", 27: "にじゅうななふん", 28: "にじゅうはっぷん", 29: "にじゅうきゅうふん", 30: "はん",
            31: "さんじゅういっぷん", 32: "さんじゅうにふん", 33: "さんじゅうさんぷん", 34: "さんじゅうよんぷん", 35: "さんじゅうごふん",
            36: "さんじゅうろっぷん", 37: "さんじゅうななふん", 38: "さんじゅうはっぷん", 39: "さんじゅうきゅうふん", 40: "よんじゅっぷん",
            41: "よんじゅういっぷん", 42: "よんじゅうにふん", 43: "よんじゅうさんぷん", 44: "よんじゅうよんぷん", 45: "よんじゅうごふん",
            46: "よんじゅうろっぷん", 47: "よんじゅうななふん", 48: "よんじゅうはっぷん", 49: "よんじゅうきゅうふん", 50: "ごじゅっぷん",
            51: "ごじゅういっぷん", 52: "ごじゅうにふん", 53: "ごじゅうさんぷん", 54: "ごじゅうよんぷん", 55: "ごじゅうごふん",
            56: "ごじゅうろっぷん", 57: "ごじゅうななふん", 58: "ごじゅうはっぷん", 59: "ごじゅうきゅうふん"
        }
        if number in minute_exceptions:
            return minute_exceptions[number]
        elif number < 10:
            return get_japanese_number(number, "default") + "ふん"
        else:
            return get_japanese_number(number // 10, "default") + "じゅう" + get_japanese_number(number % 10, "default") + "ふん"
    elif category == "day":
        day_exceptions = {
            1: "ついたち", 2: "ふつか", 3: "みっか", 4: "よっか", 5: "いつか", 6: "むいか", 7: "なのか",
            8: "ようか", 9: "ここのか", 10: "とおか", 11: "じゅういちにち", 12: "じゅうににち", 13: "じゅうさんにち",
            14: "じゅうよっか", 15: "じゅうごにち", 16: "じゅうろくにち", 17: "じゅうしちにち", 18: "じゅうはちにち",
            19: "じゅうくにち", 20: "はつか", 21: "にじゅういちにち", 22: "にじゅうににち", 23: "にじゅうさんにち",
            24: "にじゅうよっか", 25: "にじゅうごにち", 26: "にじゅうろくにち", 27: "にじゅうしちにち",
            28: "にじゅうはちにち", 29: "にじゅうくにち", 30: "さんじゅうにち", 31: "さんじゅういちにち"
        }
        return day_exceptions[number]
    elif category == "hour":
        hour_exceptions = {
            0: "じゅうにじ", 1: "いちじ", 2: "にじ", 3: "さんじ", 4: "よじ", 5: "ごじ", 6: "ろくじ", 7: "しちじ", 8: "はちじ",
            9: "くじ", 10: "じゅうじ", 11: "じゅういちじ", 12: "じゅうにじ"
        }
        return hour_exceptions[number]
    elif category == "year":
        digits = [int(d) for d in str(number)]
        year_hiragana = ""
        if number >= 1000:
            thousand_digit = digits[-4]
            year_hiragana += get_japanese_number(thousand_digit, "default") + "せん"
            number %= 1000
        if number >= 100:
            hundred_digit = digits[-3]
            year_hiragana += get_japanese_number(hundred_digit, "default") + "ひゃく"
            number %= 100
        if number >= 10:
            ten_digit = digits[-2]
            year_hiragana += get_japanese_number(ten_digit, "default") + "じゅう"
            number %= 10
        if number > 0:
            year_hiragana += get_japanese_number(number, "default")
        year_hiragana += "ねん"
        return year_hiragana
    else:
        japanese_numbers = [
            "", "いち", "に", "さん", "よん", "ご", "ろく", "なな", "はち", "きゅう"
        ]
        if number < 10:
            return japanese_numbers[number]
        elif number < 20:
            return "じゅう" + japanese_numbers[number % 10]
        else:
            return japanese_numbers[number // 10] + "じゅう" + japanese_numbers[number % 10]

def main():
    global screen, fullscreen
    running = True
    fullscreen = False

    # Initialize PhotoManager and Slideshow if enabled
    photo_manager = None
    if slideshow_enabled:
        photo_manager = PhotoManager(months_range=photo_months_range)
        slideshow = Slideshow(screen, photo_manager, transition_time)
    else:
        slideshow = None

    clock = pygame.time.Clock()

    last_token_check = time.time()
    TOKEN_CHECK_INTERVAL = 3600  # Check every hour

    last_photo_check = time.time()
    PHOTO_CHECK_INTERVAL = 300  # Check every 5 minutes

    while running:
        try:
            current_time = time.time()
            if slideshow_enabled and current_time - last_photo_check > PHOTO_CHECK_INTERVAL:
                logging.info("Performing periodic photo check")
                if slideshow.current_photo:
                    logging.info(f"Current photo: {slideshow.current_photo}")
                else:
                    logging.warning("No current photo")
                last_photo_check = current_time

            if slideshow_enabled and photo_manager and current_time - last_token_check > TOKEN_CHECK_INTERVAL:
                logging.info("Performing periodic token check...")
                photo_manager.get_credentials()  # This will refresh if necessary
                last_token_check = current_time

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_RETURN and event.mod & pygame.KMOD_ALT:
                        fullscreen = not fullscreen
                        if fullscreen:
                            screen = pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN)
                        else:
                            screen = pygame.display.set_mode((screen_width, screen_height))
                    elif event.key == pygame.K_c and event.mod & pygame.KMOD_CTRL:
                        running = False

            # Clear the screen
            screen.fill(BLACK)

            # Update and draw slideshow if enabled
            if slideshow:
                slideshow.update()
                slideshow.draw()

            # Get the current date and time
            now = datetime.datetime.now()

            # Format the date in Japanese
            year = get_japanese_number(now.year, "year")
            month = get_japanese_number(now.month, "default") + "がつ"
            day = get_japanese_number(now.day, "day")

            # Temporarily switch locale to English to get the abbreviated day name
            locale.setlocale(locale.LC_TIME, 'en_US.UTF-8')
            weekday = now.strftime("%a")
            locale.setlocale(locale.LC_TIME, 'ja_JP.UTF-8')  # Switch back to Japanese locale

            weekday_mapping = {
                "Sun": "にちようび",
                "Mon": "げつようび",
                "Tue": "かようび",
                "Wed": "すいようび",
                "Thu": "もくようび",
                "Fri": "きんようび",
                "Sat": "どようび"
            }
            weekday_text = weekday_mapping[weekday]
            date_text = f"きょうは{year}{month}{day}{weekday_text}です。"

            # Format the time in Japanese
            hour = now.hour
            is_pm = hour >= 12
            hour = hour % 12
            if hour == 0:
                hour = 12

            if hour == 12 and now.minute == 0:
                if is_pm:
                    time_text = "いまはごごじゅうにじです。"
                else:
                    time_text = "いまはごぜんれいじです。"
            else:
                hour_text = get_japanese_number(hour, "hour")
                am_pm = "ごご" if is_pm else "ごぜん"
                if now.minute == 0:
                    time_text = f"いまは{am_pm}{hour_text}です。"
                else:
                    minute = get_japanese_number(now.minute, "minute")
                    time_text = f"いまは{am_pm}{hour_text}{minute}です。"

            # Calculate the font size based on screen dimensions and text length
            max_text_length = max(len(date_text), len(time_text))
            font_size = int(min(screen_width, screen_height) / (max_text_length * 0.6))
            font = pygame.font.Font(font_path, font_size)

            # Render the date and time text
            date_surface = font.render(date_text, True, WHITE)
            time_surface = font.render(time_text, True, WHITE)

            # Calculate the position to center the text
            date_x = (screen_width - date_surface.get_width()) // 2
            date_y = (screen_height - date_surface.get_height() - time_surface.get_height()) // 2
            time_x = (screen_width - time_surface.get_width()) // 2
            time_y = date_y + date_surface.get_height()

            # Draw the date and time text on the screen
            screen.blit(date_surface, (date_x, date_y))
            screen.blit(time_surface, (time_x, time_y))

            # Update the display
            pygame.display.flip()

        except Exception as e:
            logging.error(f"An error occurred in main loop: {e}")
            print(f"An error occurred: {e}")
            print("Attempting to continue...")
            time.sleep(5)  # Wait for 5 seconds before continuing

        # Control the frame rate
        clock.tick(30)  # 30 FPS

    # Quit Pygame
    pygame.quit()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pygame.quit()
        sys.exit()
