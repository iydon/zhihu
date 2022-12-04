PYTHON = python


.PHONY: app


app:
	$(PYTHON) -m streamlit run app.py
