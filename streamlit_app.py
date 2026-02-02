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
# 🎨 التنسيقات والأنماط - كاملة
# ══���═══════════════════════════════════════════════════════════
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;900&display=swap');
    
    /* إخفاء العناصر الافتراضية */
    #MainMenu, footer, header {visibility: hidden;}
    
    /* RTL للتطبيق كامل */
    .stApp {
        direction: rtl !important;
        text-align: right !important;
        font-family: 'Cairo', sans-serif !important;
        background: #0a0e27;
    }
    
    div, p, span, h1, h2, h3, label, input, textarea, select {
        direction: rtl !important;
        text-align: right !important;
        font-family: 'Cairo', sans-serif !important;
    }
    
    /* العناوين */
    h1 {
        color: #ffffff !important;
        text-align: center !important;
        font-size: 2.8rem !important;
        font-weight: 900 !important;
        text-shadow: 0 2px 10px rgba(102, 126, 234, 0.3);
        margin-bottom: 10px !important;
    }
    
    .subtitle {
        text-align: center !important;
        color: #cbd5e1 !important;
        font-size: 1.1rem !important;
        margin-bottom: 40px !important;
        font-weight: 600 !important;
    }
    
    /* Tabs */
    .stTabs {
        direction: rtl !important;
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
        border: 2px solid transparent;
        transition: all 0.3s;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background-color: #242b4a;
        color: #ffffff;
        border-color: #667eea;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: #ffffff !important;
        border: 2px solid #8b5cf6 !important;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
    }
    
    /* Input Fields */
    .stTextInput > div > div > input {
        direction: rtl !important;
        text-align: right !important;
        background-color: #1a1f3a !important;
        border: 2px solid #334155 !important;
        border-radius: 14px !important;
        color: #ffffff !important;
        padding: 16px !important;
        font-size: 1.05rem !important;
        font-weight: 600 !important;
    }
    
    .stTextInput > div > div > input::placeholder {
        color: #64748b !important;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.15) !important;
    }
    
    .stTextInput > label {
        color: #f1f5f9 !important;
        font-weight: 700 !important;
        font-size: 1.05rem !important;
    }
    
    /* Buttons */
    .stButton > button {
        width: 100% !important;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 14px !important;
        padding: 16px 28px !important;
        font-size: 1.15rem !important;
        font-weight: 800 !important;
        box-shadow: 0 6px 16px rgba(102, 126, 234, 0.35) !important;
        transition: all 0.3s !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-3px) !important;
        box-shadow: 0 10px 25px rgba(102, 126, 234, 0.5) !important;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        direction: rtl !important;
        text-align: right !important;
        background-color: #1a1f3a !important;
        border: 2px solid #334155 !important;
        border-radius: 14px !important;
        color: #ffffff !important;
        font-weight: 800 !important;
        font-size: 1.2rem !important;
        padding: 18px 20px !important;
    }
    
    .streamlit-expanderHeader:hover {
        background-color: #242b4a !important;
        border-color: #667eea !important;
    }
    
    .streamlit-expanderContent {
        direction: rtl !important;
        text-align: right !important;
        background-color: #111827 !important;
        border: 2px solid #334155 !important;
        border-top: none !important;
        border-radius: 0 0 14px 14px !important;
        padding: 25px !important;
    }
    
    /* بطاقات التقييم */
    .metric-card {
        padding: 40px 25px;
        border-radius: 22px;
        color: white;
        text-align: center;
        margin: 18px 8px;
        box-shadow: 0 12px 35px rgba(0,0,0,0.5);
        transition: all 0.4s;
        border: 3px solid rgba(255,255,255,0.1);
        position: relative;
        overflow: hidden;
    }
    
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(135deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0) 100%);
        pointer-events: none;
    }
    
    .metric-card:hover {
        transform: translateY(-10px) scale(1.02);
        box-shadow: 0 18px 45px rgba(0,0,0,0.6);
    }
    
    .metric-title {
        font-size: 1.4rem;
        font-weight: 900;
        margin-bottom: 20px;
        text-shadow: 0 3px 10px rgba(0,0,0,0.4);
        position: relative;
        z-index: 1;
    }
    
    .metric-score {
        font-size: 5rem;
        font-weight: 900;
        margin: 28px 0;
        text-shadow: 0 5px 15px rgba(0,0,0,0.5);
        line-height: 1;
        position: relative;
        z-index: 1;
    }
    
    .metric-level {
        font-size: 1.15rem;
        margin-top: 15px;
        font-weight: 800;
        text-shadow: 0 2px 8px rgba(0,0,0,0.3);
        position: relative;
        z-index: 1;
    }
    
    /* ألوان المستويات */
    .excellent { 
        background: linear-gradient(135deg, #059669 0%, #10b981 50%, #34d399 100%);
        border-color: #6ee7b7;
    }
    
    .very-good { 
        background: linear-gradient(135deg, #7c3aed 0%, #a78bfa 50%, #c4b5fd 100%);
        border-color: #ddd6fe;
    }
    
    .good { 
        background: linear-gradient(135deg, #ea580c 0%, #f59e0b 50%, #fbbf24 100%);
        border-color: #fcd34d;
    }
    
    .needs-improvement { 
        background: linear-gradient(135deg, #dc2626 0%, #ef4444 50%, #f87171 100%);
        border-color: #fca5a5;
    }
    
    /* Student Header */
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
        text-shadow: 0 2px 8px rgba(0,0,0,0.3);
    }
    
    .student-info {
        font-size: 1.2rem;
        color: #cbd5e1;
        text-align: center;
        margin-top: 10px;
        font-weight: 600;
    }
    
    /* Alerts */
    .stAlert {
        direction: rtl !important;
        text-align: right !important;
        border-radius: 14px !important;
        font-weight: 700 !important;
        font-size: 1.05rem !important;
        padding: 18px !important;
    }
    
    .stSuccess {
        background-color: rgba(16, 185, 129, 0.15) !important;
        border: 2px solid #10b981 !important;
        color: #6ee7b7 !important;
    }
    
    .stWarning {
        background-color: rgba(245, 158, 11, 0.15) !important;
        border: 2px solid #f59e0b !important;
        color: #fcd34d !important;
    }
    
    /* Metrics */
    [data-testid="stMetricValue"] {
        direction: rtl !important;
        text-align: center !important;
        font-size: 2.8rem !important;
        color: #a78bfa !important;
        font-weight: 900 !important;
    }
    
    [data-testid="stMetricLabel"] {
        direction: rtl !important;
        text-align: center !important;
        color: #f1f5f9 !important;
        font-weight: 700 !important;
        font-size: 1.1rem !important;
    }
    
    div[data-testid="stMetric"] {
        background-color: #1a1f3a;
        padding: 25px;
        border-radius: 14px;
        border: 2px solid #334155;
    }
    
    /* Download Button */
    .stDownloadButton > button {
        background: linear-gradient(135deg, #059669 0%, #10b981 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 14px !important;
        padding: 16px 28px !important;
        font-size: 1.15rem !important;
        font-weight: 800 !important;
        width: 100% !important;
        box-shadow: 0 6px 16px rgba(5, 150, 105, 0.35) !important;
    }
    
    .stDownloadButton > button:hover {
        transform: translateY(-3px) !important;
        box-shadow: 0 10px 25px rgba(5, 150, 105, 0.5) !important;
    }
    
    /* Markdown Content */
    h2 {
        color: #f1f5f9 !important;
        font-weight: 800 !important;
        font-size: 1.9rem !important;
        margin-top: 30px !important;
    }
    
    h3 {
        color: #e2e8f0 !important;
        font-weight: 700 !important;
        font-size: 1.5rem !important;
        margin-top: 25px !important;
    }
    
    h4 {
        color: #cbd5e1 !important;
        font-weight: 700 !important;
        font-size: 1.2rem !important;
    }
    
    p {
        color: #e2e8f0 !important;
        line-height: 2 !important;
        font-size: 1.05rem !important;
        font-weight: 500 !important;
    }
    
    strong {
        color: #f1f5f9 !important;
        font-weight: 800 !important;
    }
    
    ul, ol {
        color: #e2e8f0 !important;
        line-height: 2 !important;
        font-size: 1.05rem !important;
    }
    
    li {
        margin: 8px 0 !important;
    }
    
    /* Tables */
    table {
        color: #f1f5f9 !important;
        border-color: #334155 !important;
        width: 100% !important;
    }
    
    th {
        background-color: #1a1f3a !important;
        color: #ffffff !important;
        font-weight: 800 !important;
        padding: 15px !important;
        font-size: 1.05rem !important;
    }
    
    td {
        border-color: #334155 !important;
        padding: 12px !important;
        color: #e2e8f0 !important;
        font-weight: 600 !important;
    }
    
    /* Blockquote */
    blockquote {
        border-right: 5px solid #8b5cf6 !important;
        border-left: none !important;
        background-color: #1a1f3a !important;
        padding: 20px 25px !important;
        border-radius: 12px !important;
        color: #cbd5e1 !important;
        font-size: 1.05rem !important;
    }
    
    hr {
        margin: 45px 0 !important;
        border-color: #334155 !important;
        border-width: 2px !important;
    }
    </style>
""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════���═
# 🔧 دوال مساعدة محسّنة
# ══════════════════════════════════════════════════════════════

def clean_number(num):
    """تنظيف الأرقام من المسافات والرموز"""
    if pd.isna(num) or num == "" or str(num).lower() in ['لا يوجود', 'لا يوجد', 'nan']:
        return ""
    
    num_str = str(num).strip()
    # تحويل أرقام عربية لإنجليزية
    arabic_to_english = str.maketrans('٠١٢٣٤٥٦٧٨٩', '0123456789')
    num_str = num_str.translate(arabic_to_english)
    # إزالة كل شيء ماعدا الأرقام
    num_str = re.sub(r'[^0-9]', '', num_str)
    # إزالة الأصفار من البداية
    num_str = num_str.lstrip('0')
    
    return num_str

def safe_int(value, default=0):
    """تحويل آمن للأرقام الصحيحة"""
    try:
        if pd.isna(value) or value == "" or value is None:
            return default
        return int(float(str(value).strip()))
    except:
        return default

def safe_float(value, default=0.0):
    """تحويل آمن للأرقام العشرية"""
    try:
        if pd.isna(value) or value == "" or value is None:
            return default
        return float(str(value).strip())
    except:
        return default

def find_column(df, keywords):
    """البحث عن عمود بناءً على كلمات مفتاحية - محسّن"""
    for col in df.columns:
        col_lower = col.lower().strip()
        for keyword in keywords:
            if keyword.lower() in col_lower:
                return col
    return None

def get_value(row, keywords, default=""):
    """استخراج قيمة من صف بشكل آمن - محسّن"""
    for keyword in keywords:
        for col in row.index:
            col_lower = col.lower().strip()
            if keyword.lower() in col_lower:
                val = row[col]
                if pd.notna(val) and str(val).strip() and str(val).strip().lower() not in ['nan', '', 'لا يوجد', 'لا يوجود']:
                    return str(val).strip()
    return default

def calculate_age_from_birthdate(birth_date_str):
    """حساب العمر من تاريخ الميلاد"""
    try:
        # محاولة تحويل التاريخ
        birth_date = pd.to_datetime(birth_date_str)
        today = datetime.now()
        age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
        if 0 < age <= 20:  # معقول للفئة العمرية
            return age
    except:
        pass
    return 0

def normalize_categorical_value(value, mapping):
    """تطبيع القيم الفئوية من عدة احتمالات"""
    if pd.isna(value) or value == "":
        return ""
    
    value_str = str(value).strip().lower()
    
    # البحث عن تطابق في التعيين
    for key, variations in mapping.items():
        if any(var.lower() in value_str for var in variations):
            return key
    
    # إذا لم يتم العثور على تطابق، أعد القيمة الأصلية
    return str(value).strip()

# ═════════════���════════════════════════════════════════════════
# 🗺️ معايير التطبيع للقيم الفئوية
# ══════════════════════════════════════════════════════════════

PREVIOUS_EXPERIENCE_MAP = {
    "لعب اكثر من موسم": ["لعب اكثر من موسم", "لعب من قبل", "اكثر من موسم", "خبرة"],
    "لعب فترة قصيرة": ["لعب فترة قصيرة", "فترة قصيرة", "فترة محدودة"],
    "لم يلعب من قبل": ["لم يلعب", "لم يلعب من قبل", "بدون خبرة"]
}

PLAYING_DURATION_MAP = {
    "اكثر من سنه": ["اكثر من سنه", "أكثر من سنة", "سنة كاملة"],
    "من 6 شهور الي سنة": ["من 6 شهور", "6 شهور"],
    "من 3 الي 6 شهور": ["من 3 الي 6 شهور", "3 الي 6"],
    "لم يلعب": ["لم يلعب", ""]
}

MATCH_TYPE_MAP = {
    "مباريات رسمية": ["رسمية", "رسمي"],
    "مباريات ودية": ["ودية", "ودي"],
    "لا": ["لا", "بلا", ""]
}

MOTIVATION_MAP = {
    "احتراف مستقبلي": ["احتراف", "احترافي", "مستقبل"],
    "حب كرة القدم": ["حب", "موهبة"],
    "تحسين اللياقة البدنية": ["لياقة", "تحسين"],
    "الترفيه": ["ترفيه"]
}

FITNESS_LEVEL_MAP = {
    "أكثر من طبيعي": ["أكثر من طبيعي", "عالي", "جيد جدا"],
    "مناسب": ["مناسب", "متوسط", "طبيعي"],
    "أقل من طبيعي": ["أقل من طبيعي", "ضعيف", "منخفض"]
}

SKILLS_MAP = {
    "يتحكم بشكل جيد": ["يتحكم", "محترف", "جيد"],
    "يجري بسهولة": ["يجري", "سهولة"],
    "لا يعرف": ["لا يعرف", "لا يعرفها"]
}

RULES_MAP = {
    "يتحكم في القوانين": ["يتحكم", "يعرف"],
    "بسيط": ["بسيط", "يجري"],
    "لا يعرف قوانين كرة القدم": ["لا يعرف", "غير"]
}

# ══════════════════════════════════════════════════════════════
# ⚽ محرك التقييم الذكي - محسّن
# ══════════════════════════════════════════════════════════════

class PlayerEvaluationEngine:
    """محرك تقييم اللاعبين بناءً على معايير علمية عالمية"""
    
    # المعايير العالمية حسب العمر
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
        },
        "17+": {
            "height": {"min": 165, "ideal": 180, "max": 200},
            "weight": {"min": 55, "ideal": 75, "max": 95},
        }
    }
    
    @staticmethod
    def get_age_group(age):
        """تحديد الفئة العمرية"""
        if age <= 0:
            return "11-13"  # القيمة الافتراضية
        elif 8 <= age <= 10:
            return "8-10"
        elif 11 <= age <= 13:
            return "11-13"
        elif 14 <= age <= 16:
            return "14-16"
        else:
            return "17+"
    
    @staticmethod
    def calculate_physical_score(age, height, weight):
        """💪 التقييم البدني"""
        if age <= 0 or height <= 0:
            return 50  # درجة افتراضية
            
        age_group = PlayerEvaluationEngine.get_age_group(age)
        standards = PlayerEvaluationEngine.AGE_STANDARDS[age_group]
        
        # تقييم الطول (50 نقطة)
        height_score = 0
        if height >= standards["height"]["ideal"]:
            height_score = 50
        elif height >= standards["height"]["min"]:
            ratio = (height - standards["height"]["min"]) / (standards["height"]["ideal"] - standards["height"]["min"])
            height_score = 30 + (ratio * 20)
        else:
            height_score = 20
        
        # تقييم الوزن (50 نقطة)
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
        
        # الخبرة السابقة (40 نقطة)
        exp_map = {
            "لعب اكثر من موسم": 40,
            "لعب فترة قصيرة": 25,
            "لم يلعب من قبل": 10
        }
        exp_normalized = normalize_categorical_value(previous_exp, PREVIOUS_EXPERIENCE_MAP)
        score += exp_map.get(exp_normalized, 15)
        
        # مدة اللعب (30 نقطة)
        duration_map = {
            "اكثر من سنه": 30,
            "من 6 شهور الي سنة": 20,
            "من 3 الي 6 شهور": 15,
            "لم يلعب": 5
        }
        duration_normalized = normalize_categorical_value(duration, PLAYING_DURATION_MAP)
        score += duration_map.get(duration_normalized, 10)
        
        # المهارات (30 نقطة)
        skills_normalized = normalize_categorical_value(skills, SKILLS_MAP)
        skill_score = 15
        
        if "يتحكم" in skills_normalized or "محترف" in skills_normalized:
            skill_score += 15
        elif "يجري" in skills_normalized or "جيد" in skills_normalized:
            skill_score += 10
        elif "لا يعرف" in skills_normalized:
            skill_score += 2
        
        score += min(30, skill_score)
        
        return min(100, score)
    
    @staticmethod
    def calculate_mental_score(motivation, matches, parent_present):
        """🧠 التقييم الذهني"""
        score = 0
        
        # الدافع (50 نقطة)
        motivation_map = {
            "احتراف مستقبلي": 50,
            "حب كرة القدم": 40,
            "تحسين اللياقة البدنية": 30,
            "الترفيه": 25
        }
        motivation_normalized = normalize_categorical_value(motivation, MOTIVATION_MAP)
        score += motivation_map.get(motivation_normalized, 30)
        
        # المباريات (30 نقطة)
        match_normalized = normalize_categorical_value(matches, MATCH_TYPE_MAP)
        if "رسمية" in match_normalized:
            score += 30
        elif "ودية" in match_normalized:
            score += 20
        else:
            score += 10
        
        # حضور ولي الأمر (20 نقطة)
        parent_normalized = str(parent_present).strip().lower()
        if "نعم" in parent_normalized:
            score += 20
        elif "ربما" in parent_normalized:
            score += 10
        else:
            score += 5
        
        return min(100, score)
    
    @staticmethod
    def calculate_tactical_score(knows_rules, fitness_level, registered_in_club):
        """🎯 التقييم التكتيكي"""
        score = 0
        
        # معرفة القوانين (40 نقطة)
        rules_normalized = normalize_categorical_value(knows_rules, RULES_MAP)
        if "يتحكم" in rules_normalized or "يعرف" in rules_normalized:
            score += 40
        elif "بسيط" in rules_normalized or "يجري" in rules_normalized:
            score += 25
        elif "لا يعرف" in rules_normalized:
            score += 10
        else:
            score += 20
        
        # مستوى اللياقة (35 نقطة)
        fitness_normalized = normalize_categorical_value(fitness_level, FITNESS_LEVEL_MAP)
        fitness_map = {
            "أكثر من طبيعي": 35,
            "مناسب": 30,
            "أقل من طبيعي": 15
        }
        score += fitness_map.get(fitness_normalized, 25)
        
        # التسجيل في نادي (25 نقطة)
        club_normalized = str(registered_in_club).strip().lower()
        if "نعم" in club_normalized:
            score += 25
        else:
            score += 10
        
        return min(100, score)
    
    @staticmethod
    def get_level_category(score):
        """تحديد المستوى بناءً على الدرجة"""
        if score >= 85:
            return "ممتاز ⭐⭐⭐", "excellent"
        elif score >= 70:
            return "جيد جداً ⭐⭐", "very-good"
        elif score >= 50:
            return "جيد ⭐", "good"
        else:
            return "يحتاج تطوير 📈", "needs-improvement"
    
    @staticmethod
    def generate_report(player_name, age, scores):
        """📄 توليد تقرير احترافي كامل"""
        
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
- **الاسم:** {player_name}
- **السن:** {age} سنة
- **التقييم العام:** {avg_score:.0f}/100 - **{overall_level}**

---

### 💚 التحليل التفصيلي

عزيزي ولي الأمر،

يسعدنا تقديم تقرير تقييم شامل لابنك **{player_name}** بناءً على معايير علمية عالمية.

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
- مكافأة التقدم والمجهود
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

ابنك **{player_name}** يمتلك أساساً **{overall_level}** ويظهر إمكانيات واعدة. 

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

*تم إنشاء هذا التقرير بواسطة نظام EDUVIA الرياضي الذكي - {datetime.now().strftime('%Y-%m-%d')}*
"""
        
        return report

# ══════════════════════════════════════════════════════════════
# 🔌 الاتصال بقاعدة البيانات
# ══════════════════════════════���═══════════════════════════════

@st.cache_resource(show_spinner="🔄 جاري الاتصال بقاعدة البيانات...")
def get_sheet():
    """الاتصال بـ Google Sheets"""
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
    # قراءة البيانات
    data = ws.get_all_records()
    if not data:
        st.info("📭 الورقة فارغة")
        st.stop()
    
    df = pd.DataFrame(data)
    df.columns = df.columns.str.strip()
    
    # تنظيف أعمدة الأرقام
    phone_cols = [col for col in df.columns if 'موبايل' in col.lower() or 'واتساب' in col.lower()]
    for col in phone_cols:
        df[f'{col}_clean'] = df[col].apply(clean_number)
    
    # التبويبات
    tab1, tab2 = st.tabs(["🔍 البحث عن طالب", "📊 إحصائيات عامة"])
    
    # ═══════════════════════════════════════════════════════════
    # TAB 1: البحث عن الطلاب
    # ═══════════════════════════════════════════════════════════
    with tab1:
        st.subheader("ابحث عن طالب للحصول على تقييمه الكامل")
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            search = st.text_input(
                "اسم الطفل أو رقم الموبايل",
                placeholder="مثال: محمد طارق  أو  01229920187",
                key="search"
            ).strip()
        
        with col2:
            st.write("")
            st.write("")
            search_btn = st.button("🔍 بحث", type="primary", use_container_width=True)
        
        if search_btn and search:
            search_clean = clean_number(search)
            
            # البحث في الأسماء
            name_col = find_column(df, ['اسم'])
            mask = df[name_col].astype(str).str.contains(search, case=False, na=False) if name_col else pd.Series([False] * len(df))
            
            # البحث في الأرقام
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
                    # استخراج البيانات
                    student_name = get_value(row, ['اسم'], 'طالب')
                    
                    # حساب العمر من تاريخ الميلاد أو من حقل السن
                    birth_date_col = find_column(df, ['ميلاد', 'تاريخ'])
                    age = safe_int(get_value(row, ['السن', 'العمر'], '0'))
                    
                    if age <= 0 and birth_date_col:
                        age = calculate_age_from_birthdate(row[birth_date_col])
                    
                    if age <= 0:
                        age = 12  # القيمة الافتراضية
                    
                    with st.expander(f"📋 {student_name} ({age} سنة) - اضغط للتفاصيل", expanded=True):
                        
                        # Header الطالب
                        st.markdown(f"""
                        <div class="student-header">
                            <h2 class="student-name">⭐ {student_name}</h2>
                            <p class="student-info">العمر: {age} سنة | التقييم الشامل</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # استخراج البيانات للتقييم
                        height = safe_float(get_value(row, ['طول', 'سنتيمتر'], '0'))
                        weight = safe_float(get_value(row, ['وزن', 'كيلوجرام'], '0'))
                        
                        # حساب الدرجات مع معالجة البيانات الفارغة
                        scores = {
                            "physical": PlayerEvaluationEngine.calculate_physical_score(
                                age, height, weight
                            ),
                            "technical": PlayerEvaluationEngine.calculate_technical_score(
                                get_value(row, ['أكاديمية', 'لعب']),
                                get_value(row, ['مدة', 'لعب']),
                                get_value(row, ['بنطبق', 'مهارات', 'يجري'])
                            ),
                            "mental": PlayerEvaluationEngine.calculate_mental_score(
                                get_value(row, ['انضمام', 'سبب']),
                                get_value(row, ['مباريات']),
                                get_value(row, ['متواجد', 'أمر'])
                            ),
                            "tactical": PlayerEvaluationEngine.calculate_tactical_score(
                                get_value(row, ['قوانين', 'بنطبق']),
                                get_value(row, ['تقدير', 'لياقة']),
                                get_value(row, ['نادي'])
                            )
                        }
                        
                        # عرض البطا��ات
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
                        report = PlayerEvaluationEngine.generate_report(student_name, age, scores)
                        st.markdown(report)
                        
                        # زر التحميل
                        st.download_button(
                            label="📥 تحميل التقرير كملف نصي",
                            data=report,
                            file_name=f"تقرير_{student_name.replace(' ', '_')}.txt",
                            mime="text/plain",
                            use_container_width=True,
                            key=f"download_{idx}_{hash(student_name + str(age))}"
                        )
    
    # ═══════════════════════════════════════════════════════════
    # TAB 2: الإحصائيات
    # ═══════════════════════════════════════════════════════════
    with tab2:
        st.subheader("📊 إحصائيات عامة")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("إجمالي الطلاب", len(df))
        
        with col2:
            # حساب متوسط العمر بشكل آمن
            ages = []
            birth_date_col = find_column(df, ['ميلاد', 'تاريخ'])
            
            for _, row in df.iterrows():
                age = safe_int(get_value(row, ['السن', 'العمر'], '0'))
                
                if age <= 0 and birth_date_col:
                    age = calculate_age_from_birthdate(row[birth_date_col])
                
                if age > 0 and age <= 20:  # معقول
                    ages.append(age)
            
            avg_age = sum(ages) / len(ages) if ages else 0
            st.metric("متوسط العمر", f"{avg_age:.1f} سنة")
        
        with col3:
            # حساب عدد من لديهم خبرة
            exp_col = find_column(df, ['أكاديمية', 'لعب'])
            if exp_col:
                has_exp = df[exp_col].astype(str).str.contains('لعب', na=False, case=False).sum()
            else:
                has_exp = 0
            st.metric("لديهم خبرة سابقة", f"{has_exp} طالب")

except Exception as e:
    st.error(f"❌ خطأ في قراءة البيانات: {str(e)}")
    st.exception(e)

st.markdown("---")
st.caption("⚽ نظام EDUVIA الرياضي الذكي | تطوير مستمر")
