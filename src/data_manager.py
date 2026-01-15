
import pandas as pd
import os
from typing import Optional

# Constants
DATA_FILE_PATH = "data/match_data.csv"

# Internal standard columns
# Internal standard columns
STANDARD_COLUMNS = [
    "Date", "Quarter", "Time", "Down", "Distance", "FieldPosition", 
    "PlayType", "RunCourse", "PassCourse", "Detail", "YardsGained", "Success"
]

# Column mapping for user's custom format
# Maps user's column names -> standard column names
COLUMN_MAPPINGS = {
    # User format 1 (original)
    "Date": "Date",
    "Down": "Down", 
    "Distance": "Distance",
    "FieldPosition": "FieldPosition",
    "PlayType": "PlayType",
    "Detail": "Detail",
    "YardsGained": "YardsGained",
    "Success": "Success",
    
    # User format 2 (shuma's format)
    "Play #": "PlayNumber",
    "Play Type": "PlayType",
    "PorFG": "PorFG",
    "Start Yard": "FieldPosition",
    "Yards to EDown": "Distance",
    "Yards to FGained Yards": "YardsGained",
    "Pass Success/Fail": "Success",
    "Turnover (Yes/No)": "Turnover",
    "FGgood/no": "FGResult",
    "score": "Score",
    "memo": "Memo",
    
    # New Standard Format (v2)
    "Quarter": "Quarter",
    "Time": "Time",
    "PlayNumber": "PlayNumber",
    "Team": "Team",
    "RunCourse": "RunCourse",
    "PassCourse": "PassCourse",
    "Result": "Detail",
    "Memo": "Detail"
}


def find_column(columns, *keywords):
    """Find a column that contains any of the keywords (case-insensitive)."""
    for col in columns:
        col_lower = str(col).lower()
        for keyword in keywords:
            if keyword.lower() in col_lower:
                return col
    return None

def detect_and_convert_format(df: pd.DataFrame) -> pd.DataFrame:
    """
    Detect the Excel format and convert to standard format.
    """
    columns = df.columns.tolist()
    print(f"Processing columns: {columns}")
    
    # Check if it's shuma's format (has Play Type or Play #)
    play_type_col = find_column(columns, 'play type', 'playtype')
    has_shuma_format = play_type_col is not None or find_column(columns, 'play #', 'play#') is not None
    
    if has_shuma_format:
        # Convert shuma's format to standard format
        converted = pd.DataFrame()
        
        # Map columns
        converted["Date"] = pd.Timestamp.now().strftime("%Y-%m-%d")
        
        # --- Basic Metrics ---
        # Play Type
        if play_type_col:
            converted["PlayType"] = df[play_type_col].fillna("Unknown")
        else:
            converted["PlayType"] = "Unknown"
        
        # Field Position
        field_col = find_column(columns, 'start yard', 'yardline', 'fieldposition')
        if field_col:
            converted["FieldPosition"] = df[field_col]
        else:
            converted["FieldPosition"] = ""
        
        # Distance (Yards to First Down)
        distance_col = find_column(columns, 'first down', 'to edown', 'yards to e', 'distance')
        if distance_col:
            converted["Distance"] = pd.to_numeric(df[distance_col], errors='coerce')
        else:
            converted["Distance"] = 10
            
        # Yards Gained
        gained_col = find_column(columns, 'gained yards', 'gained', 'yardsgained')
        if gained_col:
            converted["YardsGained"] = pd.to_numeric(df[gained_col], errors='coerce')
        else:
            converted["YardsGained"] = 0
            
        # Success
        success_col = find_column(columns, 'success/fail', 'success', 'fail')
        if success_col:
            converted["Success"] = df[success_col].apply(
                lambda x: 1 if str(x).lower() in ['success', 'yes', '1', 'true', '成功'] else 0
            )
        else:
            converted["Success"] = 0
            
        # Down
        down_col = find_column(columns, 'down')
        if down_col and 'first' not in str(down_col).lower() and 'yards' not in str(down_col).lower():
            converted["Down"] = pd.to_numeric(df[down_col], errors='coerce').fillna(1)
        else:
            converted["Down"] = 1

        # --- Enhanced Metrics (Time, Course, etc) ---
        
        # Quarter
        quarter_col = find_column(columns, 'quarter', 'qtr')
        if quarter_col:
            converted["Quarter"] = df[quarter_col]
        else:
            converted["Quarter"] = ""
            
        # Time
        time_col = find_column(columns, 'time', 'remaining')
        if time_col:
            converted["Time"] = df[time_col]
        else:
            converted["Time"] = ""
            
        # Run Course
        run_course_col = find_column(columns, 'run course', 'runcourse', 'run dir')
        if run_course_col:
            converted["RunCourse"] = df[run_course_col]
        else:
            converted["RunCourse"] = ""
            
        # Pass Course
        pass_course_col = find_column(columns, 'pass course', 'passcourse', 'pass route')
        if pass_course_col:
            converted["PassCourse"] = df[pass_course_col]
        else:
            converted["PassCourse"] = ""
            
        # Detail (memo or Result)
        memo_col = find_column(columns, 'memo', 'note', 'detail', 'result')
        if memo_col:
            converted["Detail"] = df[memo_col].fillna("")
        else:
            converted["Detail"] = ""
        
        print(f"Converted {len(converted)} rows with columns: {converted.columns.tolist()}")
        return converted
        
    # Check if it's the original expected format
    elif all(col in columns for col in ["PlayType", "YardsGained"]):
        # Original format - just ensure all columns exist
        result = df.copy()
        for col in STANDARD_COLUMNS:
            if col not in result.columns:
                if col == "Date":
                    result[col] = pd.Timestamp.now().strftime("%Y-%m-%d")
                elif col in ["Down", "Distance", "YardsGained"]:
                    result[col] = 0
                elif col == "Success":
                    result[col] = 0
                else:
                    result[col] = ""
        return result[STANDARD_COLUMNS]
    
    else:
        # Unknown format - try to use whatever columns exist
        result = pd.DataFrame()
        result["Date"] = pd.Timestamp.now().strftime("%Y-%m-%d")
        result["Down"] = 1
        result["Distance"] = 10
        result["FieldPosition"] = ""
        result["PlayType"] = df.iloc[:, 0] if len(df.columns) > 0 else "Unknown"
        result["Detail"] = ""
        result["YardsGained"] = 0
        result["Success"] = 0
        return result

def load_excel(file) -> tuple[Optional[pd.DataFrame], list[str]]:
    """
    Reads an uploaded Excel file and validates/formats it.
    Returns (DataFrame, logs) tuple.
    """
    logs = []
    try:
        # Read ALL sheets from Excel file
        all_sheets = pd.read_excel(file, sheet_name=None)
        
        logs.append(f"Found {len(all_sheets)} sheets: {list(all_sheets.keys())}")
        
        all_dfs = []
        
        for sheet_name, df in all_sheets.items():
            if df.empty:
                logs.append(f"Sheet '{sheet_name}' is empty, skipping")
                continue
            
            logs.append(f"Processing sheet '{sheet_name}' with {len(df)} rows")
            logs.append(f"Columns: {df.columns.tolist()}")
            
            try:
                # Detect format and convert
                converted_df = detect_and_convert_format(df)
                
                # Check for conversion success
                if converted_df.empty:
                    logs.append(f"  -> Warning: No valid data converted from sheet '{sheet_name}'")
                    continue
                    
                logs.append(f"  -> Converted columns: {converted_df.columns.tolist()}")
                
                # Add sheet name as team identifier
                converted_df["Team"] = sheet_name
                
                # Convert numeric columns
                converted_df["Down"] = pd.to_numeric(converted_df["Down"], errors='coerce').fillna(1).astype(int)
                converted_df["Distance"] = pd.to_numeric(converted_df["Distance"], errors='coerce').fillna(10)
                converted_df["YardsGained"] = pd.to_numeric(converted_df["YardsGained"], errors='coerce').fillna(0)
                
                # Drop rows with missing PlayType
                pre_filter_len = len(converted_df)
                converted_df = converted_df.dropna(subset=["PlayType"])
                converted_df = converted_df[converted_df["PlayType"].astype(str).str.strip() != ""]
                
                if len(converted_df) < pre_filter_len:
                    logs.append(f"  -> Filtered out {pre_filter_len - len(converted_df)} rows with missing PlayType")
                
                if not converted_df.empty:
                    all_dfs.append(converted_df)
                    logs.append(f"  -> Added {len(converted_df)} rows from sheet '{sheet_name}'")
                else:
                    logs.append(f"  -> Sheet result is empty after filtering")
                    
            except Exception as e:
                logs.append(f"  -> Error processing sheet '{sheet_name}': {str(e)}")
                import traceback
                logs.append(traceback.format_exc())
        
        if not all_dfs:
            logs.append("No valid data found in any sheet")
            return None, logs
        
        # Combine all sheets
        combined_df = pd.concat(all_dfs, ignore_index=True)
        logs.append(f"Total combined rows: {len(combined_df)}")
        
        return combined_df, logs
        
    except Exception as e:
        logs.append(f"Critical Error loading Excel: {str(e)}")
        import traceback
        logs.append(traceback.format_exc())
        return None, logs

def get_database() -> pd.DataFrame:
    """
    Returns the current master dataset. 
    If not exists, returns an empty DataFrame with proper schema.
    """
    if os.path.exists(DATA_FILE_PATH):
        try:
            return pd.read_csv(DATA_FILE_PATH, on_bad_lines='skip')
        except Exception as e:
            print(f"Error reading database: {e}")
            pass
            
    # Return empty dataframe structure
    return pd.DataFrame(columns=STANDARD_COLUMNS)

def update_database(new_df: pd.DataFrame) -> int:
    """
    Appends new data to the master dataset and saves it.
    Returns the number of rows added.
    """
    current_df = get_database()
    
    # Ensure new_df has all standard columns
    for col in STANDARD_COLUMNS:
        if col not in new_df.columns:
            new_df[col] = ""
    
    # Select only standard columns
    new_df = new_df[STANDARD_COLUMNS]
    
    # Concatenate
    updated_df = pd.concat([current_df, new_df], ignore_index=True)
    
    # Save
    updated_df.to_csv(DATA_FILE_PATH, index=False)
    
    return len(new_df)

def get_statistics():
    """
    Returns a dictionary with basic stats of the database.
    """
    df = get_database()
    return {
        "total_games": df["Date"].nunique() if not df.empty else 0,
        "total_plays": len(df),
        "last_update": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
    }
