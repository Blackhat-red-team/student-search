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

st.title("البحث عن بيانات الطلاب")

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

    # تنظيف أسماء الأعمدة (مهم جدًا في حالتك)
    df.columns = df.columns.str.strip().str.replace(r'\s+', ' ', regex=True)

    # عرض الأعمدة للتأكد (احذف هذا بعد ما تتأكد)
    with st.expander("أسماء الأعمدة الحقيقية بعد التنظيف"):
        st.code("\n".join(df.columns.tolist()))

    st.divider()
    st.subheader("ابحث عن طالب")

    search = st.text_input(
        "اسم الطفل أو رقم الواتساب أو الرقم البديل",
        placeholder="مثال: تيم الحسن   أو   1229920187   أو   01287975713",
        key="searchbox"
    ).strip()

    if st.button("بحث", type="primary"):
        if not search:
            st.info("اكتب اسم أو رقم")
            st.stop()

        # تنظيف نص البحث
        search_clean = re.sub(r'[^0-9\u0660-\u0669]', '', search)  # أرقام فقط (عربي + إنجليزي)

        # الأعمدة المستهدفة (استخدمنا contains عشان المسافات الزيادة)
        name_candidates = [c for c in df.columns if 'اسم الطفل' in c]
        whatsapp_col = next((c for c in df.columns if 'واتساب' in c), None)
        alt_phone_col = next((c for c in df.columns if 'بديل' in c and 'موبايل' in c), None)

        if not name_candidates or not whatsapp_col:
            st.error("مشكلة في أسماء الأعمدة — تحقق من الـ expander أعلاه")
            st.stop()

        name_col = name_candidates[0]

        # تنظيف أعمدة الأرقام بشكل قوي
        for col in [whatsapp_col, alt_phone_col]:
            if col and col in df.columns:
                df[col] = (
                    df[col]
                    .astype(str)
                    .str.strip()
                    .str.replace(r'[^0-9\u0660-\u0669]', '', regex=True)   # أرقام فقط
                    .str.replace(r'^0+', '', regex=True)                   # إزالة صفر البداية
                )

        # البحث
        mask_name  = df[name_col].astype(str).str.contains(search, case=False, na=False)

        mask_whatsapp = False
        if whatsapp_col:
            mask_whatsapp = df[whatsapp_col].str.contains(search_clean, na=False)

        mask_alt = False
        if alt_phone_col:
            mask_alt = df[alt_phone_col].str.contains(search_clean, na=False)

        results = df[mask_name | mask_whatsapp | mask_alt]

        if results.empty:
            st.warning("ما فيش نتايج مطابقة")
        else:
            st.success(f"تم العثور على {len(results)} نتيجة")
            st.dataframe(
                results,
                use_container_width=True,
                hide_index=True
            )

except Exception as e:
    st.error("خطأ أثناء قراءة البيانات")
    st.exception(e)

st.markdown("---")
st.caption("تطبيق بحث بيانات الطلاب • Streamlit + Google Sheets")
