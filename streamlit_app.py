import streamlit as st
from datetime import datetime

# Configuração da página
st.set_page_config(
    page_title="Registro de Atividades",
    page_icon="📋",
    layout="centered"
)

# CSS customizado
st.markdown("""
    <style>
        .reportview-container {
            margin-top: -2em;
        }
        #MainMenu {visibility: hidden;}
        .stDeployButton {display:none;}
        footer {visibility: hidden;}
        .stTextInput input, .stSelectbox select {
            padding: 10px !important;
            border-radius: 5px;
            border: 1px solid #ddd;
        }
        .stButton button {
            width: 100%;
            padding: 12px !important;
            background-color: #4CAF50 !important;
            color: white !important;
            border-radius: 5px;
            font-size: 16px;
        }
        .stButton button:hover {
            background-color: #45a049 !important;
        }
        .success-message {
            padding: 15px;
            background-color: #e8f5e9;
            border-radius: 5px;
            color: #2e7d32;
            margin-top: 20px;
        }
    </style>
""", unsafe_allow_html=True)

# Título do aplicativo
st.title("📋 Registro de Atividades")

# Formulário
with st.form("activity_form"):
    matricula = st.text_input("Matrícula do Usuário:", max_chars=10, placeholder="Digite sua matrícula")
    
    atividade = st.selectbox(
        "Atividade Executada:",
        ["", "Cabide", "Runner", "Descargar de caminhão", "Outros"],
        index=0
    )
    
    outros_texto = ""
    if atividade == "Outros":
        outros_texto = st.text_input("Especifique a atividade:", placeholder="Digite a atividade realizada")
    
    submitted = st.form_submit_button("Registrar Atividade")

# Validação e processamento
if submitted:
    error = False
    
    if not matricula:
        st.error("Por favor, digite a matrícula")
        error = True
    
    if not atividade:
        st.error("Por favor, selecione uma atividade")
        error = True
    elif atividade == "Outros" and not outros_texto:
        st.error("Por favor, especifique a atividade")
        error = True
    
    if not error:
        # Determina a atividade final
        atividade_final = outros_texto if atividade == "Outros" else atividade
        
        # Mensagem de sucesso
        hora_atual = datetime.now().strftime("%H:%M:%S")
        success_html = f"""
            <div class="success-message">
                <strong>✅ Registro realizado com sucesso!</strong><br><br>
                <strong>Matrícula:</strong> {matricula}<br>
                <strong>Atividade:</strong> {atividade_final}<br>
                <strong>Horário:</strong> {hora_atual}
            </div>
        """
        st.markdown(success_html, unsafe_allow_html=True)
