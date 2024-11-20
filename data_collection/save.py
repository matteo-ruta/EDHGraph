import json
import os

STORAGE_REPOSITORY = ".\\data_collection\\decks\\"
SAVE_INFO_REPOSITORY = "save\\"
HISTORY_INDEX_FILE = "history_index.txt"
HISTORY_FILE_PREF = "history_"
HISTORY_FILE_EXT = ".json"
VOCAB_FILE = "vocab.txt"

BATCH_SIZE = 10

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

    def _extract_history_index(self, history_index_txt: str):
        # remove the \n character at the end if present
        while history_index_txt.endswith("\n"):
            history_index_txt = history_index_txt[:-1]

        history_index_entry_list = history_index_txt.split("\n")
        # fill self._history_index as a list of lists
        # dim 1 = n. of history_#.json files
        # dim 2 = n. of commanders in that history_#.json file
        for history_index_entry in history_index_entry_list:
            self._history_index.append(history_index_entry.split("@"))

    def _check_all_history_files(self):
        directory_path = os.path.dirname(f"{STORAGE_REPOSITORY}{SAVE_INFO_REPOSITORY}")
        history_file_paths_list = [file_name for file_name in os.listdir(directory_path) if file_name.endswith(HISTORY_FILE_EXT)]
        try:
            for history_file_path in history_file_paths_list:
                with open(f"{STORAGE_REPOSITORY}{SAVE_INFO_REPOSITORY}{history_file_path}", "r", encoding="utf-8") as f:
                    _ = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            return False
        return True
    
    def _save_history_batch(self):
        path = f"{STORAGE_REPOSITORY}{SAVE_INFO_REPOSITORY}{HISTORY_FILE_PREF}{self._current}{HISTORY_FILE_EXT}"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self._history_batch, f, indent="\t")

    def _load_history_batch(self, batch):
        path = f"{STORAGE_REPOSITORY}{SAVE_INFO_REPOSITORY}{HISTORY_FILE_PREF}{batch}{HISTORY_FILE_EXT}"
        with open(path, "r", encoding="utf-8") as f:
            self._history_batch = json.load(f)

    # context manager methods

    def __enter__(self):
        try:
            with open(f"{STORAGE_REPOSITORY}{SAVE_INFO_REPOSITORY}{VOCAB_FILE}", "r", encoding="utf-8") as f:
                text = f.read()
                if text != "":
                    self._vocab = text.split("\n")[:-1]
                    print(f"Vocabulary restored, {len(self._vocab)} commanders identified")
                else:
                    raise FileNotFoundError
        except FileNotFoundError:
            print("Vocabulary not found, using empty one")

        try:
            with open(f"{STORAGE_REPOSITORY}{SAVE_INFO_REPOSITORY}{HISTORY_INDEX_FILE}", "r", encoding="utf-8") as f:
                self._extract_history_index(f.read()) # saved in self._history_index
                print(f"History index restored, {len(self._history_index)} files identified")
        except FileNotFoundError:
            self.history = {}
            print("History not found or wrongly formatted, new empty on just created")

        #print(self._vocab, self.history)
        # XOR to see if there are incoherences
        assert bool(self._vocab) == bool(self._history_index), "AssertionError: incoherence found with your saved state. Please backup your progresses and clear history.json and vocab.txt before restarting"
        assert self._check_all_history_files(), "AssertionError: history files corrupted, some data is missing. Unable to restart the operations"

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self._vocab != []:
            with open(f"{STORAGE_REPOSITORY}{SAVE_INFO_REPOSITORY}{VOCAB_FILE}", "w", encoding="utf-8") as f:
                for entry in self._vocab:
                    f.write(entry + "\n")

        if self._history_index != []:
            # save the (unique) loaded batch
            self._save_history_batch()

            # save the index
            with open(f"{STORAGE_REPOSITORY}{SAVE_INFO_REPOSITORY}{HISTORY_INDEX_FILE}", "w", encoding="utf-8") as f:
                for line in self._history_index:
                    f.write("@".join(line) + "\n")

        print("Progress saved")

    # public methods
    
    def __init__(self, create_key: object):
        assert create_key == StorageManager._create_key, "AssertionError: StorageManager must be created using getStorageManager() class method"
        self._history_index = []
        self._history_batch = {}
        self._vocab = []
        self._current = -1 # at the first iteration, no meaningful value of this parameter exists

    def getAlreadySavedUrlhashes(self, commander: str) -> list:
        if self._current not in range(len(self._history_index)) or commander not in self._history_index[self._current]:
            if self._current in range(len(self._history_index)):
                self._save_history_batch() # before any change, save the progress (if any)
            # if self._current is out of range, it means we have no progress loaded, and we need to do the initial loading

            try:
                # no index modifications

                # NB what you see in parenthesis is very bad, but per se the list comprehension returns a generator object, not the element bacth
                self._current = self._history_index.index([batch for batch in self._history_index if commander in batch][0])
                self._load_history_batch(self._current) # loading the batch with the commander already saved

                # no batch modifications
            except (ValueError, IndexError) as e:
                if len(self._history_index[-1]) < BATCH_SIZE:
                    self._history_index[-1].append(commander) # adding a new commander to the current batch in the index
                    
                    self._current = len(self._history_index) - 1
                    self._load_history_batch(self._current) # loading the batch that has some space inside
                    
                    self._history_batch[commander] = [] # creating a new list in the current batch for this commander
                else:
                    self._history_index.append([commander]) # creating a new entry in the index
                    
                    self._current = len(self._history_index) - 1
                    # no batch loading from disk (since it's brand new)
                    
                    self._history_batch = {commander: []} # creating a new batch
                    # the json file will be created the next time _save_history_batch() will be invoked

        return self._history_batch[commander]

    def saveDeck(self, deck: "Deck"):
        try:
            index = self._vocab.index(deck.name)
        except ValueError:
            # update vocab
            self._vocab.append(deck.name)
            index = len(self._vocab) - 1
            self._create_new_storage_file(index)

        # update history
        self._history_batch[deck.name].append(deck.urlhash)

        with open(STORAGE_REPOSITORY + f"{index}.txt", "a", encoding="utf-8") as f:
            for card in deck.cards:
                f.write(f"{card}\n")
            f.write("\n")

class Deck():

    # static methods
    @staticmethod
    def getErrorDeck():
        return Deck("", [], [])

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
        self.has_partner = commanders[1] != None if not self.isError() else None
        self.name = self._get_name() if not self.isError() else None

    def isError(self) -> bool:
        return self.commanders == []