import streamlit as st
import gspread
from google.oauth2 import service_account
import pandas as pd

# إعداد الصفحة
st.set_page_config(
    page_title="البحث عن بيانات الطلاب",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# إخفاء عناصر الـ Streamlit الافتراضية
hide_st_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
"""
st.markdown(hide_st_style, unsafe_allow_html=True)

# دعم الاتجاه من اليمين لليسار
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

# ────────────────────────────────────────────────
# دالة الاتصال بـ Google Sheet (مع cache)
# ────────────────────────────────────────────────
@st.cache_resource(show_spinner="جاري الاتصال بقاعدة البيانات...")
def get_google_sheet():
    try:
        creds_info = st.secrets["gcp_service_account"]
        
        creds = service_account.Credentials.from_service_account_info(
            creds_info,
            scopes=[
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive"
            ]
        )

        client = gspread.authorize(creds)
        
        sheet_id = st.secrets["gsheet"]["sheet_id"]
        
        spreadsheet = client.open_by_key(sheet_id)
        worksheet = spreadsheet.sheet1  # أو spreadsheet.worksheet("اسم الورقة")

        return worksheet

    except Exception as e:
        st.error(f"خطأ في الاتصال بـ Google Sheet: {str(e)}")
        st.info("تأكد من:\n• إضافة بريد الـ service account كـ Editor في الشيت\n• أسماء المفاتيح في secrets.toml صحيحة")
        return None

# ────────────────────────────────────────────────
# جلب البيانات
# ────────────────────────────────────────────────
sheet = get_google_sheet()

if sheet:
    try:
        raw_data = sheet.get_all_records()
        
        if not raw_data:
            st.info("لا توجد بيانات في الورقة بعد صف العناوين.")
        else:
            df = pd.DataFrame(raw_data)
            
            # تنظيف أسماء الأعمدة من المسافات الزائدة
            df.columns = df.columns.str.strip()
            
            # عرض أسماء الأعمدة للتشخيص (احذف هذا الجزء بعد التأكد)
            with st.expander("أسماء الأعمدة المكتشفة (للتحقق فقط)"):
                st.write(list(df.columns))
            
            st.markdown("---")
            st.subheader("ابحث عن طالب")

            search_term = st.text_input(
                "أدخل اسم الطالب أو رقم الموبايل (واتساب):",
                placeholder="اكتب الاسم أو الرقم...",
                key="search_box"
            ).strip()

            if st.button("بحث", type="primary"):
                if not search_term:
                    st.info("الرجاء إدخال كلمة بحث.")
                else:
                    # البحث في الأعمدة المناسبة
                    name_candidates = [col for col in df.columns if 'اسم الطفل' in col]
                    phone_candidates = [col for col in df.columns if 'موبايل' in col and 'واتساب' in col]

                    if not name_candidates or not phone_candidates:
                        st.error("لم يتم العثور على أعمدة تحتوي على 'اسم الطفل' أو 'رقم الموبايل واتساب'")
                        st.write("الأعمدة المتاحة:", list(df.columns))
                    else:
                        name_col = name_candidates[0]
                        phone_col = phone_candidates[0]

                        mask = (
                            df[name_col].astype(str).str.contains(search_term, case=False, na=False) |
                            df[phone_col].astype(str).str.contains(search_term, case=False, na=False)
                        )

                        results = df[mask]

                        if results.empty:
                            st.warning("لم يتم العثور على نتائج مطابقة.")
                        else:
                            st.success(f"تم العثور على {len(results)} نتيجة")
                            st.dataframe(
                                results,
                                use_container_width=True,
                                hide_index=True
                            )

    except Exception as e:
        st.error(f"خطأ أثناء قراءة البيانات: {str(e)}")
        st.info("تحقق من وجود بيانات بعد صف العناوين وصحة تنسيقها")
else:
    st.warning("تعذر الاتصال بقاعدة البيانات. تحقق من إعدادات Secrets والصلاحيات.")

st.markdown("---")
st.caption("تطبيق بحث بيانات الطلاب • Streamlit + Google Sheets")
