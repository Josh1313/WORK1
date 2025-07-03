import streamlit as st
from api_client import api_client

def app():
    st.title("🏠 Welcome to ITSM Reporting & Analytics ")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info("### 📁 Files\nUpload and manage your datasets")
        
    with col2:
        st.success("### 💬 Chat\nAnalyze data with AI assistance")
        
    with col3:
        st.warning("### 🚀 Cag \nAI Based Text Categorization")
    
    st.markdown("---")
    
    # Show recent activity if backend is connected
    if st.session_state.get('backend_status') == 'healthy':
        st.subheader("📊 Recent Datasets")
        
        try:
            files = api_client.list_files()
            if files:
                for file in files[:3]:  # Show last 3
                    with st.container():
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            st.write(f"**{file['filename']}**")
                            st.caption(f"Uploaded: {file['upload_date']} | {file['rows']:,} rows × {file['columns']} columns")
                        with col2:
                            # Check if this dataset is already selected
                            is_selected = st.session_state.get('active_dataset_id') == file['dataset_id']
                            
                            if is_selected:
                                st.success("✅ Selected")
                            else:
                                if st.button("Select", key=f"select_{file['dataset_id']}"):
                                    st.session_state.active_dataset_id = file['dataset_id']
                                    st.session_state.active_dataset_name = file['filename']
                                    st.rerun()  # Refresh to show selected state
                
                # Show navigation hint only if a dataset was just selected
                if 'active_dataset_id' in st.session_state and 'active_dataset_name' in st.session_state:
                    st.info("💬 Ready to chat! Use the sidebar to navigate to Chat.")
            else:
                st.info("No datasets uploaded yet. Go to Files to upload your first dataset!")
        except Exception as e:
            st.error(f"Error loading recent files: {str(e)}")
    else:
        st.warning("⚠️ Backend is not connected. Please ensure the backend server is running.")