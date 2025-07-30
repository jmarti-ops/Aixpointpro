# Aixpointpro – Logical Equity Distribution for Startups

This project provides a Streamlit app to calculate partner shares and investor participation in a startup. The interface lets you weigh different contribution blocks, lock percentages for each partner and compute the impact of external investors.

## Main Features

- Weighted distribution by block:
  - Concept, Idea and Foundational IP
  - Initial Economic Investment
  - Operations and Management
  - Strategy, Direction and Marketing
- Locked percentage per partner
- Interactive pie chart visualization
- Investor participation calculator
- Export results to CSV
- Data stored in `session_data.json` with a sidebar option to clear saved values

## Technologies

- Python
- Streamlit
- Pandas
- Matplotlib
- XlsxWriter

## Running locally

```bash
# Clone the repo
git clone <repo-url>
cd Aixpointpro

# Install dependencies
pip install -r requirements.txt

# Launch the app
streamlit run app_reparto_full.py
```

## Deploying on Streamlit Cloud

1. Open [Streamlit Cloud](https://share.streamlit.io/) and choose **New app**.
2. Point to this repository and set `streamlit_app.py` as the main file.
3. The application will start automatically once the requirements are installed.

## Project Structure

```
Aixpointpro/
├── app_reparto_full.py  # main Streamlit application
├── streamlit_app.py     # entry point used by Streamlit Cloud
├── Calculadora socisV2.py
├── app.py
├── app2.py
├── requirements.txt
└── .streamlit/
    └── config.toml
```

---

Developed by Jordi Martí.
