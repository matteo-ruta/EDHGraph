import json
import os

STORAGE_REPOSITORY = ".\\data_collection\\decks\\"
VOCAB_STORAGE_FILE = "vocab.txt"
URLHASH_STORAGE_FILE = "progress.json"

class StorageManager():

    _create_key = object()
    singleton = None

    @classmethod
    def getStorageManager(cls) -> "StorageManager":
        if not cls.singleton:
            cls.singleton = StorageManager(cls._create_key)
        return cls.singleton
    
    # private methods

    def _create_new_storage_file(self, deck_index):
        directory_path = os.path.dirname(STORAGE_REPOSITORY)
        _ = os.path.join(directory_path, f"{deck_index}.txt")

    # context manager methods

    def __enter__(self):
        try:
            with open(STORAGE_REPOSITORY + VOCAB_STORAGE_FILE, "r", encoding="utf-8") as f:
                text = f.read()
                if text != "":
                    self.vocab = text.split("\n")[:-1]
                    print(f"Vocabulary restored, {len(self.vocab)} commanders identified")
                else:
                    raise FileNotFoundError
        except FileNotFoundError:
            self.vocab = []
            print("Vocabulary not found, new empty one just created")

        try:
            with open(STORAGE_REPOSITORY + URLHASH_STORAGE_FILE, "r", encoding="utf-8") as f:
                self.history = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            self.history = {}
            print("History not found or wrongly formatted, new empty on just created")

        print(self.vocab, self.history)
        # XOR to see if there are incoherences
        assert bool(self.vocab) == bool(self.history), "AssertionError: incoherence found with your saved state. Please backup your progresses and clear history.json and vocab.txt before restarting"

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self.vocab != []:
            with open(STORAGE_REPOSITORY + VOCAB_STORAGE_FILE, "w", encoding="utf-8") as f:
                for entry in self.vocab:
                    f.write(entry + "\n")

        if self.history.keys != []:
            with open(STORAGE_REPOSITORY + URLHASH_STORAGE_FILE, "w", encoding="utf-8") as f:
                json.dump(self.history, f, indent="\t")

        print("Progress saved")

    # public methods
    
    def __init__(self, create_key: object):
        assert create_key == StorageManager._create_key, "AssertionError: StorageManager must be created using getStorageManager() class method"

    def saveDeck(self, deck: "Deck"):
        try:
            index = self.vocab.index(deck.name)
        except ValueError:
            self.vocab.append(deck.name)
            index = len(self.vocab) - 1
            self._create_new_storage_file(index)

        # update history
        if deck.name not in self.history.keys():
            self.history[deck.name] = [deck.urlhash]
        else:
            self.history[deck.name].append(deck.urlhash)

        with open(STORAGE_REPOSITORY + f"{index}.txt", "a", encoding="utf-8") as f:
            for card in deck.cards:
                f.write(f"{card}\n")
            f.write("\n")

class Deck():

    # private methods
    def _get_name(self):
        result = f"{self.commanders[0]}"
        if self.has_partner:
            result += f" // {self.commanders[1]}"
        return result

    # public methods
    def __init__(self, urlhash: str, commanders: list, cards: list):
        self.urlhash = urlhash
        self.commanders = commanders
        self.cards = cards
        self.has_partner = commanders[1] != None
        self.name = self._get_name()