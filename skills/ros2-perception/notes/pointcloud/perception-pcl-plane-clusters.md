---
id: perception-pcl-plane-clusters
type: reference
owner: equipo-ros2
updated: 2026-10-27
review_by: 2027-04-25
source: manual
confidentiality: internal
title: "Region filter, RANSAC plane segmentation and Euclidean clustering with python-pcl: parameters and outputs"
domain: perception
area: pointcloud
distro: humble
tested: false
audience: dev
summary: "python-pcl pipeline: region filter, make_segmenter SACMODEL_PLANE SAC_RANSAC distance 0.01, EuclideanClusterExtraction tolerance, min/max size, centroids, dimensions."
tags: [python-pcl, RANSAC, SAC_RANSAC, SACMODEL_PLANE, make_segmenter, set_distance_threshold, segment, plane coefficients, EuclideanClusterExtraction, set_ClusterTolerance, set_MinClusterSize, set_MaxClusterSize, make_kdtree, KD-tree, centroid]
see: ["[[perception-surface-detection]]", "[[perception-object-detection-pcl]]", "[[perception-pcl-python]]", "[[perception-cloud-to-base-link]]"]
requires: [ros2-core]
version_notes:
  - "python-pcl 0.3.0rc1 (master, archived): make_segmenter, set_model_type, set_method_type, set_distance_threshold, segment; make_kdtree, make_EuclideanClusterExtraction, set_ClusterTolerance, set_MinClusterSize, set_MaxClusterSize, set_SearchMethod, Extract; extract(indices); PointCloud exposes an (N, 3) float32 buffer — https://github.com/strawlab/python-pcl (PERC-V15, PERC-V16)"
  - "course: the 4.3 text calls the clustering method extract_bench_clusters(); the file names it extract_clusters() (PERC-V05)"
---
# Region filter, RANSAC plane and Euclidean clusters (python-pcl)

**TL;DR** Three steps on a cloud already in `base_link`: keep a box of interest (`x ≤ max_x_dist`, `min_height ≤ z ≤ max_height`), fit the dominant plane with RANSAC (`SACMODEL_PLANE`, 1 cm threshold), and split what remains into Euclidean clusters (2 cm tolerance, 100–80,000 points); each cluster gives a centroid and the size of its bounding box. Code: `filter_cloud()`, `extract_plane()`, `extract_clusters()` of [[perception-surface-detection]].

## 1. Region filter (`filter_cloud`)
Two conditions per point:
- **x distance**: `point[0] <= max_x_dist` (2.15 m in the course). The depth cloud shows a dark shadow at its far boundary, where the sensor's limits make the data unreliable; cutting it avoids using misread points.
- **height range**: `min_height <= point[2] <= max_height` defines the region of interest: 0.35–0.4 m for the flat bench tops, 0.4–1.2 m for objects on them.
The kept indices go to `cloud.extract(indices)`, which returns a new `pcl.PointCloud`.

## 2. Plane segmentation (`extract_plane`)
| Call | Value | Meaning |
|---|---|---|
| `seg = cloud.make_segmenter()` | | segmentation object on this cloud |
| `seg.set_model_type(pcl.SACMODEL_PLANE)` | plane | look for a plane model |
| `seg.set_method_type(pcl.SAC_RANSAC)` | RANSAC | Random Sample Consensus: robust model fitting on data with outliers |
| `seg.set_distance_threshold(0.01)` | 0.01 m | how close to the plane a point must be to count as an inlier |
| `indices, coefficients = seg.segment()` | | inlier indices and the plane `ax + by + cz + d = 0` |

`cloud.extract(indices)` returns the plane's points (`plane_cloud`); the node logs the inlier count and the coefficients.

## 3. Euclidean clustering (`extract_clusters`)
| Call | Value | Meaning |
|---|---|---|
| `tree = cloud.make_kdtree()`, `ec.set_SearchMethod(tree)` | KD-tree | speeds up the neighbor search |
| `ec = cloud.make_EuclideanClusterExtraction()` | | clustering object |
| `ec.set_ClusterTolerance(0.02)` | 0.02 m | maximum distance between neighbors of one cluster |
| `ec.set_MinClusterSize(100)` | 100 points | smaller clusters are discarded |
| `ec.set_MaxClusterSize(80000)` | 80,000 points | bigger clusters are not extracted (usually outliers or noise) |
| `cluster_indices = ec.Extract()` | | one index list per cluster |

For each cluster: `cluster = cloud.extract(indices)`; centroid `np.mean(cluster, axis=0)`; dimensions = `np.max(...) - np.min(...)` along each axis (the axis-aligned box in `base_link`); point count, centroid and dimensions are logged, and a warning is printed when nothing was extracted. The function returns the clusters, the centroids and the dimensions, used for markers and messages.

## Pitfalls
- RANSAC returns the **dominant** plane only: with the floor inside the box it wins over a bench; the height band removes it first.
- Tolerance smaller than the point spacing splits one object into many clusters; larger merges neighbors. Tune it with the cloud's density at the working distance.
- Dimensions are axis-aligned in `base_link`: a rotated bench reports a bigger box than its real length × width.
