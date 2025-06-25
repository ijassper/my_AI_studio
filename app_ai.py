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
        # 필요한 세션 상태만 초기화
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

# --- ✨ 핵심 수정 로직 (더 안전하게 변경) ✨ ---
# 현재 세션의 모델 이름과 선택된 모델이 다른지 확인하는 변수
model_changed = False
if "chat" in st.session_state:
    # 'gemini-pro'는 'models/gemini-pro'와 같이 저장되므로 endswith 사용
    if not st.session_state.chat.model_name.endswith(selected_model):
        model_changed = True

# 채팅 세션이 없거나 모델이 변경되었으면 새로 생성
if "chat" not in st.session_state or model_changed:
    model = genai.GenerativeModel(model_name=selected_model)
    st.session_state.chat = model.start_chat(history=[])
    # 모델이 바뀌면 이전 대화는 의미가 없으므로 메시지 기록 초기화
    if model_changed:
        st.session_state.messages = []
        st.info(f"✨ 모델이 {selected_model}(으)로 변경되었습니다. 새로운 대화를 시작합니다.")
        st.rerun() # UI를 즉시 새로고침하여 메시지 목록을 비움

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
