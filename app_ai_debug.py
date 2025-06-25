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
    except (KeyError, Exception) as e:
        st.error(f"API 키 설정 중 오류 발생: {e}")
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
        st.session_state.clear() # 모든 세션 상태를 확실하게 초기화
        st.rerun()

# --- 메인 화면 ---
st.title("Gemini-like Clone")
st.caption(f"현재 사용 중인 모델: {selected_model}")

# --- 🐞 디버깅 정보 출력 섹션 🐞 ---
# 이 정보가 문제 해결의 핵심입니다.
with st.expander("🐞 디버깅 정보 보기"):
    st.json(st.session_state.to_dict())


# --- ✨ 궁극의 방어 로직 ✨ ---
# 현재 채팅 세션이 유효한지 확인하는 변수
chat_is_valid = False

# st.session_state.chat이 존재하고, None이 아니며, model_name 속성을 가지고 있는지 먼저 확인
if "chat" in st.session_state and st.session_state.chat is not None and hasattr(st.session_state.chat, 'model_name'):
    # 모든 조건을 통과했으면, 모델 이름이 일치하는지 마지막으로 확인
    if st.session_state.chat.model_name.endswith(selected_model):
        chat_is_valid = True

# 채팅 세션이 유효하지 않으면, 무조건 새로 만듭니다.
if not chat_is_valid:
    # 이전에 채팅 세션이 존재했다면 '모델 변경'으로 간주
    if "chat" in st.session_state:
        st.info(f"✨ 모델을 {selected_model}(으)로 변경합니다. 새로운 대화를 시작합니다.")
        st.session_state.messages = [] # 대화 기록만 초기화

    try:
        model = genai.GenerativeModel(model_name=selected_model)
        st.session_state.chat = model.start_chat(history=[])
        # 채팅 세션을 성공적으로 생성한 후, UI를 정리하기 위해 새로고침
        st.rerun()
    except Exception as e:
        st.error(f"채팅 세션 생성 중 심각한 오류 발생: {e}")
        st.stop()


# 세션 상태에 메시지가 없으면 초기화 (모델 변경 시 위에서 초기화될 수 있음)
if "messages" not in st.session_state:
    st.session_state.messages = []

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
            response = st.write_stream(response_stream)
            st.session_state.messages.append({"role": "model", "content": response})
        except Exception as e:
            st.error(f"❌ 메시지 전송 중 오류 발생:\n {e}")
