import streamlit as st
import pandas as pd
import plotly.express as px
from duckduckgo_search import DDGS

# =========================================
# CONFIGURAÇÃO DA PÁGINA
# =========================================
st.set_page_config(
    page_title="Avi - Web IA",
    page_icon="🤖",
    layout="wide"
)

# Estilo para manter o topo bonito com as cores escolhidas
st.markdown("""
    <style>
    .nome-ia {
        text-align: center;
        font-size: 52px !important;
        font-weight: bold;
        color: #007BFF; /* Azul */
        margin-bottom: 5px;
    }
    .sub-ia {
        text-align: center;
        color: #888888;
        margin-bottom: 30px;
    }
    </style>
""", unsafe_allow_html=True)

# =========================================
# MOTOR DE BUSCA E RESPOSTA DA AVI
# =========================================

def responder_pela_internet(pergunta):
    """
    Busca na web em tempo real e monta uma resposta estruturada
    baseada exclusivamente nos melhores resultados encontrados.
    """
    try:
        with DDGS() as ddgs:
            # Faz a busca na internet pelos 4 melhores resultados
            busca = ddgs.text(pergunta, max_results=4)
            
            if not busca:
                return "Não encontrei informações recentes na internet sobre isso no momento. Pode tentar reformular a pergunta?"
            
            # Constrói o balão de resposta formatando o que achou na web
            resposta_formatada = "### 🌐 Informações encontradas na internet:\n\n"
            
            for i, resultado in enumerate(busca, 1):
                titulo = resultado.get("title", "Resultado")
                link = resultado.get("href", "")
                resumo = resultado.get("body", "")
                
                resposta_formatada += f"**{i}. {titulo}**\n"
                resposta_formatada += f"{resumo}\n"
                if link:
                    resposta_formatada += f"*Fonte:* [{link}]({link})\n\n"
            
            return resposta_formatada
            
    except Exception as e:
        return f"Desculpe, tive um problema de conexão ao acessar a internet para buscar essa resposta. Erro: {str(e)}"

# =========================================
# INTERFACE PRINCIPAL (AVI CHAT)
# =========================================

# Cabeçalho destacado
st.markdown('<p class="nome-ia">🤖 AVI</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-ia">Sua assistente de busca inteligente em tempo real</p>', unsafe_allow_html=True)

# Inicializar o histórico de balões se não existir
if "mensagens_chat" not in st.session_state:
    st.session_state.mensagens_chat = []

# Mostrar os balões de conversa antigos na tela
for msg in st.session_state.mensagens_chat:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# Caixa de texto estilo balão (Digite e aperte Enter)
if pergunta_usuario := st.chat_input("Pergunte qualquer coisa para a Avi buscar na web..."):
    
    # 1. Cria o balão do usuário na tela
    st.session_state.mensagens_chat.append({"role": "user", "content": pergunta_usuario})
    with st.chat_message("user"):
        st.write(pergunta_usuario)

    # 2. Faz a busca e cria o balão de resposta da Avi baseada na web
    with st.chat_message("assistant"):
        with st.spinner("Buscando fontes na internet..."):
            resposta_final = responder_pela_internet(pergunta_usuario)
            st.write(resposta_final)
            
    # Salva a resposta no histórico da tela
    st.session_state.mensagens_chat.append({"role": "assistant", "content": resposta_final})


# =========================================
# BARRA LATERAL (PLANILHAS E EXTENSÕES)
# =========================================
with st.sidebar:
    st.title("🛠️ Ferramentas Extras")
    st.write("Área secundária para análise de arquivos.")
    st.markdown("---")
    
    # Upload de Planilhas
    st.subheader("📊 Analisar Planilha")
    arquivo = st.file_uploader("Envie seu arquivo (CSV ou XLSX)", type=["xlsx", "csv"])
    
    if arquivo:
        if arquivo.name.endswith(".csv"):
            dados = pd.read_csv(arquivo)
        else:
            dados = pd.read_excel(arquivo)
        
        st.success("Planilha carregada!")
        
        if st.checkbox("Mostrar tabela"):
            st.dataframe(dados)
            
        colunas_numericas = dados.select_dtypes(include="number").columns
        if len(colunas_numericas) > 0:
            coluna = st.selectbox("Gerar Histograma da coluna:", colunas_numericas)
            fig = px.histogram(dados, x=coluna, title=f"Gráfico de {coluna}", color_discrete_sequence=['#007BFF'])
            st.plotly_chart(fig, use_container_width=True)
            st.metric("Média dos valores", f"{dados[coluna].mean():.2f}")