# ExamSlot | Smart Examination Scheduler

Graph-based examination timetable scheduling using greedy graph colouring.
A Streamlit app with the scheduling maths kept in plain, separate modules.

## Requirements

- Python 3.10 - 3.13 (Streamlit does not support 3.14 yet; this project ships a
  `.venv` built on Python 3.12).

## Install

```
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

(On macOS/Linux use `python3 -m venv .venv` and `.venv/bin/python`.)

## Run

```
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Then open the URL Streamlit prints (usually http://localhost:8501).

## Run just the algorithm (no UI)

```
py -3 scheduler.py
```

This prints the conflict graph, vertex degrees, greedy colouring and validation
using only the standard library.

## Files

| File | Job |
|---|---|
| sample_data.py | the 6-subject / 6-student sample dataset |
| graph_builder.py | set intersection -> conflict edges, adjacency list, degrees |
| scheduler.py | greedy graph colouring (degree order) -> slots |
| validator.py | independent re-check that no conflict shares a slot |
| app.py | Streamlit interface only |

## Note on optimality

Greedy colouring produces a valid timetable, not necessarily the minimum number
of slots. The app never claims the result is optimal.
