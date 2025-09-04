PY=python3

.PHONY: refresh app refresh-fred refresh-skills refresh-metrics

# Full refresh pipeline
refresh: refresh-fred refresh-skills refresh-metrics

# Individual refresh targets for modularity
refresh-fred:
	$(PY) -m src.sources.fred

refresh-skills:
	-$(PY) -m src.sources.lightcast_open_skills

refresh-metrics:
	$(PY) -m src.transforms.build_market_metrics

app:
	$(PY) -m streamlit run app/Home.py

app-classic:
	$(PY) -m streamlit run app/streamlit_app.py
