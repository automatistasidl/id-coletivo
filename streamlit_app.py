import streamlit as st
import pandas as pd
import datetime
import gspread
from google.oauth2.service_account import Credentials
from gspread_dataframe import set_with_dataframe

# Configuração inicial
SPREADSHEET_KEY = st.secrets["spreadsheet_key"]  # Chave da planilha
SHEET_NAME = "Registros"  # Nome da aba principal
SETORES_SHEET = "Setores"  # Nome da aba de setores
SETORES_PADRAO = [
    "Aparcador", "Runner", "Recebimento", "Carregamento",
    "Cabide", "Multiplicador", "Qualidade", "Outros"
]
ATINGIMENTO_OPCOES = [
    "Menor que 120%",
    "Maior ou igual a 120% e Menor que 130%",
    "Maior ou igual a 130% e Menor que 140%",
    "Maior do que 140%"
]

# Autenticação no Google Sheets
def get_google_sheet():
    creds = Credentials.from_service_account_info(st.secrets["gcp_service_account"])
    client = gspread.authorize(creds)
    spreadsheet = client.open_by_key(SPREADSHEET_KEY)
    return spreadsheet

# Inicializar planilha
def init_spreadsheet():
    try:
        spreadsheet = get_google_sheet()
        
        # Criar aba de registros se não existir
        try:
            sheet = spreadsheet.worksheet(SHEET_NAME)
        except:
            sheet = spreadsheet.add_worksheet(title=SHEET_NAME, rows="1000", cols="10")
            sheet.append_row(["matricula", "setor", "atingimento", "timestamp", "lider"])
        
        # Criar aba de setores se não existir
        try:
            setores_sheet = spreadsheet.worksheet(SETORES_SHEET)
        except:
            setores_sheet = spreadsheet.add_worksheet(title=SETORES_SHEET, rows="100", cols="1")
            setores_sheet.append_row(["setor"])
            for setor in SETORES_PADRAO:
                setores_sheet.append_row([setor])
                
        return True
    except Exception as e:
        st.error(f"Erro ao acessar a planilha: {e}")
        return False

# Carregar dados
def load_data():
    spreadsheet = get_google_sheet()
    sheet = spreadsheet.worksheet(SHEET_NAME)
    df = pd.DataFrame(sheet.get_all_records())
    return df

def load_setores():
    spreadsheet = get_google_sheet()
    setores_sheet = spreadsheet.worksheet(SETORES_SHEET)
    setores = setores_sheet.col_values(1)[1:]  # Ignorar cabeçalho
    return setores

# Salvar dados
def save_data(matricula, setor, atingimento, lider):
    spreadsheet = get_google_sheet()
    sheet = spreadsheet.worksheet(SHEET_NAME)
    new_row = [matricula, setor, atingimento, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), lider]
    sheet.append_row(new_row)

def save_new_setor(new_setor):
    spreadsheet = get_google_sheet()
    setores_sheet = spreadsheet.worksheet(SETORES_SHEET)
    
    # Verificar se setor já existe
    setores = setores_sheet.col_values(1)
    if new_setor in setores:
        return False
    
    setores_sheet.append_row([new_setor])
    return True

# Interface Streamlit
def main():
    st.title("🏢 Controle de Coletivo/Sinergia")
    st.subheader("Registro de Atuação de Colaboradores")
    
    # Inicializar planilha
    if not init_spreadsheet():
        st.stop()
    
    # Identificação do líder
    if 'lider' not in st.session_state:
        st.session_state.lider = ""
    
    lider = st.text_input("Nome do Líder:", value=st.session_state.lider, key="lider_name")
    st.session_state.lider = lider
    
    # Formulário principal
    with st.form("registro_form"):
        matricula = st.text_input("Matrícula do Colaborador:", max_chars=10, value="")
        
        setores_options = load_setores()
        selected_setor = st.selectbox("Setor de Atuação:", setores_options)
        
        # Campo para novo setor se "Outros" for selecionado
        novo_setor = ""
        if selected_setor == "Outros":
            novo_setor = st.text_input("Especifique o novo setor:", value="")
        
        # Campo para atingimento
        atingimento = st.selectbox("Nível de Atingimento:", ATINGIMENTO_OPCOES)
        
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
    
    try:
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
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")

if __name__ == "__main__":
    main()
