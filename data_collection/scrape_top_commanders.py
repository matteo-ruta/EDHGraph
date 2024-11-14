from bs4 import BeautifulSoup
import requests
import json
import time
import random
from pyedhrec import EDHRec, utils

JSON_URL = "https://json.edhrec.com/pages"
COMMANDERS_URL = "https://edhrec.com/commanders"
STORAGE_REPOSITORY = "C:\\Dati\\Università\\magistrale_pd\\II_anno_I_semestre\\Learning from Networks\\Project\\top_commanders\\"
COMMANDERS_FILE_RADIX = "commanders"
COMMANDERS_FILE_EXT = ".json"
RESUME_FILE = "last_page.txt"
VOCAB_FILE = "vocab.txt"
BASE_DELAY = 1.5

def takeABreath():
    time.sleep(BASE_DELAY + round(random.uniform(0, 0.5), 2))

class GenericEDHRec(EDHRec):
    def __init__(self, cookies: str = None):
        super().__init__(cookies)

    def request_json(self, endpoint: str, params: dict = None):
        """
        Make a generic request to a specified endpoint with optional parameters.

        Args:
            endpoint (str): The endpoint to make the request to.
            params (dict, optional): Dictionary of query parameters for the request.

        Returns:
            dict: The JSON response from the request.
        """
        url = f"{JSON_URL}/{endpoint}"
        response = self.session.get(url, params=params)
        response.raise_for_status()  # Raises an error for 4xx/5xx responses
        return response.json()

def extractCommandersInfoFromJSON(data, edhrec: GenericEDHRec, vocab: list) -> list:
    result = []

    with open("debug.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
    
    commanders_dict = data["cardviews"]

    for commander in commanders_dict:
        new_entry = {}

        print(f"Looking at {commander["name"]}")
        new_entry["name"] = commander["name"]
        new_entry["decks"] = commander["num_decks"]

        commander_details = edhrec.get_commander_data(commander["sanitized"])

        new_entry["color_identity"] = commander_details["container"]["json_dict"]["card"]["color_identity"]

        for tag in commander_details["panels"]["taglinks"]:
            new_entry[tag.get("value")] = tag.get("count")

            # filling the vocabulary used for the dimensionality reduction
            if tag.get("value") not in vocab:
                vocab.append(tag.get("value"))
        
        """
        if "is_partner" in commander.keys():
            query_result_0 = edhrec.get_card_details(commander["cards"][0]["url"])
            takeABreath()
            query_result_1 = edhrec.get_card_details(commander["cards"][1]["url"])

            color_id_0 = query_result_0["color_identity"]
            color_id_1 = query_result_1["color_identity"]
            
            new_entry["color_identity"] = color_id_0 + [color for color in color_id_1 if color not in color_id_0]
        else:
            query_result = edhrec.get_card_details(commander["sanitized"])

            new_entry["color_identity"] = query_result["color_identity"]
        """

        # various tags: get_commander_data -> panel -> taglinks
        # single comm color id: // -> container -> json_dict -> card
        # double comm color id: same!

        takeABreath()
        result.append(new_entry)

    return result

class SaveContext():

    # context manager methods

    def __enter__(self):
        try:
            with open(STORAGE_REPOSITORY + RESUME_FILE, "r", encoding="utf-8") as f:
                text = f.read()
                if text != "":
                    self.last_page = text

                    # getting page counter
                    string, _ = tuple(self.last_page.rsplit(".", 1))
                    _, string = (tuple(string.rsplit("-", 1)))
                    assert string.isnumeric(), "FATAL ERROR: encoding of next page json not coherent with the assumptions. Something changed in EDHRec API or this programmer sucks"
                    self.last_page_counter = int(string)
                    
                    print(f"... from page n. {self.last_page_counter}")
                else:
                    raise FileNotFoundError
        except FileNotFoundError:
            self.last_page = ""
            self.last_page_counter = -1
            print("... for the first time")

        # read vocab
        try:
            with open(STORAGE_REPOSITORY + VOCAB_FILE, "r", encoding="utf-8") as f:
                text = f.read()
                if text != "":
                    self.vocab = text.split("\n")
                    print(f"Vocabulary found")
                else:
                    raise FileNotFoundError
        except FileNotFoundError:
            self.vocab = []
            print("Vocabulary not found")

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self.last_page != "":
            with open(STORAGE_REPOSITORY + RESUME_FILE, "w", encoding="utf-8") as f:
                f.write(self.last_page)

        if self.vocab != []:
            with open(STORAGE_REPOSITORY + VOCAB_FILE, "w", encoding="utf-8") as f:
                for entry in self.vocab:
                    f.write(entry + "\n")

        print(f"Saved until page n. {self.last_page_counter} (excluded)")

if __name__ == "__main__":
    print("Starting...")

    edhrec = GenericEDHRec()

    response = requests.get(COMMANDERS_URL)
    takeABreath()

    soup = BeautifulSoup(response.text, 'html.parser')

    script_tag = soup.find('script', id='__NEXT_DATA__')
    json_data = script_tag.string
    # we want to pass the cardlists object, since is what can be retrived from the button click "Load more"
    data = json.loads(json_data)["props"]["pageProps"]["data"]["container"]["json_dict"]["cardlists"][0]
    next_page = data["more"] # assimung the first time is present as field

    with SaveContext() as save:
        page_count = -1
        
        while next_page:

            if page_count >= save.last_page_counter:
                print(f"Reading page {page_count + 1}...")
                save.last_page_counter = page_count

                retrieved_commanders = extractCommandersInfoFromJSON(data, edhrec, save.vocab)

                with open(f"{STORAGE_REPOSITORY}{COMMANDERS_FILE_RADIX}{page_count + 1}{COMMANDERS_FILE_EXT}", "w", encoding="utf-8") as f:
                    json.dump(retrieved_commanders, f, indent=4)
                    
                save.last_page = next_page

            # go ahead
            if "more" in data.keys():
                next_page = data["more"]
                data = edhrec.request_json(next_page)
            else:
                next_page = None

            page_count += 1