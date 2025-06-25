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
        key="model_choice" # selectbox 상태를 session_state에 저장
    )

    if st.button("대화 기록 초기화"):
        st.session_state.messages = [] # 메시지만 초기화
        st.rerun()

# --- 세션 상태 초기화 ---
# 앱이 처음 시작될 때 'messages' 리스트를 생성
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- ✨ 핵심 해결 로직: 매번 채팅 객체 새로 생성 ✨ ---
# 저장된 대화 기록(messages)을 바탕으로 Gemini 모델과 채팅 세션을 시작
# 이 코드는 스크립트가 실행될 때마다 호출되므로 항상 최신 상태를 반영
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
# st.session_state.messages에 저장된 모든 메시지를 순회하며 화면에 출력
for message in st.session_state.messages:
    role = "assistant" if message["role"] == "model" else message["role"]
    with st.chat_message(role):
        st.markdown(message["content"])

# --- 사용자 입력 처리 ---
if prompt := st.chat_input("무엇이든 물어보세요!"):
    # 1. 사용자 메시지를 session_state와 화면에 추가
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. 어시스턴트 응답 처리
    with st.chat_message("assistant"):
        try:
            # 새로 생성된 chat 객체를 사용해 API에 메시지 전송
            response_stream = chat.send_message(prompt, stream=True)
            
            # 스트리밍 응답을 화면에 실시간으로 표시
            response_text = st.write_stream(
                (chunk.text for chunk in response_stream)
            )

            # 3. 전체 응답을 session_state에 저장
            st.session_state.messages.append(
                {"role": "model", "content": response_text}
            )
        except Exception as e:
            st.error(f"❌ 메시지 전송 중 오류 발생: {e}")
