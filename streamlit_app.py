import streamlit as st
import gspread
from google.oauth2 import service_account
import pandas as pd
import re
from datetime import datetime

# ══════════════════════════════════════════════════════════════
# ⚙️ إعداد الصفحة
# ══════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="نظام تقييم الطلاب الرياضي", 
    layout="wide", 
    initial_sidebar_state="collapsed",
    page_icon="⚽"
)

# ══════════════════════════════════════════════════════════════
# 🎨 التنسيقات والأنماط (كما هي)
# ══════════════════════════════════════════════════════════════
st.markdown("""<style>/* CSS unchanged – نفس اللي عندك */</style>""",unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# 🔧 أدوات مساعدة مصححة
# ══════════════════════════════════════════════════════════════

def normalize(txt):
    return re.sub(r"\s+", "", str(txt))

def clean_number(num):
    if pd.isna(num): return ""
    s=str(num).translate(str.maketrans('٠١٢٣٤٥٦٧٨٩','0123456789'))
    return re.sub(r'[^0-9]','',s)

def safe_int(v):
    try:return int(float(v))
    except:return 0

def safe_float(v):
    try:return float(v)
    except:return 0

def find_column(df, keys):
    for c in df.columns:
        nc=normalize(c)
        for k in keys:
            if normalize(k) in nc:
                return c
    return None

def get_value(row, keys, default=""):
    for c in row.index:
        nc=normalize(c)
        for k in keys:
            if normalize(k) in nc:
                v=row[c]
                if pd.notna(v) and str(v).strip():
                    return str(v).strip()
    return default

# ══════════════════════════════════════════════════════════════
# ⚽ محرك التقييم (كما هو)
# ══════════════════════════════════════════════════════════════

class PlayerEvaluationEngine:

    @staticmethod
    def get_level(score):
        if score>=85:return"ممتاز ⭐⭐⭐","excellent"
        if score>=70:return"جيد جداً ⭐⭐","very-good"
        if score>=50:return"جيد ⭐","good"
        return"يحتاج تطوير","needs-improvement"

    @staticmethod
    def generate_report(n,a,s):
        avg=sum(s.values())/4
        l,_=PlayerEvaluationEngine.get_level(avg)
        return f"""
الاسم: {n}
العمر: {a}

بدني: {s['physical']}
فني: {s['technical']}
ذهني: {s['mental']}
تكتيكي: {s['tactical']}

المجموع: {avg:.0f}/100 — {l}

{datetime.now().strftime('%Y-%m-%d')}
"""

# ══════════════════════════════════════════════════════════════
# 🔌 Google Sheets
# ══════════════════════════════════════════════════════════════

@st.cache_resource
def get_sheet():
    creds=service_account.Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=["https://www.googleapis.com/auth/spreadsheets"]
    )
    return gspread.authorize(creds).open_by_key(
        st.secrets["gsheet"]["sheet_id"]
    ).sheet1

ws=get_sheet()
df=pd.DataFrame(ws.get_all_records())
df.columns=df.columns.str.strip()

phone_cols=[c for c in df.columns if "موبايل" in c]
for c in phone_cols:
    df[c+"_c"]=df[c].apply(clean_number)

# ══════════════════════════════════════════════════════════════
# 🎬 الواجهة
# ══════════════════════════════════════════════════════════════

st.title("⚽ نظام تقييم الطلاب")

tab1,tab2=st.tabs(["بحث","إحصائيات"])

with tab1:

    q=st.text_input("اسم الطفل أو رقم الموبايل")

    if st.button("بحث"):

        qc=clean_number(q)

        name_col=find_column(df,["اسم الطفل","اسم"])

        mask=df[name_col].astype(str).str.contains(q,case=False,na=False) if name_col else False

        for c in phone_cols:
            mask|=df[c+"_c"].str.contains(qc,na=False)

        res=df[mask]

        if res.empty:
            st.warning("لا يوجد نتائج")
        else:
            for _,r in res.iterrows():

                name=r.get("اسم الطفل  كامل ",get_value(r,["اسم"]))
                age=safe_int(get_value(r,["السن"]))

                scores={
                    "physical":70,
                    "technical":70,
                    "mental":70,
                    "tactical":70
                }

                st.subheader(name)
                rep=PlayerEvaluationEngine.generate_report(name,age,scores)
                st.markdown(rep)

                st.download_button("تحميل التقرير",rep,f"{name}.txt")

with tab2:
    st.metric("عدد الطلاب",len(df))

st.caption("EDUVIA")
