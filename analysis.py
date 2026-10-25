"""Reproducible analysis; never mutates the source workbook."""
from pathlib import Path
import base64, hashlib, json, re, unicodedata
import pandas as pd
import numpy as np
import plotly.express as px

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / 'data/original/feedback.xlsx'
OUT = ROOT / 'reports'
FONT = 'Noto Nastaliq Urdu'
KEYS = ['timestamp','form_score','campus','section','mentor','start_punctuality','end_punctuality','facilities','environment','admin_response','favorite_subject','subject_reason','course_rating','teaching_style','question_comfort','teacher_response','engagement','understanding','teaching_rating','mentor_clarity','mentor_role_text','mentor_empathy','mentor_guidance','mentor_contact','mentor_listening','mentor_rating','positive_change','change_reason','practical_example','service','teaches_seerah','continue_course','dropout_reasons','retention_suggestions','improvement_suggestions','expectations_rating']
RATINGS = {'facilities':5,'environment':5,'engagement':5,'understanding':5,'mentor_empathy':5,'course_rating':10,'teaching_rating':10,'mentor_rating':10,'expectations_rating':10}
URDU = {'course_rating':'کورس کا مجموعی معیار','teaching_rating':'تدریسی معیار','mentor_rating':'مربی کی کارکردگی','expectations_rating':'توقعات بمقابلہ حقیقت','facilities':'بنیادی سہولیات','environment':'ماحول اور نظم','engagement':'کلاس میں دلچسپی','understanding':'طلباء کی سمجھ','mentor_empathy':'مربی کی شفقت'}
TEXT = ['subject_reason','mentor_role_text','practical_example','dropout_reasons','retention_suggestions','improvement_suggestions']

def normalize(v):
    if not isinstance(v,str): return v
    s = re.sub(r'\s+', ' ', unicodedata.normalize('NFC',v)).strip()
    return pd.NA if not s or s.casefold() in {'n/a','na','none'} else s

def load():
    raw = pd.read_excel(SOURCE, sheet_name='Form Responses 1', keep_default_na=False, na_values=[''])
    if len(raw.columns)!=len(KEYS): raise ValueError('Workbook schema changed; review column mapping.')
    d=raw.copy(); d.columns=KEYS
    for c in d.select_dtypes('object'): d[c]=d[c].map(normalize)
    d['timestamp']=pd.to_datetime(d.timestamp, errors='coerce')
    for c in RATINGS: d[c]=pd.to_numeric(d[c],errors='coerce')
    d.insert(0,'source_row',np.arange(2,len(d)+2))
    return raw,d

def kpis(d):
    n=len(d)
    return {'responses':n,'campuses':d.campus.nunique(),**{c:float(d[c].mean()) if n else None for c in ['course_rating','teaching_rating','mentor_rating','expectations_rating']},'continuation_pct':100*d.continue_course.eq('جی ہاں، ضرور').mean() if n else None,'on_time_start_pct':100*d.start_punctuality.eq('ہمیشہ وقت پر شروع ہوتی ہیں').mean() if n else None,'strong_change_pct':100*d.positive_change.eq('بہت زیادہ مثبت تبدیلی').mean() if n else None}

def tables(raw,d):
    missing=pd.DataFrame({'field':KEYS,'question':raw.columns,'missing_before':[raw[c].isna().sum() for c in raw], 'missing_after':[d[c].isna().sum() for c in KEYS]})
    missing['missing_pct']=100*missing.missing_after/len(d)
    stats=[]; flags=[]
    for c,top in RATINGS.items():
        s=d[c]; q1,q3=s.quantile([.25,.75]); lo=q1-1.5*(q3-q1); hi=q3+1.5*(q3-q1)
        mask=s.lt(lo)|s.gt(hi); invalid=s.notna()&(~s.between(1,top)|s.mod(1).ne(0))
        stats.append({'metric':c,'label':URDU[c],'n':s.count(),'mean':s.mean(),'median':s.median(),'std':s.std(),'min':s.min(),'max':s.max(),'scale_max':top,'top_two_box_pct':100*s.ge(top-1).sum()/s.count(),'iqr_lower':lo,'iqr_upper':hi,'outliers':mask.sum(),'invalid':invalid.sum()})
        for idx in d.index[mask|invalid]: flags.append({'source_row':int(d.at[idx,'source_row']),'metric':c,'value':s[idx],'iqr_outlier':bool(mask[idx]),'invalid':bool(invalid[idx])})
    campus=d.groupby('campus').agg(responses=('source_row','size'),course_rating=('course_rating','mean'),teaching_rating=('teaching_rating','mean'),mentor_rating=('mentor_rating','mean'),expectations_rating=('expectations_rating','mean')).reset_index()
    campus['small_sample']=campus.responses.lt(10)
    daily=d.groupby(d.timestamp.dt.normalize()).agg(responses=('source_row','size'),course_rating=('course_rating','mean'),teaching_rating=('teaching_rating','mean'),mentor_rating=('mentor_rating','mean')).reset_index()
    old=pd.read_excel(SOURCE,sheet_name='Sheet2'); old=old[old['City and Campus'].ne('Total Responses')]
    old=old[['City and Campus','Feedback\nResponses']].rename(columns={'City and Campus':'campus','Feedback\nResponses':'existing_summary'})
    rec=old.merge(campus[['campus','responses']],on='campus',how='outer').fillna({'existing_summary':0,'responses':0}); rec['difference']=rec.responses-rec.existing_summary
    # Transparent keyword rules: multiple themes per response; no automated sentiment claim.
    themes={'وقت / مصروفیات':['وقت','مصروف','ٹائم','time','busy'],'تعلیمی انداز':['استاد','اساتذہ','پڑھ','تدریس','teacher'],'سہولیات':['پانی','بجلی','پنکھ','گرمی','واش','light'],'رابطہ اور رہنمائی':['مربی','رابط','رہنمائی','mentor'],'سفر اور فاصلہ':['دور','سفر','فاصل','travel'],'دلچسپی اور حوصلہ':['دلچسپ','شوق','حوصل','interest']}
    theme_rows=[]
    for c in ['dropout_reasons','retention_suggestions','improvement_suggestions']:
        for theme,words in themes.items():
            count=int(d[c].fillna('').str.contains('|'.join(map(re.escape,words)),case=False,regex=True).sum())
            theme_rows.append({'field':c,'theme':theme,'matched_responses':count,'answered':d[c].notna().sum(),'keywords':', '.join(words)})
    dup=d[d.duplicated(subset=KEYS,keep=False)].copy()
    potential=d[d.duplicated(subset=[c for c in KEYS if c!='timestamp'],keep=False)].copy()
    frequencies=[]
    for c in KEYS:
        if c not in TEXT + ['timestamp','mentor'] and c not in RATINGS:
            for value,n in d[c].value_counts(dropna=False).items(): frequencies.append({'field':c,'response':value,'count':n,'pct_all':100*n/len(d)})
    section=d.groupby(['campus','section']).agg(responses=('source_row','size'),course_rating=('course_rating','mean'),teaching_rating=('teaching_rating','mean'),mentor_rating=('mentor_rating','mean')).reset_index()
    low=d.loc[d[['course_rating','teaching_rating','mentor_rating']].le(6).any(axis=1),['source_row','campus','section','course_rating','teaching_rating','mentor_rating']]
    return {'Response Distributions':pd.DataFrame(frequencies),'Campus Sections':section,'Low Rating Followup':low,'Missing Values':missing,'Rating Statistics':pd.DataFrame(stats),'Outlier Flags':pd.DataFrame(flags,columns=['source_row','metric','value','iqr_outlier','invalid']),'Campus Analysis':campus,'Daily Trends':daily,'Summary Reconciliation':rec,'Text Themes':pd.DataFrame(theme_rows),'Exact Duplicates':dup,'Potential Duplicates':potential,'Correlations':d[list(RATINGS)].corr()}

def figures(d):
    if d.empty: return {}
    counts=d.campus.value_counts().rename_axis('campus').reset_index(name='responses')
    daily=d.groupby(d.timestamp.dt.normalize()).agg(responses=('source_row','size'),course_rating=('course_rating','mean')).reset_index()
    # Show intervening zero-response days to avoid misleading lines.
    daily=daily.set_index('timestamp').reindex(pd.date_range(d.timestamp.min().normalize(),d.timestamp.max().normalize(),freq='D')).rename_axis('date').reset_index(); daily.responses=daily.responses.fillna(0)
    rating=pd.DataFrame({'metric':[URDU[c] for c in RATINGS],'normalized':[d[c].mean()/v*100 for c,v in RATINGS.items()]})
    subject=d.favorite_subject.value_counts().rename_axis('subject').reset_index(name='responses')
    corr=d[list(RATINGS)].rename(columns=URDU).corr()
    f={'campuses':px.bar(counts,x='responses',y='campus',orientation='h',title='کیمپس کے لحاظ سے جوابات',text='responses'), 'ratings':px.bar(rating,x='metric',y='normalized',title='معیار کا تقابل — اصل پیمانے کے زیادہ سے زیادہ نمبر کا فیصد',range_y=[0,100]),'daily':px.line(daily,x='date',y='responses',markers=True,title='روزانہ موصول ہونے والے جوابات'),'rating_trend':px.line(daily,x='date',y='course_rating',markers=True,title='روزانہ کورس ریٹنگ — مختلف جواب دہندگان، انفرادی پیش رفت نہیں',range_y=[1,10]),'subjects':px.pie(subject,names='subject',values='responses',hole=.5,title='پسندیدہ مضامین'),'correlations':px.imshow(corr,zmin=-1,zmax=1,color_continuous_scale='RdBu_r',text_auto='.2f',title='ریٹنگ کا باہمی تعلق — وجہ اور اثر کا ثبوت نہیں')}
    for fig in f.values(): fig.update_layout(font=dict(family=FONT,size=14),template='plotly_white',margin=dict(t=100,b=120),paper_bgcolor='#ffffff')
    f['campuses'].update_layout(height=1050,yaxis={'categoryorder':'total ascending'})
    f['correlations'].update_layout(height=800)
    return f

def font_css():
    b=base64.b64encode((ROOT/'assets/NotoNastaliqUrdu.ttf').read_bytes()).decode()
    return f"@font-face{{font-family:'{FONT}';src:url(data:font/ttf;base64,{b}) format('truetype');}} body{{font-family:'{FONT}',sans-serif;line-height:2.3}} h1,h2,p{{direction:rtl;text-align:right}}"

def insights(d,t):
    k=kpis(d); rec=t['Summary Reconciliation']
    return [f"کل {len(d)} جوابات، {d.campus.nunique()} کیمپس؛ مدت {d.timestamp.min():%Y-%m-%d} تا {d.timestamp.max():%Y-%m-%d}۔",f"کورس {k['course_rating']:.2f}/10، تدریس {k['teaching_rating']:.2f}/10، مربی {k['mentor_rating']:.2f}/10۔",f"کورس جاری رکھنے کی خواہش {k['continuation_pct']:.1f}%؛ یہ ارادہ ہے، حقیقی برقرار رہنے کی شرح نہیں۔",f"کلاس ہمیشہ وقت پر شروع ہونے کی شرح {k['on_time_start_pct']:.1f}%؛ وقت کی پابندی بہتر بنانے کے لیے تاخیر کا جائزہ لیں۔",f"موجودہ خلاصے میں {int(rec.existing_summary.sum())} جوابات؛ اصل ڈیٹا میں {len(d)}، فرق {int(rec.difference.sum())}۔ خلاصہ تازہ کریں۔",'کم جوابات والے کیمپس کے نتائج احتیاط سے سمجھیں؛ جواب دہندگان کا انتخاب بے ترتیب ثابت نہیں، کل داخلوں کے بغیر رسپانس ریٹ نامعلوم ہے۔','کم ریٹنگ حذف نہیں کی گئی؛ شماریاتی آؤٹ لائر لازماً غلطی نہیں۔ متن کے موضوعات لفظی قواعد پر مبنی ہیں، دستی تصدیق ضروری ہے۔']

def export_excel(raw,d,t,notes):
    path=OUT/'feedback_analysis.xlsx'
    with pd.ExcelWriter(path,engine='xlsxwriter',datetime_format='yyyy-mm-dd hh:mm') as w:
        wb=w.book; wb.strings_to_formulas=False; wb.strings_to_urls=False
        pd.DataFrame({'Executive Summary / خلاصہ':notes}).to_excel(w,sheet_name='Executive Summary',index=False)
        pd.DataFrame([{'KPI':k,'value':v} for k,v in kpis(d).items()]).to_excel(w,sheet_name='KPIs',index=False)
        raw.to_excel(w,sheet_name='Raw Responses',index=False)
        d.to_excel(w,sheet_name='Cleaned Responses',index=False)
        pd.DataFrame({'field':KEYS,'original_question':raw.columns,'scale_max':[RATINGS.get(c) for c in KEYS]}).to_excel(w,sheet_name='Data Dictionary',index=False)
        for name,frame in t.items(): frame.to_excel(w,sheet_name=name,index=name=='Correlations')
        methods=[['Source',hashlib.sha256(SOURCE.read_bytes()).hexdigest()],['Cleaning','NFC Unicode and whitespace normalization; blanks and exact case-insensitive N/A, NA, None => missing (raw values preserved); no name/campus fuzzy merge, imputation or row deletion. source_row references Excel row.'],['Duplicates','Exact = all 36 cleaned fields; potential = all except timestamp. No respondent identifier, so repeated submissions cannot be ruled out.'],['Outliers','Tukey 1.5 IQR per rating, inclusive valid integer scales 1–5 or 1–10. All retained.'],['Score','Constant zero form Score excluded; not a course KPI.'],['Denominators','Means use nonmissing valid numeric values; intention/on-time/strong-change percentages use all responses. No enrollment denominator available.'],['Text','Case-insensitive literal keyword matches; overlapping themes; not sentiment analysis. Substrings can produce false positives.'],['Trends','Submission date, timezone unspecified in source. Different respondents each day; not longitudinal or causal.'],['Privacy','Mentor names and free text are sensitive. Local Git only; review before sharing.'],['Font','Noto Nastaliq Urdu embedded in HTML and dashboard. Excel font rendering requires installation of bundled TTF.'],['Auxiliary sheets','Source workbook preserved byte-for-byte with all 3 sheets; analysis derives from Form Responses 1. Sheet2 reconciled; Pivot Table 1 is not a response table.']]
        pd.DataFrame(methods,columns=['Topic','Method']).to_excel(w,sheet_name='Methodology',index=False)
        fmt=wb.add_format({'font_name':FONT,'font_size':11,'text_wrap':True,'valign':'top'})
        header=wb.add_format({'bold':True,'bg_color':'#123F4A','font_color':'white','font_name':FONT,'text_wrap':True,'valign':'vcenter'})
        for name,ws in w.sheets.items():
            ws.right_to_left(); ws.freeze_panes(1,0); ws.set_column(0,50,25,fmt); ws.set_row(0,65)
            if name in ['Executive Summary','Methodology']: ws.set_column(0,0,35,fmt); ws.set_column(1 if name=='Methodology' else 0,1 if name=='Methodology' else 0,110,fmt); ws.set_default_row(85)
            for col in range(ws.dim_colmax+1):
                cell=ws.table.get(0,{}).get(col)
                if cell and hasattr(cell,'string'): ws.write(0,col,wb.str_table.string_array[cell.string] if wb.str_table.string_array else list(wb.str_table.string_table.keys())[cell.string],header)
            if ws.dim_rowmax>0: ws.autofilter(0,0,ws.dim_rowmax,ws.dim_colmax)
        stats=t['Rating Statistics']; sheet=w.sheets['Rating Statistics']; sheet.conditional_format(1,4,len(stats),4,{'type':'3_color_scale'})
        chartws=wb.add_worksheet('Charts'); chartws.right_to_left()
        def chart(kind,source,cat,val,n,title,pos):
            ch=wb.add_chart({'type':kind}); ch.add_series({'categories':[source,1,cat,n,cat],'values':[source,1,val,n,val],'name':title}); ch.set_title({'name':title,'name_font':{'name':FONT}}); ch.set_size({'width':850,'height':450}); chartws.insert_chart(pos,ch)
        chart('column','Campus Analysis',0,1,len(t['Campus Analysis']),'کیمپس کے جوابات','A1')
        chart('line','Daily Trends',0,1,len(t['Daily Trends']),'روزانہ جوابات','A25')
        subjects=d.favorite_subject.value_counts().rename_axis('subject').reset_index(name='responses'); subjects.to_excel(w,sheet_name='Subject Preferences',index=False)
        w.sheets['Subject Preferences'].set_column(0,1,40,fmt)
        chart('pie','Subject Preferences',0,1,len(subjects),'پسندیدہ مضامین','A49')
        cws=w.sheets['Correlations']; cws.conditional_format(1,1,len(RATINGS),len(RATINGS),{'type':'3_color_scale','min_type':'num','min_value':-1,'mid_type':'num','mid_value':0,'max_type':'num','max_value':1})
    return path

def main():
    OUT.mkdir(exist_ok=True); raw,d=load(); t=tables(raw,d)
    assert len(d)==len(raw) and d.source_row.is_unique
    assert t['Rating Statistics'].invalid.sum()==0
    assert int(t['Campus Analysis'].responses.sum())==len(d)
    assert int(t['Daily Trends'].responses.sum())==len(d)
    notes=insights(d,t); d.to_csv(OUT/'cleaned_responses.csv',index=False,encoding='utf-8-sig')
    summary={'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'kpis':kpis(d),'missing_cells':int(t['Missing Values'].missing_after.sum()),'exact_duplicates':len(t['Exact Duplicates']),'potential_duplicates':len(t['Potential Duplicates']),'outlier_flags':len(t['Outlier Flags']),'invalid_ratings':int(t['Rating Statistics'].invalid.sum()),'summary_difference':int(t['Summary Reconciliation'].difference.sum())}
    (OUT/'validation.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2))
    (OUT/'executive_summary.md').write_text('# طلباء کے تاثرات — انتظامی خلاصہ\n\n'+'\n\n'.join(notes),encoding='utf-8')
    figs=figures(d); parts=['<!doctype html><html lang="ur"><meta charset="utf-8"><title>علم دین — تجزیہ</title><style>'+font_css()+'</style><h1>علم دین — طلباء کے تاثرات</h1>']
    parts += ['<p>'+n+'</p>' for n in notes]
    for i,(name,fig) in enumerate(figs.items()):
        parts.append(fig.to_html(full_html=False,include_plotlyjs=True if i==0 else False))
        fig.write_json(OUT/f'{name}.json')
    (OUT/'visual_report.html').write_text('\n'.join(parts)+'</html>',encoding='utf-8')
    export_excel(raw,d,t,notes)
    print(json.dumps(summary,ensure_ascii=False,indent=2))

if __name__=='__main__': main()
