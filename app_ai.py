import google.generativeai as genai
import streamlit as st

# --- 페이지 설정 ---
st.set_page_config(
    page_title="나만의 Gemini 챗봇",
    page_icon="✨"
)

# --- 사이드바 ---
with st.sidebar:
    st.title("✨ 나만의 Gemini 챗봇")
    st.header("설정")

    # 구글 API 키 설정
    try:
        # Streamlit Secrets에서 API 키 가져오기
        api_key = st.secrets["GOOGLE_API_KEY"]
        genai.configure(api_key=api_key)
    except (KeyError, Exception):
        # Secrets에 키가 없을 경우 사용자가 직접 입력
        api_key = st.text_input("Google AI Studio API 키를 입력하세요.", type="password")
        if api_key:
            genai.configure(api_key=api_key)
        else:
            st.info("사이드바에서 API 키를 입력해주세요.")
            st.stop()
    
    # 모델 선택 (Gemini 모델 목록)
    st.session_state["gemini_model"] = st.selectbox(
        "사용할 모델을 선택하세요.",
        ("gemini-1.5-pro-latest", "gemini-pro") # 필요에 따라 다른 모델 추가
    )

    # 대화 초기화 버튼
    if st.button("대화 기록 초기화"):
        # st.session_state의 모든 키를 삭제하여 초기화
        for key in st.session_state.keys():
            del st.session_state[key]
        st.rerun()

# --- 메인 화면 ---
st.title("Gemini-like Clone")
st.caption(f"현재 사용 중인 모델: {st.session_state['gemini_model']}")


# 세션 상태 초기화: 채팅 기록과 채팅 세션
if "messages" not in st.session_state:
    st.session_state.messages = []

# Gemini 모델 및 채팅 세션 로드
# 모델이 변경되면 채팅 세션을 다시 시작
if "chat" not in st.session_state or st.session_state.get("model_changed"):
    model = genai.GenerativeModel(st.session_state["gemini_model"])
    # 이전 대화 기록을 포함하여 채팅 세션 시작
    history = [
        {"role": msg["role"], "parts": [msg["content"]]}
        for msg in st.session_state.messages
    ]
    st.session_state.chat = model.start_chat(history=history)
    st.session_state.model_changed = False


# 이전 대화 내용 표시
for message in st.session_state.messages:
    # Gemini는 'assistant' 대신 'model' 역할을 사용
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
            # Gemini API로 메시지 전송 및 스트리밍 응답 받기
            response_stream = st.session_state.chat.send_message(prompt, stream=True)
            
            # st.write_stream을 사용하여 스트리밍 데이터를 편리하게 처리
            def stream_generator(stream):
                for chunk in stream:
                    # 일부 chunk에 text가 없는 경우가 있을 수 있으므로 예외 처리
                    try:
                        yield chunk.text
                    except Exception:
                        continue
            
            response = st.write_stream(stream_generator(response_stream))

            # 전체 응답을 세션 상태에 저장 (Gemini는 'model' 역할 사용)
            st.session_state.messages.append(
                {"role": "model", "content": response}
            )

        except Exception as e:
            st.error(f"❌ 오류가 발생했습니다: {e}")
