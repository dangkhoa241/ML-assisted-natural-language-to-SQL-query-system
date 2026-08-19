"""Renders the result table, chart, and basic insights for a query result."""
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


def visualize(intent: str, query: str, result: pd.DataFrame):
    if result.empty:
        st.warning("No data returned.")
        return

    st.subheader("Table Result")
    st.dataframe(result)

    if intent == "filter":
        st.info("Charts are only generated for aggregated, comparison, or trend queries.")
        return

    numeric_result_cols = result.select_dtypes(include="number").columns.tolist()
    text_result_cols = result.select_dtypes(exclude="number").columns.tolist()

    if not numeric_result_cols or not text_result_cols:
        return

    y_col = numeric_result_cols[0]
    x_col = text_result_cols[0]

    result = result.copy()
    result[x_col] = result[x_col].astype(str)
    result = result.sort_values(by=x_col)

    fig_w, fig_h = (4, 2.5)

    chart_options = ["Bar", "Pie", "Line", "Table only"]
    default_chart = "Line" if intent == "trend" else "Bar"
    chart_type = st.selectbox("Chart Type", chart_options, index=chart_options.index(default_chart))

    x_label = x_col.replace("_", " ").title()
    y_label = y_col.replace("_", " ").title()
    title = query.capitalize()

    st.subheader("Visualization")

    # Bar Chart
    if chart_type == "Bar":
        fig, ax = plt.subplots(figsize=(fig_w * 0.8, fig_h * 0.8))

        sns.barplot(data=result, x=x_col, y=y_col, ax=ax)

        max_val = result[y_col].max()
        offset = max_val * 0.02

        for i, v in enumerate(result[y_col]):
            ax.text(i, v + offset, f"{v:,.0f}", ha="center", va="bottom", fontsize=9, fontweight="normal")

        ax.set_xlabel(x_label, fontsize=10)
        ax.set_ylabel(y_label, fontsize=10)
        ax.set_title(title, fontsize=11, fontweight="semibold", pad=12)

        plt.xticks(rotation=15, fontsize=4)
        plt.yticks(fontsize=4)
        sns.despine()

        plt.tight_layout()
        st.pyplot(fig)

    # Pie Chart
    elif chart_type == "Pie":
        fig, ax = plt.subplots(figsize=(fig_w * 0.7, fig_h * 0.7))

        ax.pie(result[y_col], labels=result[x_col], autopct="%1.1f%%", textprops={"fontsize": 8}, startangle=90)

        ax.set_title(title, fontsize=11, pad=8)
        plt.tight_layout()
        st.pyplot(fig)

    # Line Chart
    elif chart_type == "Line":
        fig, ax = plt.subplots(figsize=(3.2, 1.8))

        sns.lineplot(data=result, x=x_col, y=y_col, marker="o", linewidth=1.2, markersize=4, ax=ax)

        ax.set_xlabel(x_label, fontsize=8)
        ax.set_ylabel(y_label, fontsize=8)
        ax.set_title(title, fontsize=9, pad=5)

        ymin, ymax = result[y_col].min(), result[y_col].max()
        pad = (ymax - ymin) * 0.6 if ymax != ymin else 1
        ax.set_ylim(ymin - pad, ymax + pad)

        plt.xticks(rotation=18, fontsize=7)
        plt.yticks(fontsize=7)
        sns.despine()

        plt.tight_layout(pad=0.3)
        st.pyplot(fig, use_container_width=False)

    # Insights
    st.subheader("Insights")
    try:
        idx_max = result[y_col].idxmax()
        idx_min = result[y_col].idxmin()

        st.write(f"Highest {y_label}: {result.loc[idx_max, x_col]} → {result.loc[idx_max, y_col]}")
        st.write(f"Lowest {y_label}: {result.loc[idx_min, x_col]} → {result.loc[idx_min, y_col]}")
    except Exception:
        st.write("No insights available.")
