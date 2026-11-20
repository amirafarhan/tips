# 💵 Restaurant Tips — Data Visualization & Analysis

A data-visualization project with **Matplotlib** and **Seaborn**, using the classic *tips* dataset (244 restaurant
bills recorded by one waiter: total bill, tip, sex, smoker, day, time and party size). It also includes an interactive
**Streamlit** dashboard that answers the notebook's questions with statistical tests.

**🔗 Live demo:** https://zvi3tnadcuvppjmdfaebwm.streamlit.app/

## 🚀 Features

- **Notebook (`tips.ipynb`):**
  - Matplotlib basics on a small sales example: scatter, bar, line, histogram, subplots, boxplot;
  - Seaborn charts of the tips data: line, bar, scatter, histogram, box, boxen, KDE, count, correlation heatmap;
  - three questions: Does the tip grow with the bill? Which gender tips more? Does party size matter?
- **Streamlit dashboard (`app.py`):**
  - filters by day, time, sex, smoker and party size;
  - the notebook's three questions answered from the filtered data, with significance tests;
  - bill-vs-tip scatter with a regression line and correlation;
  - group comparison of tip, tip % or bill by any category, with 95% confidence intervals and a Welch t-test or ANOVA;
  - histograms, box plots by day and a correlation heatmap;
  - data table with CSV download.

## 🔍 Findings (full dataset)

| Question | Result |
|---|---|
| Does the tip grow with the bill? | Yes: r = 0.68 (p < 0.001), about $1.05 more tip per $10 of bill |
| Which gender tips more? | Men tip more in dollars ($3.09 vs $2.83), but the difference is **not** statistically significant (p = 0.14); as a share of the bill women tip slightly more (16.6% vs 15.8%, p = 0.25) |
| Does party size affect the tip? | Yes in dollars (ANOVA p < 0.001), mainly because larger parties have larger bills |

## 🛠️ Tech Stack

Python · pandas · NumPy · SciPy · Matplotlib · Seaborn · Altair · Streamlit · Jupyter

## 📂 Project Structure

```
tips/
├── tips.ipynb        # Visualization notebook
├── tips.csv          # The Seaborn tips dataset (saved from seaborn.load_dataset("tips"))
├── tips_analysis.py  # Loading, group statistics and tests
├── app.py            # Streamlit dashboard
├── requirements.txt
└── .streamlit/config.toml
```

## 📦 Installation

```bash
git clone https://github.com/amirafarhan/tips.git
cd tips
python -m venv venv
# Windows: venv\Scripts\activate    Linux/Mac: source venv/bin/activate
pip install -r requirements.txt
```

## ▶️ Run

Live demo: https://zvi3tnadcuvppjmdfaebwm.streamlit.app/

Run the Streamlit dashboard locally (opens http://localhost:8501):

```bash
streamlit run app.py
```

Notebook: run `pip install jupyter matplotlib seaborn`, then `jupyter notebook`.

## 👩‍💻 Author

Amira Farhan — Machine Learning & Computer Vision Engineer
