"""Run: streamlit run app.py --server.address 0.0.0.0"""
import streamlit as st
import pandas as pd
from analysis import load, tables, figures, kpis, insights, font_css, ROOT, TEXT, URDU
st.set_page_config(page_title='علم دین | طلباء کے تاثرات',page_icon='📊',layout='wide')
st.markdown('<style>'+font_css()+'''
[data-testid="stAppViewContainer"] h1, [data-testid="stAppViewContainer"] h2,
[data-testid="stMetricLabel"], [data-testid="stSidebar"] label {font-family:'Noto Nastaliq Urdu',serif!important; line-height:2.6!important;}
[data-testid="stMetric"] {background:#edf5f4;border-radius:12px;padding:16px;}
</style>''',unsafe_allow_html=True)
raw, all_data = load()
st.title('علم دین — طلباء کے تاثرات')
st.caption('وسطِ سیشن ۲۰۲۶ | اصل معلومات محفوظ • مقامی اور نجی تجزیہ')
with st.sidebar:
    st.header('فلٹر منتخب کریں')
    campuses=st.multiselect('کیمپس',sorted(all_data.campus.dropna().unique()),default=[])
    sections=st.multiselect('سیکشن',sorted(all_data.section.dropna().unique()),default=[])
    span=st.date_input('تاریخ کی حد',value=(all_data.timestamp.min().date(),all_data.timestamp.max().date()),min_value=all_data.timestamp.min().date(),max_value=all_data.timestamp.max().date())
    subjects=st.multiselect('پسندیدہ مضمون',sorted(all_data.favorite_subject.dropna().unique()))
    min_n=st.slider('تقابل کے لیے کم از کم جوابات',1,50,10)
    st.caption('خالی فہرست = تمام اختیارات۔ فلٹر صرف اس منظر پر لاگو ہیں؛ ڈاؤن لوڈ رپورٹ مکمل ڈیٹا کی ہے۔')
d=all_data.copy()
if campuses: d=d[d.campus.isin(campuses)]
if sections: d=d[d.section.isin(sections)]
if subjects: d=d[d.favorite_subject.isin(subjects)]
if isinstance(span,(tuple,list)) and len(span)==2: d=d[d.timestamp.dt.date.between(*span)]
if d.empty:
    st.warning('منتخب فلٹرز کے لیے کوئی جواب موجود نہیں۔'); st.stop()
k=kpis(d)
cols=st.columns(6)
for col,(label,value) in zip(cols,[('کل جوابات',str(len(d))),('کیمپس',str(k['campuses'])),('کورس',f"{k['course_rating']:.2f}/10"),('تدریس',f"{k['teaching_rating']:.2f}/10"),('مربی',f"{k['mentor_rating']:.2f}/10"),('جاری رکھنے کا ارادہ',f"{k['continuation_pct']:.1f}%")]): col.metric(label,value)
t=tables(raw,d); f=figures(d)
tabs=st.tabs(['جائزہ','کیمپس اور رجحانات','معیار اور موضوعات','ڈیٹا اور طریقۂ کار'])
with tabs[0]:
    for note in insights(d,t)[:4] + insights(d,t)[5:]: st.write(note)
    st.caption('موجودہ ورک بک کے خلاصے سے موازنہ مکمل ڈیٹا کے لیے اگلے ٹیب میں ہے؛ فلٹر شدہ گروپ کا فرق مکمل خلاصے کے مقابلے میں نہیں سمجھنا چاہیے۔')
    st.plotly_chart(f['ratings'],width='stretch')
    st.plotly_chart(f['subjects'],width='stretch')
with tabs[1]:
    st.plotly_chart(f['campuses'],width='stretch')
    st.plotly_chart(f['daily'],width='stretch')
    st.plotly_chart(f['rating_trend'],width='stretch')
    eligible=t['Campus Analysis'].query('responses >= @min_n')
    st.write('کیمپس کا تقابل — نمونے کی مقررہ حد کے ساتھ')
    st.dataframe(eligible,width='stretch',hide_index=True)
    st.caption('کم نمونے یا مختلف جواب دہندگان کے باعث درجہ بندی کو حتمی کارکردگی کا ثبوت نہ سمجھیں۔')
with tabs[2]:
    st.plotly_chart(f['correlations'],width='stretch')
    st.write('موضوعات: لفظی قواعد، متعدد موضوعات ممکن، دستی جائزہ ضروری')
    st.dataframe(t['Text Themes'],hide_index=True,width='stretch')
    st.write('شماریاتی آؤٹ لائر — اصل کم ریٹنگ محفوظ رکھی گئی')
    st.dataframe(t['Rating Statistics'],hide_index=True,width='stretch')
with tabs[3]:
    st.write('اصل ورک بک کے خلاصے کا مکمل ڈیٹا سے موازنہ')
    st.dataframe(tables(raw,all_data)['Summary Reconciliation'],hide_index=True,width='stretch')
    st.dataframe(t['Missing Values'],hide_index=True,width='stretch')
    st.write(f"عین یکساں ریکارڈ: {len(t['Exact Duplicates'])}؛ وقت کے بغیر مشابہ ریکارڈ: {len(t['Potential Duplicates'])}۔ کوئی ریکارڈ حذف نہیں کیا گیا۔")
    st.warning('مربی کے نام اور کھلے جوابات حساس ہو سکتے ہیں۔ اس ایپ کو عوامی طور پر شائع کرنے سے پہلے رسائی محدود کریں۔')
    if st.checkbox('تفصیلی جوابات دکھائیں'):
        st.dataframe(d,width='stretch',hide_index=True)
    st.download_button('فلٹر شدہ ڈیٹا CSV',d.to_csv(index=False).encode('utf-8-sig'),'filtered_feedback.csv','text/csv')
    for label,name,mime in [('مکمل Excel رپورٹ','feedback_analysis.xlsx','application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'),('مکمل بصری رپورٹ','visual_report.html','text/html')]:
        p=ROOT/'reports'/name
        if p.exists(): st.download_button(label,p.read_bytes(),name,mime)
    st.caption('NFC اور خالی جگہوں کی صفائی؛ کوئی خودکار ناموں کا انضمام، گم شدہ معلومات کی بھرائی یا کم ریٹنگ کا اخراج نہیں۔ تاریخ کے ٹائم زون کا ماخذ میں ذکر نہیں۔')
