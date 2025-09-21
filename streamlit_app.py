import streamlit as st
import google.generativeai as genai

st.title("💬 チャットボット")
st.write(
    "このチャットボットは Google Gemini Flash-2.5 モデルを使って回答を生成します。"
)

api_key = st.secrets.get("gemini_api_key", "")

sp1 = '''
渋沢栄一の業績について理解しているかどうかを確認する小テストを４問（５択問題を２問、穴埋め問題を２問）作成して。
作成した４つの問題を、一度には１問だけ、順番に出題し、それに対するユーザからの答えに対して、正解か不正解かを答えて、その解説も示して。
それを４問について繰り返して、最後には、ユーザが理解していない部分がどの部分かを示して。
'''

if not api_key:
    st.info("Gemini API キーを .streamlit/secrets.toml の 'gemini_api_key' に追加してください。", icon="🗝️")
else:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.5-flash")

    # チャットメッセージ保存用のセッションステート変数
    if "messages" not in st.session_state:
        # 最初のプロンプトを追加
        st.session_state.messages = [
            {
                "role": "user",
                "content": sp1
            }
        ]
        # Gemini APIで最初のクイズ回答を取得して追加
        history = [{"role": "user", "parts": [sp1]}]
        try:
            response = model.generate_content(history)
            # Gemini APIの回答本文を取得
            content = response.candidates[0].content.parts[0].text
            st.session_state.messages.append({"role": "assistant", "content": content})
        except Exception as e:
            st.session_state.messages.append({"role": "assistant", "content": f"エラー: {e}"})

    # 既存のチャットメッセージを表示
    for message in st.session_state.messages:
        if message["role"] == "system":
            continue
        with st.chat_message("user" if message["role"] == "user" else "assistant"):
            st.markdown(message["content"])

    # チャット入力欄（日本語表示）
    if prompt := st.chat_input("質問や回答を入力してください"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Gemini API 用に履歴を整形
        history = []
        for m in st.session_state.messages:
            if m["role"] == "user":
                history.append({"role": "user", "parts": [m["content"]]})
            elif m["role"] == "assistant":
                history.append({"role": "model", "parts": [m["content"]]})

        try:
            response_stream = model.generate_content(
                history,
                stream=True,
            )
            with st.chat_message("assistant"):
                full_response = ""
                for chunk in response_stream:
                    if chunk.candidates and chunk.candidates[0].content.parts:
                        part = chunk.candidates[0].content.parts[0].text
                        st.write(part, end="")
                        full_response += part
                st.session_state.messages.append({"role": "assistant", "content": full_response})
        except Exception as e:
            st.error(f"エラー: {e}")

with st.chat_message("assistant"):
    full_response = ""
    for chunk in response_stream:
        if chunk.candidates and chunk.candidates[0].content.parts:
            part = chunk.candidates[0].content.parts[0].text
            full_response += part
    st.markdown(full_response)
