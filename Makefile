setup:
pip install -r requirements.txt

lint:
ruff advisor_chat tests

test:
pytest -q

run:
streamlit run app.py
