"""Build an offline dashboard with embedded Plotly, font, and non-identifying data."""
import json, zipfile
from plotly.offline import get_plotlyjs
from analysis import ROOT, OUT, load, font_css
_,d=load()
cols=['timestamp','campus','section','favorite_subject','course_rating','teaching_rating','mentor_rating','expectations_rating','continue_course','start_punctuality','positive_change']
a=d[cols].copy(); a['timestamp']=a.timestamp.dt.strftime('%Y-%m-%d')
data=a.to_json(orient='records',force_ascii=False).replace('</','<\\/')
html=r'''<!DOCTYPE html><html lang="ur" dir="rtl"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>علم دین — مکمل ڈیش بورڈ</title><style>FONT_CSS
*{box-sizing:border-box}body{margin:0;background:#f1f5f7;color:#153e46;padding:24px}main{max-width:1450px;margin:auto}h1{margin:0} .sub{color:#526772}.filters,.cards{display:flex;gap:15px;flex-wrap:wrap;margin:20px 0}.filters{background:white;padding:20px;border-radius:15px}.field{display:flex;flex-direction:column;flex:1;min-width:160px}select,input,button{font-family:'Noto Nastaliq Urdu',sans-serif;font-size:14px;padding:8px;min-height:48px;border:1px solid #aabfc4;border-radius:7px;background:white;color:#153e46}button{cursor:pointer;background:#136a6a;color:white;padding:8px 20px}.card{background:white;flex:1;min-width:160px;padding:18px;border-radius:12px;border-top:4px solid #168c8c}.card strong{display:block;font-family:Arial;font-size:30px;direction:ltr;text-align:right}.grid{display:grid;grid-template-columns:1fr 1fr;gap:18px}.chart{background:white;border-radius:12px;min-height:450px;direction:ltr}.wide{grid-column:1/-1}#empty{display:none;padding:30px;background:#fff1ce}.note{background:#fff;padding:20px;border-radius:12px;margin:20px 0}table{border-collapse:collapse;width:100%;font:14px Arial;direction:ltr}td,th{padding:12px;border-bottom:1px solid #dce4e6;text-align:left}th{background:#153e46;color:white}.table-wrap{overflow:auto;max-height:500px}a{color:#12696b}@media(max-width:800px){.grid{grid-template-columns:1fr}body{padding:12px}}@media print{button,.filters{display:none}.chart{break-inside:avoid}}
</style><script>PLOTLY_JS</script></head><body><main>
<h1>علم دین — طلباء کے تاثرات</h1><p class="sub">وسطِ سیشن ۲۰۲۶ • مکمل آف لائن ڈیش بورڈ • اصل ورک بک کے ۵۶۰ جوابات</p>
<div class="filters">
<div class="field"><label for="campus">کیمپس</label><select id="campus"></select></div>
<div class="field"><label for="section">سیکشن</label><select id="section"></select></div>
<div class="field"><label for="subject">پسندیدہ مضمون</label><select id="subject"></select></div>
<div class="field"><label for="from">ابتدائی تاریخ</label><input id="from" type="date" value="2026-10-02"></div>
<div class="field"><label for="to">آخری تاریخ</label><input id="to" type="date" value="2026-10-24"></div>
<div class="field"><label for="minN">کیمپس تقابل: کم از کم جوابات</label><input id="minN" type="number" min="1" max="560" value="10"></div>
<button id="reset">فلٹر صاف کریں</button><button id="download">منتخب ڈیٹا CSV</button></div>
<div id="cards" class="cards"></div><p id="empty">منتخب فلٹر کے لیے کوئی جواب موجود نہیں۔</p>
<div id="insight" class="note"></div>
<div class="grid" id="plots"><div id="ratings" class="chart"></div><div id="subjects" class="chart"></div><div id="daily" class="chart"></div><div id="trend" class="chart"></div><div id="campuses" class="chart wide"></div><div id="correlations" class="chart wide"></div></div>
<h2>کیمپس کا تقابل — نمونے کی حد کے ساتھ</h2><div id="campusTable" class="table-wrap"></div>
<div class="note"><h2>نتائج سمجھنے کا طریقہ</h2><p>اصل ورک بک کا پرانا خلاصہ ۵۰۸ جوابات دکھاتا ہے، جبکہ اصل جوابات ۵۶۰ ہیں؛ فرق ۵۲ ہے۔ اس ڈیش بورڈ کے تمام حساب اصل جوابات سے ہیں۔</p><p>جاری رکھنے کی خواہش حقیقی برقرار رہنے کی شرح نہیں۔ روزانہ کے نتائج مختلف جواب دہندگان کی رائے ہیں، ایک ہی طالب علم کی پیش رفت نہیں۔ کم نمونے کی بنیاد پر کیمپس کی حتمی درجہ بندی نہ کریں۔ کل داخلوں کی تعداد دستیاب نہیں، اس لیے رسپانس ریٹ نامعلوم ہے۔ باہمی تعلق وجہ اور اثر کا ثبوت نہیں۔</p><p>صفائی کے بعد ۱۳ خالی یا N/A، NA، None جوابات؛ کوئی عین یکساں ریکارڈ یا غلط پیمانے کی ریٹنگ نہیں۔ جائز کم ریٹنگ حذف نہیں کی گئی۔ اس آف لائن ڈیش بورڈ میں مربی کے نام اور ذاتی کھلے جوابات شامل نہیں ہیں۔</p><p>گراف پر ماؤس لے جا کر تفصیل دیکھیں؛ گراف کے اوپر موجود کنٹرول سے زوم، ری سیٹ اور تصویر محفوظ کریں۔ تمام فلٹر KPI، گراف اور CSV پر لاگو ہیں۔ کم از کم نمونے کی حد صرف کیمپس تقابل کے جدول پر لاگو ہے۔</p></div>
</main><script id="records" type="application/json">RECORDS</script><script>
const DATA=JSON.parse(document.getElementById('records').textContent);
const $=id=>document.getElementById(id), mean=(a,k)=>a.length?a.reduce((s,r)=>s+r[k],0)/a.length:null;
const keys=['course_rating','teaching_rating','mentor_rating','expectations_rating'];
const labels=['کورس','تدریس','مربی','توقعات بمقابلہ حقیقت'];
const fmt=v=>(Math.round((v+Number.EPSILON)*100)/100).toFixed(2);
function esc(s){return String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));}
for(const [id,key] of [['campus','campus'],['section','section'],['subject','favorite_subject']]){
 $(id).innerHTML='<option value="">تمام</option>'+[...new Set(DATA.map(r=>r[key]))].sort().map(v=>`<option value="${esc(v)}">${esc(v)}</option>`).join('');
}
function selected(){return DATA.filter(r=>(!$('campus').value||r.campus===$('campus').value)&&(!$('section').value||r.section===$('section').value)&&(!$('subject').value||r.favorite_subject===$('subject').value)&&(!$('from').value||r.timestamp>=$('from').value)&&(!$('to').value||r.timestamp<=$('to').value));}
function grouped(a,key){const g={};for(const r of a)(g[r[key]]??=[]).push(r);return g;}
function corr(a,x,y){const mx=mean(a,x),my=mean(a,y);let num=0,dx=0,dy=0;for(const r of a){let u=r[x]-mx,v=r[y]-my;num+=u*v;dx+=u*u;dy+=v*v;}return dx&&dy?num/Math.sqrt(dx*dy):null;}
function plot(id,traces,title,extra={}){return Plotly.react(id,traces,{title:{text:title},font:{family:'Noto Nastaliq Urdu',size:13},paper_bgcolor:'white',plot_bgcolor:'white',margin:{t:100,b:110,l:70,r:40},...extra},{responsive:true,displaylogo:false});}
function render(){
 const a=selected(),n=a.length,pct=k=>n?100*a.filter(k).length/n:0;
 const cards=[['کل جوابات',n],['کیمپس',new Set(a.map(r=>r.campus)).size],...keys.slice(0,3).map((k,i)=>[labels[i],n?fmt(mean(a,k))+'/10':'—']),['جاری رکھنے کا ارادہ',n?pct(r=>r.continue_course==='جی ہاں، ضرور').toFixed(1)+'%':'—']];
 $('cards').innerHTML=cards.map(([k,v])=>`<div class="card">${k}<strong>${v}</strong></div>`).join('');
 $('empty').style.display=n?'none':'block';$('plots').style.display=n?'grid':'none';
 if(!n){$('insight').textContent='فلٹر تبدیل کریں؛ کوئی ڈیٹا حذف نہیں ہوا۔';$('campusTable').innerHTML='';return;}
 $('insight').textContent=`ہمیشہ وقت پر شروع ہونے والی کلاسز: ${pct(r=>r.start_punctuality==='ہمیشہ وقت پر شروع ہوتی ہیں').toFixed(1)}%۔ بہت زیادہ مثبت تبدیلی: ${pct(r=>r.positive_change==='بہت زیادہ مثبت تبدیلی').toFixed(1)}%۔ منتخب جوابات: ${n} / ${DATA.length}۔`;
 plot('ratings',[{type:'bar',x:labels,y:keys.map(k=>mean(a,k)),marker:{color:['#168c8c','#225779','#74993c','#ddac39']},text:keys.map(k=>fmt(mean(a,k))),textposition:'auto'}],'اوسط ریٹنگ',{yaxis:{range:[0,10],title:{text:'/10'}}});
 const subjects=Object.entries(grouped(a,'favorite_subject'));
 plot('subjects',[{type:'pie',labels:subjects.map(v=>v[0]),values:subjects.map(v=>v[1].length),hole:.5,textinfo:'percent',hovertemplate:'%{label}<br>%{value} (%{percent})<extra></extra>'}],'پسندیدہ مضامین');
 const days=grouped(a,'timestamp'),dates=Object.keys(days).sort(),sequence=[];
 for(let t=new Date(dates[0]+'T00:00:00Z');t<=new Date(dates.at(-1)+'T00:00:00Z');t.setUTCDate(t.getUTCDate()+1))sequence.push(t.toISOString().slice(0,10));
 plot('daily',[{type:'scatter',mode:'lines+markers',x:sequence,y:sequence.map(v=>days[v]?.length??0),line:{color:'#168c8c'}}],'روزانہ موصول ہونے والے جوابات',{yaxis:{rangemode:'tozero'}});
 plot('trend',keys.slice(0,3).map((k,i)=>({type:'scatter',mode:'lines+markers',name:labels[i],x:sequence,y:sequence.map(v=>days[v]?mean(days[v],k):null),connectgaps:false})),'روزانہ ریٹنگ — جواب دہندگان بدلتے ہیں',{yaxis:{range:[1,10]},legend:{orientation:'h',y:-.3}});
 const camps=Object.entries(grouped(a,'campus')).sort((x,y)=>x[1].length-y[1].length);
 plot('campuses',[{type:'bar',orientation:'h',y:camps.map(v=>v[0]),x:camps.map(v=>v[1].length),marker:{color:'#168c8c'}}],'کیمپس کے لحاظ سے جوابات',{height:Math.max(450,camps.length*30+140),margin:{t:100,b:60,l:380,r:40},yaxis:{automargin:true}});
 const z=keys.map(x=>keys.map(y=>corr(a,x,y)));
 plot('correlations',[{type:'heatmap',x:labels,y:labels,z,zmin:-1,zmax:1,colorscale:'RdBu',text:z.map(row=>row.map(v=>v===null?'N/A':v.toFixed(2))),texttemplate:'%{text}',hoverongaps:false}],'ریٹنگ کا باہمی تعلق',{height:600,margin:{t:100,b:140,l:160,r:60}});
 const eligible=camps.filter(v=>v[1].length>=Math.max(1,Number($('minN').value)||1)).reverse();
 $('campusTable').innerHTML='<table><thead><tr><th>Campus</th><th>n</th>'+labels.slice(0,3).map(x=>'<th>'+x+'</th>').join('')+'</tr></thead><tbody>'+eligible.map(([name,rows])=>'<tr><td>'+esc(name)+'</td><td>'+rows.length+'</td>'+keys.slice(0,3).map(k=>'<td>'+fmt(mean(rows,k))+'</td>').join('')+'</tr>').join('')+'</tbody></table>'+(eligible.length?'':'<p>مقررہ حد پر کوئی کیمپس دستیاب نہیں۔</p>');
}
for(const id of ['campus','section','subject','from','to','minN'])$(id).addEventListener('change',render);
$('reset').onclick=()=>{for(const id of ['campus','section','subject'])$(id).value='';$('from').value='2026-10-02';$('to').value='2026-10-24';$('minN').value='10';render();};
$('download').onclick=()=>{const a=selected();if(!a.length)return;const keys=Object.keys(a[0]);const csv=v=>'"'+String(v??'').replace(/"/g,'""')+'"';const text='\uFEFF'+[keys.join(','),...a.map(r=>keys.map(k=>csv(/^[=+@\-]/.test(String(r[k]))?"'"+r[k]:r[k])).join(','))].join('\r\n');const u=URL.createObjectURL(new Blob([text],{type:'text/csv;charset=utf-8'})),link=document.createElement('a');link.href=u;link.download='filtered_feedback.csv';link.click();setTimeout(()=>URL.revokeObjectURL(u),1000);};
render();
</script></body></html>'''
html=html.replace('FONT_CSS',font_css()).replace('PLOTLY_JS',get_plotlyjs()).replace('RECORDS',data)
p=OUT/'dashboard.html';p.write_text(html,encoding='utf-8')
instructions='''URDU FEEDBACK DASHBOARD — OPENING INSTRUCTIONS

1. Download feedback_dashboard.zip to your computer.
2. Extract / unzip it. Do not open the HTML inside a text editor or chat preview.
3. Double-click dashboard.html, or use Open With > Chrome, Edge, Firefox or Safari.
4. Select campus, section, subject, dates. KPIs and all charts update immediately.
5. Use Reset to clear filters. Download CSV exports the selected non-identifying data.

Works offline: no Python, Streamlit, internet connection, or font installation needed.
The Urdu Nastaleeq font and Plotly are embedded. No external scripts are loaded.
Mentor names and open-text personal responses are excluded from this dashboard.
This is a browser dashboard file, not a hosted website. Keep the full original Excel private.
'''
(OUT/'OPEN_DASHBOARD.txt').write_text(instructions)
with zipfile.ZipFile(OUT/'feedback_dashboard.zip','w',zipfile.ZIP_DEFLATED) as z:
 z.write(p,'dashboard.html');z.writestr('OPEN_ME_FIRST.txt',instructions)
print('Built offline dashboard:',p)
