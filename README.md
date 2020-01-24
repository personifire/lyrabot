It's a bot. Named Lyra.

# Setup
Use a virtual environment. Requirements are in the requirements.txt. Use Python 3.5.3 or higher.

# Running
Do this thing
```$ python3 Lyra.py [discord bot token]```

Lyra will look for a file named `token.txt` that will contain the discord bot api token on the first line. If that file is not found, and none is provided, Lyra will not be able to start.

If passed an api token, Lyra will preferentially use that instead. However, `token.txt` will not be overwritten if it already exists.
