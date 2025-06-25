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

    # 구글 API 키 설정
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
    
    # 모델 선택
    model_options = ("gemini-pro", "gemini-1.5-pro-latest")
    selected_model = st.selectbox(
        "사용할 모델을 선택하세요.",
        model_options,
        index=0
    )

    # 대화 초기화 버튼
    if st.button("대화 기록 초기화"):
        st.session_state.messages = []
        st.session_state.chat = None # 채팅 세션도 초기화
        st.rerun()

# --- 메인 화면 ---
st.title("Gemini-like Clone")
st.caption(f"현재 사용 중인 모델: {selected_model}")

# 세션 상태 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- ✨ 핵심 수정 로직 ✨ ---
# 모델이 변경되었거나 채팅 세션이 아직 없으면 새로 생성
# st.session_state.chat.model_name으로 현재 채팅의 모델 이름을 확인
current_chat_model = getattr(getattr(st.session_state, 'chat', None), 'model_name', None)

if "chat" not in st.session_state or st.session_state.chat is None or not current_chat_model.endswith(selected_model):
    model = genai.GenerativeModel(selected_model)
    st.session_state.chat = model.start_chat(history=[]) # 모델이 바뀌면 대화기록은 새로 시작
    st.session_state.messages = [] # UI 메시지 기록도 초기화
    st.info(f"✨ 모델이 {selected_model}(으)로 변경되었습니다. 새로운 대화를 시작합니다.")

# 이전 대화 내용 표시
for message in st.session_state.messages:
    role = "assistant" if message["role"] == "model" else message["role"]
    with st.chat_message(role):
        st.markdown(message["content"])

# 사용자 입력 처리
if prompt := st.chat_input("무엇이든 물어보세요!"):
    # 사용자 메시지 저장 및 표시
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 어시스턴트 응답 처리
    with st.chat_message("assistant"):
        try:
            # 대화 기록을 API에 전달
            st.session_state.chat.history = [
                {"role": msg["role"], "parts": [msg["content"]]}
                for msg in st.session_state.messages[:-1] # 마지막 AI 응답은 제외
            ]
            
            response_stream = st.session_state.chat.send_message(prompt, stream=True)
            
            def stream_generator(stream):
                for chunk in stream:
                    try:
                        yield chunk.text
                    except Exception:
                        continue
            
            response = st.write_stream(stream_generator(response_stream))

            # 전체 응답을 세션 상태에 저장
            st.session_state.messages.append({"role": "model", "content": response})

        except Exception as e:
            st.error(f"❌ 오류가 발생했습니다:\n {e}")
