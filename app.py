# ExamSlot | Smart Examination Scheduler - Streamlit interface.
# The maths lives in graph_builder.py / scheduler.py / validator.py; this file
# only presents data and calls those modules.
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.patches import Patch
import networkx as nx
import streamlit as st

import graph_builder
import scheduler
import validator
from sample_data import SUBJECTS

# 3 examination slots per day; extra colours spill onto the next day.
SLOT_TIMES = ["09:00-12:00", "13:00-16:00", "16:30-19:30"]
SLOT_COLORS = ["#2563eb", "#16a34a", "#d97706", "#7c3aed", "#0891b2",
               "#db2777", "#dc2626", "#65a30d", "#4f46e5", "#ea580c"]
BRAND = "#2563eb"

st.set_page_config(page_title="ExamSlot", layout="wide")

CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Inter', system-ui, -apple-system, sans-serif; }
#MainMenu, footer { visibility: hidden; }
header[data-testid="stHeader"] { background: transparent; }
[data-testid="stToolbar"] { display: none; }
.stAppViewContainer header #MainMenu { visibility: hidden; }
button[data-testid="stToolbarActions"] { display: none; }
.block-container { padding-top: 1.3rem; padding-bottom: 2.5rem; }

.es-hero { background:#fff; border:1px solid #e2e8f0; border-left:6px solid #2563eb;
  border-radius:14px; padding:22px 26px; margin-bottom:16px; box-shadow:0 1px 2px rgba(15,23,42,.04); }
.es-hero h1 { font-size:26px; font-weight:800; color:#0f172a; margin:0; letter-spacing:-.02em; }
.es-hero p { margin:6px 0 0; color:#64748b; font-size:14.5px; }
.es-chips { margin-top:14px; display:flex; gap:8px; flex-wrap:wrap; }
.es-chip { font-size:12px; font-weight:600; color:#334155; background:#f1f5f9;
  border:1px solid #e2e8f0; border-radius:999px; padding:4px 12px; }

.es-kpi { background:#fff; border:1px solid #e2e8f0; border-radius:14px; padding:16px 18px;
  box-shadow:0 1px 2px rgba(15,23,42,.04); height:118px; }
.es-kpi .bar { height:4px; width:44px; border-radius:2px; margin-bottom:12px; }
.es-kpi .lbl { font-size:12px; font-weight:700; color:#64748b; text-transform:uppercase; letter-spacing:.05em; }
.es-kpi .val { font-size:30px; font-weight:800; color:#0f172a; margin-top:6px; line-height:1; }
.es-kpi .sub { font-size:12px; color:#94a3b8; margin-top:7px; }

.es-pill { display:inline-block; font-size:12.5px; font-weight:700; color:#fff;
  border-radius:999px; padding:3px 12px; }
.es-tag { display:inline-block; font-size:12px; font-weight:700; border-radius:6px; padding:2px 10px; }

.es-tbl { width:100%; border-collapse:separate; border-spacing:0; font-size:14px;
  border:1px solid #e2e8f0; border-radius:12px; overflow:hidden; }
.es-tbl th { background:#f1f5f9; color:#334155; font-weight:700; text-align:left;
  padding:11px 16px; border-bottom:1px solid #e2e8f0; font-size:12.5px; text-transform:uppercase; letter-spacing:.04em; }
.es-tbl td { padding:11px 16px; border-bottom:1px solid #f1f5f9; color:#0f172a; }
.es-tbl tr:last-child td { border-bottom:none; }

.stTabs [data-baseweb="tab-list"] { gap:4px; background:#f1f5f9; padding:6px;
  border-radius:12px; border:1px solid #e2e8f0; }
.stTabs [data-baseweb="tab"] { border-radius:8px; padding:8px 16px; font-weight:600; font-size:14px; color:#475569; }
.stTabs [aria-selected="true"] { background:#fff; color:#2563eb; box-shadow:0 1px 2px rgba(15,23,42,.08); }

.stButton>button { border-radius:10px; font-weight:600; border:1px solid #e2e8f0; padding:8px 18px; }
[data-testid="stDataFrame"] { border:1px solid #e2e8f0; border-radius:12px; }

.es-h { font-size:16px; font-weight:700; color:#0f172a; margin:4px 0 10px; }
.es-note { color:#64748b; font-size:13.5px; }
.es-ok { background:#ecfdf5; border:1px solid #a7f3d0; border-left:6px solid #16a34a;
  border-radius:12px; padding:14px 18px; color:#065f46; font-weight:700; }
.es-bad { background:#fef2f2; border:1px solid #fecaca; border-left:6px solid #dc2626;
  border-radius:12px; padding:14px 18px; color:#991b1b; font-weight:700; }

section[data-testid="stSidebar"] { background:#0f172a; }
section[data-testid="stSidebar"] * { color:#e2e8f0; font-family:'Inter',sans-serif; }
section[data-testid="stSidebar"] .stButton>button { background:#1e293b; color:#e2e8f0; border:1px solid #334155; }
.es-brand { font-size:21px; font-weight:800; color:#fff; letter-spacing:-.02em; }
.es-brand-sub { font-size:12.5px; color:#94a3b8; margin-top:3px; }
.es-sb-h { font-size:11px; font-weight:700; color:#64748b; text-transform:uppercase; letter-spacing:.08em; margin:18px 0 6px; }
.es-sb-row { display:flex; justify-content:space-between; font-size:13.5px; padding:3px 0; }
.es-sb-row span:last-child { font-weight:700; color:#fff; }
"""

st.markdown("<style>" + CSS + "</style>", unsafe_allow_html=True)


# ---------- state helpers ----------
def default_state():
    if "subjects" not in st.session_state:
        st.session_state.subjects = {k: sorted(v) for k, v in SUBJECTS.items()}
    if "generated" not in st.session_state:
        st.session_state.generated = False


def subjects():
    return {k: set(v) for k, v in st.session_state.subjects.items()}


def students_count(subs):
    return len({s for v in subs.values() for s in v})


def slot_label(color):
    day = (color - 1) // len(SLOT_TIMES) + 1
    t = SLOT_TIMES[(color - 1) % len(SLOT_TIMES)]
    return "Day %d, %s" % (day, t)


def slot_color(c):
    return SLOT_COLORS[(c - 1) % len(SLOT_COLORS)]


def pill(text, color):
    return '<span class="es-pill" style="background:%s">%s</span>' % (color, text)


def parse_students(text):
    return sorted({p.strip() for p in text.replace(";", ",").split(",") if p.strip()})


# ---------- graph drawing ----------
def draw_graph(subs, adj, color):
    G = nx.Graph()
    G.add_nodes_from(sorted(subs))
    for a, neighbours in adj.items():
        for b in neighbours:
            if a < b:
                G.add_edge(a, b)
    pos = nx.spring_layout(G, seed=42, k=1.9, scale=1.35)
    fig, ax = plt.subplots(figsize=(8.6, 5.2))
    fig.patch.set_facecolor("#ffffff")
    node_colors = [slot_color(color[n]) for n in G.nodes()]
    nx.draw_networkx_edges(G, pos, ax=ax, edge_color="#cbd5e1", width=1.4)
    nx.draw_networkx_nodes(G, pos, ax=ax, node_color=node_colors, node_size=3400,
                           edgecolors="white", linewidths=2.2)
    nx.draw_networkx_labels(G, pos, ax=ax, labels={n: str(color[n]) for n in G.nodes()},
                            font_color="white", font_weight="bold", font_size=13)
    label_pos = {n: (pos[n][0], pos[n][1] - 0.175) for n in G.nodes()}
    nx.draw_networkx_labels(G, label_pos, ax=ax, font_color="#0f172a", font_size=11,
                            bbox=dict(boxstyle="round,pad=0.18", fc="#ffffff", ec="#e2e8f0", alpha=0.92))
    ax.margins(0.16)
    ax.axis("off")
    slots = sorted(set(color.values()))
    handles = [Patch(facecolor=slot_color(s), label="Slot %d" % s) for s in slots]
    ax.legend(handles=handles, title="Examination slots", loc="upper left",
              fontsize=9, title_fontsize=9, frameon=True, facecolor="#f8fafc", edgecolor="#e2e8f0")
    fig.tight_layout()
    return fig


# ---------- compute ----------
default_state()
subs = subjects()
adj = graph_builder.adjacency(subs)
deg = graph_builder.degrees(adj)
pairs = graph_builder.conflicts(subs)
color = scheduler.greedy_color(adj)
n_slots = max(color.values()) if color else 0
ok, problems = validator.validate(subs, color)

# ---------- sidebar ----------
with st.sidebar:
    st.markdown('<div class="es-brand">ExamSlot</div>'
                '<div class="es-brand-sub">Smart Examination Scheduler</div>', unsafe_allow_html=True)
    st.markdown('<div class="es-sb-h">Current dataset</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="es-sb-row"><span>Subjects</span><span>%d</span></div>'
        '<div class="es-sb-row"><span>Students</span><span>%d</span></div>'
        '<div class="es-sb-row"><span>Conflicts</span><span>%d</span></div>'
        '<div class="es-sb-row"><span>Slots used</span><span>%d</span></div>'
        % (len(subs), students_count(subs), len(pairs), n_slots), unsafe_allow_html=True)
    st.markdown('<div class="es-sb-h">Status</div>', unsafe_allow_html=True)
    st.markdown('<div class="es-sb-row"><span>Timetable</span><span>%s</span></div>'
                % ("Valid" if ok else "Invalid"), unsafe_allow_html=True)
    st.markdown("---")
    if st.button("Reset to sample data", use_container_width=True):
        st.session_state.subjects = {k: sorted(v) for k, v in SUBJECTS.items()}
        st.session_state.generated = False
        st.rerun()
    st.markdown('<div class="es-sb-h">Method</div>', unsafe_allow_html=True)
    st.markdown('<div class="es-brand-sub">Greedy graph colouring on a conflict '
                'graph built from shared-student set intersections.</div>', unsafe_allow_html=True)

# ---------- hero ----------
st.markdown(
    '<div class="es-hero"><h1>ExamSlot</h1>'
    '<p>Graph-based examination timetable scheduling &mdash; turn enrolment data into a '
    'clash-free timetable using graph colouring.</p>'
    '<div class="es-chips">'
    '<span class="es-chip">Conflict graph</span>'
    '<span class="es-chip">Greedy colouring</span>'
    '<span class="es-chip">Independent validation</span>'
    '<span class="es-chip">Python &middot; Streamlit</span>'
    '</div></div>', unsafe_allow_html=True)

# ---------- KPI cards ----------
kpis = [("Subjects", len(subs), "vertices in the graph", BRAND),
        ("Students", students_count(subs), "shared across all sets", "#0891b2"),
        ("Conflicts", len(pairs), "pairs that share a student", "#d97706"),
        ("Slots", n_slots, "examination times needed", "#16a34a")]
cols = st.columns(4)
for col, (label, value, sub, accent) in zip(cols, kpis):
    col.markdown(
        '<div class="es-kpi"><div class="bar" style="background:%s"></div>'
        '<div class="lbl">%s</div><div class="val">%s</div><div class="sub">%s</div></div>'
        % (accent, label, value, sub), unsafe_allow_html=True)

# ---------- tabs ----------
dash, inp, conf, graph, timetable, val, algo = st.tabs(
    ["Overview", "Edit Data", "Conflicts", "Graph", "Timetable", "Validation", "Method"])

# 1. Overview
with dash:
    if not subs:
        st.warning("No subjects yet. Add one in the Edit Data tab.")
    st.markdown('<div class="es-h">How to read this dashboard</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="es-note">Each subject is a vertex. Two subjects are joined by an edge when they '
        'share at least one student, so they cannot sit in the same slot. The greedy colouring assigns '
        'the most connected subjects first, giving each the smallest free slot. The validator then '
        're-checks every conflict independently.</div>', unsafe_allow_html=True)
    st.markdown('<div class="es-h" style="margin-top:18px">Slot distribution</div>', unsafe_allow_html=True)
    groups = scheduler.by_slot(color)
    for c in sorted(groups):
        bar = "&nbsp;" * 1
        st.markdown(
            '%s&nbsp; <b>Slot %d</b> &middot; %s<br>'
            '<span class="es-note">%s</span>'
            % (pill(str(c), slot_color(c)), c, slot_label(c), ", ".join(groups[c])),
            unsafe_allow_html=True)
        st.write(bar)

# 2. Edit Data
with inp:
    st.markdown('<div class="es-h">Current dataset</div>', unsafe_allow_html=True)
    st.dataframe(
        [{"Subject": s, "Enrolled students": ", ".join(v), "Count": len(v)}
         for s, v in st.session_state.subjects.items()],
        width="stretch", hide_index=True)

    st.markdown('<div class="es-h" style="margin-top:18px">Add a subject</div>', unsafe_allow_html=True)
    a1, a2 = st.columns([1, 2])
    name = a1.text_input("Subject name", key="add_name")
    students = a2.text_input("Enrolled students (comma separated)", key="add_students")
    if st.button("Add subject", type="primary"):
        if not name.strip():
            st.error("Subject name cannot be empty.")
        elif name.strip() in st.session_state.subjects:
            st.error("That subject already exists.")
        elif not parse_students(students):
            st.error("Add at least one student.")
        else:
            st.session_state.subjects[name.strip()] = parse_students(students)
            st.session_state.generated = False
            st.rerun()

    st.markdown('<div class="es-h" style="margin-top:18px">Edit or remove</div>', unsafe_allow_html=True)
    col_a, col_b = st.columns(2)
    with col_a:
        target = st.selectbox("Subject", sorted(st.session_state.subjects), key="edit_target")
        new_students = st.text_input("Update student list", key="edit_students",
                                     value=", ".join(st.session_state.subjects.get(target, [])))
        if st.button("Update enrollment"):
            if parse_students(new_students):
                st.session_state.subjects[target] = parse_students(new_students)
                st.session_state.generated = False
                st.rerun()
            else:
                st.error("Need at least one student.")
    with col_b:
        st.write("")
        st.write("")
        if st.button("Remove subject"):
            st.session_state.subjects.pop(target, None)
            st.session_state.generated = False
            st.rerun()

# 3. Conflicts
with conf:
    st.markdown('<div class="es-h">Pairwise conflict detection</div>', unsafe_allow_html=True)
    rows = []
    keys = sorted(subs)
    for i in range(len(keys)):
        for j in range(i + 1, len(keys)):
            a, b = keys[i], keys[j]
            shared = sorted(subs[a] & subs[b])
            rows.append({"Subject A": a, "Subject B": b,
                         "Common students": ", ".join(shared) or "-",
                         "Conflict": "Yes" if shared else "No"})
    df = pd.DataFrame(rows)

    def _color_conflict(val):
        if val == "Yes":
            return "color:#dc2626;font-weight:700"
        return "color:#16a34a;font-weight:700"

    styled = df.style.map(_color_conflict, subset=["Conflict"])
    st.dataframe(styled, width="stretch", hide_index=True)
    st.markdown('<div class="es-note">%d of %d pairs conflict (share at least one student).</div>'
                % (len(pairs), len(rows)), unsafe_allow_html=True)

# 4. Graph
with graph:
    st.markdown('<div class="es-h">Conflict graph</div>', unsafe_allow_html=True)
    if subs:
        st.pyplot(draw_graph(subs, adj, color))
        st.markdown('<div class="es-note">The number inside each node is its examination slot; '
                    'the name below is the subject. An edge means the two subjects share a student.</div>',
                    unsafe_allow_html=True)
    else:
        st.info("Nothing to draw yet.")

# 5. Timetable
with timetable:
    if st.button("Generate examination timetable", type="primary"):
        st.session_state.generated = True
    if not st.session_state.generated:
        st.info("Click the button to schedule the examinations.")
    elif not subs:
        st.warning("Add at least one subject first.")
    else:
        head = ("<tr><th>Subject</th><th>Conflicts</th><th>Slot</th><th>Date &amp; time</th></tr>")
        body = ""
        for s in scheduler.order_by_degree(adj):
            body += ("<tr><td><b>%s</b></td><td>%d</td><td>%s</td><td>%s</td></tr>"
                     % (s, deg[s], pill("Slot %d" % color[s], slot_color(color[s])), slot_label(color[s])))
        st.markdown('<table class="es-tbl">%s%s</table>' % (head, body), unsafe_allow_html=True)

        st.markdown('<div class="es-h" style="margin-top:22px">Schedule by slot</div>', unsafe_allow_html=True)
        for c, members in sorted(scheduler.by_slot(color).items()):
            chips = "".join('<span class="es-chip">%s</span>&nbsp; ' % m for m in members)
            st.markdown('%s&nbsp; <b>%s</b><br>%s' % (pill("Slot %d" % c, slot_color(c)), slot_label(c), chips),
                        unsafe_allow_html=True)
            st.write("")

# 6. Validation
with val:
    st.markdown('<div class="es-h">Independent validation</div>', unsafe_allow_html=True)
    v1, v2 = st.columns(2)
    v1.markdown('<div class="es-kpi"><div class="bar" style="background:#d97706"></div>'
                '<div class="lbl">Conflicts checked</div><div class="val">%d</div>'
                '<div class="sub">every pair re-derived from the data</div></div>'
                % len(pairs), unsafe_allow_html=True)
    v2.markdown('<div class="es-kpi"><div class="bar" style="background:#16a34a"></div>'
                '<div class="lbl">Slots used</div><div class="val">%d</div>'
                '<div class="sub">no conflicting pair shares one</div></div>'
                % n_slots, unsafe_allow_html=True)
    st.write("")
    if ok:
        st.markdown('<div class="es-ok">Valid timetable &mdash; no two conflicting subjects share a slot.</div>',
                    unsafe_allow_html=True)
    else:
        st.markdown('<div class="es-bad">Invalid timetable &mdash; conflicting subjects share a slot.</div>',
                    unsafe_allow_html=True)
        for a, b, shared in problems:
            st.markdown('<div class="es-note">&bull; <b>%s</b> and <b>%s</b> (share %s) are both in slot %d.</div>'
                        % (a, b, ", ".join(shared), color[a]), unsafe_allow_html=True)

# 7. Method
with algo:
    st.markdown('<div class="es-h">How ExamSlot works</div>', unsafe_allow_html=True)
    steps = [
        ("Conflict graph", "Each subject is a vertex. Two subjects are joined by an edge when they share at "
         "least one student, i.e. when their student sets intersect. A shared student cannot sit two exams at "
         "once, so that pair cannot take the same slot."),
        ("Vertex degree", "The degree of a vertex is the number of subjects it conflicts with. Highly connected "
         "subjects are the hardest to place, so we schedule them first."),
        ("Greedy colouring", "Subjects are ordered by descending degree (alphabetical tie-break for a fixed "
         "result). Each subject takes the smallest slot number that none of its conflicting subjects already uses."),
        ("Slots = colours", "Because every edge connects two different colours, no two conflicting subjects ever "
         "land in the same slot. The validator re-checks this independently."),
    ]
    for i, (title, text) in enumerate(steps, 1):
        st.markdown(
            '<div style="display:flex;gap:14px;margin-bottom:14px">'
            '<div style="min-width:30px;height:30px;border-radius:50%%;background:#2563eb;color:#fff;'
            'font-weight:800;display:flex;align-items:center;justify-content:center;font-size:14px">%d</div>'
            '<div><b style="color:#0f172a">%s</b><div class="es-note">%s</div></div></div>'
            % (i, title, text), unsafe_allow_html=True)
    st.markdown('<div class="es-note" style="margin-top:8px"><b>Note:</b> greedy colouring always gives a valid '
                'timetable, but not necessarily the fewest possible slots. It never claims to be optimal.</div>',
                unsafe_allow_html=True)
