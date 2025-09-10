# app.py (versão com campo digitável e tabela estilizada)
import streamlit as st
import pandas as pd

# --- FUNÇÃO PARA INJETAR CSS ---
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

def style_table():
    """
    Adiciona CSS para estilizar a tabela de resultados com fonte maior e texto centralizado.
    """
    st.markdown("""
    <style>
    .dataframe {
        text-align: center;
    }
    .dataframe th {
        text-align: center !important;
        font-size: 18px !important;
    }
    .dataframe td {
        text-align: center !important;
        font-size: 16px !important;
    }
    </style>
    """, unsafe_allow_html=True)


# --- DADOS E FUNÇÕES PRINCIPAIS ---

# Fonte: Site oficial da Caixa Econômica Federal
PROBABILIDADES = {
    "Dia de Sorte": {7: 2629575, 8: 328697, 9: 73044, 10: 21913, 11: 8041, 12: 3446, 13: 1673, 14: 896, 15: 522},
    "Dupla Sena": {6: 15890700, 7: 2270100, 8: 567525, 9: 189175, 10: 75670, 11: 34395, 12: 17197, 13: 9260, 14: 5291, 15: 3218},
    "Lotofácil": {15: 3268760, 16: 204298, 17: 24035, 18: 4006, 19: 843, 20: 211},
    "Lotomania": {50: 11372635},
    "Mega-Sena": {6: 50063860, 7: 7151980, 8: 1787995, 9: 595998, 10: 238399, 11: 108363, 12: 54182, 13: 29175, 14: 16671, 15: 10003, 16: 6252, 17: 4045, 18: 2697, 19: 1845, 20: 1292},
    "+Milionária": {6: 238399500, 7: 34057071, 8: 7297944, 9: 2027207, 10: 675736, 11: 259898, 12: 109957},
    "Quina": {5: 24040016, 6: 4006669, 7: 1144763, 8: 429286, 9: 190794, 10: 95397, 11: 52034, 12: 30354, 13: 18679, 14: 12008, 15: 8005},
    "Super Sete": {7: 10000000, 8: 1428571, 9: 357143, 10: 119048, 11: 47619, 12: 21645, 13: 10823, 14: 5830, 15: 3331, 16: 1999, 17: 1249, 18: 807, 19: 538, 20: 370, 21: 261},
    "Timemania": {10: 26472637}
}

def calcular_probabilidade_combinada(prob_individual, qtd_jogos):
    if qtd_jogos <= 0 or prob_individual <= 0: return float('inf')
    if prob_individual == 1: return 1.0
    prob_nao_ganhar_individual = (prob_individual - 1) / prob_individual
    prob_nao_ganhar_total = prob_nao_ganhar_individual ** qtd_jogos
    prob_ganhar_total = 1 - prob_nao_ganhar_total
    if prob_ganhar_total == 0: return float('inf')
    return 1 / prob_ganhar_total

# --- INTERFACE DA APLICAÇÃO STREAMLIT ---
st.set_page_config(page_title="Calculadora de Bolões", layout="wide")
st.title("📊 Calculadora Comparativa de Bolões da Loteria")
st.markdown("Compare diferentes estratégias de bolões para ver qual oferece a melhor probabilidade de ganho.")

num_estrategias = st.number_input("Quantas estratégias de bolão você deseja comparar?", min_value=1, max_value=10, value=2, step=1)

estrategias = []
jogos_disponiveis = sorted(list(PROBABILIDADES.keys()))
dados_validos = True

st.divider()

cols = st.columns(num_estrategias)
for i in range(num_estrategias):
    with cols[i]:
        st.header(f"Estratégia #{i + 1}")
        
        jogo_escolhido = st.selectbox("Selecione o jogo:", options=jogos_disponiveis, key=f"jogo_{i}")
        valor_premio = st.number_input("Valor do prêmio (R$)", min_value=0.01, value=1000000.0, step=100000.0, format="%.2f", key=f"premio_{i}")
        qtd_jogos = st.number_input("Quantidade de jogos no bolão:", min_value=1, value=1, step=1, key=f"qtd_jogos_{i}")
        num_cotas = st.number_input("Número de cotas do bolão:", min_value=1, value=10, step=1, key=f"cotas_{i}")
        
        opcoes_dezenas = PROBABILIDADES[jogo_escolhido]
        dezenas_disponiveis = sorted(list(opcoes_dezenas.keys()))
        num_dezenas = 0

        if len(opcoes_dezenas) == 1:
            num_dezenas = dezenas_disponiveis[0]
            st.info(f"Aposta única com {num_dezenas} dezenas.")
        else:
            # Campo de dezenas agora é digitável (st.number_input)
            num_dezenas = st.number_input(
                f"Dezenas por jogo ({min(dezenas_disponiveis)}-{max(dezenas_disponiveis)})",
                min_value=min(dezenas_disponiveis),
                max_value=max(dezenas_disponiveis),
                value=min(dezenas_disponiveis),
                step=1,
                key=f"dezenas_{i}"
            )
            # Validação em tempo real
            if num_dezenas not in dezenas_disponiveis:
                st.error(f"Número de dezenas inválido para {jogo_escolhido}. Opções: {dezenas_disponiveis}")
                dados_validos = False

        estrategias.append({
            "index": i, "jogo_escolhido": jogo_escolhido, "valor_premio": valor_premio,
            "qtd_jogos": qtd_jogos, "num_cotas": num_cotas, "num_dezenas": num_dezenas
        })

st.divider()

if st.button("Analisar e Comparar Estratégias", use_container_width=True):
    if not dados_validos:
        st.error("Por favor, corrija os erros nos campos de 'dezenas' antes de comparar.")
    else:
        dados_finais = []
        for res in estrategias:
            prob_individual = PROBABILIDADES[res['jogo_escolhido']][res['num_dezenas']]
            prob_final = calcular_probabilidade_combinada(prob_individual, res['qtd_jogos'])
            premio_por_cota = res['valor_premio'] / res['num_cotas']
            dados_finais.append({
                "Estratégia": f"#{res['index'] + 1}", "Jogo": res['jogo_escolhido'],
                "Detalhes": f"{res['qtd_jogos']} jogo(s) de {res['num_dezenas']} dezenas",
                "Probabilidade (1 em)": prob_final, "Prêmio por Cota (R$)": premio_por_cota
            })
        
        df = pd.DataFrame(dados_finais)
        df = df.sort_values(by="Probabilidade (1 em)").reset_index(drop=True)

        st.subheader(" Quadro Comparativo dos Bolões")
        st.markdown("*Resultado ordenado da melhor (menor probabilidade) para a pior.*")
        
        # Aplica o estilo na tabela
        style_table()

        # Formata os números no DataFrame para exibição
        df_display = df.copy()
        df_display["Probabilidade (1 em)"] = df["Probabilidade (1 em)"].apply(lambda x: f"{x:,.0f}".replace(",", "."))
        df_display["Prêmio por Cota (R$)"] = df["Prêmio por Cota (R$)"].apply(lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

        st.dataframe(df_display, use_container_width=True, hide_index=True)
