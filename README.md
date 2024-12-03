# Train Check

A project to use a waveshare e-paper (specifically the 4.2 inch model) connected to a Raspberry Pi to display train times in the UK.

The project uses the excellent API available from [realtimetrains.co.uk](realtimetrains.co.uk).

At present defaults to 6am and 7am in the morning to display next day's results.

## Dependencies required

For the best results, use a virtual environment in Python. You can use `python venv -m /path/to/env` to create.

Use `pip install` on your raspberry pi for the following:

- waveshare-epaper
- pillow
- gpiozero
- gpiod
- lgpio
- requests