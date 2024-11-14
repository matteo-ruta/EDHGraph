from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import pickle
import os
import json
import random
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from matplotlib.colors import ListedColormap
import mplcursors

DATA_REPOSITORY = "C:\\Dati\\Università\\magistrale_pd\\II_anno_I_semestre\\Learning from Networks\\Project\\top_commanders\\"
TARGET_EXT = ".json"

def readDataAsDictionaries() -> list:
    """
    Retrieves the information stored in the json files in top_commanders folder.
    The structure of the objects inside is this:
    [
        {
            name: string.
            decks: int,
            color_identity: [
                string,
                ...
            ]
        },
        ...
    ]
    """
    commanders_list = []

    data_path = os.path.abspath(DATA_REPOSITORY)
    assert os.path.isdir(data_path), "FATAL ERROR: DATA_REPOSITORY is not a repository"

    for json_file in [file for file in os.listdir(data_path) if file.endswith(TARGET_EXT)]:
        json_data = []
        with open(os.path.join(DATA_REPOSITORY, json_file), "r", encoding="utf-8") as f:
            json_data = json.load(f)
        commanders_list.extend(json_data)

    return commanders_list

def dictToArray(deck_dict: dict, vocab: list) -> np.ndarray:

    param_list = [deck_dict["decks"]]
    param_list.append(1 if "W" in deck_dict["color_identity"] else 0)
    param_list.append(1 if "U" in deck_dict["color_identity"] else 0)
    param_list.append(1 if "R" in deck_dict["color_identity"] else 0)
    param_list.append(1 if "B" in deck_dict["color_identity"] else 0)
    param_list.append(1 if "G" in deck_dict["color_identity"] else 0)

    for entry in vocab:
        param_list.append(deck_dict[entry] if entry in deck_dict.keys() else 0)

    return np.asarray(param_list)

def plotClustering(n_clusters, projected_data, cluster_labels, labels, proxies_indices):
    colors = plt.colormaps.get_cmap("tab20b")
    custom_cmap = ListedColormap(colors(np.linspace(0, 1, n_clusters)))

    fig, ax = plt.subplots()
    scatter = ax.scatter(
        projected_data[:, 0],
        projected_data[:, 1],
        c=cluster_labels,
        cmap=custom_cmap,
        s=5
    )

    plt.colorbar(scatter, ax=ax, label='Cluster Label')

    if proxies_indices is not None and len(proxies_indices) > 0:
        proxy_points = projected_data[proxies_indices]
        ax.scatter(
            proxy_points[:, 0],
            proxy_points[:, 1],
            c='black',
            s=20,
            label="Proxies",
            edgecolor='white'
        )

    ax.set_title('KMeans Clustering with Hover Labels')
    ax.set_xlabel('Component 1')
    ax.set_ylabel('Component 2')

    # Hover functionality
    cursor = mplcursors.cursor(scatter, hover=True)

    @cursor.connect("add")
    def on_add(sel):
        sel.annotation.set(text=f'Cluster: {cluster_labels[sel.index]}\nName: {labels[sel.index]}')

    plt.show()

if __name__ == "__main__":
    vocab = []
    with open(DATA_REPOSITORY + "vocab.txt", "r", encoding="utf-8") as f:
        vocab = f.read().split("\n")[:-1]

    #random.shuffle(vocab)

    data_as_dicts = readDataAsDictionaries()

    data = np.asarray(list(map(lambda deck : dictToArray(deck, vocab), data_as_dicts)))
    labels = np.asarray([deck["name"] for deck in data_as_dicts])

    scaler = StandardScaler()
    data = scaler.fit(data).transform(data)

    pca = PCA(n_components=2)
    projected_data = pca.fit(data).transform(data)
    print(projected_data.shape)

    # clustering
    n_clusters = 100 # chosen so to have E[commanders per cluster] = 6

    clusterer = KMeans(n_clusters).fit(projected_data)
    cluster_labels = clusterer.labels_

    # save clusterer, so to have the same proxies once chosen
    with open("clusterer.pkl", "wb") as f:
        pickle.dump(clusterer, f)
    
    cluster_centroids = clusterer.cluster_centers_
    cluster_i_am_in = clusterer.predict(projected_data)

    proxy_indicies = []
    for cl_label in cluster_labels:
        cluster_elements_indexes = [index for index in range(len(cluster_i_am_in)) if cluster_i_am_in[index] == cl_label]
        centroid = cluster_centroids[cl_label]

        min_dist = -1
        for point_index in cluster_elements_indexes:
            dist = np.linalg.norm(projected_data[point_index] - centroid)
            # the negative case in only for the first iteration
            if dist < min_dist or min_dist < 0:
                repres_index = point_index
                min_dist = dist
        
        proxy_indicies.append(repres_index)

    plotClustering(n_clusters, projected_data, cluster_labels, labels, proxy_indicies)

    # creating input.txt
    M = 10000
    proxy_quantities = np.asarray([data_as_dicts[index].get("decks") for index in proxy_indicies], dtype=np.float32)
    total_sum_of_quantities = np.sum(proxy_quantities)
    proxy_distribution = proxy_quantities / total_sum_of_quantities
    final_proxy_quantities = np.round(proxy_distribution * M).astype(int)

    print("Sum:", total_sum_of_quantities)
    print("Final sum after rounding:", np.sum(final_proxy_quantities))

    with open("input.txt", "w", encoding="utf-8") as f:
        for i in range(len(proxy_indicies)):
            line = f"{data_as_dicts[proxy_indicies[i]].get("name").replace("//", "")}-{final_proxy_quantities[i]}\n"
            f.write(line)