from pathlib import Path
import numpy as np
import pandas as pd
from gensim.models import LdaModel
from gensim import corpora

from pathlib import Path
import numpy as np
import pandas as pd
from gensim.models import LdaModel
from gensim import corpora

ROOT = Path(__file__).parent

MODEL_DIRS = {
    "lda_coh":   ROOT / "lda_model_coh",
    "lda_fixed": ROOT / "lda_model_fixed",
    #"bert": ROOT /
}

topic_mats, models, dicts, dfs = {}, {}, {}, {}

for name, folder in MODEL_DIRS.items():
    model_file = folder / "lda_lyrics.model"
    dict_file  = folder / "lyrics_dictionary.dict"
    vec_file   = folder / "lda_vectors.npy"
    meta_file  = folder / "lyrics_df.pkl"


    models[name] = LdaModel.load(str(model_file))
    dicts[name] = corpora.Dictionary.load(str(dict_file))
    topic_mats[name] = np.load(vec_file)
    df = pd.read_pickle(meta_file).reset_index(drop=True)
    df.rename(columns={"track_id": "id",
                       "song": "name",
                       "artist": "artists"}, inplace=True)
    df["id"] = df["id"].astype(str)
    dfs[name] = df

print("[bootstrap] loaded models:", ", ".join(models.keys()))


def vectors_for(ids, model):
    mat = topic_mats[model]
    df  = dfs[model]

    # Build an index that preserves the order of *ids*
    order = pd.Series(range(len(ids)), index=ids, dtype=int)
    idx   = order.reindex(df["id"]).dropna().astype(int).values
    return mat[idx]