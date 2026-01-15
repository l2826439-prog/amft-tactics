"""
Create sample Excel file for testing
"""
import pandas as pd

# Sample play-by-play data
data = [
    # Game 1 - Mix of plays
    {"Date": "2025-01-01", "Down": 1, "Distance": 10, "FieldPosition": "Own 25", "PlayType": "Run", "Detail": "Inside", "YardsGained": 4, "Success": 1},
    {"Date": "2025-01-01", "Down": 2, "Distance": 6, "FieldPosition": "Own 29", "PlayType": "Pass", "Detail": "Slant", "YardsGained": 8, "Success": 1},
    {"Date": "2025-01-01", "Down": 1, "Distance": 10, "FieldPosition": "Own 37", "PlayType": "Run", "Detail": "Outside", "YardsGained": 2, "Success": 0},
    {"Date": "2025-01-01", "Down": 2, "Distance": 8, "FieldPosition": "Own 39", "PlayType": "Pass", "Detail": "Out", "YardsGained": 12, "Success": 1},
    {"Date": "2025-01-01", "Down": 1, "Distance": 10, "FieldPosition": "Opp 49", "PlayType": "Play Action", "Detail": "Deep", "YardsGained": 25, "Success": 1},
    {"Date": "2025-01-01", "Down": 1, "Distance": 10, "FieldPosition": "Opp 24", "PlayType": "Run", "Detail": "Draw", "YardsGained": 6, "Success": 1},
    {"Date": "2025-01-01", "Down": 2, "Distance": 4, "FieldPosition": "Opp 18", "PlayType": "Pass", "Detail": "Screen", "YardsGained": 10, "Success": 1},
    
    # Game 2 - More data points
    {"Date": "2025-01-08", "Down": 1, "Distance": 10, "FieldPosition": "Own 30", "PlayType": "Pass", "Detail": "Go", "YardsGained": 45, "Success": 1},
    {"Date": "2025-01-08", "Down": 1, "Distance": 10, "FieldPosition": "Opp 25", "PlayType": "Run", "Detail": "Inside", "YardsGained": 3, "Success": 0},
    {"Date": "2025-01-08", "Down": 2, "Distance": 7, "FieldPosition": "Opp 22", "PlayType": "Pass", "Detail": "Slant", "YardsGained": 7, "Success": 1},
    {"Date": "2025-01-08", "Down": 1, "Distance": 10, "FieldPosition": "Opp 15", "PlayType": "Run", "Detail": "Outside", "YardsGained": 8, "Success": 1},
    {"Date": "2025-01-08", "Down": 2, "Distance": 2, "FieldPosition": "Opp 7", "PlayType": "Run", "Detail": "Inside", "YardsGained": 3, "Success": 1},
    {"Date": "2025-01-08", "Down": 1, "Distance": 4, "FieldPosition": "Opp 4", "PlayType": "Pass", "Detail": "Fade", "YardsGained": 4, "Success": 1},
    
    # 3rd down situations
    {"Date": "2025-01-15", "Down": 3, "Distance": 5, "FieldPosition": "Own 40", "PlayType": "Pass", "Detail": "Out", "YardsGained": 6, "Success": 1},
    {"Date": "2025-01-15", "Down": 3, "Distance": 3, "FieldPosition": "Opp 35", "PlayType": "Run", "Detail": "Draw", "YardsGained": 5, "Success": 1},
    {"Date": "2025-01-15", "Down": 3, "Distance": 8, "FieldPosition": "Own 25", "PlayType": "Pass", "Detail": "Slant", "YardsGained": 10, "Success": 1},
    {"Date": "2025-01-15", "Down": 3, "Distance": 2, "FieldPosition": "Opp 10", "PlayType": "Run", "Detail": "Inside", "YardsGained": 2, "Success": 1},
    {"Date": "2025-01-15", "Down": 3, "Distance": 10, "FieldPosition": "Own 15", "PlayType": "Pass", "Detail": "Go", "YardsGained": -2, "Success": 0},
    
    # More 1st and 10 data
    {"Date": "2025-01-22", "Down": 1, "Distance": 10, "FieldPosition": "Own 20", "PlayType": "Run", "Detail": "Inside", "YardsGained": 5, "Success": 1},
    {"Date": "2025-01-22", "Down": 1, "Distance": 10, "FieldPosition": "Own 35", "PlayType": "Pass", "Detail": "Slant", "YardsGained": 15, "Success": 1},
    {"Date": "2025-01-22", "Down": 1, "Distance": 10, "FieldPosition": "Opp 40", "PlayType": "Play Action", "Detail": "Deep", "YardsGained": 30, "Success": 1},
    {"Date": "2025-01-22", "Down": 1, "Distance": 10, "FieldPosition": "Own 25", "PlayType": "Run", "Detail": "Outside", "YardsGained": 7, "Success": 1},
    {"Date": "2025-01-22", "Down": 1, "Distance": 10, "FieldPosition": "Own 40", "PlayType": "Pass", "Detail": "Screen", "YardsGained": 12, "Success": 1},
]

df = pd.DataFrame(data)
df.to_excel("assets/sample_data.xlsx", index=False)
print(f"Created sample_data.xlsx with {len(df)} plays")
