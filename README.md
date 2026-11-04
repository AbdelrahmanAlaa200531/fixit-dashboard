# FixIt Services Performance Dashboard

A Streamlit dashboard for the supplied FixIt Services dataset. It includes date, time-of-day, and client-type filters; revenue and ad-spend trends; customer mix; and comparisons by time of day.

## Run locally

```bash
python -m venv .venv
```

Activate the environment, then install dependencies and launch:

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Publish with Streamlit Community Cloud

1. Create a GitHub repository and upload `app.py`, `data.csv`, and `requirements.txt` from this folder.
2. In Streamlit Community Cloud, connect the GitHub repository, select `app.py` as the app file, and deploy.
3. Keep the repository private if the source data or technician names should not be public. Confirm repository and app visibility before sharing the app URL.

## Metric definitions and source limitations

- **Ad ROAS** = revenue ÷ ad spend. It is a marketing-efficiency proxy, not profit or ROI after all costs.
- **Returning + loyal share** = share of rows labeled `Returning` or `Loyal`. There is no client ID or visit history to calculate true retention or churn probability.
- **Revenue less ad spend** excludes labor, parts, service delivery, and overhead costs. It is not net profit.
- The file contains no marketing-channel column. Time-of-day results are not channel results.
- The source has 2,000 rows, 842 distinct service-category labels, and 462 technician names. Check the source taxonomy and confirm data-sharing permissions before publishing.
