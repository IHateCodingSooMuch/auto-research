# Automated Research Workflow


Type a topic; get a planned, sourced research dossier in `research/<year>/<slug>/`.


## Run locally


```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python scripts/research.py "heat pumps in cold climates" --max-sources 10 --depth 2
