# import streamlit as st
# import pandas as pd
# import gspread
# from oauth2client.service_account import ServiceAccountCredentials

# # ---------------------------------------------------------
# # 0. [보안] 비밀번호 설정 함수
# # ---------------------------------------------------------
# def check_password():
#     if "password_correct" not in st.session_state:
#         st.session_state.password_correct = False

#     if st.session_state.password_correct:
#         return True

#     st.markdown("### 🔒 관계자 전용 페이지")
#     password = st.text_input("비밀번호를 입력하세요", type="password")
    
#     if st.button("로그인"):
#         if password == "sanho2325": 
#             st.session_state.password_correct = True
#             st.rerun()
#         else:
#             st.error("비밀번호가 틀렸습니다.")
#     return False

# # ---------------------------------------------------------
# # 1. 페이지 설정 및 디자인 (CSS)
# # ---------------------------------------------------------
# st.set_page_config(layout="wide", page_title="산호 사전동의 현황")

# if not check_password():
#     st.stop()

# st.markdown("""
# <style>
#     .block-container { padding-top: 3rem; padding-bottom: 5rem; }
    
#     .dong-card {
#         background-color: white;
#         border: 1px solid #e0e0e0;
#         border-radius: 8px;
#         padding: 0px;
#         margin-bottom: 20px;
#         box-shadow: 0 2px 4px rgba(0,0,0,0.05);
#         overflow: hidden;
#     }
    
#     .dong-header {
#         background-color: #495057;
#         color: white;
#         padding: 15px 5px;       
#         text-align: center;
#         font-weight: bold;
#     }
    
#     .table-wrapper {
#         overflow-x: auto; 
#         -webkit-overflow-scrolling: touch;
#         width: 100%;
#         padding-bottom: 0px;
#         margin-bottom: 0px;
#     }
    
#     .table-wrapper::-webkit-scrollbar { height: 6px; background: transparent; }
#     .table-wrapper::-webkit-scrollbar-track { background: transparent; }
#     .table-wrapper::-webkit-scrollbar-thumb { background-color: #ccc; border-radius: 3px; }
    
#     .apt-table {
#         width: 100%;
#         min-width: 600px;
#         table-layout: fixed;
#         border-collapse: collapse;
#         border-spacing: 0;
#         font-size: 12px;
#         margin-bottom: 0px;
#     }
    
#     .apt-cell {
#         border: 1px solid #dee2e6;
#         padding: 6px 2px;
#         text-align: center;
#         height: 45px;
#         vertical-align: middle;
#         white-space: nowrap; 
#         overflow: hidden;
#     }

#     .floor-cell {
#         width: 45px;             
#         min-width: 45px;
#         background-color: #f8f9fa;
#         color: #495057;
#         font-weight: bold;
#         font-size: 11px;
#         border-right: 2px solid #adb5bd !important;
#         position: sticky;
#         left: 0;
#         z-index: 10;
#     }
    
#     .border-bold { border-right: 2px solid #555 !important; }
    
#     /* ★ [상태별 색상 정의] ★ */
#     .status-done { background-color: #e7f5ff; color: #1971c2; font-weight: bold; }   /* 파란색 (찬성) */
#     .status-ban { background-color: #ffe3e3; color: #c92a2a; font-weight: bold; }    /* 빨간색 (반대/연락금지) */
#     .status-waiting { background-color: #fff3cd; color: #856404; font-weight: bold; } /* 노란색 (응답대기) */
#     .status-todo { background-color: #ffffff; color: #adb5bd; }                       /* 흰색 (미접수) */
    
#     .icon-style { font-size: 14px; margin-right: 2px; }
#     .ho-text { font-size: 12px; font-family: sans-serif; font-weight: bold; } 
    
#     .entrance-row td {
#         background-color: #e9ecef;
#         color: #495057;
#         text-align: center;
#         vertical-align: middle;
#         font-size: 12px;
#         font-weight: bold;
#         height: 35px;
#         border-top: 2px solid #555;
#         border-right: 1px solid #dee2e6;
#         border-left: 1px solid #dee2e6;
#         border-bottom: none !important; 
#     }
#     .entrance-empty {
#         background-color: #fff !important;
#         border: none !important;
#         position: sticky;
#         left: 0;
#         z-index: 10;
#     }

#     .mobile-hint {
#         font-size: 12px;
#         color: #868e96;
#         font-weight: bold;
#         text-align: right;
#         padding: 5px 10px;
#         background-color: #f8f9fa;
#         border-bottom: 1px solid #eee;
#         display: none;
#     }
#     @media only screen and (max-width: 800px) { .mobile-hint { display: block; } }
# </style>
# """, unsafe_allow_html=True)

# # ---------------------------------------------------------
# # 2. 데이터 로드
# # ---------------------------------------------------------
# @st.cache_data(ttl=60)
# def load_data():
#     try:
#         scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
#         creds_dict = st.secrets["gcp_service_account"]
#         creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
#         client = gspread.authorize(creds)
#         sheet = client.open("sanho_db").worksheet("data")
#         data = sheet.get_all_records()
#         df = pd.DataFrame(data)

#         df['동'] = df['동'].astype(str)
#         df['호'] = df['호'].astype(str)
#         if '동의여부' not in df.columns: df['동의여부'] = '미조사'
#         if '거주유형' not in df.columns: df['거주유형'] = ''
        
#         def get_floor_line(h):
#             try:
#                 if len(h) >= 3: return int(h[:-2]), int(h[-2:])
#                 return 0, 0
#             except: return 0, 0
            
#         df['층'], df['라인'] = zip(*df['호'].apply(get_floor_line))
#         return df
#     except Exception as e:
#         return pd.DataFrame()

# df = load_data()

# # ---------------------------------------------------------
# # 3. HTML 생성 함수
# # ---------------------------------------------------------
# def generate_dong_html(sub_df, dong_name):
#     # 피벗 테이블 생성
#     sub_df['info'] = list(zip(sub_df['동의여부'], sub_df['거주유형'], sub_df['호']))
#     pivot = sub_df.pivot_table(index='층', columns='라인', values='info', aggfunc='first')
#     pivot = pivot.sort_index(ascending=False) 
    
#     total = len(sub_df)
    
#     # 1. 찬성 수 (동의율 계산용 분자)
#     agree_count = len(sub_df[sub_df['동의여부'] == '찬성'])
    
#     # 2. ★ 접수 수 (찬성 + 반대) -> 화면 표시용
#     submitted_count = len(sub_df[sub_df['동의여부'].isin(['찬성', '반대'])])
    
#     # 3. 동의율 (찬성 / 전체) -> 화면 표시용
#     agree_rate = (agree_count / total * 100) if total > 0 else 0
    
#     # 4. 임대 비율
#     rented_count = len(sub_df[sub_df['거주유형'] == '임대중'])
#     rented_rate = (rented_count / total * 100) if total > 0 else 0
    
#     target_dongs = ['102', '104', '106']
#     is_corridor = any(target in str(dong_name) for target in target_dongs)
    
#     num_cols = len(pivot.columns)
#     calculated_width = max(600, num_cols * 80 + 50) 
    
#     # ★ [수정됨] "XX 세대 접수 (동의율: XX%)" 로직 적용
#     # 접수: submitted_count (찬+반)
#     # 동의율: agree_rate (찬/전체)
#     html = f"""
#     <div class="dong-card">
#         <div class="dong-header">
#             <div style="font-size:20px; margin-bottom:5px;">{dong_name}동</div>
#             <div style="font-size:14px; font-weight:normal;">
#                 총 {total} 세대 중 
#                 <span style="color:#74c0fc; font-weight:bold;">{submitted_count} 세대 접수</span>
#                 (동의율: {agree_rate:.1f}%)<br>
#                 <span style="font-size:12px; color:#ced4da; margin-top:3px; display:inline-block;">(임대비율: {rented_rate:.0f}%)</span>
#             </div>
#         </div>
#         <div class="mobile-hint">👉 표를 좌우로 밀어서 보세요 👈</div>
#         <div class="table-wrapper">
#             <table class="apt-table" style="min-width: {calculated_width}px;">
#     """
    
#     for floor, row in pivot.iterrows():
#         html += "<tr>"
#         html += f'<td class="apt-cell floor-cell">{floor}F</td>'
        
#         for idx, line in enumerate(pivot.columns):
#             if is_corridor:
#                 border_class = ""
#             else:
#                 border_class = "border-bold" if (idx + 1) % 2 == 0 else ""
            
#             cell_data = row[line] 
            
#             if not isinstance(cell_data, tuple):
#                 html += f'<td class="apt-cell {border_class}"></td>'
#                 continue
            
#             status, live_type, ho_full = cell_data
            
#             if status == '찬성':
#                 cls = "status-done"      # 파란색
#             elif status == '반대':
#                 cls = "status-ban"       # 빨간색 (연락금지)
#             elif status == '응답대기':
#                 cls = "status-waiting"   # 노란색
#             else:
#                 cls = "status-todo"      # 흰색
            
#             icon = "🏠" if live_type == '실거주' else ("👤" if live_type == '임대중' else "")
            
#             html += f'<td class="apt-cell {cls} {border_class}"><span class="icon-style">{icon}</span><span class="ho-text">{ho_full}</span></td>'
#         html += "</tr>"

#     html += '<tr class="entrance-row">'
#     html += '<td class="entrance-empty"></td>'
    
#     if is_corridor:
#         html += f"""<td colspan="{num_cols}">공동 현관 (복도식)</td>"""
#     else:
#         i = 0
#         while i < num_cols:
#             if i + 1 < num_cols:
#                 html += """<td colspan="2">현관</td>"""
#                 i += 2 
#             else:
#                 html += "<td></td>"
#                 i += 1
    
#     html += """
#             </table>
#         </div>
#     </div>
#     """
#     return html

# # ---------------------------------------------------------
# # 4. 메인 화면
# # ---------------------------------------------------------
# st.sidebar.header("설정")
# cols_num = st.sidebar.slider("한 줄에 동 배치", 1, 5, 2) 

# if st.sidebar.button("🔄 데이터 새로고침"):
#     st.cache_data.clear()
#     st.rerun()

# if df.empty:
#     st.error("데이터를 불러오지 못했습니다. Google Sheets 연결 상태를 확인해주세요.")
# else:
#     total_cnt = len(df)
#     agree_cnt = len(df[df['동의여부']=='찬성'])
#     disagree_cnt = len(df[df['동의여부']=='반대'])
#     waiting_cnt = len(df[df['동의여부']=='응답대기'])
    
#     # 동의율 (전체 중 찬성 비율)
#     agree_rate = (agree_cnt / total_cnt * 100) if total_cnt > 0 else 0
    
#     st.title("산호 사전동의 현황")
    
#     k1, k2, k3, k4, k5 = st.columns(5)
    
#     k1.metric("전체 세대", f"{total_cnt}세대")
#     k2.metric("동의 세대", f"{agree_cnt}세대")
#     k3.metric("🚫 연락|방문 금지", f"{disagree_cnt}세대")
#     k4.metric("답변 대기중", f"{waiting_cnt}세대")
#     k5.metric("동의율", f"{agree_rate:.1f}%")
    
#     st.markdown("""
#     <div style="font-size:14px; color:#555; margin-top:10px; padding:10px; background-color:#f8f9fa; border-radius:5px;">
#         <strong>[범례 가이드]</strong><br>
#         🟦 <b>파란색 (동의):</b> 동의 의사 밝힌 세대<br> 
#         🟥 <b>빨간색 (연락금지):</b> 연락 및 방문 금지 세대<br>
#         🟨 <b>노란색 (답변대기중):</b> 소유자에 연락했으나 미회신 세대<br>
#         ⬜ <b>흰색 (미접수):</b> 아직 연락되지 않은 세대
#     </div>
#     """, unsafe_allow_html=True)
        
#     st.divider()
    
#     dongs = sorted(df['동'].unique())
    
#     for i in range(0, len(dongs), cols_num):
#         cols = st.columns(cols_num)
#         chunk = dongs[i:i+cols_num]
        
#         for idx, dong_name in enumerate(chunk):
#             with cols[idx]:
#                 sub_df = df[df['동'] == dong_name]
#                 st.markdown(generate_dong_html(sub_df, dong_name), unsafe_allow_html=True)

import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# ---------------------------------------------------------
# 0. [보안] 비밀번호 설정 함수
# ---------------------------------------------------------
def check_password():
    if "password_correct" not in st.session_state:
        st.session_state.password_correct = False

    if st.session_state.password_correct:
        return True

    st.markdown("### 🔒 관계자 전용 페이지")
    password = st.text_input("비밀번호를 입력하세요", type="password")
    
    if st.button("로그인"):
        if password == "sanho2325": 
            st.session_state.password_correct = True
            st.rerun()
        else:
            st.error("비밀번호가 틀렸습니다.")
    return False

# ---------------------------------------------------------
# 1. 페이지 설정 및 디자인 (CSS)
# ---------------------------------------------------------
st.set_page_config(layout="wide", page_title="산호 사전동의 현황")

if not check_password():
    st.stop()

st.markdown("""
<style>
    .block-container { padding-top: 1rem; padding-bottom: 5rem; }
    
    .dong-card {
        background-color: white;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 0px;
        margin-bottom: 30px; 
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        overflow: hidden;
        page-break-inside: avoid; 
    }
    
    .dong-header {
        background-color: #495057;
        color: white;
        padding: 15px 5px;        
        text-align: center;
        font-weight: bold;
    }
    
    .table-wrapper {
        overflow-x: auto; 
        -webkit-overflow-scrolling: touch;
        width: 100%;
        padding-bottom: 0px;
        margin-bottom: 0px;
    }
    
    .table-wrapper::-webkit-scrollbar { height: 6px; background: transparent; }
    .table-wrapper::-webkit-scrollbar-track { background: transparent; }
    .table-wrapper::-webkit-scrollbar-thumb { background-color: #ccc; border-radius: 3px; }
    
    .apt-table {
        width: 100%;
        min-width: 600px;
        table-layout: fixed;
        border-collapse: collapse;
        border-spacing: 0;
        font-size: 12px;
        margin-bottom: 0px;
    }
    
    .apt-cell {
        border: 1px solid #dee2e6;
        padding: 4px;
        text-align: center;
        height: 85px; 
        vertical-align: top; 
        white-space: normal; 
        overflow: hidden;
    }

    .floor-cell {
        width: 45px;             
        min-width: 45px;
        background-color: #f8f9fa;
        color: #495057;
        font-weight: bold;
        font-size: 11px;
        border-right: 2px solid #adb5bd !important;
        vertical-align: middle; 
        position: sticky;
        left: 0;
        z-index: 10;
    }
    
    .border-bold { border-right: 2px solid #555 !important; }
    
    /* ★ [상태별 색상 정의] ★ */
    .status-done { background-color: #e7f5ff; color: #1971c2; font-weight: bold; }   /* 파란색 (찬성) */
    .status-ban { background-color: #ffe3e3; color: #c92a2a; font-weight: bold; }    /* 빨간색 (반대/연락금지) */
    .status-visited { background-color: #fff3cd; color: #856404; font-weight: bold; } /* 노란색 (방문완료) */
    .status-todo { background-color: #ffffff; color: #adb5bd; }                        /* 흰색 (미접수) */
    
    .icon-style { font-size: 14px; margin-right: 2px; }
    .ho-text { font-size: 13px; font-family: sans-serif; font-weight: bold; display: inline-block; margin-bottom: 5px;} 
    
    /* [수정] 메모 박스 스타일 - 배경을 투명하게 변경 */
    .memo-box {
        width: 100%;
        height: 45px; 
        border: 1px dashed #adb5bd; /* 테두리는 유지 */
        border-radius: 4px;
        background-color: transparent; /* 투명하게 하여 부모 셀(호실)의 색이 보이게 함 */
        margin-top: 2px;
    }
    
    .entrance-row td {
        background-color: #e9ecef;
        color: #495057;
        text-align: center;
        vertical-align: middle;
        font-size: 12px;
        font-weight: bold;
        height: 35px;
        border-top: 2px solid #555;
        border-right: 1px solid #dee2e6;
        border-left: 1px solid #dee2e6;
        border-bottom: none !important; 
    }
    .entrance-empty {
        background-color: #fff !important;
        border: none !important;
        position: sticky;
        left: 0;
        z-index: 10;
    }

    .mobile-hint {
        font-size: 12px;
        color: #868e96;
        font-weight: bold;
        text-align: right;
        padding: 5px 10px;
        background-color: #f8f9fa;
        border-bottom: 1px solid #eee;
        display: none;
    }
    @media only screen and (max-width: 800px) { .mobile-hint { display: block; } }
    
    /* 프린트 설정 */
    @media print {
        .stSidebar, .stButton, header, footer { display: none !important; }
        .block-container { padding: 0 !important; }
        .dong-card { border: 1px solid #000; break-inside: avoid; margin-bottom: 20px; }
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. 데이터 로드
# ---------------------------------------------------------
@st.cache_data(ttl=60)
def load_data():
    try:
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        creds_dict = st.secrets["gcp_service_account"]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        client = gspread.authorize(creds)
        sheet = client.open("sanho_db").worksheet("data")
        data = sheet.get_all_records()
        df = pd.DataFrame(data)

        df['동'] = df['동'].astype(str)
        df['호'] = df['호'].astype(str)
        if '동의여부' not in df.columns: df['동의여부'] = '미조사'
        if '거주유형' not in df.columns: df['거주유형'] = ''
        
        def get_floor_line(h):
            try:
                if len(h) >= 3: return int(h[:-2]), int(h[-2:])
                return 0, 0
            except: return 0, 0
            
        df['층'], df['라인'] = zip(*df['호'].apply(get_floor_line))
        return df
    except Exception as e:
        return pd.DataFrame()

df = load_data()

# ---------------------------------------------------------
# 3. HTML 생성 함수
# ---------------------------------------------------------
def generate_dong_html(sub_df, dong_name):
    # 피벗 테이블 생성
    sub_df['info'] = list(zip(sub_df['동의여부'], sub_df['거주유형'], sub_df['호']))
    pivot = sub_df.pivot_table(index='층', columns='라인', values='info', aggfunc='first')
    pivot = pivot.sort_index(ascending=False) 
    
    total = len(sub_df)
    
    # 1. 찬성 수
    agree_count = len(sub_df[sub_df['동의여부'] == '찬성'])
    
    # 2. 접수 수 (찬성 + 반대)
    submitted_count = len(sub_df[sub_df['동의여부'].isin(['찬성', '반대'])])
    
    # 3. 동의율
    agree_rate = (agree_count / total * 100) if total > 0 else 0
    
    # 4. 임대 비율
    rented_count = len(sub_df[sub_df['거주유형'] == '임대중'])
    rented_rate = (rented_count / total * 100) if total > 0 else 0
    
    target_dongs = ['102', '104', '106']
    is_corridor = any(target in str(dong_name) for target in target_dongs)
    
    num_cols = len(pivot.columns)
    calculated_width = max(600, num_cols * 90 + 50) 
    
    html = f"""
    <div class="dong-card">
        <div class="dong-header">
            <div style="font-size:20px; margin-bottom:5px;">{dong_name}동</div>
            <div style="font-size:14px; font-weight:normal;">
                총 {total} 세대 중 
                <span style="color:#74c0fc; font-weight:bold;">{submitted_count} 세대 접수</span>
                (동의율: {agree_rate:.1f}%)<br>
                <span style="font-size:12px; color:#ced4da; margin-top:3px; display:inline-block;">(임대비율: {rented_rate:.0f}%)</span>
            </div>
        </div>
        <div class="mobile-hint">👉 표를 좌우로 밀어서 보세요 👈</div>
        <div class="table-wrapper">
            <table class="apt-table" style="min-width: {calculated_width}px;">
    """
    
    for floor, row in pivot.iterrows():
        html += "<tr>"
        html += f'<td class="apt-cell floor-cell">{floor}F</td>'
        
        for idx, line in enumerate(pivot.columns):
            if is_corridor:
                border_class = ""
            else:
                border_class = "border-bold" if (idx + 1) % 2 == 0 else ""
            
            cell_data = row[line] 
            
            if not isinstance(cell_data, tuple):
                html += f'<td class="apt-cell {border_class}"></td>'
                continue
            
            status, live_type, ho_full = cell_data
            
            if status == '찬성':
                cls = "status-done"      
            elif status == '반대':
                cls = "status-ban"       
            elif status == '방문완료':
                cls = "status-visited"   
            else:
                cls = "status-todo"      
            
            icon = "🏠" if live_type == '실거주' else ("👤" if live_type == '임대중' else "")
            
            cell_content = f'<div><span class="icon-style">{icon}</span><span class="ho-text">{ho_full}</span></div><div class="memo-box"></div>'
            html += f'<td class="apt-cell {cls} {border_class}">{cell_content}</td>'

        html += "</tr>"

    html += '<tr class="entrance-row">'
    html += '<td class="entrance-empty"></td>'
    
    if is_corridor:
        html += f"""<td colspan="{num_cols}">공동 현관 (복도식)</td>"""
    else:
        i = 0
        while i < num_cols:
            if i + 1 < num_cols:
                html += """<td colspan="2">현관</td>"""
                i += 2 
            else:
                html += "<td></td>"
                i += 1
    
    html += """
            </table>
        </div>
    </div>
    """
    return html

# ---------------------------------------------------------
# 4. 메인 화면
# ---------------------------------------------------------
st.sidebar.header("설정")
cols_num = st.sidebar.slider("한 줄에 동 배치", 1, 5, 1) 

if st.sidebar.button("🔄 데이터 새로고침"):
    st.cache_data.clear()
    st.rerun()

if df.empty:
    st.error("데이터를 불러오지 못했습니다. Google Sheets 연결 상태를 확인해주세요.")
else:
    total_cnt = len(df)
    agree_cnt = len(df[df['동의여부']=='찬성'])
    disagree_cnt = len(df[df['동의여부']=='반대'])
    visited_cnt = len(df[df['동의여부']=='방문완료'])
    
    agree_rate = (agree_cnt / total_cnt * 100) if total_cnt > 0 else 0
    
    st.title("산호 사전동의 현황")
    
    k1, k2, k3, k4, k5 = st.columns(5)
    
    k1.metric("전체 세대", f"{total_cnt}세대")
    k2.metric("동의 세대", f"{agree_cnt}세대")
    k3.metric("🚫 연락|방문 금지", f"{disagree_cnt}세대")
    k4.metric("방문 완료", f"{visited_cnt}세대") 
    k5.metric("동의율", f"{agree_rate:.1f}%")
    
    st.markdown("""
    <div style="font-size:14px; color:#555; margin-top:10px; padding:10px; background-color:#f8f9fa; border-radius:5px;">
        <strong>[범례 가이드]</strong><br>
        🟦 <b>파란색 (동의):</b> 동의 의사 밝힌 세대<br> 
        🟥 <b>빨간색 (연락금지):</b> 연락 및 방문 금지 세대<br>
        🟨 <b>노란색 (방문완료):</b> 산호 지원군 분들이 1차 방문완료하여 안내드린 세대<br>
        ⬜ <b>흰색 (미접수):</b> 아직 방문하지 않은 세대
    </div>
    """, unsafe_allow_html=True)
        
    st.divider()
    
    dongs = sorted(df['동'].unique())
    
    for i in range(0, len(dongs), cols_num):
        cols = st.columns(cols_num)
        chunk = dongs[i:i+cols_num]
        
        for idx, dong_name in enumerate(chunk):
            with cols[idx]:
                sub_df = df[df['동'] == dong_name]
                st.markdown(generate_dong_html(sub_df, dong_name), unsafe_allow_html=True)