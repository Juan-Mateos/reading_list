# Script to read and process zotero references

import logging
import re
import shutil
import numpy as np
import pandas as pd
from reading_list import PROJECT_DIR


def clean_column_names(col: str) -> str:
    """Cleans columns names"""

    return re.sub(" ", "_", col.lower())


def clean_article_title(article_path: str) -> str:
    """Cleans an article title"""

    return re.sub(
        " ",
        "_",
        re.sub("  ", " ", re.sub("-", "", article_path.lower().split("/")[-1])),
    )


MY_TAGS = {
    "0_impact_evaluation",
    "1_economics_science",
    "2_science_of_science",
    "3_ai_in_science",
    "4_protein_science",
    "5_environmental_impact",
    "6_miscellaneous",
}

MY_COLS = [
    "key",
    "title",
    "publication_year",
    "author",
    "doi",
    "url",
    "date_added",
    "manual_tags",
    "automatic_tags",
    "file_attachments",
]

if __name__ == "__main__":

    print("Reading and processing")

    readings = pd.read_csv(f"{PROJECT_DIR}/docs/my_library.csv")

    readings.columns = [clean_column_names(c) for c in readings.columns]

    readings = (
        readings[MY_COLS]
        .assign(
            project_tags=lambda df: [
                " ".join([t for t in str(tag).split(";") if t in MY_TAGS])
                for tag in df["manual_tags"]
            ]
        )
        .replace("", np.nan)
        .dropna(axis=0, subset=["project_tags"])
        .reset_index(drop=True)
    )

    print("Saving")

    for f in readings["file_attachments"].dropna():

        if ".pdf" in f:
            if ";" in f:
                fils = f.split(";")
                keep = [fil for fil in fils if "pdf" in fil][0]
                shutil.copy(
                    keep,
                    f"{PROJECT_DIR}/docs/article_files/{clean_article_title(keep)}",
                )

            else:
                shutil.copy(
                    f, f"{PROJECT_DIR}/docs/article_files/{clean_article_title(f)}"
                )

    readings.to_markdown(f"{PROJECT_DIR}/docs/master_table/master_table.md")
