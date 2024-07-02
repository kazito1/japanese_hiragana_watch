# japanese_hiragana_watch

I have created this small application to put it in a Raspberry Pi and help my Japanese learning curve.

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

7. Install pygame and Japanese truetype font
```sudo apt-get install python3-pygame fonts-horai-umefont```

8. Reboot your Raspberry Pi:
```sudo reboot```

9. Adjust `config.ini` by setting the right options for Raspberry Pi

10. Run the script:
```./japanese_hiragana_watch.py```

To exit use the `Esc` key or `Ctrl+C`
