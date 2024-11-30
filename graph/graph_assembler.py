import sys
from file_manag import FileManag

DEFALUT_DECKLIST_PER_UPDATE = 10

BASIC_LANDS = ["Forest", "Plains", "Island", "Mountain", "Swamp"]

def removeListOfCards(target_list: list, remove_list: list):
    for remove_card in remove_list:
        try:        
            target_list.remove(remove_card)
        except ValueError:
            pass

if __name__ == "__main__":

    n_decklists = DEFALUT_DECKLIST_PER_UPDATE
    if len(sys.argv) > 1:
        n_decklists = sys.argv[1]

    with FileManag() as fm:
        itsOver = False
        counter = 0
        while not itsOver:
            nodes_dict = {}
            edges_dict = {}

            for deck in fm.getNextDecklists(n_decklists):
                # check if we reached the end
                itsOver = deck == []

                if not itsOver:
                    counter += 1
                    # preproc
                    # remove basic lands
                    removeListOfCards(deck, BASIC_LANDS)

                    # alg 1:
                    # count each card
                    for card_name in deck:
                        if card_name not in nodes_dict:
                            nodes_dict[card_name] = 1
                        else:
                            nodes_dict[card_name] += 1

                    # alg 2:
                    # count each pair
                    for card_name_1 in deck:
                        first_index = deck.index(card_name_1) + 1
                        if first_index < len(deck):
                            for card_name_2 in deck[first_index:]:
                                card_pair = f"{card_name_1}@{card_name_2}" if card_name_1 > card_name_2 else f"{card_name_2}@{card_name_1}"
                                # this field names are so bad, but allow easy implementation on the other side

                                if card_pair not in edges_dict:
                                    edges_dict[card_pair] = 1
                                else:
                                    edges_dict[card_pair] += 1 
            
            fm.updateNodes(nodes_dict)
            fm.updateEdges(edges_dict)

            print(f"Done {counter} decks\n>")