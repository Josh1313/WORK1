import streamlit as st
from datetime import datetime
from api_client import api_client

def app():
    st.title("Chat")
    st.title("💬 Data Analysis Chat")
    
    if st.session_state.get('backend_status') != 'healthy':
        st.error("❌ Backend is not connected. Chat is unavailable.")
        return
    
    # Check if dataset is selected
    if 'active_dataset_id' not in st.session_state:
        st.warning("⚠️ No dataset selected. Please select a dataset from the Files page.")
        st.info("👈 Use the sidebar to navigate to Files")
        return
    
    # Show active dataset
    st.success(f"📊 Analyzing: {st.session_state.get('active_dataset_name', 'Unknown Dataset')}")
    
    # Initialize chat history ONLY if not exists or dataset changed
    if 'messages' not in st.session_state or st.session_state.get('last_dataset_id') != st.session_state.active_dataset_id:
        st.session_state.messages = []
        st.session_state.last_dataset_id = st.session_state.active_dataset_id
        try:
            history = api_client.get_chat_history(st.session_state.active_dataset_id)
            st.session_state.messages = [
                {"role": msg['role'], "content": msg['content']}
                for msg in history.get('messages', [])
            ]
        except:
            pass
    
    # Clear chat button at the top
    col1, col2, col3 = st.columns([1, 1, 3])
    with col1:
        if st.button("🗑️ Clear Chat", key="clear_chat_btn"):
            st.session_state.messages = []
            try:
                api_client.clear_chat_history(st.session_state.active_dataset_id)
            except:
                pass
            st.rerun()
    
    # Display chat messages
    for idx, message in enumerate(st.session_state.messages):
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input - Handle submission properly
    if prompt := st.chat_input("Ask me anything about your data...", key="chat_input"):
        # Add user message immediately
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Display assistant response with spinner
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            
            with st.spinner("Analyzing..."):
                try:
                    response = api_client.chat_query(
                        dataset_id=st.session_state.active_dataset_id,
                        query=prompt
                    )
                    ai_response = response['response']
                    
                    # Add to session state first
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": ai_response
                    })
                    
                    # Then display
                    message_placeholder.markdown(ai_response)
                    
                except Exception as e:
                    error_msg = f"❌ Error: {str(e)}"
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": error_msg
                    })
                    message_placeholder.error(error_msg)
        
        # Force a clean rerun to update the chat display
        st.rerun()
   