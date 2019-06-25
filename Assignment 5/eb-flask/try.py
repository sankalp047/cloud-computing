from sklearn.cluster import KMeans
import numpy as np
X = np.array([[1, 2], [1, 4], [1, 0],
               [10, 2], [10, 4], [10, 0]])

# print(X)
# mean_X = np.mean(X, axis=0)
# print("Mean: ")
# print(mean_X)

# std_X = np.std(X, axis=0)
# print("Std: ")
# print(std_X)

# new_X = (X-mean_X)/std_X
# print("New X: ")
# print(new_X)

kmeans = KMeans(n_clusters=3, random_state=0).fit(X)
print(kmeans.labels_)
# array([1, 1, 1, 0, 0, 0], dtype=int32)
print(kmeans.predict([[0, 0], [12, 3]]))
# array([1, 0], dtype=int32)
print(kmeans.cluster_centers_)
# array([[10.,  2.],
    #    [ 1.,  2.]])


def getGraphValues(data, clusters, labels):
    cluster_details = []
    cluster_count = np.shape(clusters)[0]
    for i in range(cluster_count):
        this_cluster_indices = np.where(labels == i)[0]
        print(this_cluster_indices)
        this_cluster_points = data[this_cluster_indices,:]
        this_distance = np.sqrt(np.sum((this_cluster_points - clusters[i,:])**2))
        cluster_details.append({"Centroid": str(clusters[i,:]), "Closely Packed": str(this_distance), "Cluster Size": np.shape(this_cluster_points)[1]})
        # print("Centroid: " + str(clusters[i,:]) + "..... Closely Packed: "+ str(this_distance) + "..... Cluster Size: " + str(np.shape(this_cluster_points)[1]))
        # print(np.shape(this_cluster_points))

    return cluster_details


getGraphValues(X, kmeans.cluster_centers_, kmeans.labels_)