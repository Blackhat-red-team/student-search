import streamlit as st
import gspread
from google.oauth2 import service_account
import pandas as pd

# ──── إعدادات الصفحة ────
st.set_page_config(
    page_title="البحث عن بيانات الطلاب",
    layout="wide",               # أفضل لعرض الجداول
    initial_sidebar_state="collapsed"
)

# إخفاء عناصر Streamlit الافتراضية
hide_st_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
"""
st.markdown(hide_st_style, unsafe_allow_html=True)

# دعم الاتجاه من اليمين لليسار + خط عربي مناسب
st.markdown("""
    <style>
    .stApp {
        direction: rtl;
        text-align: right;
        font-family: 'Tajawal', 'Arial', sans-serif;
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
        # ──── الـ credentials من secrets ────
        creds_info = st.secrets["gcp_service_account"]
        
        creds = service_account.Credentials.from_service_account_info(
            creds_info,
            scopes=[
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive"
            ]
        )

        client = gspread.authorize(creds)

        # جلب الـ sheet_id
        sheet_id = st.secrets["gsheet"]["sheet_id"]

        spreadsheet = client.open_by_key(sheet_id)
        worksheet = spreadsheet.sheet1   # ← غيّر إلى .worksheet("اسم الورقة") لو مش Sheet1

        return worksheet

    except Exception as e:
        st.error(f"خطأ في الاتصال: {str(e)}")
        st.info("تأكد من:\n• إضافة الإيميل كـ Editor في الشيت\n• أسماء المفاتيح في Secrets صحيحة\n• انتظر 1-2 دقيقة بعد الحفظ")
        return None

# ──── الاتصال ────
sheet = get_google_sheet()

if sheet:
    try:
        # جلب البيانات
        raw_data = sheet.get_all_records()

        if not raw_data:
            st.info("الورقة فارغة حاليًا (لا توجد صفوف بعد العنوان).")
        else:
            # تحويل إلى DataFrame
            df = pd.DataFrame(raw_data)

            # ──── تنظيف أسماء الأعمدة (إزالة المسافات الزائدة من البداية والنهاية) ────
            df.columns = df.columns.str.strip()

            # عرض أسماء الأعمدة للتشخيص (احذف السطرين دول بعد ما تتأكد)
            st.caption("أسماء الأعمدة بعد التنظيف (للتحقق):")
            st.write(list(df.columns))

            st.write("─" * 70)
            st.subheader("ابحث عن طالب")

            search_term = st.text_input(
                "أدخل اسم الطالب أو رقم الموبايل (واتساب):",
                key="search_input",
                placeholder="اكتب الاسم أو الرقم..."
            ).strip()

            if st.button("بحث", type="primary"):
                if search_term:
                    # البحث في الأعمدة المناسبة بعد التنظيف
                    name_col_candidates = [col for col in df.columns if 'اسم الطفل' in col]
                    phone_col_candidates = [col for col in df.columns if 'موبايل' in col and 'واتساب' in col]

                    if not name_col_candidates or not phone_col_candidates:
                        st.error("لم يتم العثور على أعمدة تحتوي على 'اسم الطفل' أو 'موبايل واتساب' بعد التنظيف")
                        st.write("الأعمدة المتاحة:", list(df.columns))
                    else:
                        name_col = name_col_candidates[0]     # أول عمود يطابق
                        phone_col = phone_col_candidates[0]

                        # البحث (case-insensitive + partial match)
                        mask = (
                            df[name_col].astype(str).str.contains(search_term, case=False, na=False) |
                            df[phone_col].astype(str).str.contains(search_term, case=False, na=False)
                        )

                        results = df[mask]

                        if not results.empty:
                            st.success(f"تم العثور على {len(results)} نتيجة")
                            st.dataframe(
                                results,
                                use_container_width=True,
                                hide_index=True
                            )
                        else:
                            st.warning("لم يتم العثور على نتائج مطابقة.")
                else:
                    st.info("الرجاء إدخال كلمة بحث.")
    except Exception as e:
        st.error(f"خطأ أثناء قراءة أو معالجة البيانات: {str(e)}")
        st.info("تحقق من:\n• وجود بيانات بعد صف العناوين\n• صيغة التواريخ / الأرقام صحيحة")
else:
    st.warning("تعذر الاتصال بقاعدة البيانات. راجع إعدادات Secrets والصلاحيات.")

st.markdown("---")
st.caption("تطبيق بحث بيانات الطلاب • Streamlit + Google Sheets • 2026")
