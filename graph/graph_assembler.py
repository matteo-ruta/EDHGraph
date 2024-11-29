import sys
from file_manag import FileManag

DEFALUT_DECKLIST_PER_UPDATE = 10

if __name__ == "__main__":

    n_decklists = DEFALUT_DECKLIST_PER_UPDATE
    if len(sys.argv) > 1:
        n_decklists = sys.argv[1]

    with FileManag() as fm:
        itsOver = False
        while not itsOver:
            nodes_dict = {}
            edges_dict = {}

            for deck in fm.getNextDecklists(n_decklists):
                # check if we reached the end
                itsOver = deck == []

                if not itsOver:
                    # alg 1:
                    # count each card
                    for card_name in deck:
                        nodes_dict[card_name] += 1

                    # alg 2:
                    # count each pair
                    for card_name_1 in deck:
                        first_index = deck.index(card_name_1) + 1
                        if first_index < len(deck):
                            for card_name_2 in deck[first_index:]:
                                edges_dict[f"{card_name_1}@{card_name_2}"] += 1 
                                # this field names are so bad, but allow easy implementation on the other side
            
            fm.updateNodes(nodes_dict)
            fm.updateEdges(edges_dict)