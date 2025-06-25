import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Avaliação Jetour", layout="wide")
st.title("📊 Avaliação de Grupos Concessionários - Jetour")

file = st.file_uploader("📁 Envie sua planilha com os dados de avaliação", type=["xlsx"])

if file:
    xls = pd.ExcelFile(file)
    criterios_df = pd.read_excel(xls, sheet_name="Critérios e Pesos")
    notas_df = pd.read_excel(xls, sheet_name="Notas por Grupo")

    st.sidebar.header("🔍 Filtros")
    criterios_list = criterios_df["Critério"].tolist()
    selected_criterios = st.sidebar.multiselect("Escolha os critérios para análise detalhada:", criterios_list, default=criterios_list)

    st.subheader("📌 Critérios e Pesos")
    st.dataframe(criterios_df)

    st.subheader("📝 Notas dos Grupos")
    st.dataframe(notas_df)

    pesos = criterios_df.set_index("Critério")["Peso"]
    grupos = notas_df.set_index("Grupo")

    criterios_em_comum = pesos.index.intersection(grupos.columns)
    grupos_filtrados = grupos[criterios_em_comum]
    pesos_filtrados = pesos[criterios_em_comum]

    nota_ponderada = grupos_filtrados.mul(pesos_filtrados).sum(axis=1)
    nota_ponderada_df = pd.DataFrame({"Nota Total Ponderada": nota_ponderada})

    nota_min = nota_ponderada.min()
    nota_max = nota_ponderada.max()
    nota_normalizada = (nota_ponderada - nota_min) / (nota_max - nota_min) * 10
    nota_ponderada_df["Nota Final Normalizada"] = nota_normalizada

    nota_ponderada_df = nota_ponderada_df.sort_values("Nota Final Normalizada", ascending=False)
    nota_ponderada_df["Ranking"] = range(1, len(nota_ponderada_df) + 1)

    st.subheader("🏆 Ranking dos Grupos")
    st.dataframe(nota_ponderada_df)

    st.download_button(
        label="⬇️ Baixar Ranking como CSV",
        data=nota_ponderada_df.to_csv().encode("utf-8"),
        file_name="ranking_concessionarios.csv",
        mime="text/csv"
    )

    st.subheader("📈 Gráfico Radar dos Grupos")
    grupo_selecionado = st.selectbox("Escolha um grupo para visualizar o radar:", grupos_filtrados.index)

    fig_radar = go.Figure()
    for grupo in grupos_filtrados.index:
        if grupo == grupo_selecionado:
            fig_radar.add_trace(go.Scatterpolar(
                r=grupos_filtrados.loc[grupo, selected_criterios].values,
                theta=selected_criterios,
                fill='toself',
                name=grupo
            ))

    fig_radar.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 10])),
        showlegend=True
    )
    st.plotly_chart(fig_radar, use_container_width=True)

    st.subheader("📊 Comparativo de Grupos")
    grupos_selecionados = st.multiselect("Selecione os grupos para comparar:", grupos_filtrados.index.tolist(), default=grupos_filtrados.index[:3])

    comparativo_df = grupos_filtrados.loc[grupos_selecionados, selected_criterios]
    st.dataframe(comparativo_df.style.highlight_max(axis=0))

    st.subheader("📉 Evolução Normalizada")
    st.line_chart(nota_ponderada_df["Nota Final Normalizada"])
else:
    st.info("👆 Envie uma planilha para começar.")
