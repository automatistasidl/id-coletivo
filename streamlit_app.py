import streamlit as st
import pandas as pd
import datetime
import os

# Configuração inicial
DATA_FILE = "coletivo_data.csv"
SETORES_FILE = "setores_options.csv"
SETORES_PADRAO = [
    "Aparcador", "Runner", "Recebimento", "Carregamento",
    "Cabide", "Multiplicador", "Qualidade", "Outros"
]
ATINGIMENTO_OPCOES = ["Até 120%", "Entre 120% e 130%", "Mais do que 130%"]

# Inicializar arquivos se não existirem
def init_files():
    if not os.path.exists(DATA_FILE):
        pd.DataFrame(columns=[
            "matricula", "setor", "atingimento", "timestamp", "lider"
        ]).to_csv(DATA_FILE, index=False)
    
    if not os.path.exists(SETORES_FILE):
        pd.DataFrame(SETORES_PADRAO, columns=["setor"]).to_csv(SETORES_FILE, index=False)

# Carregar dados
def load_data():
    return pd.read_csv(DATA_FILE)

def load_setores():
    df = pd.read_csv(SETORES_FILE)
    return df['setor'].tolist()

# Salvar dados
def save_data(matricula, setor, atingimento, lider):
    df = load_data()
    new_data = pd.DataFrame([{
        "matricula": matricula,
        "setor": setor,
        "atingimento": atingimento,
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "lider": lider
    }])
    df = pd.concat([df, new_data], ignore_index=True)
    df.to_csv(DATA_FILE, index=False)

def save_new_setor(new_setor):
    df = pd.read_csv(SETORES_FILE)
    if new_setor not in df['setor'].values:
        new_df = pd.DataFrame([{"setor": new_setor}])
        df = pd.concat([df, new_df], ignore_index=True)
        df.to_csv(SETORES_FILE, index=False)
        return True
    return False

# Interface Streamlit
def main():
    st.title("🏢 Controle de Coletivo/Sinergia")
    st.subheader("Registro de Atuação de Colaboradores")
    
    init_files()
    
    # Identificação do líder (mantido entre envios)
    if 'lider' not in st.session_state:
        st.session_state.lider = ""
    
    lider = st.text_input("Nome do Líder:", value=st.session_state.lider, key="lider_name")
    st.session_state.lider = lider
    
    # Inicializar estados para campos do formulário
    if 'matricula' not in st.session_state:
        st.session_state.matricula = ""
    if 'selected_setor' not in st.session_state:
        st.session_state.selected_setor = SETORES_PADRAO[0]
    if 'novo_setor' not in st.session_state:
        st.session_state.novo_setor = ""
    if 'atingimento' not in st.session_state:
        st.session_state.atingimento = ATINGIMENTO_OPCOES[0]
    
    # Formulário principal
    with st.form("registro_form"):
        matricula = st.text_input("Matrícula do Colaborador:", 
                                 max_chars=10, 
                                 value=st.session_state.matricula,
                                 key="matricula")
        
        setores_options = load_setores()
        # Tratamento para caso o setor salvo não esteja mais na lista
        try:
            default_index = setores_options.index(st.session_state.selected_setor)
        except ValueError:
            default_index = 0
        
        selected_setor = st.selectbox("Setor de Atuação:", 
                                     setores_options, 
                                     index=default_index,
                                     key="setor_select")
        
        # Campo para novo setor se "Outros" for selecionado
        novo_setor = ""
        if selected_setor == "Outros":
            novo_setor = st.text_input("Especifique o novo setor:", 
                                      value=st.session_state.novo_setor,
                                      key="new_sector")
        
        # Campo para atingimento
        atingimento = st.selectbox("Nível de Atingimento:", 
                                  ATINGIMENTO_OPCOES, 
                                  index=ATINGIMENTO_OPCOES.index(st.session_state.atingimento),
                                  key="atingimento_select")
        
        submitted = st.form_submit_button("Registrar Atuação")
        
        if submitted:
            if not lider:
                st.error("Por favor, informe o nome do líder!")
                st.stop()
                
            if not matricula.isdigit() or len(matricula) < 3:
                st.error("Matrícula inválida! Deve conter apenas números e ter pelo menos 3 dígitos.")
                st.stop()
                
            setor_final = novo_setor if selected_setor == "Outros" and novo_setor else selected_setor
            
            if selected_setor == "Outros" and not novo_setor:
                st.error("Por favor, informe o nome do novo setor!")
                st.stop()
                
            if selected_setor == "Outros" and novo_setor:
                if save_new_setor(novo_setor):
                    st.success(f"Novo setor '{novo_setor}' adicionado com sucesso!")
                else:
                    st.info(f"Setor '{novo_setor}' já existia na lista de opções")
            
            save_data(matricula, setor_final, atingimento, lider)
            st.success(f"✅ Registro salvo! Colaborador {matricula} atuando como {setor_final} com {atingimento}")
            
            # Forçar recarga da página para resetar os campos
            st.rerun()

    # Visualização de dados
    st.divider()
    st.subheader("Registros Atuais")
    
    df = load_data()
    if not df.empty:
        df = df.sort_values("timestamp", ascending=False)
        st.dataframe(df)
        
        # Estatísticas
        st.subheader("📊 Estatísticas")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total de Registros", len(df))
        with col2:
            st.metric("Setores Diferentes", df['setor'].nunique())
        with col3:
            st.metric("Líderes Ativos", df['lider'].nunique())
        
        # Gráficos
        tab1, tab2, tab3 = st.tabs(["Setores", "Atingimento", "Líderes"])
        
        with tab1:
            st.bar_chart(df['setor'].value_counts())
        
        with tab2:
            st.bar_chart(df['atingimento'].value_counts())
        
        with tab3:
            st.bar_chart(df['lider'].value_counts().head(5))
    else:
        st.info("Nenhum registro encontrado. Adicione novos registros acima.")

if __name__ == "__main__":
    main()
