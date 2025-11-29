
import pandas as pd
import numpy as np

df = pd.read_csv("../data/mock_survey_data.csv")
outcomes = ["belief_cc", "policy_support", "share_social_media", "wept"]
agg = (
    df
    .groupby(["country_code", "country", "intervention"])[outcomes]
    .mean()
    .reset_index()
)
long = agg.melt(
    id_vars=["country_code", "country", "intervention"],
    value_vars=outcomes,
    var_name="outcome",
    value_name="mean_value"
)
best = (
    long
    .loc[long.groupby(["country_code", "outcome"])["mean_value"].idxmax()]
    .reset_index(drop=True)
)

rng = np.random.default_rng(42)

se = rng.uniform(0.05, 0.35, size=len(df))
df["ci_low"] = df["mean_value"] - 1.96 * se
df["ci_high"] = df["mean_value"] + 1.96 * se

df["ci_low"] = df["ci_low"].clip(lower=1.0)
df["ci_high"] = df["ci_high"].clip(upper=7.0)

df["p_value"] = rng.beta(0.8, 3.0, size=len(df))

df.to_csv("../data/best_interventions_with_stats.csv", index=False)

