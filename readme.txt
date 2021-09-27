the programs is launched using the command line

viewer.py [ -p <pico-8 executable> | -h | -c | -i | -s <season> | -d <day> | -r <stream/Replay url> | -t <team nickname>]

-p <path>   provide the program with the path to the pico-8 executable.
            if not set, the default path is "C:\Program Files (x86)\PICO-8\pico8.exe".
            alternatively, you can set the default path by modifying the "pico_path" variable at line 7 in viewer.py.

            the program requires a purchased of copy of pico-8 to run.
            pico-8 can be purchased on https://www.lexaloffle.com/ or on https://lexaloffle.itch.io/pico-8.

            pico 8 was included in the Bundle for Racial Justice and Equality sold on itch.io during summer 2020,
            so you already own it if you bought the bundle.


-h          print the above string


-c          prefer viewing later games when the ingame days of two games overlap when "-s" and "-d" are used.
            allows you to view the coffee cup.

-i          inverts the case of most the text.
            *purely for visual purposes.


-s <season> search for game start times using https://api.sibr.dev/chronicler/v1 .
-d <day>    if succesful, streams game data from that time using https://api.sibr.dev/replay/v1 .

-r <url>    manually set url to stream data from.

            *if no stream source is by using the above arguments, the program streams data from https://www.blaseball.com/ .


-t <team>   set a team to follow the games of.
            accepts a team's full name, nickname, shorthand, or uuid

            *if the team's name is currently scattered, using uuid is preferred to avoid names getting mixed up.
            *a team's uuid can be copied https://blaseball.com by viewing the team's page, (i.e. https://www.blaseball.com/team/<uuid>)