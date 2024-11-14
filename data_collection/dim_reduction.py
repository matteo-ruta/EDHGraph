from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_samples, silhouette_score
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

def chooseNClustersWRTSilhouette(projected_data, range_n_clusters):
    for n_clusters in range_n_clusters:
        # Create a subplot with 1 row and 2 columns
        fig, (ax1, ax2) = plt.subplots(1, 2)
        fig.set_size_inches(18, 7)

        # The 1st subplot is the silhouette plot
        # The silhouette coefficient can range from -1, 1 but in this example all
        # lie within [-0.1, 1]
        ax1.set_xlim([-0.1, 1])
        # The (n_clusters+1)*10 is for inserting blank space between silhouette
        # plots of individual clusters, to demarcate them clearly.
        ax1.set_ylim([0, len(projected_data) + (n_clusters + 1) * 10])

        # Initialize the clusterer with n_clusters value and a random generator
        # seed of 10 for reproducibility.
        clusterer = KMeans(n_clusters=n_clusters, random_state=10)
        cluster_labels = clusterer.fit_predict(projected_data)

        # The silhouette_score gives the average value for all the samples.
        # This gives a perspective into the density and separation of the formed
        # clusters
        silhouette_avg = silhouette_score(projected_data, cluster_labels)
        print(
            "For n_clusters =",
            n_clusters,
            "The average silhouette_score is :",
            silhouette_avg,
        )

        # Compute the silhouette scores for each sample
        sample_silhouette_values = silhouette_samples(projected_data, cluster_labels)

        y_lower = 10
        for i in range(n_clusters):
            # Aggregate the silhouette scores for samples belonging to
            # cluster i, and sort them
            ith_cluster_silhouette_values = sample_silhouette_values[cluster_labels == i]

            ith_cluster_silhouette_values.sort()

            size_cluster_i = ith_cluster_silhouette_values.shape[0]
            y_upper = y_lower + size_cluster_i

            color = cm.nipy_spectral(float(i) / n_clusters)
            ax1.fill_betweenx(
                np.arange(y_lower, y_upper),
                0,
                ith_cluster_silhouette_values,
                facecolor=color,
                edgecolor=color,
                alpha=0.7,
            )

            # Label the silhouette plots with their cluster numbers at the middle
            ax1.text(-0.05, y_lower + 0.5 * size_cluster_i, str(i))

            # Compute the new y_lower for next plot
            y_lower = y_upper + 10  # 10 for the 0 samples

        ax1.set_title("The silhouette plot for the various clusters.")
        ax1.set_xlabel("The silhouette coefficient values")
        ax1.set_ylabel("Cluster label")

        # The vertical line for average silhouette score of all the values
        ax1.axvline(x=silhouette_avg, color="red", linestyle="--")

        ax1.set_yticks([])  # Clear the yaxis labels / ticks
        ax1.set_xticks([-0.1, 0, 0.2, 0.4, 0.6, 0.8, 1])

        # 2nd Plot showing the actual clusters formed
        colors = cm.nipy_spectral(cluster_labels.astype(float) / n_clusters)
        ax2.scatter(
            projected_data[:, 0], projected_data[:, 1], marker=".", s=30, lw=0, alpha=0.7, c=colors, edgecolor="k"
        )

        # Labeling the clusters
        centers = clusterer.cluster_centers_
        # Draw white circles at cluster centers
        ax2.scatter(
            centers[:, 0],
            centers[:, 1],
            marker="o",
            c="white",
            alpha=1,
            s=200,
            edgecolor="k",
        )

        for i, c in enumerate(centers):
            ax2.scatter(c[0], c[1], marker="$%d$" % i, alpha=1, s=50, edgecolor="k")

        ax2.set_title("The visualization of the clustered data.")
        ax2.set_xlabel("Feature space for the 1st feature")
        ax2.set_ylabel("Feature space for the 2nd feature")

        plt.suptitle(
            "Silhouette analysis for KMeans clustering on sample data with n_clusters = %d"
            % n_clusters,
            fontsize=14,
            fontweight="bold",
        )

    plt.show()

def plotClustering(n_clusters, projected_data, cluster_labels, labels, proxies_indices):
    colors = plt.colormaps.get_cmap("tab20b")  # "tab20b" provides a range of distinct colors
    custom_cmap = ListedColormap(colors(np.linspace(0, 1, n_clusters)))

    fig, ax = plt.subplots()
    scatter = ax.scatter(
        projected_data[:, 0],
        projected_data[:, 1],
        c=cluster_labels,
        cmap=custom_cmap,
        s=5
    )

    # Add color bar to indicate cluster colors
    plt.colorbar(scatter, ax=ax, label='Cluster Label')

    # Plot the proxies in black on top of the main scatter plot
    if proxies_indices is not None and len(proxies_indices) > 0:
        proxy_points = projected_data[proxies_indices]
        ax.scatter(
            proxy_points[:, 0],
            proxy_points[:, 1],
            c='black',
            s=20,  # Size of proxy points
            label="Proxies",
            edgecolor='white'  # Optional: Add a white edge to proxies for better visibility
        )

    # Add labels and title
    ax.set_title('KMeans Clustering with Hover Labels')
    ax.set_xlabel('Component 1')
    ax.set_ylabel('Component 2')

    # Hover functionality
    cursor = mplcursors.cursor(scatter, hover=True)

    @cursor.connect("add")
    def on_add(sel):
        # Display the cluster label when hovering over a point
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
    #lw_bound, up_bound = round(projected_data.shape[0] / 30), round(projected_data.shape[0] / 6)
    #range_n_clusters = np.linspace(lw_bound, up_bound, 5, dtype=int)
    #print(range_n_clusters)
    #chooseNClustersWRTSilhouette(projected_data, range_n_clusters)
    n_clusters = 100 # chosen by above (that was 60...)

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