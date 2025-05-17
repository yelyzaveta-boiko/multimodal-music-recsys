from pathlib import Path
import numpy as np
import pandas as pd

DATA_DIR   = Path("data")
MODEL_DIR = Path("lda_model_coh")
CSV_FILE   = Path(DATA_DIR /"spotify_millsongdata_en.csv")
TOPIC_FILS = {
    "lda_auto": Path(MODEL_DIR/"lda_vectors.npy")    # best K by coherence
    # "lda_custom": DATA_DIR / "lda_custom.npy",  # any K you prefer
    # "bertopic":   DATA_DIR / "bertopic.npy",    # BERTopic probabilities
}

df = pd.read_csv(CSV_FILE)

#  Load topic matrices into a dict {method → np.ndarray}
topic_mats = {m: np.load(p) for m, p in TOPIC_FILS.items()}


def vectors_for(ids, method):
    """Return a dense 2-D matrix (len(ids) × K) for the given IDs."""
    mat = topic_mats[method]
    idx = df.index[df["track_id"].isin(ids)]
    return mat[idx]
