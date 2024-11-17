from local_secrets import API_KEY
import requests
import json
from statbotics import Statbotics as StatBotics

sb = StatBotics()

# load in teams_epa_data.json as teams_epa_data
with open("teams_epa_data.json", "r") as f:
    teams_epa_data = json.load(f)

BASE_URL = "https://www.thebluealliance.com/api/v3"
HEADERS = {
    "X-TBA-Auth-Key": API_KEY
}

# Get a list of all events in a given year
def get_events(years):
    events_data = []
    for year in years:
        url = f"{BASE_URL}/events/{str(year)}"
        response = requests.get(url, headers=HEADERS)
        events_data.extend(response.json())
    return events_data

# Get a list of all teams at a given event with their OPR
def get_oprs(event_key):
    url = f"{BASE_URL}/event/{event_key}/oprs"
    response = requests.get(url, headers=HEADERS)
    try:
        return response.json()
    except Exception as e:
        print(f"Error getting OPRs for {event_key}: {e}")
        return {}

# Get team statuses for a given event
def get_team_statuses(event_key):
    event_key = '2024caph'
    url = f"{BASE_URL}/event/{event_key}/teams/statuses"
    response = requests.get(url, headers=HEADERS)
    return response.json()

# Combine team statuses and OPRs to get a list of all teams at an event with their OPRs and statuses
def get_team_performance_data(event_key, week, state_prov):
    oprs = get_oprs(event_key)
    team_statuses = get_team_statuses(event_key)
    team_performance_data = []
    try:
        for team_key in team_statuses.keys():
            if team_key == "frc1678":
                print("weekend")
            opr = oprs["oprs"][team_key] if "oprs" in oprs and team_key in oprs["oprs"] else None
            qual_ranking = team_statuses[team_key]["qual"]["ranking"]["rank"] if team_statuses[team_key]["qual"] and "ranking" in team_statuses[team_key]["qual"] and "rank" in team_statuses[team_key]["qual"]["ranking"] else None
            alliance = team_statuses[team_key]["alliance"]["number"] if team_statuses[team_key]["alliance"] else None
            pick = team_statuses[team_key]["alliance"]["pick"] if team_statuses[team_key]["alliance"] else None
            if team_statuses[team_key]["playoff"]:
                if  team_statuses[team_key]["playoff"]['level'] == 'f':
                    if team_statuses[team_key]["playoff"]["status"] == "won":
                        status = "winner"
                    else:
                        status = "finalist"
                else:
                    status = team_statuses[team_key]["playoff"]["status"]
            else:
                status = None
            team_str = team_key.strip('frc')
            year_int = int(event_key[:4])
            last_year_str = str(year_int-1)
            try:
                last_year_norm_epa = teams_epa_data[team_str][last_year_str]
            except:
                last_year_norm_epa = None
            team_data = {
                "event_key": event_key,
                "team_key": team_key,
                "opr": opr,
                "qual_ranking": qual_ranking,
                "alliance": alliance,
                "pick": pick,
                "status": status,
                "week": week,
                "state_prov": state_prov,
                "last_year_norm_epa": last_year_norm_epa
            }
            team_performance_data.append(team_data)
    except Exception as e:
        print(f"Error getting data for {event_key} {team_key}: {e}")

    return team_performance_data

def get_all_events_teams_performance_data():
    with open("all_teams_performance_data.csv", "w", encoding='utf-8') as f:
        f.write("event_key,team_key,opr,qual_ranking,alliance,pick,status,week,state_prov,last_year_norm_epa\n")
    with open("event_keys.json", "r") as f:
        event_keys = json.load(f)
    for event_key in event_keys:
        # Get week and state_prov for each event which is read from events_file.json
        with open("events_file.json", "r") as f:
            events_data = json.load(f)
            for event in events_data:
                if event["key"] == event_key:
                    if "week" in event and event["week"] is not None:
                        week = event["week"] + 1
                    else:
                        week = None
                    if "state_prov" in event:
                        state_prov = event["state_prov"]
                    else:
                        state_prov = None
        if week is None:
            continue
        teams_performance_data = get_team_performance_data(event_key, week, state_prov)
        with open("all_teams_performance_data.csv", "a", encoding='utf-8') as f:
            for team_data in teams_performance_data:
                f.write(",".join(str(value) for value in team_data.values()) + "\n")
        print(f"Saved {event_key}")

def save_events_to_file(events_data):
    with open("events_file.json", "w", encoding='utf-8') as f:
        json.dump(events_data, f)

def save_event_keys_to_file():
    with open("events_file.json", "r", encoding='utf-8') as f:
        # Make a list of all the event keys
        events_data = json.load(f)
        event_keys = [event["key"] for event in events_data]
    with open("event_keys.json", "w", encoding='utf-8') as f:
        json.dump(event_keys, f)

def get_all_teams_data():
    teams_data = []
    page_num = 0
    while True:
        url = f"{BASE_URL}/teams/{page_num}"
        response = requests.get(url, headers=HEADERS)
        data = response.json()
        if not data:
            break
        teams_data.extend(data)
        page_num += 1
    return teams_data

def save_all_teams_data_to_file(teams_data):
    with open("teams_file.json", "w", encoding='utf-8') as f:
        json.dump(teams_data, f)

# Save events to json file
""" events = get_events([2017, 2018, 2019, 2020, 2022, 2023, 2024])
save_events_to_file(events) """

# Save event keys to json file
""" save_event_keys_to_file() """

# Save all teams data to json file
""" teams_data = get_all_teams_data()
save_all_teams_data_to_file(teams_data) """

# Save all Team Performance Data for all saved events
get_all_events_teams_performance_data()