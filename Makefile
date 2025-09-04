PY=python

.PHONY: refresh app fmt

refresh:
	$(PY) -m src.sources.fred
	$(PY) -m src.sources.lightcast_open_skills
	$(PY) -m src.transforms.build_market_metrics

app:
	$(PY) -m streamlit run app/streamlit_app.py
