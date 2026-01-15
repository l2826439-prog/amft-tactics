
import pandas as pd
import os

def create_template():
    # Define standard columns based on user request + standard football metrics
    data = {
        "Date": ["2024-09-01", "2024-09-01", "2024-09-01"],
        "Quarter": ["1Q", "2Q", "3Q"],
        "Time": ["10:00", "02:30", "08:15"],
        "PlayNumber": [1, 15, 28],
        "Team": ["OffenseTeam", "OffenseTeam", "OffenseTeam"],
        "Down": [1, 2, 3],
        "Distance": [10, 6, 4], # Yards to First Down
        "FieldPosition": [25, 45, 80],
        "Hash": ["L", "M", "R"],
        "Formation": ["I-Form", "Shotgun", "Empty"],
        "PlayType": ["Run", "Pass", "Screen"],
        "RunCourse": ["Middle", "", ""],
        "PassCourse": ["", "Slant", "Screen Left"],
        "YardsGained": [4, 8, 12],
        "Result": ["", "First Down", "Touchdown"],
        "Memo": ["Power run", "Quick slant", "Good blocking"]
    }
    
    df = pd.DataFrame(data)
    
    # Define validation/help sheet
    help_data = {
        "Column": [
            "Date", "Quarter", "Time", "PlayNumber", "Team", "Down", 
            "Distance", "FieldPosition", "Hash", "Formation", 
            "PlayType", "RunCourse", "PassCourse", "YardsGained", "Result", "Memo"
        ],
        "Description": [
            "試合日 (YYYY-MM-DD)",
            "クォーター (1Q, 2Q, 3Q, 4Q, OT)",
            "残り時間 (MM:SS)",
            "プレー番号",
            "攻撃チーム名",
            "ダウン数 (1-4)",
            "ファーストダウンまでの残りヤード",
            "開始位置 (0-100, 自陣0-50, 敵陣51-100推定)",
            "ハッシュ (L, M, R)",
            "フォーメーション名",
            "プレー種別 (Run, Pass, Screen, Draw, Punt, FG)",
            "ランコース (Middle, Outside, Sweep etc)",
            "パスコース (Short, Deep, Screen, Slant etc)",
            "獲得ヤード (ロスはマイナス)",
            "結果詳細 (First Down, TD, INT etc)",
            "メモ・詳細"
        ]
    }
    help_df = pd.DataFrame(help_data)
    
    # Ensure assets directory exists
    os.makedirs("assets", exist_ok=True)
    
    # Write to Excel with multiple sheets
    file_path = "assets/template_v2.xlsx"
    with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='MatchData', index=False)
        help_df.to_excel(writer, sheet_name='Explanation', index=False)
        
    print(f"Template created at {file_path}")

if __name__ == "__main__":
    create_template()
