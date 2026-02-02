import streamlit as st
import gspread
from google.oauth2 import service_account
import pandas as pd
import re

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
# 🎨 التنسيقات والأنماط
# ══════════════════════════════════════════════════════════════
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;900&display=swap');
    
    #MainMenu, footer, header {visibility: hidden;}
    
    .stApp {
        direction: rtl !important;
        text-align: right !important;
        font-family: 'Cairo', sans-serif !important;
        background: #0a0e27;
    }
    
    div, p, span, h1, h2, h3, label {
        direction: rtl !important;
        text-align: right !important;
        font-family: 'Cairo', sans-serif !important;
    }
    
    h1 {
        color: #ffffff !important;
        text-align: center !important;
        font-size: 2.8rem !important;
        font-weight: 900 !important;
        text-shadow: 0 2px 10px rgba(102, 126, 234, 0.3);
    }
    
    .subtitle {
        text-align: center !important;
        color: #cbd5e1 !important;
        font-size: 1.1rem !important;
        margin-bottom: 40px !important;
        font-weight: 600 !important;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
        direction: rtl !important;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: #1a1f3a;
        border-radius: 14px;
        color: #94a3b8;
        padding: 14px 28px;
        font-weight: 700;
        font-size: 1.1rem;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: #ffffff !important;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
    }
    
    .stTextInput input {
        background-color: #1a1f3a !important;
        border: 2px solid #334155 !important;
        border-radius: 14px !important;
        color: #ffffff !important;
        padding: 16px !important;
        font-size: 1.05rem !important;
    }
    
    .stTextInput input:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.15) !important;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border-radius: 14px !important;
        padding: 16px 28px !important;
        font-size: 1.15rem !important;
        font-weight: 800 !important;
        box-shadow: 0 6px 16px rgba(102, 126, 234, 0.35) !important;
    }
    
    .streamlit-expanderHeader {
        background-color: #1a1f3a !important;
        border: 2px solid #334155 !important;
        border-radius: 14px !important;
        color: #ffffff !important;
        font-weight: 800 !important;
        font-size: 1.2rem !important;
        padding: 18px 20px !important;
    }
    
    .metric-card {
        padding: 40px 25px;
        border-radius: 22px;
        color: white;
        text-align: center;
        margin: 18px 8px;
        box-shadow: 0 12px 35px rgba(0,0,0,0.5);
        border: 3px solid rgba(255,255,255,0.1);
    }
    
    .metric-title {
        font-size: 1.4rem;
        font-weight: 900;
        margin-bottom: 20px;
    }
    
    .metric-score {
        font-size: 5rem;
        font-weight: 900;
        margin: 28px 0;
    }
    
    .metric-level {
        font-size: 1.15rem;
        font-weight: 800;
    }
    
    .excellent { 
        background: linear-gradient(135deg, #059669 0%, #10b981 50%, #34d399 100%);
    }
    
    .very-good { 
        background: linear-gradient(135deg, #7c3aed 0%, #a78bfa 50%, #c4b5fd 100%);
    }
    
    .good { 
        background: linear-gradient(135deg, #ea580c 0%, #f59e0b 50%, #fbbf24 100%);
    }
    
    .needs-improvement { 
        background: linear-gradient(135deg, #dc2626 0%, #ef4444 50%, #f87171 100%);
    }
    
    .student-header {
        background: linear-gradient(135deg, #1e3a5f 0%, #2d5f8d 100%);
        padding: 25px 30px;
        border-radius: 16px;
        margin-bottom: 30px;
        border: 3px solid #4a90e2;
        box-shadow: 0 8px 20px rgba(74, 144, 226, 0.3);
    }
    
    .student-name {
        font-size: 2rem;
        font-weight: 900;
        color: #ffffff;
        text-align: center;
        margin: 0;
    }
    
    .student-info {
        font-size: 1.2rem;
        color: #cbd5e1;
        text-align: center;
        margin-top: 10px;
    }
    
    h2, h3 { color: #f1f5f9 !important; }
    p { color: #e2e8f0 !important; line-height: 2 !important; }
    </style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# 🔧 دوال مساعدة
# ══════════════════════════════════════════════════════════════

def clean_number(num):
    """تنظيف الأرقام"""
    if pd.isna(num) or num == "":
        return ""
    num_str = str(num).strip()
    num_str = num_str.translate(str.maketrans('٠١٢٣٤٥٦٧٨٩', '0123456789'))
    num_str = re.sub(r'[^0-9]', '', num_str)
    return num_str.lstrip('0')

def safe_int(value, default=0):
    """تحويل آمن للأرقام"""
    try:
        if pd.isna(value) or value == "":
            return default
        return int(float(str(value).strip()))
    except:
        return default

def safe_float(value, default=0):
    """تحويل آمن للأرقام العشرية"""
    try:
        if pd.isna(value) or value == "":
            return default
        return float(str(value).strip())
    except:
        return default

def find_column(df, keywords):
    """البحث عن عمود بناءً على كلمات مفتاحية"""
    for col in df.columns:
        if any(keyword in col for keyword in keywords):
            return col
    return None

def get_value(row, keywords, default=""):
    """استخراج قيمة من صف بناءً على كلمات مفتاحية"""
    col = find_column(pd.DataFrame([row]), keywords)
    if col and col in row.index:
        val = row[col]
        if pd.notna(val) and str(val).strip():
            return str(val).strip()
    return default

# ══════════════════════════════════════════════════════════════
# ⚽ محرك التقييم
# ══════════════════════════════════════════════════════════════

class Evaluator:
    
    STANDARDS = {
        "8-10": {"height": {"min": 120, "ideal": 135}, "weight": {"ideal": 30}},
        "11-13": {"height": {"min": 135, "ideal": 155}, "weight": {"ideal": 45}},
        "14-16": {"height": {"min": 155, "ideal": 170}, "weight": {"ideal": 60}}
    }
    
    @staticmethod
    def get_age_group(age):
        if 8 <= age <= 10: return "8-10"
        elif 11 <= age <= 13: return "11-13"
        elif 14 <= age <= 16: return "14-16"
        return "11-13"
    
    @staticmethod
    def calc_physical(age, height, weight):
        group = Evaluator.get_age_group(age)
        std = Evaluator.STANDARDS[group]
        
        h_score = 50 if height >= std["height"]["ideal"] else max(20, 30 + (height - std["height"]["min"]) / (std["height"]["ideal"] - std["height"]["min"]) * 20)
        w_diff = abs(weight - std["weight"]["ideal"])
        w_score = 50 if w_diff <= 5 else (40 if w_diff <= 10 else (30 if w_diff <= 15 else 20))
        
        return min(100, h_score + w_score)
    
    @staticmethod
    def calc_technical(exp, duration, skills):
        score = {"لعب اكثر من موسم": 40, "لعب فترة قصيرة": 25, "لم يلعب من قبل": 10}.get(str(exp).strip(), 15)
        score += {"اكثر من سنه": 30, "من 6 شهور الي سنة": 20, "من 3 الي 6 شهور": 15}.get(str(duration).strip(), 10)
        
        skills_lower = str(skills).lower()
        if "يتحكم" in skills_lower: score += 15
        elif "يجري" in skills_lower: score += 10
        else: score += 5
        
        return min(100, score)
    
    @staticmethod
    def calc_mental(motivation, matches, parent):
        score = {"احتراف مستقبلي": 50, "حب كرة القدم": 40, "تحسين اللياقة البدنية": 30}.get(str(motivation).strip(), 30)
        score += 30 if "رسمية" in str(matches).lower() else (20 if "ودية" in str(matches).lower() else 10)
        score += {"نعم": 20, "ربما": 10}.get(str(parent).strip(), 5)
        return min(100, score)
    
    @staticmethod
    def calc_tactical(rules, fitness, club):
        rules_lower = str(rules).lower()
        score = 40 if "يتحكم" in rules_lower else (25 if "يجري" in rules_lower else (10 if "لا يعرف" in rules_lower else 20))
        score += {"أكثر من طبيعي": 35, "مناسب": 30, "أقل من طبيعي": 15}.get(str(fitness).strip(), 25)
        score += 25 if str(club).strip() == "نعم" else 10
        return min(100, score)
    
    @staticmethod
    def get_level(score):
        if score >= 85: return "ممتاز ⭐⭐⭐", "excellent"
        elif score >= 70: return "جيد جداً ⭐⭐", "very-good"
        elif score >= 50: return "جيد ⭐", "good"
        else: return "يحتاج تطوير 📈", "needs-improvement"

# ══════════════════════════════════════════════════════════════
# 🔌 الاتصال بقاعدة البيانات
# ══════════════════════════════════════════════════════════════

@st.cache_resource(show_spinner="🔄 جاري الاتصال...")
def get_sheet():
    try:
        creds = service_account.Credentials.from_service_account_info(
            st.secrets["gcp_service_account"],
            scopes=["https://www.googleapis.com/auth/spreadsheets"]
        )
        client = gspread.authorize(creds)
        return client.open_by_key(st.secrets["gsheet"]["sheet_id"]).sheet1
    except Exception as e:
        st.error(f"❌ خطأ: {str(e)}")
        return None

# ══════════════════════════════════════════════════════════════
# 🎬 الواجهة الرئيسية
# ══════════════════════════════════════════════════════════════

st.title("⚽ نظام تقييم الطلاب الرياضي الذكي")
st.markdown('<p class="subtitle">مؤسسة EDUVIA الرياضية | معايير عالمية</p>', unsafe_allow_html=True)

ws = get_sheet()
if not ws:
    st.stop()

try:
    df = pd.DataFrame(ws.get_all_records())
    if df.empty:
        st.info("📭 لا توجد بيانات")
        st.stop()
    
    df.columns = df.columns.str.strip()
    
    # تنظيف الأرقام
    phone_cols = [c for c in df.columns if 'موبايل' in c or 'واتساب' in c]
    for col in phone_cols:
        df[f'{col}_clean'] = df[col].apply(clean_number)
    
    tab1, tab2 = st.tabs(["🔍 البحث عن طالب", "📊 إحصائيات"])
    
    # ═══════════════════════════════════════════════════════
    # TAB 1: البحث
    # ═══════════════════════════════════════════════════════
    with tab1:
        st.subheader("ابحث عن طالب")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            search = st.text_input("اسم الطفل أو رقم الموبايل", placeholder="محمد طارق أو 01229920187").strip()
        with col2:
            st.write(""); st.write("")
            search_btn = st.button("🔍 بحث", type="primary", use_container_width=True)
        
        if search_btn and search:
            search_clean = clean_number(search)
            
            # البحث
            name_col = find_column(df, ['اسم الطفل'])
            mask = df[name_col].astype(str).str.contains(search, case=False, na=False) if name_col else pd.Series([False] * len(df))
            
            if search_clean:
                for col in phone_cols:
                    clean_col = f'{col}_clean'
                    if clean_col in df.columns:
                        mask = mask | df[clean_col].str.contains(search_clean, na=False, regex=False)
            
            results = df[mask]
            
            if results.empty:
                st.warning("❌ لا توجد نتائج")
            else:
                st.success(f"✅ {len(results)} نتيجة")
                
                for idx, row in results.iterrows():
                    name = get_value(row, ['اسم الطفل'], 'طالب')
                    age = safe_int(get_value(row, ['السن', 'العمر']))
                    
                    with st.expander(f"📋 {name} ({age} سنة)", expanded=True):
                        
                        st.markdown(f"""
                        <div class="student-header">
                            <h2 class="student-name">⭐ {name}</h2>
                            <p class="student-info">العمر: {age} سنة</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # حساب التقييمات
                        height = safe_float(get_value(row, ['طول']))
                        weight = safe_float(get_value(row, ['وزن']))
                        
                        scores = {
                            "physical": Evaluator.calc_physical(age, height, weight),
                            "technical": Evaluator.calc_technical(
                                get_value(row, ['اللعب في أكاديمية']),
                                get_value(row, ['مده اللعب', 'مدة']),
                                get_value(row, ['بنطبق', 'مهارات'])
                            ),
                            "mental": Evaluator.calc_mental(
                                get_value(row, ['سبب الانضمام']),
                                get_value(row, ['مباريات']),
                                get_value(row, ['ولي الامر متواجد'])
                            ),
                            "tactical": Evaluator.calc_tactical(
                                get_value(row, ['بنطبق', 'مهارات']),
                                get_value(row, ['تقدير', 'وزن']),
                                get_value(row, ['مسجل في نادي'])
                            )
                        }
                        
                        # البطاقات
                        cols = st.columns(4)
                        for i, (title, icon, key) in enumerate([
                            ("التكتيكي", "🎯", "tactical"),
                            ("الذهني", "🧠", "mental"),
                            ("الفني", "⚽", "technical"),
                            ("البدني", "💪", "physical")
                        ]):
                            level, css = Evaluator.get_level(scores[key])
                            with cols[i]:
                                st.markdown(f"""
                                <div class="metric-card {css}">
                                    <div class="metric-title">{icon} {title}</div>
                                    <div class="metric-score">{scores[key]:.0f}</div>
                                    <div class="metric-level">{level}</div>
                                </div>
                                """, unsafe_allow_html=True)
                        
                        st.divider()
                        
                        # التقرير
                        avg = sum(scores.values()) / 4
                        overall, _ = Evaluator.get_level(avg)
                        
                        st.markdown(f"""
## 🎯 تقرير التقييم

**الاسم:** {name} | **العمر:** {age} سنة | **التقييم:** {avg:.0f}/100 - {overall}

### 💚 التحليل

عزيزي ولي الأمر، ابنك **{name}** حصل على تقييم **{overall}**.

**نقاط القوة:** الجانب الأقوى هو **{max(scores, key=scores.get)}** بدرجة {max(scores.values()):.0f}/100

**التوصيات:**
- التدريب المنتظم 3-4 مرات أسبوعياً
- التغذية السليمة والراحة الكافية
- الدعم الأسري المستمر

| المحور | الدرجة | المستوى |
|--------|--------|---------|
| البدني | {scores['physical']:.0f}/100 | {Evaluator.get_level(scores['physical'])[0]} |
| الفني | {scores['technical']:.0f}/100 | {Evaluator.get_level(scores['technical'])[0]} |
| الذهني | {scores['mental']:.0f}/100 | {Evaluator.get_level(scores['mental'])[0]} |
| التكتيكي | {scores['tactical']:.0f}/100 | {Evaluator.get_level(scores['tactical'])[0]} |

*نظام EDUVIA الرياضي الذكي*
                        """)
                        
                        st.download_button(
                            "📥 تحميل التقرير",
                            f"تقرير تقييم {name}\n\nالتقييم العام: {avg:.0f}/100\n",
                            f"تقرير_{name.replace(' ', '_')}.txt",
                            key=f"dl_{idx}"
                        )
    
    # ═══════════════════════════════════════════════════════
    # TAB 2: الإحصائيات
    # ═══════════════════════════════════════════════════════
    with tab2:
        st.subheader("📊 إحصائيات عامة")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("إجمالي الطلاب", len(df))
        
        with col2:
            ages = []
            for _, row in df.iterrows():
                age = safe_int(get_value(row, ['السن', 'العمر']))
                if age > 0:
                    ages.append(age)
            avg_age = sum(ages) / len(ages) if ages else 0
            st.metric("متوسط العمر", f"{avg_age:.1f} سنة")
        
        with col3:
            exp_col = find_column(df, ['اللعب في أكاديمية'])
            if exp_col:
                exp_count = df[exp_col].astype(str).str.contains('لعب', na=False).sum()
            else:
                exp_count = 0
            st.metric("لديهم خبرة", f"{exp_count} طالب")

except Exception as e:
    st.error(f"❌ خطأ: {str(e)}")
    st.exception(e)

st.markdown("---")
st.caption("⚽ نظام EDUVIA | تطوير مستمر")
