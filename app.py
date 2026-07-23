import streamlit as st

from agent.react_agent import ReactAgent


st.set_page_config(page_title="智能客服", page_icon="💬")

st.title("智能客服")
st.divider()

if "agent" not in st.session_state:
    st.session_state.agent = ReactAgent()

query = st.chat_input("请输入你的问题")

if query:
    with st.chat_message("user"):
        st.write(query)

    with st.chat_message("assistant"):
        response_box = st.empty()
        response = ""
        try:
            for chunk in st.session_state.agent.execute_stream(query):
                response += chunk
                response_box.markdown(response)
        except Exception as exc:
            st.error(f"处理请求失败：{exc}")
