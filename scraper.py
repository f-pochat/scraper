import json
import requests
from bs4 import BeautifulSoup

URL = "https://www.promiedos.com.ar"


def find_leagues(obj, depth=0):
    """Recursively search the JSON structure for league data."""
    if depth > 5:
        return []
    if isinstance(obj, list):
        for item in obj:
            result = find_leagues(item, depth + 1)
            if result:
                return result
    elif isinstance(obj, dict):
        if "games" in obj and "name" in obj:
            return [obj]
        for val in obj.values():
            if isinstance(val, list) and val and isinstance(val[0], dict):
                if any("games" in item for item in val if isinstance(item, dict)):
                    return val
            result = find_leagues(val, depth + 1)
            if result:
                return result
    return []


def fetch_matches():
    resp = requests.get(URL, timeout=10)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")
    script_tag = soup.find("script", id="__NEXT_DATA__")
    if not script_tag:
        print("Could not find __NEXT_DATA__ on the page.")
        return

    data = json.loads(script_tag.string)
    page_props = data.get("props", {}).get("pageProps", {})

    leagues = page_props.get("leagues", []) or find_leagues(page_props)
    if not leagues:
        print("No league data found.")
        return

    liga = next(
        (l for l in leagues if "argentina" in l.get("name", "").lower() and "liga" in l.get("name", "").lower()),
        None,
    )
    if not liga:
        print("Liga Profesional not found. Available leagues:")
        for l in leagues:
            print(f"  - {l.get('name')}")
        return

    games = liga.get("games", [])
    if not games:
        print("No matches found.")
        return

    round_name = games[0].get("stage_round_name", "")
    print(f"{'='*56}")
    print(f"  {liga['name']} - {round_name}")
    print(f"{'='*56}")
    print()

    for game in games:
        teams = game.get("teams", [])
        scores = game.get("scores", [None, None])
        status = game.get("status", {}).get("name", "")
        start_time = game.get("start_time", "")

        home = teams[0]["name"] if len(teams) > 0 else "?"
        away = teams[1]["name"] if len(teams) > 1 else "?"

        home_score = scores[0] if scores[0] is not None else "-"
        away_score = scores[1] if scores[1] is not None else "-"

        print(f"  {home:>20}  {home_score} - {away_score}  {away:<20}  [{status}] {start_time}")

    print()


if __name__ == "__main__":
    fetch_matches()
