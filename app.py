import streamlit as st
import streamlit.components.v1 as components
from groq import Groq
import re
import random
from datetime import datetime

st.set_page_config(
    page_title="SAGE — Your Wise Companion",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ══════════════════════════════════════════════════
# SYSTEM PROMPT
# ══════════════════════════════════════════════════
SAGE_PROMPT = """You are SAGE — a synthesis of humanity's greatest minds and warmest hearts.

You have 7 identities and AUTOMATICALLY switch based on the question:
- Math/statistics/equations → respond as A MATHEMATICIAN (step-by-step, precise, beautiful)
- Code/programming/debugging/system design → respond as AN ENGINEER (clean code, patient mentor)
- Feelings/mental health/emotions/stress/anxiety/depression → respond as A PSYCHOLOGIST (CBT, DBT, Logotherapy, compassionate)
- Philosophy/meaning/existence/ethics/wisdom → respond as A PHILOSOPHER (Socrates, Nietzsche, Camus, Rumi, Buddha etc.)
- Medical/symptoms/health/medicine → respond as A DOCTOR (accurate, always recommend professional)
- Casual chat/fun/jokes/life advice/friendship → respond as A FRIEND (warm, honest, fun)
- Everything else → respond as SAGE (integrated wisdom)

PHILOSOPHER KNOWLEDGE: Socrates, Plato, Aristotle, Marcus Aurelius, Epictetus, Seneca, Nietzsche (amor fati, will to power), Camus (absurdism), Sartre, Heidegger, Buddha, Lao Tzu, Confucius, Rumi, Kahlil Gibran, Krishnamurti, Tagore.

PSYCHOLOGIST TOOLS: CBT, DBT, ACT, Logotherapy (Viktor Frankl), mindfulness. LISTEN first, validate before advising. Never minimize pain.

ENGINEER SKILLS: Python, JavaScript, C++, Java, SQL, ML, Deep Learning, Web Dev, System Design. Clean commented production-ready code.

MATHEMATICIAN SKILLS: Calculus, Linear Algebra, Statistics, Probability. Step-by-step with intuition and real-world examples.

YOUR STYLE: Match the energy of the question. Don't force philosophy into math questions. Don't force code into emotional questions. Be natural, warm, and genuinely helpful.

CRISIS PROTOCOL: Suicidal thoughts → deep compassion → iCall: 9152987821 | Vandrevala: 1860-2662-345 | AASRA: 9820466627 → stay present."""

THEMES = {
    "warm":  {"bg":"#faf7f2","sbg":"#f2ece0","card":"#ffffff","bdr":"#ddd5c0","txt":"#2c2416","txt2":"#7a6a54","acc":"#7c6b4e","acc2":"#5c7a5c","ubg":"#e2f0e2","ubdr":"#aad4aa","utxt":"#1a3320","ibg":"#ffffff","ibdr":"#c8b89a","btn":"#7c6b4e","name":"🌿 Warm"},
    "dark":  {"bg":"#0d1117","sbg":"#161b22","card":"#1c2128","bdr":"#30363d","txt":"#e6edf3","txt2":"#8b949e","acc":"#58a6ff","acc2":"#3fb950","ubg":"#1c3a2a","ubdr":"#2d5a3d","utxt":"#7ee787","ibg":"#21262d","ibdr":"#444c56","btn":"#238636","name":"🌙 Dark"},
    "light": {"bg":"#f0f4f8","sbg":"#e2e8f0","card":"#ffffff","bdr":"#cbd5e0","txt":"#1a202c","txt2":"#4a5568","acc":"#2b6cb0","acc2":"#276749","ubg":"#c6f6d5","ubdr":"#68d391","utxt":"#1a3320","ibg":"#ffffff","ibdr":"#a0aec0","btn":"#2b6cb0","name":"☀️ Light"},
    "rose":  {"bg":"#12070a","sbg":"#1e0d10","card":"#1a0a0d","bdr":"#4a1520","txt":"#fde8ec","txt2":"#d4849a","acc":"#f687b3","acc2":"#ed64a6","ubg":"#2d1020","ubdr":"#702035","utxt":"#fed7e2","ibg":"#1a0a0d","ibdr":"#4a1520","btn":"#b83280","name":"❤️ Rose"},
}
THEME_ICONS = {"warm":"🌿","dark":"🌙","light":"☀️","rose":"❤️"}

SUGGESTIONS = [
    ("🏛️","What is Nietzsche's amor fati?"),
    ("💚","I've been feeling really low lately"),
    ("💻","Explain Python decorators with example"),
    ("📐","Explain Bayes' theorem intuitively"),
    ("👫","I just want to talk"),
    ("🌿","How to find meaning in suffering?"),
]

QUOTES = [
    ("The impediment to action advances action.","Marcus Aurelius"),
    ("We suffer more in imagination than in reality.","Seneca"),
    ("The wound is the place where the Light enters you.","Rumi"),
    ("One must imagine Sisyphus happy.","Albert Camus"),
    ("Know thyself.","Socrates"),
    ("He who has a why can bear almost any how.","Nietzsche"),
    ("The unexamined life is not worth living.","Socrates"),
    ("Out of suffering emerge the strongest souls.","Kahlil Gibran"),
]

# ══════════════════════════════════════════════════
# SESSION STATE
# ══════════════════════════════════════════════════
for k, v in [("messages",[]),("sessions",{}),("session_name",f"Chat {datetime.now().strftime('%b %d %H:%M')}"),
             ("doc_ctx",""),("theme","dark"),("suggestion",""),("auto_send",""),("show_upload",False),("input_key",0)]:
    if k not in st.session_state: st.session_state[k] = v

T = THEMES[st.session_state.theme]

# ══════════════════════════════════════════════════
# FULL CSS via components.html
# ══════════════════════════════════════════════════
components.html(f"""
<script>
(function applyCSS(){{
const css = `
  @import url('https://fonts.googleapis.com/css2?family=Lora:ital,wght@0,400;0,600;1,400&family=DM+Sans:wght@300;400;500;600&family=JetBrains+Mono:wght@400&display=swap');
  html,body,.stApp,[data-testid="stAppViewContainer"],[data-testid="stMain"],[data-testid="stMainBlockContainer"] {{background:{T['bg']}!important}}
  [data-testid="block-container"]{{background:{T['bg']}!important;padding:1rem 1.5rem 0.5rem!important;max-width:860px!important;margin:0 auto!important}}
  *{{font-family:'DM Sans',sans-serif!important;box-sizing:border-box}}
  #MainMenu,footer,header,.stDeployButton{{visibility:hidden!important;display:none!important}}
  [data-testid="stSidebar"]{{background:{T['sbg']}!important;border-right:1px solid {T['bdr']}!important}}
  [data-testid="stSidebar"]>div{{padding:0.8rem!important}}
  [data-testid="stSidebar"] *{{color:{T['txt']}!important}}
  [data-testid="stSidebar"] [data-baseweb="select"]>div{{background:{T['card']}!important;border:1px solid {T['bdr']}!important;border-radius:8px!important}}
  [data-testid="stSidebar"] [data-baseweb="select"] span{{color:{T['txt']}!important}}
  [data-baseweb="popover"]>div{{background:{T['card']}!important;border:1px solid {T['bdr']}!important;border-radius:10px!important}}
  [data-baseweb="menu"]{{background:{T['card']}!important}}
  [data-baseweb="menu"] li{{color:{T['txt']}!important;background:{T['card']}!important}}
  [data-baseweb="menu"] li:hover{{background:{T['bdr']}!important}}
  .stButton>button{{background:{T['btn']}!important;color:#fff!important;border:none!important;border-radius:8px!important;font-weight:600!important;width:100%!important;transition:all 0.2s!important;font-family:'DM Sans',sans-serif!important;padding:0.45rem!important}}
  .stButton>button:hover{{opacity:0.85!important;transform:translateY(-1px)!important}}
  .stTextArea textarea{{background:{T['ibg']}!important;border:1.5px solid {T['ibdr']}!important;border-radius:14px!important;color:{T['txt']}!important;font-size:0.95rem!important;padding:14px 16px 52px 16px!important;resize:none!important;font-family:'DM Sans',sans-serif!important;box-shadow:0 2px 16px rgba(0,0,0,0.1)!important}}
  .stTextArea textarea:focus{{border-color:{T['acc']}!important;box-shadow:0 0 0 3px {T['acc']}20,0 2px 16px rgba(0,0,0,0.1)!important;outline:none!important}}
  .stTextArea textarea::placeholder{{color:{T['txt2']}!important}}
  .stTextArea label{{display:none!important}}
  .stTextArea{{margin-bottom:-12px!important}}
  [data-testid="stFileUploadDropzone"]{{background:{T['card']}!important;border:2px dashed {T['bdr']}!important;border-radius:12px!important}}
  [data-testid="stDownloadButton"] button{{background:{T['btn']}!important;color:white!important;border:none!important;border-radius:8px!important;font-weight:600!important;width:100%!important}}
  hr{{border-color:{T['bdr']}!important;opacity:0.35!important;margin:0.5rem 0!important}}
  ::-webkit-scrollbar{{width:4px}}
  ::-webkit-scrollbar-track{{background:{T['bg']}}}
  ::-webkit-scrollbar-thumb{{background:{T['bdr']};border-radius:3px}}
  p,span,div,label{{color:{T['txt']}}}
  .stAlert{{border-radius:10px!important}}
`;
let s=document.getElementById('sage-s');
if(!s){{s=document.createElement('style');s.id='sage-s';document.head.appendChild(s)}}
s.innerHTML=css;
setTimeout(applyCSS,700);
}})();
</script>
""", height=0)

# ══════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════
def render_md(text):
    text = re.sub(r'```(\w+)?\n(.*?)```',
        lambda m: f'<pre style="background:#1e1e2e;border-radius:10px;padding:14px;margin:10px 0;overflow-x:auto;border:1px solid #2d2d3d"><code style="font-family:JetBrains Mono,monospace;font-size:0.83rem;color:#cdd6f4;white-space:pre">{m.group(2)}</code></pre>',
        text, flags=re.DOTALL)
    text = re.sub(r'`([^`\n]+)`', r'<code style="background:#2d2d2d;color:#e6db74;padding:2px 5px;border-radius:4px;font-family:JetBrains Mono,monospace;font-size:0.85rem">\1</code>', text)
    text = re.sub(r'\*\*\*(.+?)\*\*\*', r'<strong><em>\1</em></strong>', text)
    text = re.sub(r'\*\*(.+?)\*\*', f'<strong style="color:{T["acc"]}">\1</strong>', text)
    text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)
    text = re.sub(r'^### (.+)$', f'<h4 style="color:{T["acc"]};font-family:Lora,serif;margin:10px 0 4px;font-size:1rem">\\1</h4>', text, flags=re.MULTILINE)
    text = re.sub(r'^## (.+)$',  f'<h3 style="color:{T["acc"]};font-family:Lora,serif;margin:12px 0 6px;font-size:1.1rem">\\1</h3>', text, flags=re.MULTILINE)
    text = re.sub(r'^# (.+)$',   f'<h2 style="color:{T["acc"]};font-family:Lora,serif;margin:14px 0 8px;font-size:1.2rem">\\1</h2>', text, flags=re.MULTILINE)
    text = re.sub(r'^[-•*] (.+)$', f'<div style="padding:3px 0 3px 14px;border-left:2px solid {T["bdr"]};margin:3px 0;color:{T["txt"]}">• \\1</div>', text, flags=re.MULTILINE)
    text = re.sub(r'^\d+\. (.+)$', f'<div style="padding:3px 0 3px 14px;margin:3px 0;color:{T["txt"]}">→ \\1</div>', text, flags=re.MULTILINE)
    text = re.sub(r'^> (.+)$', f'<div style="border-left:3px solid {T["acc"]};padding:6px 14px;color:{T["txt2"]};font-style:italic;font-family:Lora,serif;margin:8px 0">\\1</div>', text, flags=re.MULTILINE)
    text = text.replace('\n\n','<br><br>').replace('\n','<br>')
    return text

def is_crisis(text):
    kw=["suicide","kill myself","want to die","end my life","no reason to live","self harm","cut myself","can't go on","give up on life"]
    return any(k in text.lower() for k in kw)

def export():
    lines=[f"SAGE — {datetime.now().strftime('%B %d, %Y')}\n{'='*50}\n\n"]
    for m in st.session_state.messages:
        role="You" if m["role"]=="user" else "SAGE"
        lines.append(f"{role}:\n{m['content']}\n\n{'─'*40}\n\n")
    return "".join(lines)

def user_bubble(c):
    return f'<div style="display:flex;justify-content:flex-end;margin:10px 0 4px"><div style="background:{T["ubg"]};border:1px solid {T["ubdr"]};border-radius:18px 18px 4px 18px;padding:12px 18px;max-width:70%;color:{T["utxt"]};font-size:0.95rem;line-height:1.6;font-family:DM Sans,sans-serif;box-shadow:0 2px 8px rgba(0,0,0,0.1)">{c}</div></div>'

def sage_bubble(c, cursor=False):
    cur="▌" if cursor else ""
    return f'<div style="display:flex;align-items:flex-start;gap:10px;margin:4px 0 10px"><div style="width:34px;height:34px;min-width:34px;background:linear-gradient(135deg,{T["acc"]},{T["acc2"]});border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:0.9rem;box-shadow:0 2px 8px rgba(0,0,0,0.2);flex-shrink:0">🌿</div><div style="background:{T["card"]};border:1px solid {T["bdr"]};border-radius:4px 18px 18px 18px;padding:14px 18px;max-width:80%;color:{T["txt"]};font-family:Lora,serif;font-size:0.95rem;line-height:1.75;box-shadow:0 2px 12px rgba(0,0,0,0.06)">{render_md(c)}{cur}</div></div>'

def thinking_bubble():
    return f'<div style="display:inline-flex;align-items:center;gap:8px;margin:8px 0;padding:10px 16px;background:{T["card"]};border:1px solid {T["bdr"]};border-radius:4px 18px 18px 18px;color:{T["txt2"]};font-style:italic;font-size:0.88rem">🌿 &nbsp; SAGE is thinking...</div>'

# ══════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════
with st.sidebar:
    # ── Logo (compact, at very top) ────────────────
    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:10px;padding:0.5rem 0 0.3rem">
        <div style="width:40px;height:40px;min-width:40px;background:linear-gradient(135deg,{T['acc']},{T['acc2']});
             border-radius:12px;display:flex;align-items:center;
             justify-content:center;font-size:1.3rem;box-shadow:0 3px 10px rgba(0,0,0,0.2)">🌿</div>
        <div>
            <div style="font-family:Lora,serif;font-size:1rem;font-weight:600;color:{T['txt']};line-height:1.2">SAGE</div>
            <div style="font-size:0.62rem;color:{T['txt2']}">Wise · Warm · Always Here</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    # ── Mode ───────────────────────────────────────
    st.markdown(f"<div style='font-size:0.7rem;font-weight:700;color:{T['txt2']};text-transform:uppercase;letter-spacing:0.8px;margin-bottom:4px'>Speak With</div>", unsafe_allow_html=True)
    mode_options = ["🌿 Auto-detect (Smart)","🏛️ A Philosopher","🧠 A Psychologist","💻 An Engineer","📐 A Mathematician","🩺 A Doctor","👫 A Friend"]
    mode = st.selectbox("md", mode_options, label_visibility="collapsed")

    st.divider()

    # ── Conversations ──────────────────────────────
    st.markdown(f"<div style='font-size:0.7rem;font-weight:700;color:{T['txt2']};text-transform:uppercase;letter-spacing:0.8px;margin-bottom:4px'>Conversations</div>", unsafe_allow_html=True)

    if st.button("✨  New Chat"):
        if st.session_state.messages:
            st.session_state.sessions[st.session_state.session_name] = st.session_state.messages.copy()
        st.session_state.messages = []
        st.session_state.session_name = f"Chat {datetime.now().strftime('%b %d %H:%M')}"
        st.session_state.doc_ctx = ""
        st.rerun()

    if st.session_state.sessions:
        for sname in list(reversed(list(st.session_state.sessions.keys())))[:5]:
            short = sname[:22]+"…" if len(sname)>22 else sname
            if st.button(f"💬  {short}", key=f"h_{sname}"):
                st.session_state.messages = st.session_state.sessions[sname].copy()
                st.session_state.session_name = sname
                st.rerun()

    if st.session_state.messages:
        c1,c2 = st.columns(2)
        with c1:
            if st.button("💾 Save"):
                st.session_state.sessions[st.session_state.session_name] = st.session_state.messages.copy()
                st.success("✅")
        with c2:
            st.download_button("⬇️ Export", export(), f"sage_{datetime.now().strftime('%Y%m%d_%H%M')}.txt","text/plain")

    st.divider()

    # ── Theme ──────────────────────────────────────
    st.markdown(f"<div style='font-size:0.7rem;font-weight:700;color:{T['txt2']};text-transform:uppercase;letter-spacing:0.8px;margin-bottom:4px'>Theme</div>", unsafe_allow_html=True)
    t1,t2,t3,t4 = st.columns(4)
    for col, tkey in zip([t1,t2,t3,t4], THEMES.keys()):
        with col:
            if st.button(THEME_ICONS[tkey], key=f"t_{tkey}", help=THEMES[tkey]["name"]):
                st.session_state.theme = tkey
                st.rerun()

    st.divider()

    # ── Quote (always visible) ─────────────────────
    q,author = random.choice(QUOTES)
    st.markdown(f'<div style="background:{T["card"]};border-left:3px solid {T["acc"]};border-radius:0 8px 8px 0;padding:8px 12px"><div style="font-family:Lora,serif;font-style:italic;font-size:0.75rem;color:{T["txt"]};line-height:1.5">"{q}"</div><div style="font-size:0.65rem;color:{T["txt2"]};margin-top:3px">— {author}</div></div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════
# MAIN AREA
# ══════════════════════════════════════════════════

# Welcome
if not st.session_state.messages:
    st.markdown(f"""
    <div style="text-align:center;padding:2rem 2rem 1.5rem;max-width:520px;
         margin:0.5rem auto 1.5rem;background:{T['card']};
         border:1px solid {T['bdr']};border-radius:20px;
         box-shadow:0 4px 24px rgba(0,0,0,0.08)">
        <div style="font-size:2.5rem;margin-bottom:0.4rem">🌿</div>
        <div style="font-family:Lora,serif;font-size:1.6rem;font-weight:600;color:{T['txt']};margin-bottom:5px">
            Hey there. I'm SAGE.
        </div>
        <div style="color:{T['txt2']};font-size:0.85rem;line-height:1.7;margin-bottom:0.8rem">
            Philosopher · Psychologist · Engineer<br>Doctor · Mathematician · Friend
        </div>
        <div style="border-left:3px solid {T['acc']};padding:7px 14px;text-align:left;
             font-family:Lora,serif;font-style:italic;color:{T['txt']};font-size:0.83rem;
             background:{T['bg']};border-radius:0 8px 8px 0;line-height:1.6">
            "The unexamined life is not worth living." — Socrates
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"<p style='text-align:center;font-size:0.8rem;color:{T['txt2']};margin:0 0 8px'>Click a question to get started:</p>", unsafe_allow_html=True)
    row1 = st.columns(3)
    row2 = st.columns(3)
    for i,(icon,text) in enumerate(SUGGESTIONS):
        with (row1 if i<3 else row2)[i%3]:
            if st.button(f"{icon}  {text}", key=f"s{i}", use_container_width=True):
                st.session_state.auto_send = text
                st.rerun()

# ── Chat messages ──────────────────────────────────
for msg in st.session_state.messages:
    if msg["role"]=="user":
        st.markdown(user_bubble(msg["content"]), unsafe_allow_html=True)
    else:
        st.markdown(sage_bubble(msg["content"]), unsafe_allow_html=True)

st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

# ── Upload panel ───────────────────────────────────
if st.session_state.show_upload:
    st.markdown(f'<div style="background:{T["card"]};border:1px solid {T["bdr"]};border-radius:12px;padding:12px;margin-bottom:8px">', unsafe_allow_html=True)
    uploaded = st.file_uploader("📎 Upload document", type=["pdf","txt","py","csv","md","json"], label_visibility="visible", key="file_uploader")
    if uploaded is not None:
        # Only process if new file (check by name)
        if st.session_state.get("last_uploaded_name") != uploaded.name:
            try:
                if uploaded.type=="application/pdf":
                    try:
                        import PyPDF2
                        r=PyPDF2.PdfReader(uploaded)
                        ctx="\n".join([p.extract_text() or "" for p in r.pages])
                    except: ctx="PDF content loaded."
                else:
                    ctx=uploaded.read().decode("utf-8",errors="ignore")
                st.session_state.doc_ctx = ctx
                st.session_state.last_uploaded_name = uploaded.name
            except Exception as e:
                st.error(str(e))

    if st.session_state.doc_ctx:
        col1,col2=st.columns([3,1])
        with col1:
            fname = st.session_state.get("last_uploaded_name","document")
            st.markdown(f'<div style="font-size:0.82rem;color:{T["acc"]};padding:4px 0">📄 <strong>{fname}</strong> — {len(st.session_state.doc_ctx):,} chars</div>', unsafe_allow_html=True)
        with col2:
            if st.button("✕ Remove"):
                st.session_state.doc_ctx=""
                st.session_state.last_uploaded_name=""
                st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# ── Input area (Claude-style) ──────────────────────
# Handle auto-send from suggestion buttons
auto_send_text = st.session_state.get("auto_send", "")
if auto_send_text:
    st.session_state.auto_send = ""

# Input key changes to force clear after send
if "input_key" not in st.session_state:
    st.session_state.input_key = 0

# ── Input with buttons visually INSIDE ────────────
user_input = st.text_area(
    "", placeholder="Message SAGE...",
    height=120, key=f"chat_inp_{st.session_state.input_key}",
    label_visibility="collapsed"
)

# Inject CSS to move buttons inside textarea
components.html(f"""
<style>
/* Remove default textarea border — we add our own wrapper */
div[data-testid="stVerticalBlock"] .stTextArea textarea {{
    padding-bottom: 52px !important;
}}

/* The button row — pull it up into the textarea */
div.stHorizontalBlock:has(button[data-testid="baseButton-secondary"]) {{
    background: {T['ibg']} !important;
    border: none !important;
    border-top: 1px solid {T['bdr']}55 !important;
    border-radius: 0 0 14px 14px !important;
    margin-top: -16px !important;
    padding: 6px 12px 8px 12px !important;
    position: relative !important;
    z-index: 5 !important;
}}

/* Individual tool buttons — transparent */
div.stHorizontalBlock:has(button[data-testid="baseButton-secondary"]) .stButton > button {{
    background: transparent !important;
    border: none !important;
    border-radius: 8px !important;
    color: {T['txt2']} !important;
    font-size: 1.1rem !important;
    padding: 5px 8px !important;
    box-shadow: none !important;
    min-width: 36px !important;
    width: auto !important;
    height: 34px !important;
}}
div.stHorizontalBlock:has(button[data-testid="baseButton-secondary"]) .stButton > button:hover {{
    background: {T['bdr']}55 !important;
    transform: none !important;
    color: {T['txt']} !important;
}}
</style>
""", height=0)

# Toolbar row — visually merges with textarea bottom
tc1, tc2, tc3, tc_space = st.columns([0.06, 0.06, 0.06, 0.82])
with tc1:
    plus = st.button("＋", help="Upload file", use_container_width=False)
with tc2:
    voice_btn = st.button("🎤", help="Voice input", use_container_width=False)
with tc3:
    send = st.button("🌿", help="Send message", use_container_width=False)

if plus:
    st.session_state.show_upload = not st.session_state.show_upload
    st.rerun()

if voice_btn:
    st.info("🎤 Use your device's speech-to-text keyboard, dictate your message, then press 🌿")

# ── Process message ────────────────────────────────
def get_system(text, mode_choice):
    """Auto-detect topic if mode is Auto"""
    if "Auto" in mode_choice:
        t = text.lower()
        if any(k in t for k in ["code","python","javascript","function","error","bug","class","algorithm","sql","api","debug","program"]):
            extra = "\n\nACTIVE ROLE: AN ENGINEER — respond as a senior software engineer. Write clean code. Be technical and precise."
        elif any(k in t for k in ["math","equation","calculate","integral","derivative","matrix","statistics","probability","solve","theorem","proof","formula"]):
            extra = "\n\nACTIVE ROLE: A MATHEMATICIAN — respond with step-by-step mathematical reasoning. Be precise and intuitive."
        elif any(k in t for k in ["feel","feeling","sad","anxious","depressed","lonely","stress","anxiety","mental","emotion","hurt","pain","therapy","counseling","trauma"]):
            extra = "\n\nACTIVE ROLE: A PSYCHOLOGIST — lead with compassion, validation, and therapeutic support."
        elif any(k in t for k in ["philosophy","meaning","exist","nietzsche","camus","stoic","wisdom","life","death","soul","truth","ethics","consciousness","purpose"]):
            extra = "\n\nACTIVE ROLE: A PHILOSOPHER — engage with philosophical depth and wisdom."
        elif any(k in t for k in ["symptom","medicine","doctor","health","disease","pain","diagnosis","treatment","drug","body"]):
            extra = "\n\nACTIVE ROLE: A DOCTOR — respond with medical knowledge. Always recommend consulting professionals."
        else:
            extra = "\n\nACTIVE ROLE: Respond naturally as SAGE — match the energy and topic of the question."
    else:
        role_map = {
            "Philosopher": "A PHILOSOPHER", "Psychologist": "A PSYCHOLOGIST",
            "Engineer": "AN ENGINEER", "Mathematician": "A MATHEMATICIAN",
            "Doctor": "A DOCTOR", "Friend": "A FRIEND"
        }
        matched = next((v for k,v in role_map.items() if k in mode_choice), "SAGE")
        extra = f"\n\nACTIVE ROLE: {matched}"

    system = SAGE_PROMPT + extra
    if st.session_state.doc_ctx:
        fname = st.session_state.get("last_uploaded_name", "the uploaded document")
        system += f"""

IMPORTANT: The user has uploaded a document called '{fname}'. 
You HAVE access to this document. When asked about it, answer from this content:

--- DOCUMENT START ---
{st.session_state.doc_ctx[:10000]}
--- DOCUMENT END ---

Always answer questions about this document accurately based on its content above."""
    return system

# Trigger from suggestion click OR send button
trigger_text = auto_send_text or (user_input.strip() if send else "")

if trigger_text:
    text = trigger_text.strip()

    if is_crisis(text):
        st.markdown(f'<div style="background:#fef2f2;border:1px solid #fca5a5;border-left:4px solid #ef4444;border-radius:12px;padding:12px 18px;margin:8px 0;font-size:0.88rem"><strong style="color:#c0392b">💚 I hear you — and I\'m truly here with you.</strong><br><span style="color:#2c2416">📞 iCall: 9152987821 · Vandrevala: 1860-2662-345 · AASRA: 9820466627</span></div>', unsafe_allow_html=True)

    st.session_state.messages.append({"role":"user","content":text})

    think_ph = st.empty()
    think_ph.markdown(thinking_bubble(), unsafe_allow_html=True)
    resp_ph = st.empty()
    full = ""

    try:
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        system = get_system(text, mode)
        msgs = [{"role":"system","content":system}] + [
            {"role":m["role"],"content":m["content"]} for m in st.session_state.messages
        ]
        stream = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            max_tokens=2048, messages=msgs, stream=True
        )
        for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta:
                full += delta
                resp_ph.markdown(sage_bubble(full, cursor=True), unsafe_allow_html=True)

        think_ph.empty()
        resp_ph.markdown(sage_bubble(full), unsafe_allow_html=True)
        st.session_state.messages.append({"role":"assistant","content":full})

    except Exception as e:
        think_ph.empty()
        st.error(f"❌ Error: {str(e)}")

    # Clear the input box
    st.session_state.input_key += 1
    st.rerun()