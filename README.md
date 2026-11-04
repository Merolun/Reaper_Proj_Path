# Reaper_Proj_Path

A ReaScript that writes the path of the current Reaper project into the **Notes** of the objects selected in Wwise, through WAAPI.

Run it from a keyboard shortcut: every selected Wwise object gets the `.rpp` path on a new line in its Notes. Objects that already contain the path are left alone, so pressing the shortcut twice is safe.

## Demo

[Watch the step-by-step demo](media/demo.mp4) (about 1 min 15 s, no audio).

## Install (Windows)

1. Install [Python](https://www.python.org/downloads/) and tick **Add Python to PATH**.
2. Double-click `install_dependencies.bat`.
3. In Reaper:
   - **Options > Preferences > Plug-ins > ReaScript**: tick **Enable Python for use with ReaScript**. If it says "No compatible version of Python was found", set **Custom path to Python dll directory** to your Python install folder (for example `C:\Users\<you>\AppData\Local\Programs\Python\Python313`) and **Force ReaScript to use specific Python .dll** to your DLL name (for example `python313.dll`). Click OK and restart Reaper.
   - **Actions > Show action list > New action > Load ReaScript...** and pick `reaper_to_wwise.py`.
   - Right-click the new action to assign a keyboard shortcut.

In Wwise, WAAPI must be enabled (**Project > User Preferences > Enable Wwise Authoring API**).

## Use

1. Save your Reaper project.
2. Select one or more objects in Wwise.
3. Press your shortcut. The Reaper console reports how many objects were updated.

If something is wrong (project not saved, Wwise not running, nothing selected, library missing), the console says what to do.

## Development

```
pip install -r requirements-dev.txt
pytest
```

## License

[MIT](LICENSE) - Kevin PANCHOUT ([Merolun](https://github.com/Merolun))
