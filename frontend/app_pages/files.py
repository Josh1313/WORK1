# import streamlit as st
# import pandas as pd
# from datetime import datetime
# import asyncio
# import time
# from api_client import api_client



# def app():
#     st.title("📁 File Management")
    
#     if st.session_state.get('backend_status') != 'healthy':
#         st.error("❌ Backend is not connected. File operations are unavailable.")
#         return
    
#     # Tabs for upload, manage, and clustering
#     tab1, tab2, tab3 = st.tabs(["📤 Upload", "📋 Manage", "🔬 Clustering"])
    
#     with tab1:
#         show_upload_section()
    
#     with tab2:
#         show_manage_section()
    
#     with tab3:
#         show_clustering_section()

# def show_upload_section():
#     st.subheader("Upload New Dataset")
    
#     uploaded_file = st.file_uploader(
#         "Choose a CSV or Excel file",
#         type=['csv', 'xlsx'],
#         help="Maximum file size: 100MB"
#     )
    
#     if uploaded_file is not None:
#         # File details
#         col1, col2, col3 = st.columns(3)
#         with col1:
#             st.metric("File Name", uploaded_file.name)
#         with col2:
#             st.metric("Size", f"{uploaded_file.size / 1024 / 1024:.2f} MB")
#         with col3:
#             st.metric("Type", uploaded_file.type)
        
#         # Description field
#         description = st.text_area("Description (optional)", placeholder="Describe this dataset...")
        
#         # Upload button
#         if st.button("📤 Upload", type="primary"):
#             with st.spinner("Uploading..."):
#                 try:
#                     # Read file content once
#                     file_content = uploaded_file.read()
                    
#                     # Upload to backend
#                     response = api_client.upload_file(
#                         file=file_content,
#                         filename=uploaded_file.name,
#                         description=description
#                     )
                    
#                     st.success(f"✅ File uploaded successfully! Dataset ID: {response['dataset_id']}")
#                     st.balloons()
                    
#                     # Option to use immediately
#                     col1, col2 = st.columns(2)
#                     with col1:
#                         if st.button("🚀 Use in Chat"):
#                             st.session_state.active_dataset_id = response['dataset_id']
#                             st.session_state.active_dataset_name = uploaded_file.name
#                             st.switch_page("pages/chat.py")
#                     with col2:
#                         if st.button("📤 Upload Another"):
#                             st.rerun()
                            
#                 except Exception as e:
#                     st.error(f"❌ Upload failed: {str(e)}")

# def show_manage_section():
#     st.subheader("Your Datasets")
    
#     try:
#         files = api_client.list_files()
        
#         if not files:
#             st.info("No datasets uploaded yet.")
#             return
        
#         # Active dataset indicator
#         if 'active_dataset_id' in st.session_state:
#             st.info(f"🎯 Active dataset: {st.session_state.get('active_dataset_name', 'Unknown')}")
        
#         # List datasets
#         for idx, file in enumerate(files):
#             with st.container():
#                 col1, col2, col3, col4, col5, col6 = st.columns([3, 1, 1, 1, 1, 1])
                
#                 with col1:
#                     st.write(f"**{file['filename']}**")
#                     upload_date = datetime.fromisoformat(file['upload_date'])
#                     st.caption(
#                         f"📅 {upload_date.strftime('%Y-%m-%d %H:%M')} | "
#                         f"📊 {file['rows']:,} rows × {file['columns']} cols | "
#                         f"💾 {file['size_mb']} MB"
#                     )
#                     if file.get('description'):
#                         st.caption(f"📝 {file['description']}")
                
#                 with col2:
#                     if st.button("👁️", key=f"view_{idx}", help="Preview"):
#                         with st.spinner("Loading preview..."):
#                             preview = api_client.preview_file(file['dataset_id'])
#                             df_preview = pd.DataFrame(preview['data'])
#                             st.dataframe(df_preview)
                
#                 with col3:
#                     is_active = st.session_state.get('active_dataset_id') == file['dataset_id']
#                     btn_label = "✅" if is_active else "📊"
#                     if st.button(btn_label, key=f"use_{idx}", help="Use in Chat", disabled=is_active):
#                         st.session_state.active_dataset_id = file['dataset_id']
#                         st.session_state.active_dataset_name = file['filename']
#                         st.success(f"✅ Now using: {file['filename']}")
                
#                 with col4:
#                     if st.button("🔬", key=f"cluster_{idx}", help="Analyze with Clustering"):
#                         st.session_state.clustering_dataset_id = file['dataset_id']
#                         st.session_state.clustering_dataset_name = file['filename']
#                         st.info("Go to Clustering tab to start analysis")
                
#                 with col5:
#                     if st.button("📥", key=f"download_{idx}", help="Download"):
#                         data = api_client.download_file(file['dataset_id'])
#                         st.download_button(
#                             label="💾",
#                             data=data['content'],
#                             file_name=data['filename'],
#                             mime="text/csv",
#                             key=f"dl_btn_{idx}"
#                         )
                
              
#                 with col6:
#                     # Allow deletion of any dataset, including active ones
#                     if st.button("🗑️", key=f"delete_{idx}", help="Delete"):
#                         try:
#                             # Show warning if deleting active dataset
#                             is_active_deletion = st.session_state.get('active_dataset_id') == file['dataset_id']
                            
#                             api_client.delete_file(file['dataset_id'])
                            
#                             # Clear active dataset if it was deleted
#                             if is_active_deletion:
#                                 if 'active_dataset_id' in st.session_state:
#                                     del st.session_state.active_dataset_id
#                                 if 'active_dataset_name' in st.session_state:
#                                     del st.session_state.active_dataset_name
#                                 st.warning("⚠️ Active dataset deleted. Please select a new one for chat.")
                            
#                             st.success("✅ Dataset deleted successfully! Refresh page to update list.")
#                             # Mark for refresh instead of rerun
#                             st.session_state.refresh_files = True
#                             st.rerun()
#                         except Exception as e:
#                             st.error(f"❌ Delete failed: {str(e)}") 
                
#                 st.divider()
                
#     except Exception as e:
#         st.error(f"Error loading files: {str(e)}")

# def show_clustering_section():
#     st.subheader("🔬 Intelligent Clustering Analysis")
    
#     st.info("""
#     This feature will:
#     1. Clean your data descriptions
#     2. Generate AI embeddings
#     3. Perform intelligent clustering
#     4. Provide insights for each cluster
#     """)
    
#     # Check if dataset is selected for clustering
#     if 'clustering_dataset_id' not in st.session_state:
#         st.warning("⚠️ Please select a dataset from the Manage tab first")
#         return
    
#     st.success(f"📊 Selected dataset: {st.session_state.clustering_dataset_name}")
    
#     # Preview dataset to select columns
#     with st.expander("Dataset Preview"):
#         preview = api_client.preview_file(st.session_state.clustering_dataset_id)
#         df_preview = pd.DataFrame(preview['data'])
#         st.dataframe(df_preview)
#         columns = preview['columns']
    
#     # Configuration form
#     with st.form("clustering_config"):
#         st.write("### Configuration")
        
#         description_column = st.selectbox(
#             "Select description column",
#             columns,
#             help="Column containing text descriptions to analyze"
#         )
        
#         number_column = st.selectbox(
#             "Select ID/Number column (optional)",
#             ["None"] + columns,
#             help="Column containing unique identifiers"
#         )
        
#         n_clusters = st.slider(
#             "Number of clusters",
#             min_value=0,
#             max_value=10,
#             value=0,
#             help="Set to 0 for automatic detection"
#         )
        
#         submitted = st.form_submit_button("🚀 Start Clustering Analysis")
    
#     if submitted:
#         # Start clustering process
#         with st.spinner("Starting clustering process..."):
#             try:
#                 response = api_client.start_clustering(
#                     dataset_id=st.session_state.clustering_dataset_id,
#                     description_column=description_column,
#                     number_column=None if number_column == "None" else number_column,
#                     n_clusters=n_clusters
#                 )
                
#                 task_id = response['task_id']
#                 st.session_state.clustering_task_id = task_id
                
#                 # Show progress
#                 progress_bar = st.progress(0)
#                 status_text = st.empty()
                
#                 # --- START OF REVISED POLLING LOGIC ---
#                 max_retries = 20  # 20 retries * 2s sleep = 40s timeout for task registration
#                 retries = 0
                
#                 # Poll for status, handling initial 404 until task is registered
#                 while True:
#                     status = None
#                     try:
#                         status = api_client.get_clustering_status(task_id)
#                     except Exception as e:
#                         # This block now correctly handles the 404 exception
#                         if "404" in str(e):
#                             retries += 1
#                             if retries > max_retries:
#                                 st.error("❌ Task not found after multiple attempts. The backend might be overloaded. Please try again later.")
#                                 break # Exit the loop
                            
#                             status_text.text(f"⏳ Waiting for task to register... (Attempt {retries}/{max_retries})")
#                             time.sleep(2)  # Wait before retrying
#                             continue # Skip the rest of the loop and retry
#                         else:
#                             # Handle other, unexpected API errors
#                             st.error(f"❌ An unexpected API error occurred: {e}")
#                             break    
                    
#                     progress_bar.progress(status['progress'] / 100)
#                     status_text.text(f"Status: {status['message']}")
                    
#                     if status['status'] == 'completed':
#                         st.success(f"✅ {status['message']}")
                        
#                         # Show result options
#                         result_id = status['result']
#                         col1, col2 = st.columns(2)
                        
#                         with col1:
#                             if st.button("📊 Use Result in Chat"):
#                                 st.session_state.active_dataset_id = result_id
#                                 st.session_state.active_dataset_name = f"clustered_{st.session_state.clustering_dataset_name}"
#                                 st.switch_page("pages/chat.py")
                        
#                         with col2:
#                             if st.button("📋 View in Manage Tab"):
#                                 st.rerun()
                        
#                         break
                    
#                     elif status['status'] == 'failed':
#                         st.error(f"❌ {status['message']}")
#                         break
                    
#                     time.sleep(2)  # Poll every 2 seconds
                    
#             except Exception as e:
#                 st.error(f"❌ Error: {str(e)}")
import streamlit as st
import pandas as pd
from datetime import datetime
import asyncio
import time
from api_client import api_client

def app():
    st.title("📁 File Management")
    
    if st.session_state.get('backend_status') != 'healthy':
        st.error("❌ Backend is not connected. File operations are unavailable.")
        return
    
    # Tabs for upload, manage, and clustering
    tab1, tab2, tab3 = st.tabs(["📤 Upload", "📋 Manage", "🔬 Clustering"])
    
    with tab1:
        show_upload_section()
    
    with tab2:
        show_manage_section()
    
    with tab3:
        show_clustering_section()

def show_upload_section():
    st.subheader("Upload New Dataset")
    
    uploaded_file = st.file_uploader(
        "Choose a CSV or Excel file",
        type=['csv', 'xlsx'],
        help="Maximum file size: 100MB"
    )
    
    if uploaded_file is not None:
        # File details
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("File Name", uploaded_file.name)
        with col2:
            st.metric("Size", f"{uploaded_file.size / 1024 / 1024:.2f} MB")
        with col3:
            st.metric("Type", uploaded_file.type)
        
        # Description field
        description = st.text_area("Description (optional)", placeholder="Describe this dataset...")
        
        # Upload button
        if st.button("📤 Upload", type="primary"):
            with st.spinner("Uploading..."):
                try:
                    # Read file content once
                    file_content = uploaded_file.read()
                    
                    # Upload to backend
                    response = api_client.upload_file(
                        file=file_content,
                        filename=uploaded_file.name,
                        description=description
                    )
                    
                    st.success(f"✅ File uploaded successfully! Dataset ID: {response['dataset_id']}")
                    st.balloons()
                    
                    # Option to use immediately
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("🚀 Use in Chat"):
                            st.session_state.active_dataset_id = response['dataset_id']
                            st.session_state.active_dataset_name = uploaded_file.name
                            st.switch_page("pages/chat.py")
                    
                    with col2:
                        if st.button("📤 Upload Another"):
                            st.rerun()
                            
                except Exception as e:
                    st.error(f"❌ Upload failed: {str(e)}")

def show_manage_section():
    st.subheader("Your Datasets")
    
    try:
        files = api_client.list_files()
        
        if not files:
            st.info("No datasets uploaded yet.")
            return
        
        # Active dataset indicator
        if 'active_dataset_id' in st.session_state:
            st.info(f"🎯 Active dataset: {st.session_state.get('active_dataset_name', 'Unknown')}")
        
        # List datasets
        for idx, file in enumerate(files):
            with st.container():
                col1, col2, col3, col4, col5, col6 = st.columns([3, 1, 1, 1, 1, 1])
                
                with col1:
                    st.write(f"**{file['filename']}**")
                    upload_date = datetime.fromisoformat(file['upload_date'])
                    st.caption(
                        f"📅 {upload_date.strftime('%Y-%m-%d %H:%M')} | "
                        f"📊 {file['rows']:,} rows × {file['columns']} cols | "
                        f"💾 {file['size_mb']} MB"
                    )
                    if file.get('description'):
                        st.caption(f"📝 {file['description']}")
                
                with col2:
                    if st.button("👁️", key=f"view_{idx}", help="Preview"):
                        with st.spinner("Loading preview..."):
                            preview = api_client.preview_file(file['dataset_id'])
                            df_preview = pd.DataFrame(preview['data'])
                            st.dataframe(df_preview)
                
                with col3:
                    is_active = st.session_state.get('active_dataset_id') == file['dataset_id']
                    btn_label = "✅" if is_active else "📊"
                    if st.button(btn_label, key=f"use_{idx}", help="Use in Chat", disabled=is_active):
                        st.session_state.active_dataset_id = file['dataset_id']
                        st.session_state.active_dataset_name = file['filename']
                        st.success(f"✅ Now using: {file['filename']}")
                
                with col4:
                    if st.button("🔬", key=f"cluster_{idx}", help="Analyze with Clustering"):
                        st.session_state.clustering_dataset_id = file['dataset_id']
                        st.session_state.clustering_dataset_name = file['filename']
                        st.info("Go to Clustering tab to start analysis")
                
                with col5:
                    if st.button("📥", key=f"download_{idx}", help="Download"):
                        data = api_client.download_file(file['dataset_id'])
                        st.download_button(
                            label="💾",
                            data=data['content'],
                            file_name=data['filename'],
                            mime="text/csv",
                            key=f"dl_btn_{idx}"
                        )
                
                with col6:
                    # Allow deletion of any dataset, including active ones
                    if st.button("🗑️", key=f"delete_{idx}", help="Delete"):
                        try:
                            # Show warning if deleting active dataset
                            is_active_deletion = st.session_state.get('active_dataset_id') == file['dataset_id']
                            
                            # Clear clustering dataset if it's being deleted
                            if st.session_state.get('clustering_dataset_id') == file['dataset_id']:
                                if 'clustering_dataset_id' in st.session_state:
                                    del st.session_state.clustering_dataset_id
                                if 'clustering_dataset_name' in st.session_state:
                                    del st.session_state.clustering_dataset_name
                            
                            api_client.delete_file(file['dataset_id'])
                            
                            # Clear active dataset if it was deleted
                            if is_active_deletion:
                                if 'active_dataset_id' in st.session_state:
                                    del st.session_state.active_dataset_id
                                if 'active_dataset_name' in st.session_state:
                                    del st.session_state.active_dataset_name
                                st.warning("⚠️ Active dataset deleted. Please select a new one for chat.")
                            
                            st.success("✅ Dataset deleted successfully! Refresh page to update list.")
                            # Mark for refresh instead of rerun
                            st.session_state.refresh_files = True
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Delete failed: {str(e)}")
                
                st.divider()
    
    except Exception as e:
        st.error(f"Error loading files: {str(e)}")

def show_clustering_section():
    st.subheader("🔬 Intelligent Clustering Analysis")
    
    st.info("""
    This feature will:
    1. Clean your data descriptions
    2. Generate AI embeddings
    3. Perform intelligent clustering
    4. Provide insights for each cluster
    """)
    
    # Check if dataset is selected for clustering
    if 'clustering_dataset_id' not in st.session_state:
        st.warning("⚠️ Please select a dataset from the Manage tab first")
        return
    
    st.success(f"📊 Selected dataset: {st.session_state.clustering_dataset_name}")
    
    # Preview dataset to select columns - with error handling
    try:
        with st.expander("Dataset Preview"):
            preview = api_client.preview_file(st.session_state.clustering_dataset_id)
            df_preview = pd.DataFrame(preview['data'])
            st.dataframe(df_preview)
            columns = preview['columns']
    except Exception as e:
        # Handle case where dataset was deleted
        if "404" in str(e):
            st.error("❌ Selected dataset no longer exists. Please select another dataset from the Manage tab.")
            # Clear invalid session state
            if 'clustering_dataset_id' in st.session_state:
                del st.session_state.clustering_dataset_id
            if 'clustering_dataset_name' in st.session_state:
                del st.session_state.clustering_dataset_name
            return
        else:
            st.error(f"❌ Error loading dataset: {str(e)}")
            return
    
    # Configuration form
    with st.form("clustering_config"):
        st.write("### Configuration")
        
        description_column = st.selectbox(
            "Select description column",
            columns,
            help="Column containing text descriptions to analyze"
        )
        
        number_column = st.selectbox(
            "Select ID/Number column (optional)",
            ["None"] + columns,
            help="Column containing unique identifiers"
        )
        
        n_clusters = st.slider(
            "Number of clusters",
            min_value=0,
            max_value=10,
            value=0,
            help="Set to 0 for automatic detection"
        )
        
        submitted = st.form_submit_button("🚀 Start Clustering Analysis")
    
    if submitted:
        # Start clustering process
        with st.spinner("Starting clustering process..."):
            try:
                response = api_client.start_clustering(
                    dataset_id=st.session_state.clustering_dataset_id,
                    description_column=description_column,
                    number_column=None if number_column == "None" else number_column,
                    n_clusters=n_clusters
                )
                
                task_id = response['task_id']
                st.session_state.clustering_task_id = task_id
                
                # Show progress
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                # --- START OF REVISED POLLING LOGIC ---
                max_retries = 20  # 20 retries * 2s sleep = 40s timeout for task registration
                retries = 0
                
                # Poll for status, handling initial 404 until task is registered
                while True:
                    status = None
                    try:
                        status = api_client.get_clustering_status(task_id)
                    except Exception as e:
                        # This block now correctly handles the 404 exception
                        if "404" in str(e):
                            retries += 1
                            if retries > max_retries:
                                st.error("❌ Task not found after multiple attempts. The backend might be overloaded. Please try again later.")
                                break  # Exit the loop
                            status_text.text(f"⏳ Waiting for task to register... (Attempt {retries}/{max_retries})")
                            time.sleep(2)  # Wait before retrying
                            continue  # Skip the rest of the loop and retry
                        else:
                            # Handle other, unexpected API errors
                            st.error(f"❌ An unexpected API error occurred: {e}")
                            break    
                    
                    progress_bar.progress(status['progress'] / 100)
                    status_text.text(f"Status: {status['message']}")
                    
                    if status['status'] == 'completed':
                        st.success(f"✅ {status['message']}")
                        
                        # Show result options
                        result_id = status['result']
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            if st.button("📊 Use Result in Chat"):
                                st.session_state.active_dataset_id = result_id
                                st.session_state.active_dataset_name = f"clustered_{st.session_state.clustering_dataset_name}"
                                st.switch_page("pages/chat.py")
                        
                        with col2:
                            if st.button("📋 View in Manage Tab"):
                                st.rerun()
                        
                        break
                    elif status['status'] == 'failed':
                        st.error(f"❌ {status['message']}")
                        break
                    
                    time.sleep(2)  # Poll every 2 seconds
                    
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")