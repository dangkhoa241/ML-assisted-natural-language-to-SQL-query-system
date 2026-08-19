# ML-Assisted Natural Language to SQL Query System

This project implements an end-to-end pipeline that allows users to query **any tabular CSV dataset**
using **plain English** — not just the healthcare example dataset it ships with. Upload any CSV and
the app adapts to its columns automatically.

**User question → Intent classification → SQL generation → Query execution → Table → Chart**

---

## 🚀 Enhanced Version

This is an enhanced version of the original project:
[dangkhoa241/LLMs-powered-natural-language-query-system-for-healthcare](https://github.com/dangkhoa241/LLMs-powered-natural-language-query-system-for-healthcare).

### What changed

* **Generalized beyond healthcare** — the original app only worked against `healthcare_dataset.csv`, with
  column names, category values, and keyword lists (gender, blood type, insurance provider, admission type,
  etc.) hardcoded directly into the SQL-generation logic. The app now inspects whatever CSV is uploaded at
  runtime and derives its column types, categories, and values from the data itself, so the same code works
  on a sales dataset, an HR dataset, a student dataset, and so on, unmodified.
* **Retrained the intent classifier on a domain-neutral dataset** — `intent_dataset.csv` previously contained
  only healthcare-phrased questions. It now contains 1,250 examples (250 per intent) spanning 14 domains
  (retail, education, HR, finance, sports, restaurants, real estate, IoT, library, logistics, social media,
  manufacturing, ecommerce, healthcare) so the BERT classifier generalizes instead of overfitting to one
  domain's vocabulary.
* **Graceful degradation without a trained model** — previously the app would hard-stop if `intent_model/`
  wasn't present. It now falls back to a lightweight keyword-based intent guesser so it's usable immediately,
  while still preferring the trained BERT classifier when available.
* **More robust filter/aggregate/trend logic** — numeric comparisons now correctly handle phrasing like
  "under age 40" (a word between the comparison term and the number), column matching uses exact word-token
  matching instead of substring matching (avoiding false positives like "orders" matching a column named
  `Order ID`), and trend queries now aggregate the metric actually asked about instead of always returning a
  raw row count.
* **Cleaner dependencies** — removed an invalid/non-existent package (`sqlite3-binary`) from
  `requirements.txt`; `sqlite3` is part of the Python standard library.

### What was evaluated and intentionally left out

* An LLM-API-driven SQL generator and two small local open-source text-to-SQL models were both evaluated.
  Both produced unreliable SQL for aggregate/compare/trend queries (missing `GROUP BY`, dropped aggregate
  functions, wrong comparison operators). The final design instead uses fully self-contained, rule-based SQL
  generation driven by the uploaded schema — no external API calls and no model download required to run it.

The system contains two major components:

### 1. **Intent Classification Model**

* A custom fine-tuned intent classifier trained using `intent_dataset.csv`
* Built on top of a pretrained **BERT (`bert-base-uncased`)** Transformer model
* Trained on domain-neutral example questions (retail, education, HR, finance, sports, healthcare,
  and more) so it generalizes to whatever dataset is uploaded, rather than one specific domain
* Produces intent categories: *filter, count, aggregate, compare, trend*
* Stored in the `intent_model/` folder after training
* Used to decide which type of SQL query to generate and which chart to show
* Optional: if `intent_model/` hasn't been trained yet, the app falls back to a lightweight
  keyword-based intent guesser so it still works out of the box

### 2. **Schema-Aware SQL Generator**

* Hand-built, rule-based NL→SQL engine — no external LLM API calls
* Reads the uploaded CSV's actual columns, data types, and values at runtime, then:
  * matches mentioned category values against the real distinct values in each column
  * matches numeric comparisons ("over 90000", "under age 40") to the right numeric column
  * detects date-like columns and grouping columns from the data itself
* Because everything is derived from the uploaded schema instead of hardcoded column names,
  the same logic works on a healthcare dataset, a sales dataset, an HR dataset, etc.

### 3. **Streamlit Web Application (`app.py`)**

* Interactive UI for uploading a CSV and entering queries
* Displays:

  * 🧠 Detected intent + generated SQL
  * 📄 Clean results table
  * 📈 Automatically generated chart based on intent (bar / pie / line)
  * 📝 Basic insights (highest / lowest values)
* Fully end-to-end: from CSV upload + text input → visualization

---

## 📂 What This Project Contains

```text
data/
  healthcare_dataset.csv   # Example dataset (one of many CSVs the app can load)
  intent_dataset.csv       # Domain-neutral training data for the intent classifier

intent_model/              # Saved fine-tuned BERT intent classification model (after training)

src/
  app.py                    # Streamlit entry point — thin orchestrator wiring the pieces together
  data_context.py            # CSV loading, type inference, SQLite table setup
  intent.py                   # BERT intent classifier + keyword-based fallback
  sql_builder.py               # Schema-aware, rule-based NL -> SQL generation
  visualization.py              # Chart rendering + insights
  model_training.ipynb           # Notebook for training the intent model

logs/                       # Training logs
requirements.txt           # Dependencies
```

---

## 🧠 Model Training (Intent Classifier)

The intent classification model is built by fine-tuning a **BERT-based Transformer (`bert-base-uncased`)** on a labeled, domain-neutral intent dataset.

### Base Model

* **Pretrained Model:** `bert-base-uncased`
* **Architecture:** Bidirectional Transformer Encoder
* **Tokenizer:** WordPiece tokenizer (uncased)
* **Framework:** PyTorch + Hugging Face Transformers

### Training Dataset

* Source file: `data/intent_dataset.csv`
* 1,250 examples (250 per intent) spanning 14 domains — retail, education, HR, finance, sports,
  restaurants, real estate, IoT, library, logistics, social media, manufacturing, ecommerce, and
  healthcare — so the classifier isn't tied to healthcare phrasing
* Each sample contains:

  * A natural language question
  * A corresponding intent label (filter, count, aggregate, compare, or trend)

### Training Objective

The model is fine-tuned for a **multi-class text classification task** to learn how to map user questions to the correct analytical intent. The trained intent model directly controls:

* The structure of generated SQL queries
* The selection of visualization types (bar, line, pie, etc.)

### Training Pipeline

* Input: Natural language questions across many domains
* Tokenization: BERT tokenizer
* Model: `AutoModelForSequenceClassification`
* Loss Function: Cross-entropy loss
* Optimizer: AdamW
* Output: Trained intent classification model saved to `intent_model/`

### Purpose in the System

The fine-tuned BERT intent model enables:

* Accurate understanding of user analytical goals
* Reduced ambiguity before SQL generation
* Automatic and correct chart type selection

---

## 🔍 What Makes This Project Unique

* Combines **ML-based intent classification + a self-built, schema-aware SQL generator**
* Works on **any uploaded CSV**, not a single fixed dataset — columns, types, and values are
  discovered at runtime
* Full *intent-aware* NL→SQL system
* Automatic **chart selection** based on predicted intent
* No external LLM API calls — everything runs locally
* End-to-end **Streamlit application** included
* Reproducible model training notebook

---

## 🧠 Example Workflow

**User uploads `healthcare_dataset.csv` and asks:**

> “Show emergency cases under age 40 with billing less than 12,000”

**System:**

1. Intent model → **filter**
2. SQL generator → matches "emergency" to the `Admission Type` column's real values, "under age 40"
   to the `Age` column, "billing less than 12,000" to the `Billing Amount` column
3. Executor → runs the generated SQL against the uploaded data
4. Result → filtered table (charts are generated for aggregate/compare/trend queries)

The same pipeline works unmodified if the user instead uploads a sales, HR, or student dataset —
only the column names and values found in the CSV change, not the code.

---

## 🖥️ Running the Application

```bash
pip install -r requirements.txt
streamlit run src/app.py
```

Training the intent classifier (optional — the app falls back to keyword-based intent detection
without it) needs a few extra dependencies, kept in a separate file so the deployed app doesn't
have to install them:

```bash
pip install -r requirements-train.txt
jupyter notebook src/model_training.ipynb
```

---

## ☁️ Deployment

The app is deployable as-is on [Streamlit Community Cloud](https://streamlit.io/cloud) (free,
connects directly to a GitHub repo):

1. Push this repo to GitHub.
2. On [share.streamlit.io](https://share.streamlit.io), create a new app pointing at this repo,
   branch `main`, and main file path `src/app.py`.
3. Deploy. `intent_model/` is gitignored (it's a ~400MB trained model, not meant for git), so the
   deployed app runs on the keyword-based intent fallback out of the box — no extra setup required.

To have the deployed app use the actual trained BERT classifier instead of the fallback:

1. Push the contents of `intent_model/` to a model repo on the
   [Hugging Face Hub](https://huggingface.co/new) (e.g. `your-username/intent-model`).
2. In the Streamlit Cloud app's settings, add a secret/environment variable
   `INTENT_MODEL_PATH=your-username/intent-model`.
3. Redeploy — `src/intent.py` reads that variable and loads the model from the Hub instead of the
   local `intent_model/` folder.

