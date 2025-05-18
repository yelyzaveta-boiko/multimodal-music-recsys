"""
LDA-only recommendation engine driven by real user ratings
"""
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from gensim.models import LdaModel
from gensim import corpora
from topic_models import topic_mats, dfs
from spotify_api import enrich

_user_ratings = []

def random_songs(n=5, default_model="lda_coh"):
    df   = dfs[default_model]
    META = ["id", "name", "artists"]
    sample = df.sample(n)
    print("[random] track_ids:", list(sample["id"]))
    return enrich(sample[META].to_dict("records"))


def save_ratings(ratings):
    global _user_ratings
    _user_ratings = ratings
    print("[save] ratings:", _user_ratings)


def _profile_embed(model_name):
    ids = np.array([int(r["id"]) for r in _user_ratings])
    scores = np.array([float(r["score"]) for r in _user_ratings])
    vecs = topic_mats[model_name]
    profile = (scores[:, None] * vecs[ids]).sum(axis=0) / (scores.sum() + 1e-8)
    return profile

def _recommend(model_name, k=5):
    profile = _profile_embed(model_name)
    vecs = topic_mats[model_name]
    df = dfs[model_name]

    # similarity of profile vs. every song
    sims = cosine_similarity(profile[None, :], vecs).ravel()
    

    # exclude songs already rated
    for r in _user_ratings:
        sims[int(r["id"])] = -1

    # top-k indices
    idx = sims.argsort()[::-1][:k]
    recs = df.loc[idx, ["id", "name", "artists"]].copy()
    recs["similarity"] = sims[idx]
    print(f"[recs:{model_name}] idx:", idx)
    print(f"[recs:{model_name}] sims:", sims[idx])
    return enrich(recs.to_dict("records"))

def recommendations(k=5, model_name="lda_coh"):
    """Return k recs from the chosen engine."""
    if not _user_ratings:
        raise RuntimeError("No ratings stored")
    return _recommend(model_name, k)