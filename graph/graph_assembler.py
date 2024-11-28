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
            for deck in fm.getNextDecklists(n_decklists):
                # check if we reached the end
                itsOver = deck == []

                if not itsOver:
                    # alg 1:
                    # count each card

                    # alg 2:
                    # count each pair
                    pass
            
            # send the updates to the file_manager