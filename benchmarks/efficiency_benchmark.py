# -*- coding: utf-8 -*-

"""Test how fast the calls can be made to the GILDA remote API."""

import random
import time
from textwrap import dedent

import click
import matplotlib.pyplot as plt
import pandas as pd
import requests
import seaborn as sns
from more_click import force_option, verbose_option
from tqdm import tqdm, trange
from tqdm.contrib.logging import logging_redirect_tqdm

import gilda
from gilda.api import grounder
from medmentions import MODULE, iterate_corpus

RESULTS_PATH = MODULE.join(name="efficiency.tsv")
RESULTS_AGG_PATH = MODULE.join(name="efficiency_agg.tsv")
RESULTS_AGG_TEX_PATH = MODULE.join(name="efficiency_agg.tex")
FIG_PATH = MODULE.join(name="efficiency.svg")
FIG_PDF_PATH = MODULE.join(name="efficiency.pdf")


def ground_package(text, context):
    return gilda.ground(text)


def ground_package_context(text, context):
    return gilda.ground(text, context=context)


def ground_app_local(text, context):
    return requests.post("http://localhost:8001/ground", json={"text": text}).json()


def ground_app_local_context(text, context):
    return requests.post(
        "http://localhost:8001/ground", json={"text": text, "context": context}
    ).json()


def ground_app_remote(text, context):
    return requests.post(
        "http://grounding.indra.bio/ground", json={"text": text}
    ).json()


def ground_app_remote_context(text, context):
    return requests.post(
        "http://grounding.indra.bio/ground", json={"text": text, "context": context}
    ).json()


FUNCTIONS = [
    ("python", False, ground_package),
    ("python", True, ground_package_context),
    ("local", False, ground_app_local),
    ("local", True, ground_app_local_context),
    ("remote", False, ground_app_remote),
    ("remote", True, ground_app_remote_context),
]


def run_trial(*, trials, chunk, corpus, func, desc):
    rv = []
    outer_it = trange(trials, desc=desc)
    for trial in outer_it:
        random.shuffle(corpus)
        test_corpus = corpus[:chunk]
        inner_it = tqdm(test_corpus, desc="Examples", leave=False)
        for document_id, abstract, umls_id, text, start, end, types in inner_it:
            with logging_redirect_tqdm():
                start = time.time()
                matches = func(text, context=abstract)
                rv.append((trial, len(matches), time.time() - start))
    return rv


def build(trials: int, chunk: int) -> pd.DataFrame:
    click.secho("Preparing medmentions corpus")
    corpus = list(iterate_corpus())

    click.secho("Warming up python grounder")
    grounder.get_grounder()

    click.secho("Warming up local api grounder")
    ground_app_local_context("ER", context="Calcium is released from the ER.")

    click.secho("Warming up remote api grounder")
    ground_app_remote_context("ER", context="Calcium is released from the ER.")

    rows = []
    for tag, uses_context, func in FUNCTIONS:
        rv = run_trial(
            trials=trials,
            chunk=chunk,
            corpus=corpus,
            func=func,
            desc=f"{tag}{' with context' if uses_context else ''} trial",
        )
        rows.extend((tag, uses_context, *row) for row in rv)
    df = pd.DataFrame(rows, columns=["type", "context", "trial", "matches", "duration"])
    return df


@click.command()
@click.option("--trials", type=int, default=3, show_default=True)
@click.option("--chunk", type=int, default=300, show_default=True)
@verbose_option
@force_option
def main(trials: int, chunk: int, force: bool):
    if RESULTS_PATH.is_file() and not force:
        df = pd.read_csv(RESULTS_PATH, sep="\t")
    else:
        df = build(trials=trials, chunk=chunk)
        df.to_csv(RESULTS_PATH, sep="\t", index=False)

    df["type"] = df["type"].map(
        {
            "python": "Python Package",
            "local": "Local Gilda App",
            "remote": "Remote Gilda App",
        }
    )

    df["duration"] = df["duration"].map(lambda x: 1 / x)

    _grouped = df[["type", "context", "duration"]].groupby(["type", "context"])
    agg_mean_df = _grouped.mean()
    agg_mean_df.rename(columns={"duration": "duration_mean"}, inplace=True)
    agg_std_df = _grouped.std()
    agg_std_df.rename(columns={"duration": "duration_std"}, inplace=True)
    agg_df = pd.merge(agg_mean_df, agg_std_df, left_index=True, right_index=True)
    agg_df = agg_df.round(1)
    agg_df.to_csv(RESULTS_AGG_PATH, sep="\t")
    agg_df.to_latex(RESULTS_AGG_TEX_PATH, label="tab:responsiveness-benchmark", caption=dedent(f"""\
        Benchmarking of the responsiveness of the Gilda service when running synchronously
        through its Python package, when run locally as a web service, and when run remotely
        as a web service. Each scenario was also tested with and without context added.
        The Python usage had the fastest time due to the lack of overhead from
        network communication. The local web service performed better than the remote one
        for the same reason in addition to the possibility of external users requesting at the
        same time.
    """))

    fig, ax = plt.subplots(figsize=(6, 3))
    sns.boxplot(data=df, y="duration", x="type", hue="context", ax=ax)
    ax.set_title("Gilda Responsiveness Benchmark")
    ax.set_yscale("log")
    ax.set_ylabel("Responses per Second")
    ax.set_xlabel("")
    fig.savefig(FIG_PATH)
    fig.savefig(FIG_PDF_PATH)


if __name__ == "__main__":
    main()
