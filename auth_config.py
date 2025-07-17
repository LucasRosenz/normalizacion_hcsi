"""
Configuración de autenticación para Agendas Salud
Usa Streamlit Secrets en producción y valores por defecto en desarrollo
"""
import streamlit as st
import os

def get_auth_config():
    """
    Obtiene configuración de autenticación segura
    """
    try:
        # Intentar usar Streamlit Secrets (en producción)
        if hasattr(st, 'secrets') and 'auth' in st.secrets:
            return {
                "admin": st.secrets["auth"]["admin_password"],
                "gerencia": st.secrets["auth"]["gerencia_password"],
                "medico": st.secrets["auth"]["medico_password"]
            }, st.secrets["auth"]["master_password"]
    except:
        pass
    
    # Fallback para desarrollo local
    users = {
        "admin": os.getenv("ADMIN_PASSWORD", "admin123"),
        "gerencia": os.getenv("GERENCIA_PASSWORD", "gerencia2024"),
        "medico": os.getenv("MEDICO_PASSWORD", "medico123")
    }
    master_password = os.getenv("MASTER_PASSWORD", "master123")
    
    return users, master_password

# Configuración actual
USERS, MASTER_PASSWORD = get_auth_config()