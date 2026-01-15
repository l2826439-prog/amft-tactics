import streamlit as st
import pandas as pd
import sys
import os
from datetime import datetime, timedelta

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Force reload of data_manager to ensure latest code is used
import importlib
import src.data_manager
import src.analyzer
import src.security
importlib.reload(src.data_manager)
importlib.reload(src.analyzer)
importlib.reload(src.security)

from src.data_manager import load_excel, get_database, update_database, get_statistics
from src.analyzer import analyze_situation
from src.security import (
    verify_password, change_password, is_locked_out, 
    get_failed_attempts, log_access, get_access_log,
    is_security_enabled, MAX_FAILED_ATTEMPTS, SESSION_TIMEOUT_MINUTES
)

# ========================
# Page Config
# ========================
st.set_page_config(
    page_title="🏈 アメフト戦術提案",
    page_icon="🏈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ========================
# Session State Initialization
# ========================
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "auth_time" not in st.session_state:
    st.session_state.auth_time = None

# ========================
# Session Timeout Check
# ========================
def check_session_timeout():
    """Check if session has timed out"""
    if st.session_state.auth_time:
        elapsed = datetime.now() - st.session_state.auth_time
        if elapsed > timedelta(minutes=SESSION_TIMEOUT_MINUTES):
            st.session_state.authenticated = False
            st.session_state.auth_time = None
            log_access("session_timeout")
            return True
    return False

# ========================
# Login Screen
# ========================
def show_login_screen():
    """Display the login screen"""
    st.markdown("""
    <style>
        .login-container {
            max-width: 400px;
            margin: 100px auto;
            padding: 40px;
            background: white;
            border-radius: 15px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
            text-align: center;
        }
        .login-title {
            color: #1b5e20;
            font-size: 28px;
            margin-bottom: 20px;
        }
        .security-warning {
            color: #d32f2f;
            font-size: 12px;
            margin-top: 15px;
        }
    </style>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("### 🔐 ログイン")
        st.write("このアプリはパスワードで保護されています。")
        
        # Check lockout
        locked, remaining = is_locked_out()
        if locked:
            st.error(f"🚫 セキュリティロック中です。あと {remaining} 分お待ちください。")
            st.caption("連続してログインに失敗したため、一時的にロックされています。")
            return
        
        # Show failed attempts warning
        failed = get_failed_attempts()
        if failed > 0:
            st.warning(f"⚠️ ログイン失敗: {failed}/{MAX_FAILED_ATTEMPTS} 回")
        
        # Password input with HTML form for browser password save
        # Using a form with proper autocomplete attributes
        with st.form("login_form"):
            password = st.text_input(
                "パスワード", 
                type="password", 
                key="login_password",
                help="Chromeにパスワードを保存するには、ログイン後にブラウザの鍵アイコンをクリックしてください"
            )
            
            submitted = st.form_submit_button("🔑 ログイン", use_container_width=True, type="primary")
            
            if submitted:
                if verify_password(password):
                    st.session_state.authenticated = True
                    st.session_state.auth_time = datetime.now()
                    st.rerun()
                else:
                    st.error("パスワードが正しくありません")
        
        st.markdown("---")
        st.caption("🔒 初期パスワード: `tactics2026`")
        st.caption("ログイン後、設定からパスワードを変更してください。")
        
        # Tip for password saving
        st.info("💡 **Chromeにパスワードを保存するには:**\n1. ログイン後、アドレスバー右の🔑アイコンをクリック\n2. 「保存」を選択")

# ========================
# Security Check Gate
# ========================
if is_security_enabled():
    check_session_timeout()
    
    if not st.session_state.authenticated:
        show_login_screen()
        st.stop()  # Stop rendering rest of the app

# ========================
# Clean Light Theme CSS
# ========================
st.markdown("""
<style>
    /* Clean light background */
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #e8ecef 100%);
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #ffffff 0%, #f0f2f6 100%);
        border-right: 2px solid #2e7d32;
    }
    
    /* Headers - green football theme */
    h1, h2, h3 {
        color: #1b5e20 !important;
    }
    
    /* Metric cards */
    [data-testid="stMetric"] {
        background: white;
        border: 2px solid #4caf50;
        border-radius: 12px;
        padding: 15px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    
    /* Primary button - green */
    .stButton > button[kind="primary"] {
        background: linear-gradient(90deg, #2e7d32 0%, #4caf50 100%);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 12px 35px;
        font-weight: bold;
        font-size: 16px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(46, 125, 50, 0.4);
    }
    
    .stButton > button[kind="primary"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(46, 125, 50, 0.6);
    }
    
    /* Suggestion card styling */
    .suggestion-card {
        background: white;
        border: 2px solid #4caf50;
        border-radius: 15px;
        padding: 25px;
        margin: 15px 0;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    
    .play-type {
        font-size: 28px;
        font-weight: bold;
        color: #1b5e20;
        margin-bottom: 15px;
    }
    
    .stat-value {
        font-size: 26px;
        color: #2e7d32;
        font-weight: bold;
    }
    
    .stat-label {
        color: #666;
        font-size: 13px;
        margin-bottom: 5px;
    }
    
    /* Alternative card */
    .alt-card {
        background: white;
        border: 1px solid #c8e6c9;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    }
    
    .alt-card:hover {
        border-color: #4caf50;
        box-shadow: 0 4px 12px rgba(76, 175, 80, 0.2);
    }

    /* Responsive Stats Container */
    .stats-container {
        display: flex;
        gap: 50px;
        margin-top: 20px;
    }
    
    /* Mobile Optimization */
    @media (max-width: 600px) {
        .suggestion-card {
            padding: 15px;
        }
        .play-type {
            font-size: 22px;
        }
        .stats-container {
            flex-direction: column;
            gap: 15px;
        }
        .stat-value {
            font-size: 22px;
        }
        .alt-card {
            padding: 10px;
        }
    }
    
    /* Flex container for alternatives */
    .alt-cards-container {
        display: flex;
        flex-wrap: wrap;
        gap: 15px;
        justify-content: center;
        margin-top: 10px;
    }
    
    .alt-card-wrapper {
        flex: 1 1 200px; /* Grow, shrink, basis */
        max-width: 300px;
    }
</style>
""", unsafe_allow_html=True)

# ========================
# Sidebar - Data Management
# ========================
with st.sidebar:
    st.image("https://img.icons8.com/color/96/american-football.png", width=80)
    st.title("📊 データ管理")
    
    # Get current stats
    stats = get_statistics()
    
    st.markdown("---")
    
    # Stats display
    col1, col2 = st.columns(2)
    with col1:
        st.metric("総試合数", stats["total_games"])
    with col2:
        st.metric("総プレー数", stats["total_plays"])
    
    st.caption(f"最終更新: {stats['last_update']}")
    
    # 🔐 Logout & Security Section
    st.markdown("---")
    st.subheader("🔐 セキュリティ")
    
    # Logout button
    if st.button("🚪 ログアウト", use_container_width=True):
        st.session_state.authenticated = False
        st.session_state.auth_time = None
        log_access("logout")
        st.rerun()
    
    # Security settings expander
    with st.expander("⚙️ セキュリティ設定"):
        st.caption("パスワード変更")
        old_pw = st.text_input("現在のパスワード", type="password", key="old_pw")
        new_pw = st.text_input("新しいパスワード", type="password", key="new_pw")
        confirm_pw = st.text_input("新しいパスワード(確認)", type="password", key="confirm_pw")
        
        if st.button("🔄 パスワード変更"):
            if new_pw != confirm_pw:
                st.error("新しいパスワードが一致しません")
            else:
                success, msg = change_password(old_pw, new_pw)
                if success:
                    st.success(msg)
                else:
                    st.error(msg)
        
        st.markdown("---")
        st.caption("📋 アクセスログ（最新10件）")
        logs = get_access_log(10)
        if logs:
            for entry in logs:
                timestamp = entry['timestamp'][:16].replace('T', ' ')
                event = entry['event']
                icon = "✅" if "success" in event else "❌" if "failed" in event else "🔒" if "lock" in event else "📝"
                st.caption(f"{icon} {timestamp}: {event}")
        else:
            st.caption("ログがありません")

    # 📱 Mobile Access Info
    st.markdown("---")
    with st.expander("📱 スマホからアクセス"):
        st.markdown("""
        **🌐 外出先・モバイル回線からアクセスするには:**
        
        1. PCで **「公開モードで起動.bat」** をダブルクリック
        2. 表示される**公開URL**をスマホに送信
        3. スマホでURLを開く（Wi-Fi不要、ギガでOK）
        
        ---
        
        **📡 同じWi-Fi内からのアクセス:**
        """)
        
        import socket
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            url = f"http://{ip}:8501"
            st.code(url, language="text")
            
            # QR Code
            qr_api = f"https://api.qrserver.com/v1/create-qr-code/?size=120x120&data={url}"
            st.image(qr_api, caption="同じWi-Fi用QR", use_container_width=False)
        except:
            st.caption("(ローカルIP取得不可)")
            
    st.markdown("---")
    
    # File uploader section
    st.subheader("📁 データ管理")
    
    # Create tabs for data management
    tab1, tab2, tab3, tab4 = st.tabs(["📤 データ追加", "📥 テンプレート", "👁️ データ確認", "🗑️ リセット"])
    
    with tab2:
        st.caption("入力用テンプレートをダウンロード")
        try:
            with open("assets/template_v2.xlsx", "rb") as file:
                st.download_button(
                    label="📥 拡張テンプレート (Excel)",
                    data=file,
                    file_name="football_template_v2.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
        except Exception:
            st.warning("テンプレート生成中...")
            
    with tab4:
        st.caption("データベースの初期化")
        if st.checkbox("誤操作防止用チェック", key="reset_check"):
            if st.button("🗑️ データを全削除してリセット", type="primary"):
                if os.path.exists("data/match_data.csv"):
                    os.remove("data/match_data.csv")
                    st.success("データベースをリセットしました")
                    st.rerun()

    with tab3:
        st.caption("現在保存されているデータの中身を確認")
        if os.path.exists("data/match_data.csv"):
            try:
                existing_df = pd.read_csv("data/match_data.csv", on_bad_lines='skip') # Try to skip bad lines first to show something
                st.markdown(f"**総データ数:** {len(existing_df)} 件")
                st.dataframe(existing_df.head(50), use_container_width=True)
            except Exception as e:
                st.error("⚠️ データファイルが破損しているため読み込めません。")
                st.warning("「リセット」タブからデータベースを初期化してください。")
                st.code(f"Error: {e}")
        else:
            st.info("データはまだありません。")

    with tab1:
        st.caption("ExcelファイルまたはNFLデータから追加")
        
        # NFL Section
        with st.expander("🏈 NFLデータのインポート (2023)", expanded=False):
            st.write("NFLの試合データを自動ダウンロードして追加します。")
            if st.button("NFLデータを追加ダウンロード"):
                with st.spinner("ダウンロード中..."):
                    try:
                        import import_nfl_data
                        # Force reload to get updated script
                        import importlib
                        importlib.reload(import_nfl_data)
                        
                        count = import_nfl_data.main()
                        st.success(f"✅ {count} 件のNFLデータをデータベースに追加しました！")
                    except Exception as e:
                        st.error(f"エラー: {e}")

        # Excel Section
        st.caption("Excelデータ追加")
    # File uploader
    uploaded_file = st.file_uploader(
        "試合データをアップロード",
        type=["xlsx", "xls"],
        help="列: Date, Down, Distance, FieldPosition, PlayType, Detail, YardsGained, Success"
    )
    
    if uploaded_file is not None:
        # First, read raw Excel to show columns and sheets
        try:
            import pandas as pd
            all_sheets = pd.read_excel(uploaded_file, sheet_name=None)
            sheet_names = list(all_sheets.keys())
            st.info(f"📋 検出されたシート数: {len(sheet_names)} ({', '.join(sheet_names[:5])}{'...' if len(sheet_names) > 5 else ''})")
            
            # Show columns from first sheet
            first_sheet = list(all_sheets.values())[0]
            st.info(f"📋 列名: {list(first_sheet.columns)}")
            
            uploaded_file.seek(0)  # Reset file pointer
        except Exception as e:
            st.error(f"ファイル読み込みエラー: {e}")
        
        try:
            uploaded_file.seek(0)  # Reset file pointer again
            result = load_excel(uploaded_file)
            
            # Robust unpacking to handle potential stale module loading
            if isinstance(result, tuple):
                df_preview_result, logs = result
            else:
                df_preview_result = result
                logs = ["⚠️ モジュールの再読み込みが不完全な可能性があります。詳細ログは利用できません。"]
            
            # Unpack logs
            if df_preview_result is None:
                df_preview = None
            else:
                df_preview = df_preview_result
                
            # Show logs in expander for debugging
            with st.expander("🔍 読み込みログ (デバッグ用)", expanded=False):
                for log in logs:
                    st.text(log)
                    
        except Exception as e:
            import traceback
            st.error(f"❌ 読み込みエラー: {e}")
            st.code(traceback.format_exc())
            df_preview = None
        
        if df_preview is not None:
            st.success(f"✅ {len(df_preview)} 件のデータを読み込みました（全シート合計）")
            
            with st.expander("📋 プレビュー"):
                st.dataframe(df_preview.head(20), use_container_width=True)
            
            if st.button("✨ データベースに追加", use_container_width=True):
                added = update_database(df_preview)
                st.success(f"🎉 {added} 件追加しました！")
                st.rerun()
        elif df_preview is None:
            st.warning("⚠️ データの読み込みに失敗しました。")
            st.info("👆 上記の「読み込みログ」を確認して、エラー内容を教えてください。")
    
    st.markdown("---")
    st.caption("Made with ❤️ for American Football")

# ========================
# Main Content
# ========================
st.title("🏈 アメフト戦術提案システム")
st.markdown("##### 試合状況を入力して、最適なプレーを提案します")

st.markdown("---")

# Input Form - Row 1
col1, col2, col3 = st.columns(3)

with col1:
    down_options = ["指定なし", "1", "2", "3", "4"]
    down = st.selectbox(
        "🔢 ダウン",
        options=down_options,
        index=0,
        help="現在のダウン数"
    )
    
    quarter_options = ["指定なし", "1Q", "2Q", "3Q", "4Q", "OT"]
    quarter = st.selectbox(
        "⏰ クォーター",
        options=quarter_options,
        index=0,
        help="試合のクォーター"
    )

with col2:
    use_distance = st.checkbox("残りヤードを考慮する", value=True)
    if use_distance:
        distance = st.number_input(
            "📏 残りヤード (Distance)",
            min_value=1,
            max_value=99,
            value=10,
            step=1
        )
    else:
        distance = None
        st.caption("残りヤード: 指定なし")
        
    use_time = st.checkbox("残り時間を考慮する", value=False)
    if use_time:
        time_rem = st.text_input("残り時間 (MM:SS)", value="10:00")
    else:
        time_rem = None

with col3:
    use_score = st.checkbox("点差を考慮する", value=False)
    if use_score:
        score_diff = st.number_input("点差 (自チーム - 敵チーム)", value=0)
    else:
        score_diff = None

# Input Form - Row 2: Field Position Slider (more detailed)
st.markdown("##### 📍 フィールド位置")
use_field_pos = st.checkbox("フィールド位置を考慮する", value=True)

if use_field_pos:
    field_position = st.slider(
        "自陣エンドゾーン(0) ← → 敵陣エンドゾーン(100)",
        min_value=0,
        max_value=100,
        value=25,
        step=5,
        help="0=自陣ゴールライン, 50=ミッドフィールド, 100=敵陣ゴールライン",
        format="%d ヤード"
    )
else:
    field_position = None
    st.info("フィールド位置: 指定なし")

# Display field position in a readable format
if use_field_pos and field_position is not None:
    if field_position <= 20:
        st.info("🛡️ 自陣深く (Deep Own Territory)")
    elif field_position >= 80:
        st.error("🚨 レッドゾーン (Red Zone)!")
    else:
        st.success("🏃 フィールド中央 (Mid Field)")

# Store in session state for analyzer
# The original code had a 'situation' dictionary later. This section seems to be an attempt to define it earlier.
# I will integrate the new fields into the 'situation' dictionary that is already present before the analysis.

# Display field position in a readable format (original logic, kept for display)
if field_position is not None: # Added check for None
    if field_position <= 50:
        pos_text = f"自陣 {field_position} ヤードライン"
    else:
        pos_text = f"敵陣 {100 - field_position} ヤードライン"
        
    if field_position >= 80:
        pos_text += " 🔴 レッドゾーン!"
        
    st.caption(f"現在位置: **{pos_text}**")
else:
    st.caption("現在位置: 指定なし")


st.markdown("")

# Suggest Button
if st.button("⚡ 戦術を提案する", use_container_width=True, type="primary"):
    
    # Get data
    df = get_database()
    
    if df.empty:
        st.warning("📭 データがありません。まずExcelファイルをアップロードしてください。")
    else:
        # Analyze
        situation = {
            "Down": int(down) if down != "指定なし" else None,
            "Distance": distance,
            "FieldPosition": field_position,
            "ScoreDiff": score_diff,
            "Quarter": quarter if quarter != "指定なし" else None,
            "TimeRemaining": time_rem
        }
        
        suggestions = analyze_situation(df, situation)
        
        if not suggestions:
            st.info("🔍 類似の状況が見つかりませんでした。もう少しデータを追加してください。")
        else:
            st.markdown("## 💡 推奨プレー")
            
            # Top suggestion - Hero card
            top = suggestions[0]
            st.markdown(f"""
            <div class="suggestion-card">
                <div class="play-type">🥇 推奨: {top['play_type']}</div>
                <div class="stats-container">
                    <div>
                        <div class="stat-label">期待獲得ヤード</div>
                        <div class="stat-value">{top['avg_gain']} yd</div>
                    </div>
                    <div>
                        <div class="stat-label">成功率</div>
                        <div class="stat-value">{top['success_rate']}</div>
                    </div>
                    <div>
                        <div class="stat-label">サンプル数</div>
                        <div class="stat-value">{top['sample_size']}</div>
                    </div>
                </div>
                <div style="margin-top: 20px; color: #555; font-size: 14px; background: #f5f5f5; padding: 10px; border-radius: 8px;">
                    📝 {top['reason']}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Other options
            if len(suggestions) > 1:
                st.markdown("### 🔄 その他の選択肢")
                
                # Show next 3 alternatives in responsive cards
                cards_html = '<div class="alt-cards-container">'
                for sug in suggestions[1:4]:
                    cards_html += f"""
                    <div class="alt-card-wrapper">
                        <div class="alt-card">
                            <div style="font-size: 20px; color: #2e7d32; font-weight: bold;">
                                {sug['play_type']}
                            </div>
                            <div style="color: #1b5e20; font-size: 24px; margin: 12px 0; font-weight: bold;">
                                {sug['avg_gain']} yd
                            </div>
                            <div style="color: #666; font-size: 13px;">
                                成功率: {sug['success_rate']} | n={sug['sample_size']}
                            </div>
                        </div>
                    </div>
                    """
                cards_html += '</div>'
                st.markdown(cards_html, unsafe_allow_html=True)
                
                # Show Full List if more than 4 items (1 hero + 3 cards)
                if len(suggestions) > 4:
                    with st.expander(f"📋 すべての選択肢を見る ({len(suggestions)}件)"):
                        # Convert suggestions to DataFrame for display
                        all_sugs_df = pd.DataFrame(suggestions)
                        # Rename columns for display
                        display_df = all_sugs_df[["play_type", "avg_gain", "success_rate", "sample_size", "reason"]].copy()
                        display_df.columns = ["プレー種別", "平均獲得ヤード", "成功率", "サンプル数", "理由・詳細"]
                        st.dataframe(display_df, use_container_width=True)

# ========================
# Footer with current data preview
# ========================
st.markdown("---")

with st.expander("📊 現在のデータベース確認"):
    df = get_database()
    if not df.empty:
        st.dataframe(df, use_container_width=True, height=300)
    else:
        st.info("データがまだありません。Excelファイルをアップロードしてください。")
