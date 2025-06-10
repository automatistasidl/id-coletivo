import streamlit as st
import pandas as pd
import datetime
import gspread
import traceback
from google.oauth2.service_account import Credentials
from gspread_dataframe import set_with_dataframe

# Configuração inicial
SPREADSHEET_KEY = st.secrets["spreadsheet"]["key"]
SHEET_NAME = "Registros"
SETORES_SHEET = "Setores"
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

# Escopos necessários
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

# Autenticação no Google Sheets
@st.cache_resource(ttl=300, show_spinner="Conectando ao Google Sheets...")
def get_google_sheet():
    try:
        # Obter informações da conta de serviço
        sa_info = st.secrets["gcp_service_account"]
        
        # Verificar se a chave privada está correta
        if not sa_info["private_key"].startswith("-----BEGIN PRIVATE KEY-----"):
            st.error("Formato inválido da chave privada. Verifique as quebras de linha.")
            st.stop()
            
        creds = Credentials.from_service_account_info(
            sa_info,
            scopes=SCOPES
        )
        client = gspread.authorize(creds)
        spreadsheet = client.open_by_key(SPREADSHEET_KEY)
        
        # Verificar acesso
        try:
            spreadsheet.title  # Tentar acessar o título da planilha
        except Exception as e:
            st.error(f"Falha ao acessar a planilha: {str(e)}")
            st.error(f"Verifique se a planilha foi compartilhada com: {sa_info['client_email']}")
            st.stop()
            
        return spreadsheet
    except Exception as e:
        st.error(f"Erro na autenticação: {traceback.format_exc()}")
        st.stop()

# Inicializar planilha com tratamento detalhado de erros
def init_spreadsheet():
    try:
        spreadsheet = get_google_sheet()
        
        # Criar/validar aba de registros
        try:
            sheet = spreadsheet.worksheet(SHEET_NAME)
            # Verificar se tem cabeçalho
            if not sheet.row_values(1):
                sheet.append_row(["matricula", "setor", "atingimento", "timestamp", "lider"])
        except gspread.WorksheetNotFound:
            # Se não existir, criar a aba
            sheet = spreadsheet.add_worksheet(title=SHEET_NAME, rows="1000", cols="10")
            sheet.append_row(["matricula", "setor", "atingimento", "timestamp", "lider"])
        
        # Criar/validar aba de setores
        try:
            setores_sheet = spreadsheet.worksheet(SETORES_SHEET)
            # Verificar se tem dados
            if len(setores_sheet.get_all_values()) <= 1:
                setores_sheet.clear()
                setores_sheet.append_row(["setor"])
                for setor in SETORES_PADRAO:
                    setores_sheet.append_row([setor])
        except gspread.WorksheetNotFound:
            # Se não existir, criar a aba
            setores_sheet = spreadsheet.add_worksheet(title=SETORES_SHEET, rows="100", cols="1")
            setores_sheet.append_row(["setor"])
            for setor in SETORES_PADRAO:
                setores_sheet.append_row([setor])
                
        return True
    except Exception as e:
        error_msg = f"Erro crítico ao acessar a planilha: {traceback.format_exc()}"
        st.error(error_msg)
        st.error("Verifique se:")
        st.error(f"1. A planilha foi compartilhada com: {st.secrets['gcp_service_account']['client_email']}")
        st.error("2. A chave da planilha está correta")
        st.error("3. O formato da chave privada está correto (com quebras de linha)")
        st.stop()
        return False

# Carregar dados com cache
@st.cache_data(ttl=120, show_spinner="Carregando registros...")
def load_data():
    try:
        sheet = get_google_sheet().worksheet(SHEET_NAME)
        return pd.DataFrame(sheet.get_all_records())
    except Exception as e:
        st.error(f"Erro ao carregar dados: {traceback.format_exc()}")
        return pd.DataFrame()

@st.cache_data(ttl=300)
def load_setores():
    try:
        setores_sheet = get_google_sheet().worksheet(SETORES_SHEET)
        return setores_sheet.col_values(1)[1:]  # Ignorar cabeçalho
    except:
        return SETORES_PADRAO

# Salvar dados
def save_data(matricula, setor, atingimento, lider):
    try:
        sheet = get_google_sheet().worksheet(SHEET_NAME)
        new_row = [
            matricula.strip(),
            setor.strip(),
            atingimento,
            datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            lider.strip()
        ]
        sheet.append_row(new_row)
        return True
    except Exception as e:
        st.error(f"Falha ao salvar registro: {traceback.format_exc()}")
        return False

def save_new_setor(new_setor):
    new_setor = new_setor.strip()
    if not new_setor:
        return False, "Nome do setor não pode ser vazio"
    
    try:
        setores_sheet = get_google_sheet().worksheet(SETORES_SHEET)
        setores = setores_sheet.col_values(1)
        
        if new_setor in setores:
            return False, f"Setor '{new_setor}' já existe"
        
        setores_sheet.append_row([new_setor])
        load_setores.clear()
        return True, f"Setor '{new_setor}' adicionado com sucesso!"
    except Exception as e:
        return False, f"Erro ao salvar setor: {traceback.format_exc()}"

# Interface Streamlit
def main():
    st.title("🏢 Controle de Coletivo/Sinergia")
    st.subheader("Registro de Atuação de Colaboradores")
    
    # Mostrar e-mail do service account para referência
    sa_email = st.secrets["gcp_service_account"]["client_email"]
    st.caption(f"Service Account: {sa_email}")
    
    # Inicializar planilha
    init_spreadsheet()
    
    # Identificação do líder
    lider = st.text_input("Nome do Líder:", value=st.session_state.get("lider", ""), key="lider_name")
    st.session_state.lider = lider
    
    # Formulário principal
    with st.form("registro_form", clear_on_submit=True):
        matricula = st.text_input("Matrícula do Colaborador:", max_chars=10, value="").strip()
        
        setores_options = load_setores()
        selected_setor = st.selectbox("Setor de Atuação:", setores_options)
        
        novo_setor = ""
        if selected_setor == "Outros":
            novo_setor = st.text_input("Especifique o novo setor:", value="").strip()
        
        atingimento = st.selectbox("Nível de Atingimento:", ATINGIMENTO_OPCOES)
        
        submitted = st.form_submit_button("Registrar Atuação")
        
        if submitted:
            error = False
            
            if not lider:
                st.error("Por favor, informe o nome do líder!")
                error = True
                
            if not matricula or not matricula.isdigit() or len(matricula) < 4:
                st.error("Matrícula inválida! Deve conter apenas números e ter pelo menos 4 dígitos.")
                error = True
                
            setor_final = novo_setor if selected_setor == "Outros" and novo_setor else selected_setor
            
            if selected_setor == "Outros" and not novo_setor:
                st.error("Por favor, informe o nome do novo setor!")
                error = True
            
            if error:
                st.stop()
                
            if selected_setor == "Outros" and novo_setor:
                success, message = save_new_setor(novo_setor)
                if success:
                    st.toast(message, icon="✅")
                else:
                    st.warning(message)
            
            if save_data(matricula, setor_final, atingimento, lider):
                st.toast(f"✅ Registro salvo! Colaborador {matricula} atuando como {setor_final}", icon="✅")
                st.session_state.submitted = True

    # Visualização de dados
    st.divider()
    st.subheader("Registros Atuais")
    
    if st.button("Atualizar Dados", help="Recarregar dados da planilha"):
        load_data.clear()
        load_setores.clear()
        st.toast("Dados atualizados!", icon="🔄")
    
    try:
        df = load_data()
        if not df.empty:
            df = df.sort_values("timestamp", ascending=False)
            
            # Filtros
            st.subheader("Filtros")
            col1, col2, col3 = st.columns(3)
            with col1:
                setor_filtro = st.selectbox("Setor:", ["Todos"] + list(df['setor'].unique()))
            with col2:
                lider_filtro = st.selectbox("Líder:", ["Todos"] + list(df['lider'].unique()))
            with col3:
                data_filtro = st.date_input("Data:", datetime.date.today())
            
            # Aplicar filtros
            if setor_filtro != "Todos":
                df = df[df['setor'] == setor_filtro]
            if lider_filtro != "Todos":
                df = df[df['lider'] == lider_filtro]
            if data_filtro:
                df = df[pd.to_datetime(df['timestamp']).dt.date == data_filtro]
            
            st.dataframe(df, use_container_width=True)
            
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
        st.error(f"Erro ao processar dados: {traceback.format_exc()}")

if __name__ == "__main__":
    main()
