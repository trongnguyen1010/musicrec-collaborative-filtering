"""Execute checksum-verified author definitions, without importing their main entrypoint."""

import ast
import difflib
import json
import math
from typing import Any, cast
from unittest.mock import patch

import networkx as nx
import numpy as np
import pandas as pd
from scipy import sparse

from musicrec.recommenders.diffusion import DiffusionRecommender, Variant
from musicrec.research.io import OUT, ROOT, SPLITS, Split, sha256, write_json


def author_namespace() -> dict[str, Any]:
    """Extract unchanged definitions from the pinned files verified by Git blob/SHA256."""
    manifest = json.loads((OUT / "download_manifest.json").read_text(encoding="utf-8"))
    folder = ROOT / "data/interim/aiprobs-source"
    namespace: dict[str, Any] = {"np": np, "nx": nx, "pd": pd, "sp": sparse, "math": math}
    definitions = {
        "DhcExtension.py": {"DHC_extension"},
        "main.py": {"Dhc", "To_Networkx", "Create_Dhc_Features", "Measure_Similarity_Dhc"},
        "MD_DHC_Recbole.py": {"ComputeSimilarity"},
    }
    records = {row["path"].replace("\\", "/"): row for row in manifest["upstream_files"]}
    for name, selected in definitions.items():
        path = folder / name
        if sha256(path) != records[f"data/interim/aiprobs-source/{name}"]["sha256"]:
            raise ValueError("Author code checksum mismatch")
        tree = ast.parse(path.read_text(encoding="utf-8"))
        tree.body = [
            node
            for node in tree.body
            if isinstance(node, (ast.FunctionDef, ast.ClassDef)) and node.name in selected
        ]
        exec(compile(tree, str(path), "exec"), namespace)
    return namespace


def verify_tiny_reference() -> dict[str, Any]:
    """Unmodified author code vs sparse kernels, with disconnected/padding nodes."""
    namespace = author_namespace()
    coordinates = np.asarray(
        [
            (1, 1),
            (1, 2),
            (1, 3),
            (2, 1),
            (2, 3),
            (2, 4),
            (3, 1),
            (3, 2),
            (4, 3),
            (4, 4),
            (5, 5),
            (6, 5),
        ]
    )
    matrix = sparse.csr_matrix((np.ones(len(coordinates)), coordinates.T), shape=(8, 9))
    frame = pd.DataFrame(coordinates, columns=["user_id", "item_id"])
    similarity = namespace["Measure_Similarity_Dhc"](frame.copy(), 7, 8, "cosine")
    expected_ai = (
        namespace["ComputeSimilarity"](matrix.astype(np.float32), similarity, "max-min + mean")
        .compute_similarity()
        .toarray()
    )
    a = matrix.toarray()
    r = a.sum(axis=1)
    c = a.sum(axis=0)
    row = np.divide(a, r[:, None], out=np.zeros_like(a), where=r[:, None] != 0)
    col = np.divide(a, c[None, :], out=np.zeros_like(a), where=c[None, :] != 0)
    expected = {"pure_dhc": similarity, "probs": (a @ col.T) @ row, "aiprobs": expected_ai}
    errors = {}
    for variant in expected:
        model = DiffusionRecommender(
            cast(Variant, variant), [str(i) for i in range(8)], [str(i) for i in range(9)]
        ).fit_matrix(matrix)
        actual = model.score_batch(np.arange(8, dtype=np.int64))
        np.testing.assert_allclose(actual, expected[variant], rtol=1e-6, atol=1e-8)
        errors[variant] = float(np.max(np.abs(actual - expected[variant])))
    result = {
        "status": "passed",
        "source_commit": "051ab349c1bfe493cb5eabd3b6ec1fe0c3a3e0f2",
        "reference": "unchanged extracted author definitions; ProbS dense equation 1",
        "max_absolute_score_error": errors,
        "rtol": 1e-6,
        "atol": 1e-8,
    }
    write_json(OUT / "tiny_reference_verification.json", result)
    return result


def verify_full_reference() -> dict[str, Any]:
    """Full split 0: author normalization/scoring, with graph allocation patch only."""
    namespace = author_namespace()
    split = Split.load(SPLITS / "aiprobs-original/split_00.npz")
    matrix = split.matrix()

    def sparse_dhc(adjacency: Any) -> list[Any]:
        adjacency = adjacency.tocsr()
        neighborhoods = [
            adjacency.indices[adjacency.indptr[i] : adjacency.indptr[i + 1]]
            for i in range(adjacency.shape[0])
        ]
        current = np.asarray(adjacency.sum(axis=1)).ravel()
        features = [current]
        updater = namespace["DHC_extension"]()
        while True:
            updated = updater.UpdataDistribution(neighborhoods, current)
            if np.array_equal(updated, current):
                return features
            features.append(updated)
            current = updated

    original = ast.parse((ROOT / "data/interim/aiprobs-source/main.py").read_text(encoding="utf-8"))
    original_dhc = next(
        node for node in original.body if isinstance(node, ast.FunctionDef) and node.name == "Dhc"
    )
    import inspect

    patched_source = inspect.getsource(sparse_dhc)
    original_source = ast.unparse(original_dhc)
    (OUT / "reference_graph_allocation.patch").write_text(
        "Patch nx.to_numpy_array -> nx.to_scipy_sparse_array; replace Dhc input scanning "
        "with CSR neighborhoods. Original DHC_extension updater unchanged.\n"
        + "\n".join(
            difflib.unified_diff(
                original_source.splitlines(),
                patched_source.splitlines(),
                fromfile="author/Dhc",
                tofile="adapter/sparse_dhc",
            )
        ),
        encoding="utf-8",
    )
    namespace["Dhc"] = sparse_dhc
    frame = pd.DataFrame(split.train, columns=["user_id", "item_id"])
    with patch.object(
        nx,
        "to_numpy_array",
        lambda graph: nx.to_scipy_sparse_array(graph, dtype=np.dtype(np.float64), format="csr"),
    ):
        similarity = namespace["Measure_Similarity_Dhc"](
            frame, len(split.users) - 1, len(split.items) - 1, "cosine"
        )
    errors = {}
    model = DiffusionRecommender("pure_dhc", split.users, split.items).fit_matrix(matrix)
    max_error = 0.0
    for start in range(0, len(split.users), 64):
        ids = np.arange(start, min(start + 64, len(split.users)), dtype=np.int64)
        actual = model.score_batch(ids)
        np.testing.assert_allclose(actual, similarity[ids], rtol=1e-6, atol=1e-8)
        max_error = max(max_error, float(np.abs(actual - similarity[ids]).max()))
    errors["pure_dhc"] = max_error
    del model
    print("Full reference: DHC/cosine verified; running original ComputeSimilarity", flush=True)
    expected = namespace["ComputeSimilarity"](
        matrix.astype(np.float32), similarity, "max-min + mean"
    ).compute_similarity()
    del similarity
    model = DiffusionRecommender("aiprobs", split.users, split.items).fit_matrix(matrix)
    max_error = 0.0
    for start in range(0, len(split.users), 64):
        ids = np.arange(start, min(start + 64, len(split.users)), dtype=np.int64)
        actual, wanted = model.score_batch(ids), expected[ids].toarray()
        np.testing.assert_allclose(actual, wanted, rtol=1e-6, atol=1e-8)
        max_error = max(max_error, float(np.abs(actual - wanted).max()))
    errors["aiprobs"] = max_error
    result = {
        "status": "passed",
        "split_sha256": sha256(split.path),
        "scope": "every user/item score in author split 0; Pure-DHC and AIProbS",
        "source_commit": "051ab349c1bfe493cb5eabd3b6ec1fe0c3a3e0f2",
        "patch": "CSR graph/neighborhood allocation only; original similarity and "
        "ComputeSimilarity normalization/scoring unchanged",
        "max_absolute_score_error": errors,
        "rtol": 1e-6,
        "atol": 1e-8,
    }
    write_json(OUT / "full_reference_verification.json", result)
    return result
