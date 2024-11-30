import os

RAW_DATA_REPOSITORY = ".\\data_collection\\decks\\"
RAW_FILE_EXT = ".txt"
RESUME_FILE_PATH = ".\\graph\\resume.txt"

NODES_STORAGE_FILE = ".\\graph\\nodes.txt"
EDGES_STORAGE_FILE = ".\\graph\\edges.txt"

class FileManag():

    # init

    def __init__(self):
        self._raw_data_files = [file for file in os.listdir(RAW_DATA_REPOSITORY) if file.endswith(RAW_FILE_EXT)]
        self._current_file = 0
        self._current_deck = 0
        self._file = []

        self._nodes = {}
        self._edges = {}

    # context manager methods
    # we need to keep in memory where to resume (file, deck)

    def __enter__(self):
        try:
            with open(RESUME_FILE_PATH, "r", encoding="utf-8") as f:
                text = f.read()
                if text != "":
                    self._current_file, self._current_deck = tuple([int(value) for value in text.split(";")])
                    print(f"Resume from file {self._current_file}, deck {self._current_deck}")
                else:
                    raise FileNotFoundError
        except FileNotFoundError:
            print("Starting from the beginning")

        try:
            with open(NODES_STORAGE_FILE, "r", encoding="utf-8") as f:
                text = f.read()
                if text != "":
                    while text.endswith("\n"):
                        text = text[:-1]

                    for entry in text.split("\n"):
                        card_name, number = tuple(entry.split("@"))
                        self._nodes[card_name] = number
                    
                    print(f"Found {len(self._nodes)} nodes")
                else:
                    raise FileNotFoundError
        except FileNotFoundError:
            print("No previous node found")

        try:
            with open(EDGES_STORAGE_FILE, "r", encoding="utf-8") as f:
                text = f.read()
                if text != "":
                    while text.endswith("\n"):
                        text = text[:-1]
                        
                    for entry in text.split("\n"):
                        card_pair, number = tuple(entry.split("@"))
                        self._edges[card_pair] = number

                    print(f"Found {len(self._edges)} edges")
                else:
                    raise FileNotFoundError
        except FileNotFoundError:
            print("No previous edge found")

        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        with open(RESUME_FILE_PATH, "w", encoding="utf-8") as f:
            f.write(f"{self._current_file};{self._current_deck}")

        if self._nodes != {}:
            with open(NODES_STORAGE_FILE, "w", encoding="utf-8") as f:
                for card_name, number in self._nodes.items():
                    f.write(f"{card_name}@{number}\n")

        if self._edges != {}:
            with open(EDGES_STORAGE_FILE, "w", encoding="utf-8") as f:
                for card_pair, number in self._edges.items():
                    f.write(f"{card_pair}@{number}\n")

        print("Checkpoint saved")

    # private methods
    
    def _next_file(self) -> bool:
        plain_string = ""
        try:
            with open(f"{RAW_DATA_REPOSITORY}{self._current_file}{RAW_FILE_EXT}", "r", encoding="utf-8") as f:
                plain_string = f.read()
                while plain_string.endswith("\n"):
                    plain_string = plain_string[:-1]

                self._file = [decklist.split("\n") for decklist in plain_string.split("\n\n")]
                self._current_file += 1
                self._current_deck = 0
        except FileNotFoundError as e:
            print("Next file not found, seems it's already over...")
            return False
        
        return True

    # public methods
    
    def getNextDecklist(self) -> list:
        result = []
        if self._current_deck >= len(self._file):
            if self._next_file():
                result = self._file[self._current_deck]
                self._current_deck += 1
        else:
            result = self._file[self._current_deck]
            self._current_deck += 1
        return result
    
    def getNextDecklists(self, n_decklists):
        for i in range(n_decklists):
            yield self.getNextDecklist()
    
    def updateNodes(self, node_values: dict):
        added = 0
        updated = 0
        for card_name in node_values.keys():
            if card_name not in self._nodes.keys():
                self._nodes[card_name] = node_values[card_name]
                added += 1
            else:
                self._nodes[card_name] += node_values[card_name]
                updated += 1
        print(f"Nodes: Added {added}; Updated {updated}")

    def updateEdges(self, edge_values: dict):
        added = 0
        updated = 0
        for card_pair in edge_values.keys():
            if card_pair not in self._edges.keys():
                self._edges[card_pair] = edge_values[card_pair]
                added += 1
            else:
                self._edges[card_pair] += edge_values[card_pair]
                updated += 1
        print(f"Edges: Added {added}; Updated {updated}")