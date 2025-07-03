import streamlit as st
from streamlit_option_menu import option_menu
from config import config
from api_client import api_client
from utils.steamlit_style import hide_streamlit_style
from dotenv import load_dotenv

# Import pages
#from pages import home, files, chat, settings
# Cargar variables de entorno
load_dotenv()

# Page configuration
st.set_page_config(
    page_title= config.PAGE_TITLE,
    page_icon=config.PAGE_ICON,
    layout="wide"
)

hide_streamlit_style()

# Check backend connection once
if 'backend_status' not in st.session_state:
    health = api_client.health_check()
    st.session_state.backend_status = health.get('status', 'unhealthy')

class MultiApp:
    def __init__(self):
        self.apps = []
    
    def add_app(self, title, func):
        """Add application page"""
        self.apps.append({
            "title": title,
            "function": func
        })
    
    def run(self):
        """Run the application - simplified like working example"""
        with st.sidebar:
            # Backend status indicator
            if st.session_state.backend_status == 'healthy':
                st.success("✅ Backend Connected")
            else:
                st.error("❌ Backend Disconnected")
                if st.button("🔄 Retry Connection"):
                    health = api_client.health_check()
                    st.session_state.backend_status = health.get('status', 'unhealthy')
            
            st.markdown("---")
            
            # Get page titles
            page_titles = [app["title"] for app in self.apps]
            
            # Navigation menu - simplified without session state tracking
            choice = option_menu(
                menu_title='Navigation',
                options=page_titles,
                icons=['house-fill', 'file-earmark-text-fill', 'chat-dots-fill', 'rocket-fill'],
                default_index=0,  # Fixed index instead of dynamic
                orientation="vertical",
                styles={
                    "container": {"padding": "5!important", "background-color": "black"},
                    "icon": {"color": "white", "font-size": "23px"},
                    "nav-link": {"color": "white", "font-size": "20px", "text-align": "left", "margin": "0px", "--hover-color": "blue"},
                    "nav-link-selected": {"background-color": "#02ab21"},
                }
            )
        
        # Direct navigation like working example - no reruns!
        for app_data in self.apps:
            if app_data["title"] == choice:
                app_data["function"]()  # Direct function call


if __name__ == "__main__":
    from app_pages import home, files, chat, cag
    multi_app = MultiApp()
    multi_app.add_app("Home", home.app)
    multi_app.add_app("Files", files.app)
    multi_app.add_app("Chat", chat.app)
    multi_app.add_app("About", cag.app)
    
    multi_app.run()