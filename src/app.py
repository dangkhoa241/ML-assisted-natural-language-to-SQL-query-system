import streamlit as st
import pandas as pd

from data_context import load_dataset
from intent import load_intent_classifier, get_intent
from sql_builder import build_sql
from visualization import visualize

SAMPLE_DATASET_PATH = "data/healthcare_dataset.csv"
SAMPLE_QUERIES = [
    "average billing amount by insurance provider",
    "how many emergency admissions",
    "trend of patient admissions by year",
    "compare male and female patients by billing amount",
]
QUERY_KEY = "user_query"

st.set_page_config(page_title="Natural Language Data Assistant", layout="wide")
st.title("Natural Language Data Assistant")
st.caption("Upload any CSV and ask questions about it in plain English.")

if "use_sample" not in st.session_state:
    st.session_state.use_sample = False

uploaded_file = st.file_uploader("Upload your dataset (CSV)", type=["csv"])
if st.button("Try with sample data (healthcare dataset)"):
    st.session_state.use_sample = True

if uploaded_file is not None:
    st.session_state.use_sample = False  # an explicit upload always takes priority
    data_source = uploaded_file
    using_sample = False
elif st.session_state.use_sample:
    data_source = SAMPLE_DATASET_PATH
    using_sample = True
else:
    data_source = None
    using_sample = False

if data_source is None:
    st.info('Upload a CSV above, or click "Try with sample data" to explore a demo healthcare dataset.')
    st.stop()

dataset = load_dataset(data_source)

st.write(f"Loaded {dataset.df.shape[0]} rows and {dataset.df.shape[1]} columns")
st.dataframe(dataset.df.head())

clf = load_intent_classifier()
if clf is None:
    st.info(
        "No local `intent_model/` found — using keyword-based intent detection. "
        "Run `model_training.ipynb` to train the BERT intent classifier for more accurate results."
    )

if using_sample:
    st.write("Try an example question:")
    cols = st.columns(len(SAMPLE_QUERIES))
    for col, example in zip(cols, SAMPLE_QUERIES):
        if col.button(example):
            st.session_state[QUERY_KEY] = example

query = st.text_input("Ask a question about your data:", key=QUERY_KEY)

if query:
    intent = get_intent(query, clf)
    intent, sql = build_sql(query, intent, dataset)
    st.write(f"Detected intent: {intent}")
    st.code(sql, language="sql")

    try:
        result_df = pd.read_sql_query(sql, dataset.conn)
        visualize(intent, query, result_df)
    except Exception as e:
        st.error(f"SQL execution error: {e}")
