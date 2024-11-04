_Magic The Gathering_ is a very extended trading card game, which can be played in many different ways. Each of these way is called _format_. In this project, we propose an analysis of the Commander format via network. The data has been collected from [EDHRec](https://www.EDHRec.com).

## Data collection
EDHRec is a useful tool for searching Commander decks. Using web scraping, we inspected the data collected upon these decks to select a sample of the whole database. In Commander, each deck must have a representative card, called _commander_. In order to get a representative sample of the EDHRec database (that we assume represents the _metagame_ - the "state", so to say -  of the format), we decided to first select a bunch of commanders among the most populars and then to retrieve a number of decklists for each commander related to the it's popularity.

We first looked at the 600 most used commanders on EDHRec, getting information as related colors and common subtypes. We used these data as features for a PCA (Principal Component Analysis), which projected our data into a 2-dimensional space. From there, we used Lloyd's algorithm and k-means++ to solve a k-means clustering problem. We choose k=100, in a way that each cluster is expected to be of size 6.
From the clusters we identified the closest point from the centroid (a "proxy" for that centroid), which function is to represent the whole cluster for our data sample. In total, we ended up with 100 commanders (one for each cluster).

### TODO
From this list of commanders, we looked at the amount of decks $d_c$ for each commander $c$ on EDHRec. We computed the ratio between that number and the total number of possible decklists we could choose using only the commanders in our list. We call this value 
'''math
p_c=\frac{d_c}{\sum_{c'}{d_{c'}}}
'''
This number represents the probability that we could get a deck for commander $c$ if we had only decks from commanders in the list in our dataset. We also choosed the total number of decks to download $M$, with $M<\sum_{c'}{d_c}$, then we computed the number of decks to download for each commander using $d_c^{final}=d_c*M$

## Graph creation
Once we had the set of decklists, we proceed to create our graph. Each node is associated to unique card, and 2 cards are linked with an edge if and only if they appered in the same decklist at least once. Each edge is weighted with the exact amount of deckists which contains both cards.