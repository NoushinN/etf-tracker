from pathlib import Path

import pandas as pd


def save_reports(df: pd.DataFrame, directory: Path) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    df.to_csv(directory / "latest.csv", index=False)
    df.to_excel(directory / "latest.xlsx", index=False)
    archive = directory / "history.csv"
    snapshot = df.copy()
    snapshot.insert(0, "snapshot_date", pd.Timestamp.today().date().isoformat())
    if archive.exists():
        old = pd.read_csv(archive)
        old = old[old["snapshot_date"] != snapshot["snapshot_date"].iloc[0]]
        snapshot = pd.concat([old, snapshot], ignore_index=True)
    snapshot.to_csv(archive, index=False)


