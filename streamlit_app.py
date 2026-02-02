import streamlit as st
import gspread
from google.oauth2 import service_account
import pandas as pd

# ──── إعدادات الصفحة ────
st.set_page_config(
    page_title="البحث عن بيانات الطلاب",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# إخفاء عناصر واجهة Streamlit الافتراضية
hide_st_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
"""
st.markdown(hide_st_style, unsafe_allow_html=True)

# دعم الاتجاه من اليمين لليسار + خط عربي
st.markdown("""
    <style>
    .stApp {
        direction: rtl;
        text-align: right;
        font-family: 'Arial', 'Tajawal', sans-serif;
    }
    .stTextInput > div > div > label {
        width: 100%;
    }
    </style>
""", unsafe_allow_html=True)

st.title("البحث عن بيانات الطلاب")

# ──── دالة الاتصال بالـ Sheet (cache للأداء) ────
@st.cache_resource(show_spinner="جاري الاتصال بقاعدة البيانات...")
def get_google_sheet():
    try:
        # ──── استخدام الـ secrets بالشكل الصحيح ────
        creds_info = st.secrets["gcp_service_account"]
        
        creds = service_account.Credentials.from_service_account_info(
            creds_info,
            scopes=[
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive"   # مهم لو هتكتب بيانات في المستقبل
            ]
        )

        client = gspread.authorize(creds)

        # جيب الـ sheet_id من الـ secrets
        sheet_id = st.secrets["gsheet"]["sheet_id"]   # أو st.secrets["sheet_id"] لو حاططها كده

        spreadsheet = client.open_by_key(sheet_id)
        worksheet = spreadsheet.sheet1   # أو spreadsheet.worksheet("اسم الورقة")

        return worksheet

    except Exception as e:
        st.error(f"خطأ في الاتصال بـ Google Sheet: {str(e)}")
        st.info("""
        الحلول الشائعة:
        • تأكد من إضافة الـ service account email كـ Editor في الـ Sheet (Share)
        • تأكد من اسماء المفاتيح في Secrets متطابقة تمامًا
        • انتظر 1-2 دقيقة بعد حفظ الـ Secrets
        """)
        return None

# ──── الاتصال ────
sheet = get_google_sheet()

if sheet:
    try:
        # جلب البيانات
        data = sheet.get_all_records(expected_headers=None)  # يتعامل مع الأعمدة حتى لو مش كاملة
        if not data:
            st.info("الورقة فارغة حاليًا.")
        else:
            df = pd.DataFrame(data)

            st.write("─" * 60)
            st.subheader("ابحث عن طالب")

            search_term = st.text_input(
                "أدخل اسم الطالب أو رقم الموبايل للبحث:",
                key="search_input",
                placeholder="اكتب الاسم أو الرقم..."
            )

            if st.button("بحث", type="primary"):
                if search_term.strip():
                    # بحث case-insensitive + partial match
                    mask_name = df['اسم الطفل كامل'].astype(str).str.contains(search_term, case=False, na=False)
                    mask_phone = df['رقم الموبايل ( واتساب )'].astype(str).str.contains(search_term, case=False, na=False)
                    
                    results = df[mask_name | mask_phone]

                    if not results.empty:
                        st.success(f"تم العثور على {len(results)} نتيجة")
                        st.dataframe(
                            results,
                            use_container_width=True,
                            hide_index=True
                        )
                    else:
                        st.warning("لم يتم العثور على أي نتائج مطابقة.")
                else:
                    st.info("الرجاء إدخال كلمة بحث.")
    except Exception as e:
        st.error(f"خطأ أثناء قراءة البيانات: {e}")
        st.info("تأكد من وجود الأعمدة المطلوبة: 'اسم الطفل كامل' و 'رقم الموبايل ( واتساب )'")
else:
    st.warning("تعذر الاتصال بقاعدة البيانات. تحقق من إعدادات Secrets والصلاحيات.")

st.markdown("---")
st.caption("تم تطوير التطبيق باستخدام Streamlit & Google Sheets")
