import streamlit as st
import gspread
from google.oauth2 import service_account
import pandas as pd
import re
from datetime import datetime

# ──── إعداد الصفحة ────
st.set_page_config(
    page_title="نظام تقييم الطلاب الرياضي", 
    layout="wide", 
    initial_sidebar_state="collapsed",
    page_icon="⚽"
)

# ══════════════════════════════════════════════════════════════
# 🎨 التنسيقات والأنماط - RTL كامل + ألوان واضحة
# ══════════════════════════════════════════════════════════════
st.markdown("""
    <style>
    /* إخفاء عناصر Streamlit */
    #MainMenu, footer, header {visibility: hidden;}
    
    /* RTL للتطبيق بالكامل */
    .stApp {
        direction: rtl !important;
        text-align: right !important;
        font-family: 'Cairo', 'Tajawal', 'Segoe UI', Arial, sans-serif !important;
        background: #0a0e27;
    }
    
    /* RTL لجميع العناصر */
    div, p, span, h1, h2, h3, label, input, textarea, select {
        direction: rtl !important;
        text-align: right !important;
    }
    
    /* Header */
    h1 {
        color: #ffffff;
        text-align: center !important;
        margin-bottom: 5px;
        font-size: 2.5rem !important;
        font-weight: 700 !important;
    }
    
    /* Subtitle */
    .subtitle {
        text-align: center !important;
        color: #9ba3af;
        font-size: 1rem;
        margin-bottom: 40px;
        font-weight: 500;
    }
    
    /* Tabs */
    .stTabs {
        direction: rtl !important;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        direction: rtl !important;
        background-color: transparent;
    }
    
    .stTabs [data-baseweb="tab"] {
        direction: rtl !important;
        text-align: right !important;
        background-color: #1a1f3a;
        border-radius: 12px;
        color: #9ba3af;
        padding: 12px 24px;
        font-weight: 600;
        font-size: 1rem;
        border: 2px solid transparent;
        transition: all 0.3s;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background-color: #242b4a;
        color: #ffffff;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: #ffffff !important;
        border: 2px solid #8b5cf6;
    }
    
    /* Input Fields */
    .stTextInput > div > div > input {
        direction: rtl !important;
        text-align: right !important;
        background-color: #1a1f3a;
        border: 2px solid #2d3748;
        border-radius: 12px;
        color: #ffffff;
        padding: 14px;
        font-size: 1rem;
        font-weight: 500;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    .stTextInput > label {
        color: #ffffff !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        margin-bottom: 8px !important;
    }
    
    /* Buttons */
    .stButton > button {
        width: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 14px 24px;
        font-size: 1.1rem;
        font-weight: 700;
        cursor: pointer;
        transition: all 0.3s;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(102, 126, 234, 0.5);
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        direction: rtl !important;
        text-align: right !important;
        background-color: #1a1f3a !important;
        border: 2px solid #2d3748 !important;
        border-radius: 12px !important;
        color: #ffffff !important;
        font-weight: 700 !important;
        font-size: 1.1rem !important;
        padding: 16px !important;
    }
    
    .streamlit-expanderHeader:hover {
        background-color: #242b4a !important;
        border-color: #667eea !important;
    }
    
    .streamlit-expanderContent {
        direction: rtl !important;
        text-align: right !important;
        background-color: #0a0e27 !important;
        border: 2px solid #2d3748 !important;
        border-top: none !important;
        border-radius: 0 0 12px 12px !important;
        padding: 20px !important;
    }
    
    /* بطاقات التقييم */
    .metric-card {
        padding: 35px 20px;
        border-radius: 20px;
        color: white;
        text-align: center;
        margin: 15px 5px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.4);
        transition: all 0.3s;
        border: 3px solid transparent;
    }
    
    .metric-card:hover {
        transform: translateY(-8px);
        box-shadow: 0 15px 40px rgba(0,0,0,0.5);
    }
    
    .metric-title {
        font-size: 1.3rem;
        font-weight: 900;
        margin-bottom: 18px;
        text-shadow: 0 2px 8px rgba(0,0,0,0.3);
        letter-spacing: 0.5px;
    }
    
    .metric-score {
        font-size: 4.5rem;
        font-weight: 900;
        margin: 25px 0;
        text-shadow: 0 4px 12px rgba(0,0,0,0.4);
        line-height: 1;
    }
    
    .metric-level {
        font-size: 1.1rem;
        margin-top: 12px;
        font-weight: 700;
        text-shadow: 0 2px 6px rgba(0,0,0,0.2);
    }
    
    /* ألوان المستويات - محسّنة للوضوح */
    .excellent { 
        background: linear-gradient(135deg, #059669 0%, #10b981 100%);
        border-color: #34d399;
    }
    
    .very-good { 
        background: linear-gradient(135deg, #7c3aed 0%, #a78bfa 100%);
        border-color: #c4b5fd;
    }
    
    .good { 
        background: linear-gradient(135deg, #d97706 0%, #f59e0b 100%);
        border-color: #fbbf24;
    }
    
    .needs-improvement { 
        background: linear-gradient(135deg, #dc2626 0%, #ef4444 100%);
        border-color: #f87171;
    }
    
    /* Alert boxes */
    .stAlert {
        direction: rtl !important;
        text-align: right !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
    }
    
    /* Success/Warning/Error messages */
    .stSuccess, .stWarning, .stError, .stInfo {
        direction: rtl !important;
        text-align: right !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
    }
    
    /* Metrics */
    [data-testid="stMetricValue"] {
        direction: rtl !important;
        text-align: center !important;
        font-size: 2.5rem !important;
        color: #8b5cf6 !important;
        font-weight: 900 !important;
    }
    
    [data-testid="stMetricLabel"] {
        direction: rtl !important;
        text-align: center !important;
        color: #ffffff !important;
        font-weight: 700 !important;
        font-size: 1rem !important;
    }
    
    div[data-testid="stMetric"] {
        background-color: #1a1f3a;
        padding: 20px;
        border-radius: 12px;
        border: 2px solid #2d3748;
    }
    
    /* Download button */
    .stDownloadButton > button {
        background: linear-gradient(135deg, #059669 0%, #10b981 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 14px 24px !important;
        font-size: 1.1rem !important;
        font-weight: 700 !important;
        width: 100% !important;
        box-shadow: 0 4px 12px rgba(5, 150, 105, 0.3) !important;
        transition: all 0.3s !important;
    }
    
    .stDownloadButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 20px rgba(5, 150, 105, 0.5) !important;
    }
    
    /* Divider */
    hr {
        margin: 40px 0;
        border-color: #2d3748;
        border-width: 2px;
    }
    
    /* Markdown content */
    .element-container {
        direction: rtl !important;
    }
    
    /* Headers in markdown */
    h2, h3, h4 {
        color: #ffffff !important;
        font-weight: 700 !important;
    }
    
    /* Paragraphs */
    p {
        color: #d1d5db !important;
        line-height: 1.8 !important;
        font-size: 1rem !important;
    }
    
    /* Lists */
    ul, ol {
        color: #d1d5db !important;
        line-height: 1.8 !important;
    }
    
    /* Tables */
    table {
        color: #ffffff !important;
        border-color: #2d3748 !important;
    }
    
    th {
        background-color: #1a1f3a !important;
        color: #ffffff !important;
        font-weight: 700 !important;
    }
    
    td {
        border-color: #2d3748 !important;
    }
    
    /* Blockquote */
    blockquote {
        border-right: 4px solid #8b5cf6 !important;
        border-left: none !important;
        background-color: #1a1f3a !important;
        padding: 15px 20px !important;
        border-radius: 8px !important;
        color: #d1d5db !important;
    }
    </style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# 🔧 دوال مساعدة
# ══════════════════════════════════════════════════════════════

def clean_number(num):
    """تنظيف الأرقام من أي رموز أو مسافات"""
    if pd.isna(num) or num == "" or str(num).lower() in ['لا يوجود', 'لا يوجد', 'nan']:
        return ""
    
    num_str = str(num).strip()
    arabic_to_english = str.maketrans('٠١٢٣٤٥٦٧٨٩', '0123456789')
    num_str = num_str.translate(arabic_to_english)
    num_str = re.sub(r'[^0-9]', '', num_str)
    num_str = num_str.lstrip('0')
    
    return num_str

def safe_float(value, default=0):
    try:
        if pd.isna(value) or value == "" or value is None:
            return default
        return float(str(value).strip())
    except:
        return default

def safe_int(value, default=0):
    try:
        if pd.isna(value) or value == "" or value is None:
            return default
        return int(float(str(value).strip()))
    except:
        return default

# ══════════════════════════════════════════════════════════════
# ⚽ محرك التقييم الذكي
# ══════════════════════════════════════════════════════════════

class PlayerEvaluationEngine:
    """محرك تقييم اللاعبين بناءً على معايير علمية"""
    
    AGE_STANDARDS = {
        "8-10": {
            "height": {"min": 120, "ideal": 135, "max": 145},
            "weight": {"min": 20, "ideal": 30, "max": 40},
        },
        "11-13": {
            "height": {"min": 135, "ideal": 155, "max": 170},
            "weight": {"min": 28, "ideal": 45, "max": 60},
        },
        "14-16": {
            "height": {"min": 155, "ideal": 170, "max": 185},
            "weight": {"min": 45, "ideal": 60, "max": 75},
        }
    }
    
    @staticmethod
    def get_age_group(age):
        if 8 <= age <= 10:
            return "8-10"
        elif 11 <= age <= 13:
            return "11-13"
        elif 14 <= age <= 16:
            return "14-16"
        return "11-13"
    
    @staticmethod
    def calculate_physical_score(age, height, weight):
        """💪 التقييم البدني"""
        age_group = PlayerEvaluationEngine.get_age_group(age)
        standards = PlayerEvaluationEngine.AGE_STANDARDS[age_group]
        
        height_score = 0
        if height >= standards["height"]["ideal"]:
            height_score = 50
        elif height >= standards["height"]["min"]:
            ratio = (height - standards["height"]["min"]) / (standards["height"]["ideal"] - standards["height"]["min"])
            height_score = 30 + (ratio * 20)
        else:
            height_score = 20
        
        ideal_weight = standards["weight"]["ideal"]
        weight_diff = abs(weight - ideal_weight)
        
        if weight_diff <= 5:
            weight_score = 50
        elif weight_diff <= 10:
            weight_score = 40
        elif weight_diff <= 15:
            weight_score = 30
        else:
            weight_score = 20
        
        return min(100, height_score + weight_score)
    
    @staticmethod
    def calculate_technical_score(previous_exp, duration, skills):
        """⚽ التقييم الفني"""
        score = 0
        
        exp_map = {
            "لعب اكثر من موسم": 40,
            "لعب فترة قصيرة": 25,
            "لم يلعب من قبل": 10
        }
        score += exp_map.get(str(previous_exp).strip(), 15)
        
        duration_map = {
            "اكثر من سنه": 30,
            "من 6 شهور الي سنة": 20,
            "من 3 الي 6 شهور": 15,
            "لم يلعب": 5
        }
        score += duration_map.get(str(duration).strip(), 10)
        
        skills_text = str(skills).lower()
        skill_score = 15
        
        if "يتحكم" in skills_text or "محترف" in skills_text:
            skill_score += 15
        elif "يجري بسهولة" in skills_text or "جيد" in skills_text:
            skill_score += 10
        elif "لا يعرف" in skills_text:
            skill_score += 2
        
        score += min(30, skill_score)
        
        return min(100, score)
    
    @staticmethod
    def calculate_mental_score(motivation, matches, parent_present):
        """🧠 التقييم الذهني"""
        score = 0
        
        motivation_map = {
            "احتراف مستقبلي": 50,
            "حب كرة القدم": 40,
            "تحسين اللياقة البدنية": 30,
            "الترفيه": 25
        }
        score += motivation_map.get(str(motivation).strip(), 30)
        
        matches_text = str(matches).lower()
        if "رسمية" in matches_text:
            score += 30
        elif "ودية" in matches_text:
            score += 20
        else:
            score += 10
        
        if str(parent_present).strip() == "نعم":
            score += 20
        elif str(parent_present).strip() == "ربما":
            score += 10
        else:
            score += 5
        
        return min(100, score)
    
    @staticmethod
    def calculate_tactical_score(knows_rules, fitness_level, registered_in_club):
        """🎯 التقييم التكتيكي"""
        score = 0
        
        rules_text = str(knows_rules).lower()
        if "يتحكم" in rules_text or "يعرف" in rules_text:
            score += 40
        elif "بسيط" in rules_text or "يجري" in rules_text:
            score += 25
        elif "لا يعرف" in rules_text:
            score += 10
        else:
            score += 20
        
        fitness_map = {
            "أكثر من طبيعي": 35,
            "مناسب": 30,
            "أقل من طبيعي": 15
        }
        score += fitness_map.get(str(fitness_level).strip(), 25)
        
        if str(registered_in_club).strip() == "نعم":
            score += 25
        else:
            score += 10
        
        return min(100, score)
    
    @staticmethod
    def get_level_category(score):
        if score >= 85:
            return "ممتاز ⭐⭐⭐", "excellent"
        elif score >= 70:
            return "جيد جداً ⭐⭐", "very-good"
        elif score >= 50:
            return "جيد ⭐", "good"
        else:
            return "يحتاج تطوير 📈", "needs-improvement"
    
    @staticmethod
    def generate_report(player_data, scores):
        """📄 توليد تقرير احترافي"""
        name = player_data.get('اسم الطفل  كامل ', 'الطالب')
        age = safe_int(player_data.get('السن', 0))
        
        avg_score = sum(scores.values()) / len(scores)
        overall_level, _ = PlayerEvaluationEngine.get_level_category(avg_score)
        
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        strongest = sorted_scores[0]
        weakest = sorted_scores[-1]
        
        names_ar = {
            "technical": "الفني",
            "physical": "البدني",
            "mental": "الذهني",
            "tactical": "التكتيكي"
        }
        
        report = f"""
## 🎯 تقرير التقييم الشامل

### معلومات الطالب
- **الاسم:** {name}
- **السن:** {age} سنة
- **التقييم العام:** {avg_score:.0f}/100 - **{overall_level}**

---

### 💚 التحليل التفصيلي

عزيزي ولي الأمر،

يسعدنا تقديم تقرير تقييم شامل لابنك **{name}** بناءً على معايير علمية عالمية.

#### ⭐ نقاط القوة

الجانب **{names_ar[strongest[0]]}** حصل على **{strongest[1]:.0f}/100** - وهي درجة ممتازة! """
        
        if strongest[0] == "technical":
            report += "\n\nهذا يدل على مهارات فنية جيدة وقدرة على التعامل مع الكرة."
        elif strongest[0] == "physical":
            report += "\n\nهذا يعكس بنية جسدية ممتازة ومناسبة للمرحلة العمرية."
        elif strongest[0] == "mental":
            report += "\n\nهذا يظهر دافعية عالية والتزام قوي - أهم عوامل النجاح!"
        elif strongest[0] == "tactical":
            report += "\n\nهذا يعني فهم جيد للعبة وذكاء تكتيكي واعد."
        
        if weakest[1] < 65:
            report += f"""

#### 🎯 فرص التطوير

الجانب **{names_ar[weakest[0]]}** حصل على **{weakest[1]:.0f}/100** - وهذا **طبيعي جداً** في هذا السن.

"""
            
            if weakest[0] == "physical":
                report += """**💪 توصيات التطوير البدني:**
- تمارين الإطالة والمرونة (10 دقائق يومياً)
- تغذية متوازنة غنية بالبروتين والفيتامينات
- النوم الكافي (8-10 ساعات)
- ممارسة الرياضة بانتظام 3-4 مرات أسبوعياً
"""
            elif weakest[0] == "technical":
                report += """**⚽ توصيات التطوير الفني:**
- التدريب على المهارات الأساسية (التحكم، التمرير، التسديد)
- مشاهدة مباريات المحترفين وتحليل الحركات
- اللعب مع أصدقاء بمستوى أعلى
- الالتحاق ببرنامج تدريبي منتظم
"""
            elif weakest[0] == "mental":
                report += """**🧠 توصيات التطوير الذهني:**
- التشجيع المستمر والإيجابي من الأسرة
- وضع أهداف صغيرة قابلة للتحقيق
- المشاركة في مباريات ودية لزيادة الثقة
- مكافأة التقدم والمجهود (وليس النتائج فقط)
"""
            elif weakest[0] == "tactical":
                report += """**🎯 توصيات التطوير التكتيكي:**
- مشاهدة مباريات تعليمية مع شرح القوانين
- قراءة كتيبات مبسطة عن قوانين كرة القدم
- المشاركة في تدريبات جماعية منظمة
- لعب FIFA أو PES (يعلم التكتيكات بشكل ممتع!)
"""
        
        report += f"""

### 🌟 الخلاصة والتوقعات

ابنك **{name}** يمتلك أساساً **{overall_level}** ويظهر إمكانيات واعدة. 

**جميع النقاط التي تحتاج تطوير هي أمور طبيعية ومتوقعة** في هذا السن، ومع:
- ✅ التدريب المنتظم (3-4 مرات أسبوعياً)
- ✅ الدعم الأسري المستمر
- ✅ التغذية السليمة والراحة الكافية
- ✅ المتابعة الدورية مع المدربين

**سيحقق تقدماً ملحوظاً خلال 3-6 أشهر إن شاء الله!**

---

### 📊 ملخص الدرجات

| المحور | الدرجة | المستوى |
|--------|--------|---------|
"""
        
        for key, value in scores.items():
            level, _ = PlayerEvaluationEngine.get_level_category(value)
            report += f"| {names_ar[key]} | {value:.0f}/100 | {level} |\n"
        
        report += f"\n| **المجموع** | **{avg_score:.0f}/100** | **{overall_level}** |\n"
        
        report += """

---

> **💡 ملاحظة هامة:** هذا التقييم أداة إرشادية لمساعدتك في متابعة تطور ابنك. 
> النجاح الحقيقي يُقاس بالتقدم المستمر والاستمتاع باللعبة! ⚽💚

*تم إنشاء هذا التقرير بواسطة نظام EDUVIA الرياضي الذكي*
"""
        
        return report

# ══════════════════════════════════════════════════════════════
# 🔌 الاتصال بـ Google Sheets
# ══════════════════════════════════════════════════════════════

@st.cache_resource(show_spinner="🔄 جاري الاتصال بقاعدة البيانات...")
def get_sheet():
    try:
        creds = service_account.Credentials.from_service_account_info(
            st.secrets["gcp_service_account"],
            scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        )
        client = gspread.authorize(creds)
        sheet_id = st.secrets["gsheet"]["sheet_id"]
        ss = client.open_by_key(sheet_id)
        return ss.sheet1
    except Exception as e:
        st.error(f"❌ خطأ في الاتصال: {str(e)}")
        return None

# ══════════════════════════════════════════════════════════════
# 🎬 الواجهة الرئيسية
# ══════════════════════════════════════════════════════════════

st.title("⚽ نظام تقييم الطلاب الرياضي الذكي")
st.markdown('<p class="subtitle">مؤسسة EDUVIA الرياضية | نظام تقييم شامل بمعايير عالمية</p>', unsafe_allow_html=True)

ws = get_sheet()

if not ws:
    st.stop()

try:
    data = ws.get_all_records()
    if not data:
        st.info("📭 الورقة فارغة")
        st.stop()
    
    df = pd.DataFrame(data)
    df.columns = df.columns.str.strip()
    
    # تنظيف أعمدة الأرقام
    phone_cols = [col for col in df.columns if 'موبايل' in col or 'واتساب' in col]
    for col in phone_cols:
        df[f'{col}_clean'] = df[col].apply(clean_number)
    
    tab1, tab2 = st.tabs(["🔍 البحث عن طالب", "📊 إحصائيات عامة"])
    
    with tab1:
        st.subheader("ابحث عن طالب للحصول على تقييمه الكامل")
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            search = st.text_input(
                "اسم الطفل أو رقم الموبايل",
                placeholder="مثال: محمد طارق  أو  01229920187",
                key="search",
                label_visibility="visible"
            ).strip()
        
        with col2:
            st.write("")
            st.write("")
            search_btn = st.button("🔍 بحث", type="primary", use_container_width=True)
        
        if search_btn and search:
            search_clean = clean_number(search)
            
            name_col = next((c for c in df.columns if 'اسم الطفل' in c), None)
            mask = df[name_col].astype(str).str.contains(search, case=False, na=False) if name_col else pd.Series([False] * len(df))
            
            if search_clean:
                for col in phone_cols:
                    clean_col = f'{col}_clean'
                    if clean_col in df.columns:
                        mask = mask | df[clean_col].str.contains(search_clean, na=False, regex=False)
            
            results = df[mask]
            
            if results.empty:
                st.warning("❌ لم يتم العثور على نتائج مطابقة")
            else:
                st.success(f"✅ تم العثور على {len(results)} نتيجة")
                
                for idx, row in results.iterrows():
                    student_name = row.get('اسم الطفل  كامل ', 'طالب')
                    
                    with st.expander(f"📋 {student_name} - اضغط للتفاصيل", expanded=True):
                        
                        age = safe_int(row.get('السن', 0))
                        height = safe_float(row.get('طول الطفل بالسنتيمتر', 0))
                        weight = safe_float(row.get('وزن الطفل بالكيلوجرام ', 0))
                        
                        scores = {
                            "physical": PlayerEvaluationEngine.calculate_physical_score(
                                age, height, weight
                            ),
                            "technical": PlayerEvaluationEngine.calculate_technical_score(
                                row.get('هل سبق للطفل اللعب في أكاديمية كرة قدم ؟', ''),
                                row.get('مده اللعب ', ''),
                                row.get('اختر ما بنطبق  علي الطفل ', '')
                            ),
                            "mental": PlayerEvaluationEngine.calculate_mental_score(
                                row.get('سبب الانضمام للأكاديمية ', ''),
                                row.get('هل شارك في مباريات ؟', ''),
                                row.get('هل ولي الامر متواجد اثناء التدريب', '')
                            ),
                            "tactical": PlayerEvaluationEngine.calculate_tactical_score(
                                row.get('اختر ما بنطبق  علي الطفل ', ''),
                                row.get('تقدير ولي الأمر لوزن الطفل', ''),
                                row.get('هل الطفل مسجل في نادي حاليا؟', '')
                            )
                        }
                        
                        # عرض البطاقات في صف واحد - من اليمين لليسار
                        cols = st.columns(4)
                        
                        metrics_data = [
                            ("التكتيكي", "🎯", scores["tactical"]),
                            ("الذهني", "🧠", scores["mental"]),
                            ("الفني", "⚽", scores["technical"]),
                            ("البدني", "💪", scores["physical"])
                        ]
                        
                        for i, (title, icon, score) in enumerate(metrics_data):
                            level, css_class = PlayerEvaluationEngine.get_level_category(score)
                            with cols[i]:
                                st.markdown(f"""
                                <div class="metric-card {css_class}">
                                    <div class="metric-title">{icon} {title}</div>
                                    <div class="metric-score">{score:.0f}</div>
                                    <div class="metric-level">{level}</div>
                                </div>
                                """, unsafe_allow_html=True)
                        
                        st.divider()
                        
                        # التقرير الكامل
                        report = PlayerEvaluationEngine.generate_report(row.to_dict(), scores)
                        st.markdown(report)
                        
                        # زر التحميل بـ key فريد
                        st.download_button(
                            label="📥 تحميل التقرير كملف نصي",
                            data=report,
                            file_name=f"تقرير_{student_name.replace(' ', '_')}.txt",
                            mime="text/plain",
                            use_container_width=True,
                            key=f"download_{idx}_{student_name[:10]}"  # ✅ key فريد لكل طالب
                        )
    
    with tab2:
        st.subheader("📊 إحصائيات عامة")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("إجمالي الطلاب", len(df))
        
        with col2:
            avg_age = df['السن'].apply(safe_int).mean()
            st.metric("متوسط العمر", f"{avg_age:.1f} سنة")
        
        with col3:
            has_exp = df['هل سبق للطفل اللعب في أكاديمية كرة قدم ؟'].apply(
                lambda x: 1 if 'لعب' in str(x) else 0
            ).sum()
            st.metric("لديهم خبرة سابقة", f"{has_exp} طالب")

except Exception as e:
    st.error("❌ خطأ في قراءة البيانات")
    st.exception(e)

st.markdown("---")
st.caption("⚽ نظام EDUVIA الرياضي الذكي | تطوير مستمر")
