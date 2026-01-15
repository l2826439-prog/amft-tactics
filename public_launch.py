"""
公開URL起動スクリプト (固定URL版)
localtunnel を使用して固定のURLでアクセス可能にします。
"""

import subprocess
import threading
import time
import sys
import random
import string

def install_package(package):
    """パッケージをインストール"""
    print(f"{package}をインストール中...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", package], 
                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def get_subdomain():
    """固定のサブドメイン名を生成（チーム名ベース）"""
    # サブドメイン名を設定ファイルから読み込むか、新規生成
    import os
    config_file = "data/subdomain.txt"
    
    os.makedirs("data", exist_ok=True)
    
    if os.path.exists(config_file):
        with open(config_file, 'r') as f:
            subdomain = f.read().strip()
            if subdomain:
                return subdomain
    
    # 新規生成 (ランダムな固定名)
    subdomain = "amefuto-tactics-" + ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    with open(config_file, 'w') as f:
        f.write(subdomain)
    
    return subdomain

def run_streamlit():
    """Streamlitアプリをバックグラウンドで起動"""
    process = subprocess.Popen([
        sys.executable, "-m", "streamlit", "run", "app.py",
        "--server.port", "8501",
        "--server.address", "0.0.0.0",
        "--server.headless", "true"
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return process

def main():
    print("=" * 55)
    print("  🏈 アメフト戦術提案アプリ - 公開URL起動モード")
    print("=" * 55)
    print()
    
    # 1. 必要なパッケージを確認
    try:
        from pyngrok import ngrok
    except ImportError:
        install_package("pyngrok")
        from pyngrok import ngrok
    
    # 2. Streamlitを起動
    print("📱 Streamlitアプリを起動中...")
    streamlit_proc = run_streamlit()
    time.sleep(4)
    
    # 3. ngrokトンネルを開始
    print("🌐 公開URLを生成中...")
    print()
    
    try:
        # ngrokのauthtoken設定チェック
        # 無料アカウントでも固定ドメインが使えるようになった
        public_url = ngrok.connect(8501, bind_tls=True)
        
        print("=" * 55)
        print("✅ 公開準備完了！")
        print("=" * 55)
        print()
        print(f"🌐 公開URL: {public_url}")
        print()
        print("📱 このURLをスマホに送信してください")
        print("   （LINEやメールでコピペ）")
        print()
        print("⚠️ 注意:")
        print("   - このウィンドウを閉じるとアクセスできなくなります")
        print("   - URLは起動ごとに変わります")
        print("   - 固定URLにするにはngrokの無料登録が必要です")
        print("     https://ngrok.com/signup")
        print()
        print("🔒 固定URLを設定するには:")
        print("   1. https://ngrok.com で無料アカウント作成")
        print("   2. Dashboard > Your Authtoken をコピー")
        print("   3. コマンドプロンプトで:")
        print('      ngrok config add-authtoken <あなたのトークン>')
        print()
        print("-" * 55)
        print("終了するには Ctrl+C を押してください")
        print("-" * 55)
        
        # プロセスを維持
        try:
            ngrok.get_ngrok_process().proc.wait()
        except KeyboardInterrupt:
            print("\n終了中...")
            
    except Exception as e:
        print(f"❌ エラー: {e}")
        print()
        print("解決方法:")
        print("1. ngrok の無料アカウントを作成: https://ngrok.com/signup")
        print("2. Dashboard から Authtoken をコピー")
        print("3. コマンドプロンプトで以下を実行:")
        print('   ngrok config add-authtoken <あなたのトークン>')
        print()
        input("Enterキーで終了...")
    
    finally:
        streamlit_proc.terminate()
        ngrok.kill()

if __name__ == "__main__":
    main()
