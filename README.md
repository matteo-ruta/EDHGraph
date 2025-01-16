_Magic The Gathering_ is a very extended trading card game that can be played in many different ways. Each of these ways is called a _format_. In this project, we propose an analysis of the Commander format via network. The data has been collected from [EDHRec](https://www.EDHRec.com).

## Data collection
EDHRec is a useful tool for searching Commander decks. Using web scraping, we inspected the data collected upon these decks to select a sample of the whole database. In Commander, each deck must have a representative card, called _commander_. To get a representative sample of the EDHRec database (that we assume represents the metagame - the "state", so to say - of the format), we decided first to select a bunch of commanders among the most popular and then to retrieve several decklists for each commander related to its popularity.

We first looked at the 600 most used commanders on EDHRec, getting information on related colours and common subtypes. We used these data as features for a PCA (Principal Component Analysis), which projected our data into a 2-dimensional space. From there, we used Lloyd's algorithm and k-means++ to solve a k-means clustering problem. We choose k=100, so each cluster is expected to be of size 6. From the clusters, we identified the closest point from the centroid (a "proxy" for that centroid), whose function is to represent the whole cluster for our data sample. In total, we ended up with 100 commanders (one for each cluster).

From this list of commanders, we looked at the amount of decks $d_c$ for each commander $c$ on EDHRec. We computed the ratio between that number and the total number of possible decklists we could choose using only the commanders in our list. We call this value

$$p_c=\frac{d_c}{\sum_{c'}{d_{c'}}}$$

This number represents the probability that we could get a deck for commander $c$ if we had only decks from commanders in the list in our dataset. We also choosed the total number of decks to download $M$, with $M<\sum_{c'}{d_{c'}}$, then we computed the number of decks to download for each commander using $d_c^{final}=d_c*M$

## Graph creation
Once we had the set of decklists, we proceed to create our graph. Each node is associated to unique card, and 2 cards are linked with an edge if and only if they appeared in the same decklist at least once. Each edge is weighted with the exact amount of deckists which contains both cards. During the computation of the centralities, we exchanged these values in order to get a proper significance for our scores.

# Repository Content

## data_collection
Contains all the code relative to the creation of the net, from the scraping part to the construction of the graph.
- `input.txt`: contains the updated version of the input for `request.py`, so basically which and how many decks were downloaded. Was populated by `dim_reduction.py`
- `request.py`: script that downloads decks as specified in `input.txt`
- `dim_reduction.py`: gathered the information stored in `top_commaders` directory and computes a PCA + clustering as specified above. It stores the output in `input.txt`
- `dim_reduction_model.pkl`: scikit-learn model used for the PCA + clustering part in `dim_reduction.py` NOTE: in order to get the same result, you shall put this file in the same folder of `dim_reduction.py` before run it on local!
## graph
Contains the notebook `Graph.ipynb`, which contains the code for the graph creation, save and the computation of the embedding and the clustering we used for the analysis.