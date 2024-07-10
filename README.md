![Screenshot 1](images/Screenshot1.png)

# japanese_hiragana_watch

I have created this small application to put it in a Raspberry Pi and help my Japanese learning curve. It shows the date and the time in hiragana.
If configured, it creates a slideshow of your most recent favorite photos in Google Photos.

# To make it work on a Raspberry Pi

1. Open a terminal on your Raspberry Pi.

2. Edit the locale configuration file:
```sudo nano /etc/locale.gen```

3. Find the line that says `# ja_JP.UTF-8 UTF-8` and uncomment it by removing the `#` at the beginning of the line.

4. Save the file and exit the editor (in nano, press Ctrl+X, then Y, then Enter).

5. Generate the new locale:
```sudo locale-gen```

6. Update the locale settings:
```sudo update-locale```

7. Install pygame, google authentication stuff and Japanese truetype font
```sudo apt-get install python3-pygame python3-google-auth-httplib2 python3-google-auth-oauthlib fonts-horai-umefont ```

8. Reboot your Raspberry Pi:
```sudo reboot```

9. If you want to make a slide show of your own photos, go to https://console.cloud.google.com/ and get the `credentials.json` file:

    1. Go to the Google Cloud Console (https://console.cloud.google.com/)
    2. Create a new project or select an existing one
    3. Enable the Google Photos Library API for your project
    4. Go to the "Credentials" section
    5. Create a new OAuth 2.0 Client ID (choose "Desktop app" as the application type)
    6. Download the client configuration file, which will be your credentials.json
    7. Put the credentials.json file in the same directory as the rest of the clock's files

10. Adjust `config.ini` by setting the right options for Raspberry Pi (and slide show if you want)

11. Run the script:
```./japanese_hiragana_watch.py```

12. If you decided to enable the slideshow, log into your google account when asked for it.

*NOTE*: If you are curious, this application generates a log file named `watch.log` in the same directory is launched.

To exit use the `Esc` key or `Ctrl+C`
