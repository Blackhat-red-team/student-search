
import streamlit as st
import gspread
import json
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd

# إعدادات الصفحة
st.set_page_config(
    page_title="البحث عن بيانات الطلاب",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# إخفاء عناصر واجهة المستخدم الافتراضية لـ Streamlit
hide_st_style = """
        <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        </style>
        """
st.markdown(hide_st_style, unsafe_allow_html=True)

# تصميم الواجهة العربية
st.markdown("""
    <style>
    .stApp {
        direction: rtl;
        text-align: right;
        font-family: 'Arial', sans-serif;
    }
    .stTextInput label {
        width: 100%;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("البحث عن بيانات الطلاب")

# دالة للاتصال بـ Google Sheet
@st.cache_resource
def connect_to_sheet():
    try:
        # استخدام Streamlit Secrets لإدارة بيانات الاعتماد
        creds_json = st.secrets["google_credentials"]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_json, ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive'])
        client = gspread.authorize(creds)

        # اسم ورقة العمل أو ID الخاص بها
        # يجب استبدال 'اسم_ورقة_العمل_الخاصة_بك' أو 'ID_ورقة_العمل_الخاصة_بك'
        # تأكد من مشاركة ورقة العمل مع البريد الإلكتروني الخاص بحساب الخدمة
        sheet_id = st.secrets["google_sheet_id"]
        sheet = client.open_by_key(sheet_id).sheet1
        return sheet
    except Exception as e:
        st.error(f"خطأ في الاتصال بـ Google Sheet: {e}")
        st.info("يرجى التأكد من إعداد Google Sheet و Streamlit Secrets بشكل صحيح.")
        return None

sheet = connect_to_sheet()

if sheet:
    # قراءة جميع البيانات من ورقة العمل
    data = sheet.get_all_records()
    df = pd.DataFrame(data)

    if not df.empty:
        st.write("--- ")
        st.subheader("ابحث عن طالب")

        search_term = st.text_input("أدخل اسم الطالب أو رقم الموبايل للبحث:", key="search_input")

        if st.button("بحث"):
            if search_term:
                # البحث في عمود 'اسم الطفل كامل' و 'رقم الموبايل ( واتساب )'
                results = df[
                    df['اسم الطفل كامل'].astype(str).str.contains(search_term, case=False, na=False) |
                    df['رقم الموبايل ( واتساب )'].astype(str).str.contains(search_term, case=False, na=False)
                ]

                if not results.empty:
                    st.success(f"تم العثور على {len(results)} نتيجة:")
                    # عرض النتائج في جدول
                    st.dataframe(results)
                else:
                    st.warning("لم يتم العثور على أي نتائج مطابقة.")
            else:
                st.info("الرجاء إدخال كلمة للبحث.")
    else:
        st.info("لا توجد بيانات في ورقة العمل حتى الآن.")
else:
    st.warning("تعذر الاتصال بـ Google Sheet. يرجى التحقق من الإعدادات.")

