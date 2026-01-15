
import pandas as pd
from typing import Dict, List, Any

def filter_data(df: pd.DataFrame, down: int = None, distance: int = None, field_pos: int = None, quarter: str = None) -> pd.DataFrame:
    """
    Filters the dataset based on the current situation.
    If a parameter is None, that filter is ignored.
    """
    if df.empty:
        return df
        
    filtered = df.copy()
        
    # Filter by Down
    if down is not None:
        filtered = filtered[filtered["Down"] == down]
    
    # Filter by Distance (Range: Distance - 2 to Distance + 2)
    if distance is not None:
        min_dist = max(0, distance - 2)
        max_dist = distance + 2
        filtered = filtered[(filtered["Distance"] >= min_dist) & (filtered["Distance"] <= max_dist)]
        
    # Filter by Field Position (Range: +- 10 yards)
    if field_pos is not None:
        # Assuming FieldPosition is stored as int 0-100
        # If it's string in DB, might need conversion. Assuming int here as per data_manager
        # Only apply if 'FieldPosition' column exists and is numeric
        if "FieldPosition" in filtered.columns:
            # Try to convert to numeric just in case
            filtered["FieldPosition_Num"] = pd.to_numeric(filtered["FieldPosition"], errors='coerce')
            
            min_pos = max(0, field_pos - 10)
            max_pos = min(100, field_pos + 10)
            
            filtered = filtered[(filtered["FieldPosition_Num"] >= min_pos) & (filtered["FieldPosition_Num"] <= max_pos)]
    
    # Filter by Quarter
    if quarter is not None and "Quarter" in filtered.columns:
        filtered = filtered[filtered["Quarter"].astype(str) == str(quarter)]
        
    return filtered

def analyze_situation(df: pd.DataFrame, current_situation: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Analyzes the filtered data and returns suggestions.
    """
def analyze_situation(df: pd.DataFrame, current_situation: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Analyzes the filtered data and returns suggestions.
    """
    down = current_situation.get("Down")
    distance = current_situation.get("Distance")
    field_pos = current_situation.get("FieldPosition")
    quarter = current_situation.get("Quarter")
    
    # 1. Filter relevant past plays
    relevant_plays = filter_data(df, down, distance, field_pos, quarter)
    
    if relevant_plays.empty:
        return []
        
    # 2. Create 'Strategy' column for detailed analysis
    # Combines PlayType with RunCourse or PassCourse if available
    df_calc = relevant_plays.copy()
    
    def get_strategy_name(row):
        pt = str(row.get("PlayType", "")).strip()
        
        # Map numeric or short codes if necessary (handling legacy data)
        code_map = {
            "1": "パス (Pass)", "1.0": "パス (Pass)",
            "2": "ラン (Run)", "2.0": "ラン (Run)",
            "3": "スクリーン (Screen)", "3.0": "スクリーン (Screen)",
            "4": "ドロー (Draw)", "4.0": "ドロー (Draw)",
            "P": "パント (Punt)", "FG": "フィールドゴール (FG)"
        }
        
        if pt in code_map:
            pt = code_map[pt]
        elif str(pt).replace(".0", "") in code_map:
             pt = code_map[str(pt).replace(".0", "")]

        # Add course detail
        detail = ""
        if "Pass" in pt or "Pass" in str(row.get("PlayType", "")):
            course = str(row.get("PassCourse", "")).strip()
            if course and course != "nan":
                detail = f" - {course}"
        elif "Run" in pt or "Run" in str(row.get("PlayType", "")):
            course = str(row.get("RunCourse", "")).strip()
            if course and course != "nan":
                detail = f" - {course}"
                
        return f"{pt}{detail}"

    df_calc["Strategy"] = df_calc.apply(get_strategy_name, axis=1)

    # 3. Group by Strategy
    stats = df_calc.groupby("Strategy").agg(
        avg_gain=("YardsGained", "mean"),
        success_rate=("Success", "mean"),
        count=("YardsGained", "count")
    ).reset_index()
    
    # 4. Rank plays
    # Sort by metrics. For Kick-related plays, AvgGain might be 0, so maybe sort by count or success too?
    # For now, stick to avg_gain descending, but maybe push high frequency plays up?
    stats = stats.sort_values(by=["avg_gain", "count"], ascending=[False, False])
    
    suggestions = []
    
    for _, row in stats.iterrows():
        if row["count"] > 0:
            strategy_name = row["Strategy"]
            avg_gain = row["avg_gain"]
            count = row["count"]
            
            # Analyze detail for context (Why is it negative? Why is it high?)
            # Get original rows for this strategy
            subset = df_calc[df_calc["Strategy"] == strategy_name]
            
            context_notes = []
            
            # Check for negative plays (Sacks, Loss)
            neg_plays = subset[subset["YardsGained"] < 0]
            if not neg_plays.empty:
                neg_count = len(neg_plays)
                # Check desc for "sack"
                sack_count = neg_plays["Detail"].str.contains("sack", case=False, na=False).sum()
                if sack_count > 0:
                    context_notes.append(f"サック{sack_count}回")
                elif neg_count > 0:
                    context_notes.append(f"ロス{neg_count}回")
            
            # Check for big plays
            big_plays = subset[subset["YardsGained"] > 20]
            if not big_plays.empty:
                context_notes.append(f"ビッグゲインあり({len(big_plays)}回)")

            reason_text = f"{count}回の類似プレーに基づく (平均 {round(avg_gain, 1)} yd)。"
            if context_notes:
                reason_text += " 要因: " + "、".join(context_notes)

            suggestions.append({
                "play_type": strategy_name,
                "avg_gain": round(avg_gain, 1),
                "success_rate": f"{row['success_rate']*100:.0f}%" if "success_rate" in row else "N/A",
                "sample_size": count,
                "reason": reason_text
            })
            
    return suggestions
