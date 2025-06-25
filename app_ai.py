import google.generativeai as genai
import streamlit as st

# --- 페이지 설정 ---
st.set_page_config(
    page_title="나만의 Gemini AI",
    page_icon="✨"
)

# --- 사이드바 ---
with st.sidebar:
    st.title("✨ 나만의 Gemini")
    st.header("설정")

    try:
        api_key = st.secrets["GOOGLE_API_KEY"]
        genai.configure(api_key=api_key)
    except (KeyError, Exception):
        api_key = st.text_input("Google AI Studio API 키를 입력하세요.", type="password")
        if api_key:
            genai.configure(api_key=api_key)
        else:
            st.info("사이드바에서 API 키를 입력해주세요.")
            st.stop()
    
    model_options = ("gemini-pro", "gemini-1.5-pro-latest")
    selected_model = st.selectbox(
        "사용할 모델을 선택하세요.",
        model_options,
        index=0
    )

    if st.button("대화 기록 초기화"):
        st.session_state.messages = []
        if "chat" in st.session_state:
            del st.session_state["chat"]
        st.rerun()

# --- 메인 화면 ---
st.title("Gemini-like Clone")
st.caption(f"현재 사용 중인 모델: {selected_model}")

# 세션 상태 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- ✨ 핵심 수정 로직 (가장 안정적인 최종 버전) ✨ ---
# 다음 세 가지 경우 중 하나라도 해당되면 새로운 채팅 세션을 생성합니다.
# 1. 'chat' 세션이 아예 없는 경우 (앱 최초 실행)
# 2. 'chat' 세션이 있지만 그 값이 None인 경우 (초기화 등으로 인해)
# 3. 'chat' 세션이 있지만, 현재 선택된 모델과 다른 모델로 만들어진 경우
if "chat" not in st.session_state or st.session_state.get("chat") is None or not st.session_state.chat.model_name.endswith(selected_model):
    # 새로운 모델로 채팅 객체를 생성
    model = genai.GenerativeModel(model_name=selected_model)
    st.session_state.chat = model.start_chat(history=[])
    # 모델이 변경되었을 때만 메시지 기록을 초기화 (최초 실행 시에는 불필요)
    # 이미 'chat'이 있었다는 것은 모델이 '변경'되었다는 의미
    if "chat" in st.session_state and st.session_state.get("chat") is not None:
         st.session_state.messages = []
         st.info(f"✨ 모델이 {selected_model}(으)로 변경되었습니다. 새로운 대화를 시작합니다.")

# 이전 대화 내용 표시
for message in st.session_state.messages:
    role = "assistant" if message["role"] == "model" else message["role"]
    with st.chat_message(role):
        st.markdown(message["content"])

# 사용자 입력 처리
if prompt := st.chat_input("무엇이든 물어보세요!"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            response_stream = st.session_state.chat.send_message(prompt, stream=True)
            
            def stream_generator(stream):
                for chunk in stream:
                    try:
                        yield chunk.text
                    except Exception:
                        continue
            
            response = st.write_stream(stream_generator(response_stream))
            st.session_state.messages.append({"role": "model", "content": response})

        except Exception as e:
            st.error(f"❌ 오류가 발생했습니다:\n {e}")
