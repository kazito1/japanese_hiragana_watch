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

9. Adjust `config.ini` by setting the right options for Raspberry Pi (and slide show if you want). For the slideshow, make sure to copy your photos in the directory you configure in `config.ini`

10. Run the script:
```./japanese_hiragana_watch.py```

11. If you decided to enable the slideshow, log into your google account when asked for it.

*NOTE*: If you are curious, this application generates a log file named `watch.log` in the same directory is launched.

To exit use the `Esc` key or `Ctrl+C`
