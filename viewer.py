import subprocess, asyncio, sys, getopt
from requests import get
from json import loads
from blaseball_mike.events import stream_events
from datetime import datetime, timedelta

pico_path = "C:\Program Files (x86)\PICO-8\pico8.exe"

#weather mappings
url = "https://raw.githubusercontent.com/xSke/blaseball-site-files/main/data/weather.json"
weather_json = loads(get(url).text)

async def ticker_event(event, event_old, game_id_old, date_old, game_uuid_old):
    ticker = loads(get(base_url+"/database/globalEvents").text)
    for e in ticker:
        if not e:
            continue

        #print("sending ticker event: "+e["msg"])
        ticker_string = e["msg"]+" "
        pico.stdin.write(ticker_string.encode(encoding="ascii",errors="replace"))
        pico.stdin.flush()
        #print("done")
        pico.stdin.write(">".encode(encoding="ascii",errors="replace"))
        
        if event != event_old:
            #print("retrieved new event")
            event_old = event
            game_id = False

            if "games" in event:
                try:
                    season = event["games"]["sim"]["season"]+1
                    day = event["games"]["sim"]["day"]+1
                    date_string = "_Season "+str(season)+", Day "+str(day)+"."

                    if date_string != date_old:
                        date_old = date_string
                        send(date_string)
                        pico.stdin.flush()

                    for g in event["games"]["schedule"]:
                        if g["awayTeam"]==team or g["homeTeam"]==team:
                            game_id=g
                        if not game_id:
                            game_id=g

                    game_uuid = game_id["id"]
                    if game_uuid != game_uuid_old and get(url=("https://blaseball.com/database/gameById/"+game_uuid)).status_code == 200:
                        game_uuid_old = game_uuid
                        print("Game url: https://blaseball.com/game/"+game_uuid)

                    if game_id_old:
                        if "playCount" in game_id_old:
                            turn = game_id_old["playCount"]
                        else:
                            turn = -1
                    else:
                        turn = -1

                    if "playCount" in game_id:
                       cturn = game_id["playCount"]
                    else:
                        cturn = 0 

                    if game_id and game_id["lastUpdate"] and game_id != game_id_old and (cturn > turn or (game_id_old["gameComplete"] and not game_id["gameComplete"])):
                        game_id_old=game_id
                        send(">_")
                        #game log (2)
                        send(game_id["lastUpdate"].strip())
                        
                        print(game_id["lastUpdate"].strip())

                        send(">")

                        #score display (3)
                        home_score = game_id["homeScore"]
                        away_score = game_id["awayScore"]
                        score_string = "_"+str(home_score)+"^"+str(away_score)+"="
                        
                        send(score_string)

                        send(">")

                        #out,strikes,balls (4)
                        atouts = game_id["halfInningOuts"]
                        atstrikes = game_id["atBatStrikes"]
                        atballs = game_id["atBatBalls"]
                        half_inning_string = "_"+str(atballs)+"^"+str(atstrikes)+"."+str(atouts)

                        send(half_inning_string)

                        send(">")

                        #team score board (5)
                        top = game_id["topOfInning"]
                        if top:
                            outs = 3
                            strikes = 4
                            balls = 4

                            if "awayOuts" in game_id:
                                outs = game_id["awayOuts"]
                            if "awayStrikes" in game_id:
                                strikes = game_id["awayStrikes"]
                            if "awayBalls" in game_id:
                                balls = game_id["awayBalls"]
                        else:
                            outs = 3
                            strikes = 4
                            balls = 4

                            if "homeOuts" in game_id:
                                outs = game_id["homeOuts"]
                            if "homeStrikes" in game_id:
                                strikes = game_id["homeStrikes"]
                            if "homeBalls" in game_id:
                                balls = game_id["homeBalls"]
                        
                        scoreboard_string = "_"+str(balls-1)+"^"+str(strikes-1)+"."+str(outs-1)

                        send(scoreboard_string)

                        send(">")

                        #bases (6)
                        if top:
                            nbases = 4
                            if "awayBases" in game_id:
                                nbases = game_id["awayBases"]
                        else:
                            nbases = 4
                            if "homeBases" in game_id:
                                nbases = game_id["homeBases"]
                        
                        obases = game_id["basesOccupied"]
                        obases_string = "_"

                        for o in obases:
                            obases_string = obases_string+str(o+1)

                        obases_string = obases_string+"^"+str(nbases-1)+"="

                        send(obases_string)

                        send(">")

                        #turn (7)
                        if "playCount" in game_id:
                            turn_string = "_"+str(game_id["playCount"])+"="
                            send(turn_string)

                        send(">")

                        #team names (8)
                        home_name = game_id["homeTeamName"]
                        if len(home_name) > 20:
                            home_name = game_id["homeTeamNickname"]
                        away_name = game_id["awayTeamName"]
                        if len(away_name) > 20:
                            away_name = game_id["awayTeamNickname"]

                        team_name_string = "^_"+home_name+"._"+away_name+"="
                        send(team_name_string)

                        send(">")

                        #inning (9)
                        inning = game_id["inning"]

                        if top:
                            inning_string = "_"+str(inning+1)+"^"
                        else:
                            inning_string = "_"+str(inning+1)+"."

                        send(inning_string+"=")

                        send(">")

                        #weather (10)
                        weather = "_"+weather_json[game_id["weather"]]["name"]+"="

                        send(weather)

                        send(">")

                        #active players (11)

                        if top:
                            if "homePitcherName" in game_id:
                                home_player = initials(game_id["homePitcherName"])
                            else:
                                home_player = "-"
                            
                            if "awayBatterName" in game_id:
                                away_player = initials(game_id["awayBatterName"])
                            else:
                                away_player = "-"
                        else:
                            if "homeBatterName" in game_id:
                                home_player = initials(game_id["homeBatterName"]).strip()
                            
                            if "awayPitcherName" in game_id:
                                away_player = initials(game_id["awayPitcherName"]).strip()

                        send("_"+home_player+"^"+away_player+"=")
                        
                        send("<<<<<<<<<<")
                        pico.stdin.flush()
                except Exception as e:
                    print("error in games: "+str(e))
 
        await asyncio.sleep(2)
        send("|")
    return event_old, game_id_old, date_old, game_uuid_old

def send(string : str):
    if not invert:
        string = string.swapcase()
    pico.stdin.write(string.encode(encoding="ascii",errors="replace"))

def initials(string : str):
    strings = string.split()
    return "".join([f"{n[0]}." for n in strings])

async def playback():
    eo = False
    go = False
    do = False
    io = False
    while not pico.poll():
        try:
            async for e in stream_events(url=stream_url, retry_base=0.5, retry_max=300):
                if not e:
                    continue
                eo, go, do, io = await ticker_event(e, eo, go, do, io)
        except OSError:
            sys.exit("OSError: [Errno 22] Invalid argument, Pico-8 was likely closed")

if __name__ == "__main__":
    invert = False
    season = False
    day = False
    team = False
    coffee = False
    base_url = "https://blaseball.com"
    stream_url = "https://blaseball.com/events/streamData"

    try:
        opts, args = getopt.getopt(sys.argv[1:],"hp:ir:s:d:t:c")
    except getopt.GetoptError:
        print("viewer.py [ -p <pico-8 executable> | h | -c | -i | -s <season> | -d <day> | -r <stream/Replay url> | -t <team nickname>]")
        sys.exit(2)
    
    for opt, arg in opts:
        if opt == '-h':
            print("viewer.py [ -p <pico-8 executable> | -c | -i | -s <season> | -d <day> | -r <stream/Replay url> | -t <team nickname>]")
            sys.exit()
        elif opt == "-p":
            pico_path = arg
        elif opt == "-i":
            invert = True
        elif opt == "-b": #deactivated
            base_url = "https://before.sibr.dev"
            stream_url = "https://before.sibr.dev/events/streamData"
        elif opt == "-r":
            stream_url = arg
        elif opt == "-s":
            season = int(arg)
        elif opt == "-d":
            day = int(arg)
        elif opt == "-t":
            for t in loads(get("https://blaseball.com/database/allTeams").text):
                if t["nickname"].lower() == arg.lower() or t["shorthand"].lower() == arg.lower() or t["fullName"].lower() == arg.lower() or t["id"] == arg:
                    team = t["id"]
                    break
            if not team:
                print("Team name not found")
        elif opt == "-c":
            coffee = True

    if season and day:
        time_map = loads(get("https://api.sibr.dev/chronicler/v1/time/map").text)
        start_time = False
        if day == 1:
            for times in time_map["data"]:
                if times["season"] == season - 1 and times["day"] == day:
                    start_time = datetime.strptime(times["startTime"], "%Y-%m-%dT%H:%M:%S.%fZ") - timedelta(hours=1)
                    start_time = start_time.isoformat()+"Z"
                    if not coffee:
                        break
        else:
            for times in time_map["data"]:
                if times["season"] == season - 1 and times["day"] == day - 1:
                    start_time = str(times["startTime"])
                    if not coffee:
                        break

        if not start_time:
            start_time = str(time_map["data"][-1]["startTime"])

        stream_url = "https://api.sibr.dev/replay/v1/replay?from="+start_time

    print("Stream url: "+stream_url)

    pico = subprocess.Popen(pico_path+" -windowed 1 -run "+sys.path[0]+"/blaseball.p8", stdin=subprocess.PIPE, stderr=subprocess.PIPE)
    loop = asyncio.get_event_loop()
    loop.create_task(playback())
    loop.run_forever()