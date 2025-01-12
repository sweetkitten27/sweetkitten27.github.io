import xbmc, xbmcaddon, xbmcgui, requests
import requests
from bs4 import BeautifulSoup
from ..plugin import Plugin, run_hook
from tabulate import tabulate
import xml.etree.ElementTree as ET

CACHE_TIME = 0  # change to the desired cache time in seconds

sports = ["mlb", "nhl", "nba", "nfl"]
# 
suffixes = {
    "mlb": "WILDCARD",
    "nhl": "CONFERENCE",
    "nba": "CONFERENCE",
    "nfl": "PLAYOFFS"
}

headers = {
    "mlb": ['Team', 'W', 'L', 'GB', "Home", "Away", "Streak", "L10"],
    "nhl": ['Team', 'Played', 'W', 'L', 'OTL', 'PTS', 'ROW', 'HOME', 'ROAD', 'L10', 'STREAK', 'ODDS'],
    "nba": ['Team', 'W', 'L', 'Pct', 'GB', "Home", "DIV", "CONF", "L10", "STREAK", "ODDS"],
    "nfl": ['Team', 'W', 'L', 'Pct', "DIV", "HOME", "AWAY", "DIV", "CONF", "L5", "STREAK"]
}
# textbox = xbmcgui.ControlTextBox(303)



# Add the control to the window
# window.addControl(textbox)
def notification(notify_message: str) -> None:
    class Notify(xbmcgui.WindowXMLDialog):
        KEY_NAV_BACK = 92
        TEXTBOX = 300
        # TEXT = 303
        CLOSEBUTTON = 302
        
        def onInit(self):
            self.getControl(self.TEXTBOX).setText(notify_message)
            
        def onAction(self, action):
            if action.getId() == self.KEY_NAV_BACK:
                self.Close()
    
        def onClick(self, controlId):
            if controlId == self.CLOSEBUTTON:
                self.Close()

        def Close(self):
            self.close()
    
    d = Notify('notify.xml', xbmcaddon.Addon().getAddonInfo('path'), 'Default', '720p')
    d.doModal()
    del d

def scoreboard(sport):
    res = []
    r = requests.get(f"https://sports.yahoo.com/{sport}/scoreboard").text
    soup = BeautifulSoup(r, "html.parser")

    game_lists = soup.find_all('ul')
    for game_list in game_lists:
        games = game_list.find_all('li')

        for game in games:
            team_elements = game.find_all('span', {'data-tst': 'first-name'})

            if len(team_elements) >= 2:
                team1_name = team_elements[0].text + ' ' + team_elements[0].find_next('div', {'class': 'Fw(n) Fz(12px)'}).text
                team2_name = team_elements[1].text + ' ' + team_elements[1].find_next('div', {'class': 'Fw(n) Fz(12px)'}).text

                score_elements = game.find_all('span', {'class': 'YahooSans Fw(700)! Va(m) Fz(24px)!'})
                score1 = score_elements[0].text.strip() if score_elements else ''
                score2 = score_elements[1].text.strip() if score_elements else ''

                inning_element = game.find('div', {'class': 'Ta(end) Cl(b) Fw(b) YahooSans Fw(700)! Fz(11px)!'})
                inning = inning_element.find('span').text.strip()

                network_element = game.find('div', {'class': 'Ta(start) D(b) C(secondary-text)'})
                network = network_element.find_all('span')[-1].text.strip() if network_element else ''

                icon1_element = game.find('img', class_='icon1')
                icon1_source = icon1_element['src'] if icon1_element and 'src' in icon1_element.attrs else 'Image N/A'
                icon1_element = '<texture colordiffuse="white">{}</texture>'.format(icon1_source)

                icon2_element = game.find('img', class_='icon2')
                icon2_source = icon2_element['src'] if icon2_element and 'src' in icon2_element.attrs else 'Image N/A'
                icon2_element = '<texture colordiffuse="white">{}</texture>'.format(icon2_source)
                
                image_element = game.find('img')
                image_source = image_element['src'] if image_element and 'src' in image_element.attrs else 'Image N/A'
                res.append({
                    'team1': team1_name,
                    'team2': team2_name,
                    'score1': score1,
                    'score2': score2,
                    'inning': inning,
                    'network': network,
                    # 'icon1': icon1_source,
                    # 'icon2': icon2_source
                })

    return res

# 
def scoreboard_links(sport):
    res = []

    r = requests.get(f"https://sports.yahoo.com/{sport}/scoreboard").text
    soup = BeautifulSoup(r, "html.parser")

    game_lists = soup.find_all('ul')
    for game_list in game_lists:
        games = game_list.find_all('li')
        for game in games:
            team_elements = game.find_all('span', {'data-tst': 'first-name'})
            if len(team_elements) >= 2:
                team1_name = team_elements[0].text + ' ' + team_elements[0].find_next('div', {'class': 'Fw(n) Fz(12px)'}).text
                team2_name = team_elements[1].text + ' ' + team_elements[1].find_next('div', {'class': 'Fw(n) Fz(12px)'}).text

                score_elements = game.find_all('span', {'class': 'YahooSans Fw(700)! Va(m) Fz(24px)!'})
                score1 = score_elements[0].text.strip() if score_elements else ''
                score2 = score_elements[1].text.strip() if len(score_elements) >= 2 else ''

                inning_element = game.find('div', {'class': 'Ta(end) Cl(b) Fw(b) YahooSans Fw(700)! Fz(11px)!'})
                inning = inning_element.find('span').text.strip() if inning_element else 'n/a'

                network_element = game.find('div', {'class': 'Ta(start) D(b) C(secondary-text)'})
                network = network_element.find_all('span')[-1].text.strip() if network_element else 'Network N/A'
                
                image_element = game.find('img')
                image_source = image_element['src'] if image_element and 'src' in image_element.attrs else 'Image N/A'

                res.append({
                    'title': f'{team1_name} vs {team2_name} | {score1} - {score2} |\nInning: {inning}  TV:{network}',
                    'thumbnail': image_source,
                    'type': 'dir',
                    'search_json': team1_name.lower(),
                    'link': f'https://magnetic1.ratpack.appboxes.co/MAD_TITAN_SPORTS/SPORTS/LEAGUE/titansports_{sport}.json'
                })

    return res

def scoreboard_table(sport):
    res = scoreboard(sport)
    table_headers = ['Team 1', 'Team 2', 'Score 1', 'Score 2', 'Inning', 'Network']
    table = [list(d.values()) for d in res]
    table_str = tabulate(table, table_headers, tablefmt='grid')
    return table_str

def standings(sport):
    res = []

    response = requests.get(f"https://sports.yahoo.com/{sport}/standings/?selectedTab={suffixes[sport]}", headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36"})
    soup = BeautifulSoup(response.content, 'html.parser')
    tbody_tags = soup.find_all('tbody')

    for tbody in tbody_tags:
        rows = tbody.find_all('tr')

        heading_element = tbody.find_previous_sibling("thead").find("span")
        if sport in ["mlb", "nfl"]:
            if heading_element != None:
                heading = heading_element.text
                res.append({
                    'team_name': heading,
                })
        else:
            heading_element = tbody.find_previous_sibling("thead").find("th")
            if heading_element != None:
                heading = heading_element.text
                res.append({
                    'team_name': heading,
                })
        
        for row in rows:
            team_element = row.find('a', class_="C(primary-text)")
            team_name = team_element['title'] if team_element else 'Team N/A'

            record_elements = row.find_all('td', class_="Bdb(primary-border) Ta(end) Px(cell-padding-x)")
            wins = record_elements[0].text.strip()
            losses = record_elements[1].text.strip()
            percentage = record_elements[2].text.strip()
            games_behind = record_elements[3].text.strip()
            home = record_elements[4].text.strip()
            away = record_elements[5].text.strip()
            streak = record_elements[6].text.strip()
            rs = record_elements[7].text.strip()
            ra = record_elements[8].text.strip()
            l10 = record_elements[9].text.strip()
            odds = record_elements[10].text.strip()
            try:
                one = record_elements[11].text.strip()
                two = record_elements[12].text.strip()
            except IndexError:
                one = 'N/A'
                two = 'N/A'

            if sport == "mlb":
                res.append({
                    'team_name': team_name,
                    'wins': wins,
                    'losses': losses,
                    'games_behind': games_behind,
                    'home': home,
                    'away':away,
                    'streak':streak,
                    'l10'  : l10,
                    'one':one,
                    'two':two,
                })

            elif sport == "nhl":
                res.append({
                    'team_name': team_name,
                    'wins': wins,
                    'losses': losses,
                    'percentage': percentage,
                    'games_behind': games_behind,
                    'home': home,
                    'away':away,
                    # 'streak':streak,
                    # 'rs' : rs,
                    'ra' : ra,
                    'l10'  : l10,
                    'odds': odds,
                    'one':one,
                    'two':two,
                })

            elif sport == "nba":
                res.append({
                    'team_name': team_name,
                    'wins': wins,
                    'losses': losses,
                    'percentage': percentage,
                    'games_behind': games_behind,
                    'home': home,
                    'away':away,
                    'streak':streak,
                    'rs' : rs,
                    # 'ra' : ra,
                    # 'l10'  : l10,
                    'odds': odds,
                    'one':one,
                    'two':two,
                })

            elif sport == "nfl":
                res.append({
                    'team_name': team_name,
                    'wins': wins,
                    'losses': losses,
                    'percentage': percentage,
                    'games_behind': games_behind,
                    # 'home': home,
                    # 'away':away,
                    'streak':streak,
                    'rs' : rs,
                    'ra' : ra,
                    'l10'  : l10,
                    'odds': odds,
                    'one':one,
                    'two':two,
                })                     
            else:
                res.append({
                    'team_name': team_name,
                    'wins': wins,
                    'losses': losses,
                    'percentage': percentage,
                    'games_behind': games_behind,
                    'home': home,
                    'away':away,
                    'streak':streak,
                    'rs' : rs,
                    'ra' : ra,
                    'l10'  : l10,
                    'odds': odds,
                    'one':one,
                    'two':two,
                })

    return res
    
def standings_table(sport):
    res = standings(sport)
    table = [list(r.values()) for r in res]
    table_str = tabulate(table, headers[sport], tablefmt='grid')
    return table_str


class YahooScores(Plugin):
    name = "yahoo_scores" 
    priority = 100

    def process_item(self, item):
        if self.name in item:
            sport = item[self.name]
            thumbnail = item.get("thumbnail", "")
            fanart = item.get("fanart", "")
            list_item = xbmcgui.ListItem(item.get("title", item.get("name", "")), offscreen=True)
            list_item.setArt({"thumb": thumbnail, "fanart": fanart})
            item["list_item"] = list_item
            item["is_dir"] = True
            item["link"] = self.name + "/" + sport
            return item
    
    def routes(self, plugin):
        @plugin.route(f"/{self.name}/scoreboard/<sport>")
        def yahoo_scoreboard(sport: str):
            res = scoreboard_table(sport)
            notification(res)
        
        @plugin.route(f"/{self.name}/standings/<sport>")
        def yahoo_standings(sport: str):
            res = standings_table(sport)
            notification(res)
        
        @plugin.route(f"/{self.name}/links/<sport>")
        def yahoo_links(sport: str):
            jen_list = scoreboard_links(sport)
            jen_list = [run_hook("process_item", item) for item in jen_list]
            jen_list = [run_hook("get_metadata", item) for item in jen_list]
            run_hook("display_list", jen_list)
