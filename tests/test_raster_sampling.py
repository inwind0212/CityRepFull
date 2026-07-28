from __future__ import annotations

import geopandas as gpd
import numpy as np
import rasterio
from rasterio.transform import from_origin, xy

from urban_benchmark.align import align_embedding
from urban_benchmark.embeddings import RasterEmbedding
from urban_benchmark.tasks import Task


def test_matching_grid_sampling_equals_direct_cell_index(tmp_path):
    array = np.arange(3 * 4 * 5, dtype=np.float32).reshape(3, 4, 5)
    path = tmp_path / "embedding.tif"
    transform = from_origin(0, 4, 1, 1)
    with rasterio.open(
        path,
        "w",
        driver="GTiff",
        height=4,
        width=5,
        count=3,
        dtype="float32",
        crs="EPSG:4326",
        transform=transform,
    ) as dst:
        dst.write(array)

    rows = np.asarray([3, 0, 2, 1], dtype=np.int64)
    cols = np.asarray([4, 1, 0, 3], dtype=np.int64)
    xs, ys = xy(transform, rows, cols, offset="center")
    samples = gpd.GeoDataFrame(
        {
            "sample_id": [f"s{i}" for i in range(len(rows))],
            "row": rows,
            "col": cols,
            "x": xs,
            "y": ys,
        },
        geometry=gpd.points_from_xy(xs, ys),
        crs="EPSG:4326",
    )
    task = Task("test.regression.2026", "regression", samples, np.zeros((4, 1)), ["label"], {"labels_path": str(path)})
    aligned = align_embedding(task, RasterEmbedding("test", str(path)), normalize=False)

    np.testing.assert_array_equal(aligned.X, array[:, rows, cols].T)
    assert aligned.report["aligner"] == "raster_cell"
