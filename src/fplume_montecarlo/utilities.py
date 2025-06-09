from fplume_montecarlo.config import ERUPTIONS_FILE

def progress_bar(url, save_path, chunk_size=1024):
    """
    Downloads a file from a URL with a progress bar.
    """

    import os
    import requests
    from tqdm import tqdm

    response = requests.get(url, stream=True)
    total_size = int(response.headers.get('content-length', 0))  # Total size in bytes

    with tqdm(total=total_size, unit='B', unit_scale=True, desc=os.path.basename(save_path)) as pbar:
        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=chunk_size):
                if chunk:  # filter out keep-alive new chunks
                    f.write(chunk)
                    pbar.update(len(chunk))

def load_eruptions(filepath):
    """
    Load the txt file containing the Etna eruptions
    """
    import pandas as pd

    return pd.read_csv(
        filepath,
        sep="\t",
        encoding="utf-8",
        engine="python",
        dtype={"year": str, "month": str, "day": str, "hour": str}
    )



def load_events(filepath, code=None):
    """
    Load eruption events. If "code" is provided, return only that event.

    Parameters:
        filepath (str or Path): Path to the eruptions file.
        code (int, optional): Specific event code to extract. If None, return all.

    Returns:
        dict: A single event dict if code is provided.
        list[dict]: A list of event dicts if no code is provided.
    """

    df = load_eruptions(ERUPTIONS_FILE)

    if code is not None:
        event_row = df[df["code"] == code]
        if event_row.empty:
            raise ValueError(f"No event found with code {code}")
        event = event_row.iloc[0].to_dict()
        event["date_prefix"] = f"{event['year']}_{event['month']}_{event['day']}_{event['hour']}"
        return event

    events = []
    for _, row in df.iterrows():
        event = row.to_dict()
        event["date_prefix"] = f"{event['year']}_{event['month']}_{event['day']}_{event['hour']}"
        events.append(event)
    return events