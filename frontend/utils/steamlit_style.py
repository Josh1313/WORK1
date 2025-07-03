import streamlit as st

def hide_streamlit_style():
    """Oculta los estilos por defecto de Streamlit."""
    hide_menu = """
        <style>
            /* Oculta el menú principal */
            #MainMenu {
                visibility: hidden;
            }
            
            /* Oculta el botón de Deploy */
            .stAppDeployButton {
                display: none;
            }
            
            /* Oculta el footer */
            footer {
                visibility: hidden;
            }
            
            /* Oculta la barra de decoración superior */
            #stDecoration {
                display: none;
            }
        </style>
    """
    st.markdown(hide_menu, unsafe_allow_html=True)
    
    ## para ocultar el menu tenemos que inspecionar la pagina y buscar el id del menu y ponerlo en hidden
    ## en este caso es MainMenu y stAppDeployButton para el boton de deploy