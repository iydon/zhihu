PYTHON = python


.PHONY: app


app:
	$(PYTHON) -m streamlit run script/app.py
