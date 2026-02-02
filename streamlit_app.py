import streamlit as st
import gspread
from google.oauth2 import service_account
import pandas as pd
import re

# ──── إعداد الصفحة ────
st.set_page_config(page_title="البحث عن بيانات الطلاب", layout="wide", initial_sidebar_state="collapsed")

# إخفاء عناصر Streamlit الافتراضية + اتجاه عربي
st.markdown("""
    <style>
    #MainMenu, footer, header {visibility: hidden;}
    .stApp {direction: rtl; text-align: right; font-family: 'Tajawal', Arial, sans-serif;}
    .stTextInput > div > div > label {width: 100%;}
    </style>
""", unsafe_allow_html=True)

st.title("🔍 البحث عن بيانات الطلاب")

# ──── دالة تنظيف الأرقام ────
def clean_number(num):
    """تنظيف الأرقام من أي رموز أو مسافات وتحويل الأرقام العربية للإنجليزية"""
    if pd.isna(num):
        return ""
    
    num_str = str(num).strip()
    
    # تحويل الأرقام العربية للإنجليزية
    arabic_to_english = str.maketrans('٠١٢٣٤٥٦٧٨٩', '0123456789')
    num_str = num_str.translate(arabic_to_english)
    
    # إزالة كل شيء ماعدا الأرقام
    num_str = re.sub(r'[^0-9]', '', num_str)
    
    # إزالة الأصفار من البداية
    num_str = num_str.lstrip('0')
    
    return num_str

# ──── الاتصال بـ Google Sheet ────
@st.cache_resource(show_spinner="جاري الاتصال...")
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
        st.error(f"خطأ في الاتصال: {str(e)}")
        return None

ws = get_sheet()

if not ws:
    st.stop()

# ──── قراءة + تنظيف ────
try:
    data = ws.get_all_records()
    if not data:
        st.info("الورقة فارغة أو بدون بيانات بعد صف العناوين.")
        st.stop()

    df = pd.DataFrame(data)

    # تنظيف أسماء الأعمدة
    df.columns = df.columns.str.strip().str.replace(r'\s+', ' ', regex=True)

    # البحث عن الأعمدة المهمة
    name_col = None
    whatsapp_col = None
    alt_phone_col = None
    
    for col in df.columns:
        col_lower = col.lower()
        if 'اسم' in col and 'طفل' in col:
            name_col = col
        elif 'واتساب' in col or 'whatsapp' in col_lower:
            whatsapp_col = col
        elif 'بديل' in col or 'آخر' in col:
            alt_phone_col = col

    if not name_col:
        st.error("⚠️ لم يتم العثور على عمود 'اسم الطفل'")
        st.stop()

    # إنشاء أعمدة منظفة للأرقام
    if whatsapp_col:
        df['whatsapp_clean'] = df[whatsapp_col].apply(clean_number)
    
    if alt_phone_col:
        df['alt_phone_clean'] = df[alt_phone_col].apply(clean_number)

    # عرض معلومات للتأكد
    with st.expander("📋 معلومات الأعمدة"):
        st.write(f"**عمود الاسم:** {name_col}")
        st.write(f"**عمود الواتساب:** {whatsapp_col}")
        st.write(f"**عمود الموبايل البديل:** {alt_phone_col}")
        st.write(f"**إجمالي الصفوف:** {len(df)}")

    st.divider()
    st.subheader("ابحث عن طالب")

    search = st.text_input(
        "اسم الطفل أو رقم الواتساب أو الرقم البديل",
        placeholder="مثال: تيم الحسن   أو   1229920187   أو   01287975713",
        key="searchbox"
    ).strip()

    if st.button("🔍 بحث", type="primary", use_container_width=True):
        if not search:
            st.info("⚠️ من فضلك اكتب اسم أو رقم للبحث")
            st.stop()

        # تنظيف نص البحث
        search_clean = clean_number(search)
        
        # البحث بالاسم
        mask_name = df[name_col].astype(str).str.contains(search, case=False, na=False)

        # البحث بالأرقام
        mask_whatsapp = False
        mask_alt = False
        
        if search_clean:  # إذا كان البحث يحتوي على أرقام
            if whatsapp_col and 'whatsapp_clean' in df.columns:
                mask_whatsapp = df['whatsapp_clean'].str.contains(search_clean, na=False, regex=False)
            
            if alt_phone_col and 'alt_phone_clean' in df.columns:
                mask_alt = df['alt_phone_clean'].str.contains(search_clean, na=False, regex=False)

        # دمج النتائج
        results = df[mask_name | mask_whatsapp | mask_alt]

        if results.empty:
            st.warning("❌ لم يتم العثور على نتائج مطابقة")
            st.info(f"**نص البحث المُدخل:** {search}")
            if search_clean:
                st.info(f"**الرقم بعد التنظيف:** {search_clean}")
        else:
            st.success(f"✅ تم العثور على {len(results)} نتيجة")
            
            # إخفاء الأعمدة المساعدة من العرض
            display_cols = [col for col in results.columns if not col.endswith('_clean')]
            
            st.dataframe(
                results[display_cols],
                use_container_width=True,
                hide_index=True
            )

except Exception as e:
    st.error("❌ خطأ أثناء قراءة البيانات")
    st.exception(e)

st.markdown("---")
st.caption("تطبيق بحث بيانات الطلاب • Streamlit + Google Sheets")
