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

# Inicializar arquivos se não existirem
def init_files():
    if not os.path.exists(DATA_FILE):
        pd.DataFrame(columns=["matricula", "setor", "timestamp", "lider"]).to_csv(DATA_FILE, index=False)
    
    if not os.path.exists(SETORES_FILE):
        pd.DataFrame(SETORES_PADRAO, columns=["setor"]).to_csv(SETORES_FILE, index=False)

# Carregar dados
def load_data():
    return pd.read_csv(DATA_FILE)

def load_setores():
    df = pd.read_csv(SETORES_FILE)
    return df['setor'].tolist()

# Salvar dados
def save_data(matricula, setor, lider):
    df = load_data()
    new_data = pd.DataFrame([{
        "matricula": matricula,
        "setor": setor,
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
    
    # Identificação do líder
    lider = st.text_input("Nome do Líder:", key="lider_name")
    
    # Formulário principal
    with st.form("registro_form"):
        matricula = st.text_input("Matrícula do Colaborador:", max_chars=10)
        
        setores_options = load_setores()
        selected_setor = st.selectbox("Setor de Atuação:", setores_options, index=0)
        
        # Campo para novo setor se "Outros" for selecionado
        novo_setor = ""
        if selected_setor == "Outros":
            novo_setor = st.text_input("Especifique o novo setor:", key="new_sector")
        
        submitted = st.form_submit_button("Registrar Atuação")
        
        if submitted:
            if not lider:
                st.error("Por favor, informe o nome do líder!")
                return
                
            if not matricula.isdigit() or len(matricula) < 3:
                st.error("Matrícula inválida! Deve conter apenas números e ter pelo menos 3 dígitos.")
                return
                
            setor_final = novo_setor if selected_setor == "Outros" and novo_setor else selected_setor
            
            if selected_setor == "Outros" and not novo_setor:
                st.error("Por favor, informe o nome do novo setor!")
                return
                
            if selected_setor == "Outros" and novo_setor:
                if save_new_setor(novo_setor):
                    st.success(f"Novo setor '{novo_setor}' adicionado com sucesso!")
                else:
                    st.info(f"Setor '{novo_setor}' já existia na lista de opções")
            
            save_data(matricula, setor_final, lider)
            st.success(f"Registro salvo! Colaborador {matricula} atuando como {setor_final}")

    # Visualização de dados
    st.divider()
    st.subheader("Registros Atuais")
    
    df = load_data()
    if not df.empty:
        df = df.sort_values("timestamp", ascending=False)
        st.dataframe(df)
        
        # Estatísticas
        st.subheader("📊 Estatísticas")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total de Registros", len(df))
        with col2:
            st.metric("Setores Diferentes", df['setor'].nunique())
        
        # Top setores
        st.bar_chart(df['setor'].value_counts())
    else:
        st.info("Nenhum registro encontrado. Adicione novos registros acima.")

if __name__ == "__main__":
    main()
