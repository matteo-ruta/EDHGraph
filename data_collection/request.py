from pyedhrec import EDHRec
import sys
import json
import requests
import time
from bs4 import BeautifulSoup
from save import Deck, StorageManager

BAR_SIZE = 20
AVG_SLEEP_TIME = 2.5

def get_decklist_from_urlhash(urlhash) -> Deck:
    url = f"https://edhrec.com/deckpreview/{urlhash}"
    response = requests.get(url)
    response.raise_for_status()

    # Parse the HTML content
    soup = BeautifulSoup(response.text, 'html.parser')

    script_tag = soup.find('script', id='__NEXT_DATA__')

    # Extract the content of the <script> tag (which is JSON)
    json_data = script_tag.string

    data = json.loads(json_data)
    deck_data = data['props']['pageProps']['data']

    cards = deck_data.get('cards', [])
    commanders = deck_data.get('commanders', [])

    return Deck(urlhash, commanders, cards)

if __name__ == "__main__":

    input_path = sys.argv[1]
    with open(input_path, "r", encoding="utf-8") as f:
        args = f.read()

    # getting arguments
    commanders_list = []
    quantity_list = []
    arg_list = args.split("\n")
    for arg in arg_list:
        commander, quantity = arg.split("-")
        commanders_list.append(commander)
        quantity_list.append(int(quantity))
    
    edhrec = EDHRec()
    
    ## NB:
    # partners must be written in sequential order (no separators)

    print(f"Starting data fetching session for {len(commanders_list)} commanders")

    with StorageManager.getStorageManager() as save:
        for i in range(len(commanders_list)):
            commander = commanders_list[i]
            quantity = quantity_list[i]

            print(f"Requesting decks for \'{commander}\' - {i + 1}/{len(commanders_list)}")

            request = edhrec.get_commander_decks(commander)

            urlhash_list = [deck["urlhash"] for deck in request["table"]]

            # removing already saved decks from the checklist
            if commander in save.history.keys():
                already_saved_urlhash_list = save.history[commander]
                urlhash_list = [urlhash for urlhash in urlhash_list if urlhash not in already_saved_urlhash_list]

            # reduce the checklist to the specified size
            urlhash_list = urlhash_list[:quantity]

            total_decks = len(urlhash_list)
            counter = 0

            # init of the fancy progress-bar
            print(f"[{'.' * BAR_SIZE}] {0.00:.2f}%", end="\r")

            for urlhash in urlhash_list:
                decklist = get_decklist_from_urlhash(urlhash)
                save.saveDeck(decklist)

                # fancy progress-bar
                counter += 1
                percentage = counter / total_decks * 100
                if counter < total_decks:
                    done = round(percentage / 100 * BAR_SIZE)
                    print(f"[{'=' * done}{'.' * (BAR_SIZE - done)}] {percentage:.2f}%", end="\r")
                else:
                    done = BAR_SIZE
                    print(f"[{'=' * done}{'.' * (BAR_SIZE - done)}] {percentage:.2f}%", end="\n")

                # avoid congestion
                time.sleep(1.75)