
import pandas as pd
import requests
import io
import os

def fetch_nfl_data(year=2023, limit=5000):
    """
    Fetches NFL play-by-play data from nflverse.
    """
    url = f"https://github.com/nflverse/nflverse-data/releases/download/pbp/play_by_play_{year}.csv"
    print(f"Downloading data from {url}...")
    
    try:
        # Bypass SSL verification
        import ssl
        ssl._create_default_https_context = ssl._create_unverified_context
        
        # Use pandas directly to read from URL
        # Use simpler low_memory=False to avoid mixed type warnings, or specify types
        # Limit rows for speed in this environment
        df = pd.read_csv(url, nrows=limit, low_memory=False)
        return df
    except Exception as e:
        print(f"Error downloading data: {e}")
        return None

def process_nfl_data(df):
    """
    Converts NFL verse data to our app's format.
    """
    if df is None:
        return pd.DataFrame()

    print(f"Processing {len(df)} rows...")
    
    # Filter for only relevant plays (pass/run/punt/field_goal)
    relevant_types = ['pass', 'run', 'punt', 'field_goal']
    df = df[df['play_type'].isin(relevant_types)].copy()
    
    converted = pd.DataFrame()
    
    # 1. Date
    converted["Date"] = pd.to_datetime(df["game_date"]).dt.strftime("%Y-%m-%d")
    
    # 2. Quarter
    converted["Quarter"] = df["qtr"].astype(str) + "Q"
    
    # 3. Time
    converted["Time"] = df["time"].astype(str)
    
    # 4. Down
    converted["Down"] = df["down"].fillna(1).astype(int)
    
    # 5. Distance (Yards to Go)
    converted["Distance"] = df["ydstogo"].fillna(10).astype(int)
    
    # 6. Field Position
    converted["FieldPosition"] = (100 - df["yardline_100"]).fillna(25).astype(int)
    
    # 7. Play Type
    type_map = {
        'pass': 'パス (Pass)',
        'run': 'ラン (Run)',
        'punt': 'パント (Punt)',
        'field_goal': 'FG (Field Goal)'
    }
    converted["PlayType"] = df["play_type"].map(type_map).fillna("Unknown")
    
    # 8. Detail (Description)
    converted["Detail"] = df["desc"].str.slice(0, 200) # Limit length
    
    # 9. Yards Gained
    converted["YardsGained"] = df["yards_gained"].fillna(0).astype(float)
    
    # 10. Success (Custom Logic)
    converted["Success"] = df["success"].fillna(0).astype(int)
    
    # 11. Run/Pass Course 
    def get_course(row):
        if row['play_type'] == 'pass':
            loc = row.get('pass_location', '')
            length = row.get('pass_length', '') # short, deep
            if pd.isna(loc): loc = ''
            if pd.isna(length): length = ''
            return f"{length} {loc}".strip()
        elif row['play_type'] == 'run':
            loc = row.get('run_location', '')
            gap = row.get('run_gap', '') 
            if pd.isna(loc): loc = ''
            if pd.isna(gap): gap = ''
            return f"{loc} {gap}".strip()
        elif row['play_type'] == 'punt':
            return ""
        elif row['play_type'] == 'field_goal':
            dist = row.get('kick_distance', '')
            return f"{dist}yds" if not pd.isna(dist) else ""
        return ""
        
    # Apply is slow, but okay for 5000 rows
    # We'll split into RunCourse and PassCourse
    converted["RunCourse"] = df.apply(lambda x: get_course(x) if x['play_type'] == 'run' else "", axis=1)
    converted["PassCourse"] = df.apply(lambda x: get_course(x) if x['play_type'] == 'pass' else "", axis=1)
    
    # Team (Store in Detail or ignore for now if not in Standard Columns? 
    # Standard Columns: Date, Quarter, Time, Down, Distance, FieldPosition, PlayType, RunCourse, PassCourse, Detail, YardsGained, Success
    # We will ignore 'Team' column for now to match the schema, or append it to detail.
    converted["Detail"] = converted["Detail"] + " (" + df["posteam"] + ")"

    # STRICTLY ORDER COLUMNS TO MATCH database schema
    # otherwise append will corrupt data
    std_columns = [
        "Date", "Quarter", "Time", "Down", "Distance", "FieldPosition", 
        "PlayType", "RunCourse", "PassCourse", "Detail", "YardsGained", "Success"
    ]
    
    # Ensure all exist
    for col in std_columns:
        if col not in converted.columns:
            converted[col] = "" # fallback
            
    return converted[std_columns]

def main():
    # 1. Fetch
    raw_df = fetch_nfl_data(limit=5000) # Fetch 5000 rows for quick start
    
    if raw_df is not None:
        # 2. Process
        clean_df = process_nfl_data(raw_df)
        
        # 3. Save
        # Check if DB exists to append or create
        output_path = "data/match_data.csv"
        
        # Ensure directory
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
        if os.path.exists(output_path):
            # Append but be careful with columns matching
            clean_df.to_csv(output_path, mode='a', header=False, index=False)
            print(f"Appended {len(clean_df)} plays to {output_path}")
        else:
            clean_df.to_csv(output_path, index=False)
            print(f"Created {output_path} with {len(clean_df)} plays")
            
        return len(clean_df)
    return 0

if __name__ == "__main__":
    main()
