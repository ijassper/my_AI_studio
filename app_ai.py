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
        # 필요한 세션만 명시적으로 초기화
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

# --- ✨ 핵심 수정 로직 (최종 방어 버전) ✨ ---
# 채팅 세션을 새로 만들어야 하는지 결정하는 로직
create_new_chat = False
# 1. 'chat' 세션이 아예 존재하지 않는 경우
if "chat" not in st.session_state:
    create_new_chat = True
# 2. 'chat' 세션이 존재는 하지만, 그 값이 None인 경우
elif st.session_state.chat is None:
    create_new_chat = True
# 3. 'chat' 세션이 존재하고 None도 아니지만, 모델이 다른 경우
else:
    # 이 블록은 st.session_state.chat이 유효한 객체일 때만 실행되므로 안전함
    if not st.session_state.chat.model_name.endswith(selected_model):
        create_new_chat = True
        # 모델 변경 시, 대화 기록을 초기화하고 사용자에게 알림
        st.session_state.messages = []
        st.info(f"✨ 모델이 {selected_model}(으)로 변경되었습니다. 새로운 대화를 시작합니다.")

# 위 조건에 따라 새로운 채팅 세션을 생성
if create_new_chat:
    model = genai.GenerativeModel(model_name=selected_model)
    st.session_state.chat = model.start_chat(history=[])
    # 새로운 채팅이 생성되었으므로, 화면을 한번 새로고침하여 적용
    # 이 rerun은 무한루프를 일으키지 않고 UI를 깨끗하게 만들어 줌
    if "messages" not in st.session_state or len(st.session_state.messages) == 0:
        st.rerun()

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
