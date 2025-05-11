import numpy as np
import matplotlib.pyplot as plt
import umap.umap_ as umap

# Generate a synthetic 3-cluster 3-D point cloud (replace this with your own NxD data)
rng = np.random.default_rng(0)
cluster_centers = np.array([[0, 0, 0], [5, 5, 5], [-4, 4, -3]])
points_per_cluster = 300
X = np.vstack([
    center + rng.normal(scale=0.8, size=(points_per_cluster, 3))
    for center in cluster_centers
])

# Run UMAP to 2D
reducer = umap.UMAP(
    n_components=2,
    n_neighbors=15,
    min_dist=0.1,
    metric='euclidean',
    random_state=42
)
embedding = reducer.fit_transform(X)

# Scatter plot
plt.figure(figsize=(6, 6))
plt.scatter(embedding[:, 0], embedding[:, 1], s=10)
plt.title("UMAP projection to 2D")
plt.xlabel("UMAP-1")
plt.ylabel("UMAP-2")
plt.tight_layout()
plt.show()
