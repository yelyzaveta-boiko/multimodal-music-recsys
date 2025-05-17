"""
LDA-only recommendation engine driven by real user ratings
"""
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from gensim.models import LdaModel
from gensim import corpora

from spotify_api import enrich


# artefacts 
ROOT   = Path(__file__).parent
MODELS = ROOT / "lda_model_coh"
DATA   = ROOT / "data/spotify_millsongdata_en"


lda = LdaModel.load(str(MODELS / "lda_lyrics.model"))
dictionary = corpora.Dictionary.load(str(MODELS / "lyrics_dictionary.dict"))
vectors = np.load(str(MODELS / "lda_vectors.npy")) # (N, topics)

df = pd.read_pickle(MODELS / "lyrics_df.pkl").reset_index(drop=True)

df.rename(columns={
    "track_id": "id", 
    "song": "name", 
    "artist": "artists"
    }, inplace=True)
df["id"] = df["id"].astype(str) 

META = ["id", "name", "artists"]

_user_ratings = []

def random_songs(n=5):
    sample = df.sample(n)
    print("[random]  track_ids:", list(sample["id"]))
    return enrich(sample[META].to_dict("records"))


def save_ratings(ratings):
    global _user_ratings
    _user_ratings = ratings
    print("[save] ratings:", _user_ratings)


def _profile_embed():
    ids = np.array([int(r["id"]) for r in _user_ratings])
    scores = np.array([float(r["score"]) for r in _user_ratings])

    profile = (scores[:, None] * vectors[ids]).sum(axis=0) / (scores.sum() + 1e-8)
    return profile

def recommendations(k=5):
    if not _user_ratings:
        raise RuntimeError("No ratings yet.")

    profile = _profile_embed()

    # similarity of profile vs. every song
    sims = cosine_similarity(profile[None, :], vectors).ravel()

    # exclude songs already rated
    for r in _user_ratings:
        sims[int(r["id"])] = -1

    # top-k indices
    idx = np.argsort(-sims)[:k]

    print("[recs] idx:", idx)
    print("[recs] cosine similarities:", sims[idx])

    recs = df.loc[idx, META]
    recs["similarity"] = sims[idx]
    return enrich(recs.to_dict("records"))