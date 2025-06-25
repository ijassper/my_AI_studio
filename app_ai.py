import google.generativeai as genai
import streamlit as st

# --- 페이지 설정 및 제목 ---
st.set_page_config(page_title="나만의 Gemini AI", page_icon="✨")
st.title("Gemini-like Clone")

# --- 사이드바 설정 ---
with st.sidebar:
    st.title("✨ 나만의 Gemini")
    st.header("설정")

    try:
        api_key = st.secrets["GOOGLE_API_KEY"]
        genai.configure(api_key=api_key)
    except Exception as e:
        st.error(f"API 키 설정 중 오류: {e}")
        st.stop()

    model_choice = st.selectbox(
        "사용할 모델을 선택하세요.",
        ("gemini-pro", "gemini-1.5-pro-latest"),
        key="model_choice"
    )

    if st.button("대화 기록 초기화"):
        st.session_state.messages = []
        st.rerun()

# --- 세션 상태 초기화 ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 채팅 객체 생성 ---
try:
    model = genai.GenerativeModel(model_name=model_choice)
    chat = model.start_chat(
        history=[
            {"role": m["role"], "parts": [m["content"]]}
            for m in st.session_state.messages
        ]
    )
except Exception as e:
    st.error(f"모델을 로드하는 중 오류가 발생했습니다: {e}")
    st.stop()

# --- 대화 내용 표시 ---
for message in st.session_state.messages:
    role = "assistant" if message["role"] == "model" else message["role"]
    with st.chat_message(role):
        st.markdown(message["content"])

# --- 사용자 입력 처리 ---
if prompt := st.chat_input("무엇이든 물어보세요!"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            response_stream = chat.send_message(prompt, stream=True)
            
            # 더 안전한 스트림 제너레이터 함수
            def stream_handler(stream):
                for chunk in stream:
                    # 안전하게 텍스트 추출 시도
                    try:
                        yield chunk.text
                    except Exception:
                        continue # 텍스트가 없는 청크는 건너뜀
            
            response_text = st.write_stream(stream_handler(response_stream))

            st.session_state.messages.append(
                {"role": "model", "content": response_text}
            )
        except Exception as e:
            st.error(f"❌ 메시지 전송 중 오류 발생:\n {e}")
