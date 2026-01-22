import flet as ft
import google.generativeai as genai

# --- 1. Geminiの設定 ---
# 【重要】もし動かない場合は、新しいAPIキーを取得してここに貼り付けてください
API_KEY = "AIzaSyCT-RtMklRNQ8_kezCr2cjHSpLi_mK-g8g"
genai.configure(api_key=API_KEY)

SYSTEM_PROMPT = (
    "あなたは世界で一番優しいおばあちゃんです。相談者に対し『〜だねぇ』『〜だよ』と穏やかに話し、"
    "どんな悩みも否定せず受け入れてください。最後に温かい一言を添えてください。🍵"
)

def get_best_model():
    try:
        # 利用可能なモデルを確認して最適なものを選択
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        
        if 'models/gemini-1.5-flash' in available_models:
            target = 'models/gemini-1.5-flash'
        elif 'models/gemini-pro' in available_models:
            target = 'models/gemini-pro'
        else:
            target = available_models[0]
            
        return genai.GenerativeModel(model_name=target, system_instruction=SYSTEM_PROMPT)
    except Exception:
        # 取得に失敗した場合は、最も標準的な名前で試みる
        return genai.GenerativeModel(model_name='gemini-1.5-flash')

model = get_best_model()

# --- 2. アプリのメイン処理 ---
def main(page: ft.Page):
    page.title = "おばあちゃんの相談室"
    page.window_width = 450
    page.window_height = 700
    page.bgcolor = "#FDF5E6"
    page.theme_mode = ft.ThemeMode.LIGHT
    
    # チャット履歴を管理するセッション
    if model:
        chat_session = model.start_chat(history=[])
    else:
        chat_session = None

    chat_history = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True, spacing=15)

    def send_message(e):
        if not user_input.value or not chat_session:
            return
        
        user_text = user_input.value
        user_input.value = "" # 先に入力欄を空にする
        
        # ユーザーの発言を表示
        chat_history.controls.append(
            ft.Row([
                ft.Container(
                    content=ft.Text(f"あなた: {user_text}", color="white"),
                    bgcolor="#8D6E63",
                    padding=12,
                    border_radius=ft.border_radius.only(top_left=15, top_right=15, bottom_left=15),
                )
            ], alignment=ft.MainAxisAlignment.END)
        )
        page.update()

        # おばあちゃんの返答を取得
        try:
            response = chat_session.send_message(user_text)
            chat_history.controls.append(
                ft.Row([
                    ft.Container(
                        content=ft.Text(f"おばあちゃん: {response.text}", size=16),
                        bgcolor="#E8F5E9",
                        padding=12,
                        border_radius=ft.border_radius.only(top_left=15, top_right=15, bottom_right=15),
                        width=320
                    )
                ], alignment=ft.MainAxisAlignment.START)
            )
        except Exception as ex:
            chat_history.controls.append(
                ft.Text(f"【おばあちゃんからのメモ】: {ex}", color="red", size=11)
            )
        
        page.update()
        chat_history.scroll_to(offset=-1, duration=300)

    # 入力欄
    user_input = ft.TextField(
        hint_text="おばあちゃん、あのね...", 
        expand=True, 
        border_radius=20,
        on_submit=send_message
    )

    # --- 修正の要：エラーを避けるために文字のボタンに変更 ---
    send_button = ft.ElevatedButton(
        content=ft.Text("送信"), 
        on_click=send_message,
        bgcolor="#A5D6A7",
        color="black"
    )

    # 画面全体のレイアウト
    page.add(
        ft.Container(
            content=ft.Text("👵 おばあちゃんの相談室", size=24, weight="bold", color="#5D4037"),
            alignment=ft.alignment.center,
            padding=10
        ),
        ft.Divider(height=2),
        ft.Container(content=chat_history, expand=True, padding=10),
        ft.Container(
            content=ft.Row([user_input, send_button], spacing=10),
            padding=10
        )
    )

if __name__ == "__main__":
    ft.app(target=main)