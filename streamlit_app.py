import streamlit as st
import gspread
from google.oauth2 import service_account
import pandas as pd
import re

# ──── إعداد الصفحة ────
st.set_page_config(
    page_title="البحث عن بيانات الطلاب",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# إخفاء عناصر الواجهة الافتراضية
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stApp {
        direction: rtl;
        text-align: right;
        font-family: 'Tajawal', 'Arial', sans-serif;
    }
    .stTextInput > div > div > label {width: 100%;}
    </style>
""", unsafe_allow_html=True)

st.title("البحث عن بيانات الطلاب")

# ──── الاتصال بـ Google Sheet (مع cache) ────
@st.cache_resource(show_spinner="جاري الاتصال بقاعدة البيانات...")
def load_worksheet():
    try:
        creds = service_account.Credentials.from_service_account_info(
            st.secrets["gcp_service_account"],
            scopes=[
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive"
            ]
        )
        client = gspread.authorize(creds)
        sheet_id = st.secrets["gsheet"]["sheet_id"]
        spreadsheet = client.open_by_key(sheet_id)
        return spreadsheet.sheet1   # ← غيّر إلى spreadsheet.worksheet("اسم الورقة") إذا لزم

    except Exception as e:
        st.error(f"فشل الاتصال بـ Google Sheets\n{str(e)}")
        st.info("التحقق من:\n• إيميل الـ service account مضاف كـ Editor في الشيت\n• أسماء المفاتيح في Secrets مطابقة")
        return None


# ──── تحميل البيانات ────
ws = load_worksheet()

if ws is None:
    st.stop()

try:
    raw_rows = ws.get_all_records()

    if not raw_rows:
        st.info("لا توجد بيانات بعد صف العناوين.")
        st.stop()

    df = pd.DataFrame(raw_rows)

    # تنظيف أسماء الأعمدة
    df.columns = (
        df.columns
        .str.strip()
        .str.replace(r'\s+', ' ', regex=True)
        .str.replace(r'[\(\)]', '', regex=True)   # إزالة الأقواس إذا أردت
    )

    # ──── عرض أسماء الأعمدة للتصحيح (يمكنك تعليقه لاحقًا) ────
    with st.expander("أسماء الأعمدة بعد التنظيف (للتحقق فقط)", expanded=False):
        st.code("\n".join(f"• {col}" for col in df.columns), language="text")

    st.divider()
    st.subheader("ابحث عن طالب")

    search_text = st.text_input(
        "اسم الطالب أو رقم الموبايل (واتساب)",
        placeholder="اكتب الاسم أو الرقم بدون مسافات أو +",
        key="search_input"
    ).strip()

    col1, col2 = st.columns([3, 1])
    with col2:
        search_button = st.button("بحث", type="primary", use_container_width=True)

    if search_button and search_text:
        # تنظيف نص البحث
        search_clean = re.sub(r'[^0-9]', '', search_text)  # أرقام فقط

        # تنظيف أعمدة البحث
        name_candidates = [c for c in df.columns if 'اسم الطفل' in c]
        phone_candidates = [c for c in df.columns if 'موبايل' in c and 'واتساب' in c]

        if not name_candidates or not phone_candidates:
            st.error("لم يتم العثور على أعمدة البحث المتوقعة")
            st.write("الأعمدة المتاحة:", list(df.columns))
            st.stop()

        name_col = name_candidates[0]
        phone_col = phone_candidates[0]

        # تنظيف عمود الرقم بشكل شامل
        df[phone_col] = (
            df[phone_col]
            .astype(str)
            .str.strip()
            .str.replace(r'[^0-9]', '', regex=True)          # إبقاء الأرقام فقط
            .str.replace(r'^0+', '', regex=True)             # إزالة الصفر في البداية إن وجد
        )

        # البحث
        mask_name = (
            df[name_col]
            .astype(str)
            .str.contains(search_text, case=False, na=False)
        )

        mask_phone = (
            df[phone_col]
            .str.contains(search_clean, na=False)
            | df[phone_col].str.endswith(search_clean)      # نهاية الرقم
            | df[phone_col].str.startswith(search_clean)    # بداية الرقم
        )

        results = df[mask_name | mask_phone].copy()

        if results.empty:
            st.warning("لم يتم العثور على نتائج مطابقة.")
        else:
            st.success(f"تم العثور على {len(results)} نتيجة")
            st.dataframe(
                results,
                use_container_width=True,
                hide_index=True,
                column_config={
                    col: st.column_config.TextColumn(col, width="medium")
                    for col in results.select_dtypes(include='object').columns
                }
            )

except Exception as e:
    st.error("حدث خطأ أثناء معالجة البيانات")
    st.exception(e)

st.markdown("---")
st.caption("تطبيق بحث بيانات الطلاب • Streamlit + Google Sheets")
