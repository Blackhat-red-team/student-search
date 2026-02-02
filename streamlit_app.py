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
# 🎨 التنسيقات والأنماط
# ══════════════════════════════════════════════════════════════
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;900&display=swap');
    
    #MainMenu, footer, header {visibility: hidden;}
    
    .stApp {
        direction: rtl !important;
        text-align: right !important;
        font-family: 'Cairo', 'Segoe UI', Arial, sans-serif !important;
        background: #0a0e27;
    }
    
    div, p, span, h1, h2, h3, label, input, textarea, select {
        direction: rtl !important;
        text-align: right !important;
        font-family: 'Cairo', sans-serif !important;
    }
    
    h1 {
        color: #ffffff !important;
        text-align: center !important;
        margin-bottom: 5px !important;
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
    
    .stTabs {
        direction: rtl !important;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
        direction: rtl !important;
        background-color: transparent;
    }
    
    .stTabs [data-baseweb="tab"] {
        direction: rtl !important;
        text-align: right !important;
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
        margin-bottom: 10px !important;
    }
    
    .stButton > button {
        width: 100% !important;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 14px !important;
        padding: 16px 28px !important;
        font-size: 1.15rem !important;
        font-weight: 800 !important;
        cursor: pointer !important;
        transition: all 0.3s !important;
        box-shadow: 0 6px 16px rgba(102, 126, 234, 0.35) !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-3px) !important;
        box-shadow: 0 10px 25px rgba(102, 126, 234, 0.5) !important;
    }
    
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
        letter-spacing: 0.5px;
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
        transition: all 0.3s !important;
    }
    
    .stDownloadButton > button:hover {
        transform: translateY(-3px) !important;
        box-shadow: 0 10px 25px rgba(5, 150, 105, 0.5) !important;
    }
    
    hr {
        margin: 45px 0 !important;
        border-color: #334155 !important;
        border-width: 2px !important;
    }
    
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
    
    blockquote {
        border-right: 5px solid #8b5cf6 !important;
        border-left: none !important;
        background-color: #1a1f3a !important;
        padding: 20px 25px !important;
        border-radius: 12px !important;
        color: #cbd5e1 !important;
        font-size: 1.05rem !important;
        line-height: 1.8 !important;
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
        text-shadow: 0 2px 8px rgba(0,0,0,0.3);
    }
    
    .student-info {
        font-size: 1.2rem;
        color: #cbd5e1;
        text-align: center;
        margin-top: 10px;
        font-weight: 600;
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

def get_student_name(row):
    """استخراج اسم الطالب بشكل صحيح من أي عمود ممكن"""
    # جرب كل احتمالات أسماء الأعمدة
    possible_columns = [
        'اسم الطفل  كامل ',  # مع مسافات زيادة
        'اسم الطفل كامل',
        'اسم الطفل  كامل',
        'اسم الطفل',
        'الاسم الكامل',
        'الاسم'
    ]
    
    for col in possible_columns:
        if col in row.index:
            value = row[col]
            if pd.notna(value) and str(value).strip() and str(value).strip().lower() != 'nan':
                return str(value).strip()
    
    # لو مالقيناش، جرب أي عمود فيه كلمة "اسم"
    for col in row.index:
        if 'اسم' in col and 'ولي' not in col and 'نادي' not in col:
            value = row[col]
            if pd.notna(value) and str(value).strip() and str(value).strip().lower() != 'nan':
                return str(value).strip()
    
    return "طالب"

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
    def generate_report(player_name, player_data, scores):
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
                    # استخراج الاسم بشكل صحيح
                    student_name = get_student_name(row)
                    age = safe_int(row.get('السن', 0))
                    
                    with st.expander(f"📋 {student_name} ({age} سنة) - اضغط للتفاصيل", expanded=True):
                        
                        # عرض اسم الطالب بشكل بارز في Header
                        st.markdown(f"""
                        <div class="student-header">
                            <h2 class="student-name">⭐ {student_name}</h2>
                            <p class="student-info">العمر: {age} سنة | التقييم الشامل</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
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
                        
                        # عرض البطاقات
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
                        
                        # التقرير الكامل مع اسم الطالب الصحيح
                        report = PlayerEvaluationEngine.generate_report(student_name, row.to_dict(), scores)
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
