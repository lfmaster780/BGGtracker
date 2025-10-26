import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.bgg_api import BGGAPI
from utils.analyzer import PreferenceAnalyzer
from utils.recommender import GameRecommender

# Configuração da página
st.set_page_config(
    page_title="Board Game Analyzer",
    page_icon="🎲",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS customizado
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
    .recommendation-card {
        border-left: 4px solid #1f77b4;
        padding: 1rem;
        margin: 0.5rem 0;
        background-color: #f8f9fa;
    }
    .game-table {
        width: 100%;
        border-collapse: collapse;
    }
    .game-table th, .game-table td {
        padding: 12px;
        text-align: left;
        border-bottom: 1px solid #ddd;
    }
    .game-table th {
        background-color: #f8f9fa;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

def main():
    st.markdown('<h1 class="main-header">🎲 Board Game Analyzer</h1>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("🔧 Configurações")
        username = st.text_input("Usuário BGG", placeholder="Digite seu usuário do BoardGameGeek")
        load_data = st.button("🎯 Carregar Minha Coleção")
        
        st.markdown("---")
        st.header("🎪 Preferências")
        min_players = st.slider("Mínimo de Jogadores", 1, 6, 2)
        max_players = st.slider("Máximo de Jogadores", 2, 8, 4)
        max_complexity = st.slider("Complexidade Máxima", 1.0, 5.0, 4.0)
    
    # Inicialização de sessão
    if 'collection' not in st.session_state:
        st.session_state.collection = None
    if 'preferences' not in st.session_state:
        st.session_state.preferences = None
    if 'recommendations' not in st.session_state:
        st.session_state.recommendations = None
    
    # Carregar dados
    if load_data and username:
        with st.spinner("🔄 Carregando sua coleção do BGG... (isso pode levar alguns segundos)"):
            try:
                bgg_api = BGGAPI()
                collection = bgg_api.get_user_collection(username)
                
                if collection:
                    st.session_state.collection = collection
                    st.success(f"✅ {len(collection)} jogos carregados com sucesso!")
                    
                    # Analisar preferências
                    analyzer = PreferenceAnalyzer(collection)
                    st.session_state.preferences = analyzer.analyze_preferences()
                    
                    # Gerar recomendações
                    recommender = GameRecommender()
                    st.session_state.recommendations = recommender.get_recommendations(
                        st.session_state.preferences['avg_complexity']
                    )
                    
                else:
                    st.error("❌ Nenhum jogo encontrado. Verifique se:")
                    st.info("• O usuário está correto")
                    st.info("• Você tem jogos marcados como 'Own' no BGG")
                    st.info("• Sua coleção é pública")
                    
            except Exception as e:
                st.error(f"❌ Erro ao carregar dados: {str(e)}")
                st.info("Tente novamente em alguns segundos. O BGG pode estar processando sua requisição.")
    
    # Exibir conteúdo
    if st.session_state.collection is not None:
        display_analysis()
        display_recommendations()
    else:
        display_welcome()

def display_welcome():
    st.markdown("""
    ## 🎉 Bem-vindo ao Board Game Analyzer!
    
    **Descubra insights sobre sua coleção e receba recomendações personalizadas!**
    
    ### 🚀 Como usar:
    1. **Digite seu usuário** do BoardGameGeek na sidebar ←
    2. **Clique em** "Carregar Minha Coleção"
    3. **Explore** as análises e recomendações!
    
    ### 📊 O que você vai ver:
    - 📈 **Estatísticas** da sua coleção
    - 🎯 **Seu perfil** de jogador
    - 💡 **Recomendações** personalizadas
    - 📊 **Gráficos** interativos
    
    *💡 Dica: Quanto mais jogos você tiver avaliado, melhores serão as análises!*
    """)
    
    # Exemplo de como ficará
    with st.expander("👀 Preview da Aplicação"):
        st.image("https://via.placeholder.com/800x400/4CAF50/white?text=Board+Game+Analyzer+Preview", 
                caption="Sua aplicação terá uma interface similar a esta")

def display_analysis():
    st.header("📊 Análise da Sua Coleção")
    
    collection_df = pd.DataFrame(st.session_state.collection)
    preferences = st.session_state.preferences
    
    # Métricas principais
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("🎲 Total de Jogos", preferences['total_games'])
    with col2:
        st.metric("⭐ Sua Média", f"{preferences['avg_rating']:.1f}")
    with col3:
        st.metric("⚖️ Complexidade Média", f"{preferences['avg_complexity']:.1f}/5")
    with col4:
        st.metric("🎯 Tendência", preferences['rating_tendency'])
    
    # Tabela de jogos
    st.subheader("📋 Sua Coleção")
    
    # Preparar dados para tabela
    display_df = collection_df[['name', 'complexity', 'my_rating', 'bgg_rating', 'year']].copy()
    display_df.columns = ['Jogo', 'Complexidade', 'Sua Nota', 'Nota BGG', 'Ano']
    display_df = display_df.round(2)
    
    st.dataframe(
        display_df,
        use_container_width=True,
        height=400
    )
    
    # Gráficos
    col1, col2 = st.columns(2)
    
    with col1:
        # Gráfico de complexidade
        if len(collection_df) > 0:
            fig_complexity = px.histogram(
                collection_df, 
                x='complexity',
                title='📈 Distribuição de Complexidade',
                labels={'complexity': 'Complexidade (0-5)'},
                color_discrete_sequence=['#1f77b4']
            )
            fig_complexity.update_layout(showlegend=False)
            st.plotly_chart(fig_complexity, use_container_width=True)
    
    with col2:
        # Gráfico de ratings
        if len(collection_df) > 0:
            fig_ratings = px.scatter(
                collection_df, 
                x='bgg_rating', 
                y='my_rating',
                hover_data=['name'],
                title='🎯 Suas Notas vs Notas BGG',
                labels={'bgg_rating': 'Nota BGG', 'my_rating': 'Sua Nota'},
                color_discrete_sequence=['#ff7f0e']
            )
            # Adicionar linha de referência
            fig_ratings.add_shape(
                type="line", line=dict(dash="dash", color="gray"),
                x0=min(collection_df['bgg_rating']), y0=min(collection_df['my_rating']),
                x1=max(collection_df['bgg_rating']), y1=max(collection_df['my_rating'])
            )
            st.plotly_chart(fig_ratings, use_container_width=True)

def display_recommendations():
    st.header("💡 Recomendações para Você")
    
    if st.session_state.recommendations:
        recommendations = st.session_state.recommendations
        
        st.markdown(f"""
        ### 🎯 Baseado no seu estilo de jogo, você pode gostar de:
        
        *Encontramos {len(recommendations)} jogos que combinam com suas preferências*
        """)
        
        for i, game in enumerate(recommendations[:5]):  # Top 5 recomendações
            with st.container():
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    match_score = game.get('match_score', 0)
                    reason = game.get('reason', 'Combina com seu estilo')
                    
                    st.markdown(f"""
                    <div class="recommendation-card">
                        <h4>#{i+1} {game['name']} ({game.get('year', 'N/A')})</h4>
                        <p><strong>🎯 Compatibilidade:</strong> {match_score:.0f}%</p>
                        <p><strong>💡 Porque recomendar:</strong> {reason}</p>
                        <p><strong>⚖️ Complexidade:</strong> {game.get('complexity', 0):.1f}/5 | 
                           <strong>👥 Jogadores:</strong> {game.get('min_players', '?')}-{game.get('max_players', '?')} | 
                           <strong>⏱️ Tempo:</strong> {game.get('playtime', '?')}min</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    bgg_url = f"https://boardgamegeek.com/boardgame/{game['id']}"
                    st.markdown(f"[🔗 Ver no BGG]({bgg_url})")
                
                st.markdown("---")
        
        if len(recommendations) > 5:
            st.info(f"💡 Temos mais {len(recommendations) - 5} recomendações disponíveis!")
    else:
        st.info("""
        💡 **As recomendações aparecerão aqui após carregar sua coleção!**
        
        *Elas são geradas baseadas na complexidade dos jogos que você mais gosta.*
        """)

if __name__ == "__main__":
    main()