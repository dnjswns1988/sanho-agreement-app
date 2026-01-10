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
#         border-collapse: collapse; /* 테두리 겹침 허용 */
#         border-spacing: 0;
#         font-size: 12px;
#         margin-bottom: 0px;
#     }
    
#     /* ▼▼▼ [수정됨] 층 구분선(가로) 확실하게 변경 ▼▼▼ */
#     .apt-cell {
#         /* 가로선: 층 바닥을 검정색(#000) 2px 실선으로 처리 */
#         border-bottom: 2px solid #000 !important;
        
#         /* 세로선: 호수 사이는 연한 회색 유지 */
#         border-left: 1px solid #dee2e6;
#         border-right: 1px solid #dee2e6;
        
#         /* 위쪽 선은 없애서 이중선 방지 (윗집의 바닥선이 내 천장이 됨) */
#         border-top: 0px !important;

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
        
#         /* 층수 표시 셀도 바닥선 검정색으로 통일 */
#         border-bottom: 2px solid #000 !important;
#         border-right: 2px solid #adb5bd !important; /* 층수와 호수 사이는 조금 진한 회색 */
#         border-top: 0px !important;
        
#         position: sticky;
#         left: 0;
#         z-index: 10;
#     }
    
#     .border-bold { border-right: 2px solid #555 !important; }
    
#     /* 상태별 색상 */
#     .status-done { background-color: #e7f5ff; color: #1971c2; font-weight: bold; }   
#     .status-ban { background-color: #ffe3e3; color: #c92a2a; font-weight: bold; }    
#     .status-visited { background-color: #fff3cd; color: #856404; font-weight: bold; } 
#     .status-todo { background-color: #ffffff; color: #adb5bd; }                       
    
#     .icon-style { font-size: 14px; margin-right: 2px; }
    
#     /* 폰트 크기 18px */
#     .ho-text { font-size: 18px; font-family: sans-serif; font-weight: bold; } 
    
#     .entrance-row td {
#         background-color: #e9ecef;
#         color: #495057;
#         text-align: center;
#         vertical-align: middle;
#         font-size: 12px;
#         font-weight: bold;
#         height: 35px;
        
#         /* 1층 바닥 아래(현관 위)도 검정선 처리 */
#         border-top: 2px solid #000 !important; 
        
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
    
#     # 1. 찬성 수
#     agree_count = len(sub_df[sub_df['동의여부'] == '찬성'])
    
#     # 2. 접수 수
#     submitted_count = len(sub_df[sub_df['동의여부'].isin(['찬성', '반대'])])
    
#     # 3. 동의율
#     agree_rate = (agree_count / total * 100) if total > 0 else 0
    
#     # 4. 임대 비율
#     rented_count = len(sub_df[sub_df['거주유형'] == '임대중'])
#     rented_rate = (rented_count / total * 100) if total > 0 else 0
    
#     target_dongs = ['102', '104', '106']
#     is_corridor = any(target in str(dong_name) for target in target_dongs)
    
#     num_cols = len(pivot.columns)
#     calculated_width = max(600, num_cols * 80 + 50) 
    
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
#                 cls = "status-done"      
#             elif status == '반대':
#                 cls = "status-ban"       
#             elif status == '방문완료':
#                 cls = "status-visited"   
#             else:
#                 cls = "status-todo"      
            
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
#     visited_cnt = len(df[df['동의여부']=='방문완료'])
    
#     agree_rate = (agree_cnt / total_cnt * 100) if total_cnt > 0 else 0
    
#     st.title("산호 사전동의 현황")
    
#     k1, k2, k3, k4, k5 = st.columns(5)
    
#     k1.metric("전체 세대", f"{total_cnt}세대")
#     k2.metric("동의 세대", f"{agree_cnt}세대")
#     k3.metric("🚫 연락|방문 금지", f"{disagree_cnt}세대")
#     k4.metric("방문 완료", f"{visited_cnt}세대")
#     k5.metric("동의율", f"{agree_rate:.1f}%")
    
#     st.markdown("""
#     <div style="font-size:14px; color:#555; margin-top:10px; padding:10px; background-color:#f8f9fa; border-radius:5px;">
#         <strong>[범례 가이드]</strong><br>
#         🟦 <b>파란색 (동의):</b> 동의 의사 밝힌 세대<br> 
#         🟥 <b>빨간색 (연락금지):</b> 연락 및 방문 금지 세대<br>
#         🟨 <b>노란색 (방문완료):</b> 방문하였으나 부재/보류 등<br>
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
    .block-container { padding-top: 3rem; padding-bottom: 5rem; }
    
    .dong-card {
        background-color: white;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 0px;
        margin-bottom: 20px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        overflow: hidden;
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
    
    /* ▼▼▼ [수정됨] 높이 80px로 확장 및 상단 정렬 ▼▼▼ */
    .apt-cell {
        /* 가로선: 층 바닥을 검정색(#000) 2px 실선 */
        border-bottom: 2px solid #000 !important;
        
        /* 세로선: 호수 사이는 연한 회색 */
        border-left: 1px solid #dee2e6;
        border-right: 1px solid #dee2e6;
        
        border-top: 0px !important;

        padding: 8px 2px;     /* 내부 여백 약간 조정 */
        text-align: center;
        height: 80px;         /* 높이를 키움 (메모 공간) */
        vertical-align: top;  /* 글씨를 위쪽으로 붙임 */
        white-space: normal;  /* 메모가 길면 줄바꿈 되도록 */
        overflow: hidden;
    }

    .floor-cell {
        width: 45px;             
        min-width: 45px;
        background-color: #f8f9fa;
        color: #495057;
        font-weight: bold;
        font-size: 11px;
        
        border-bottom: 2px solid #000 !important;
        border-right: 2px solid #adb5bd !important; 
        border-top: 0px !important;
        
        vertical-align: middle; /* 층수는 가운데 정렬 유지 */
        position: sticky;
        left: 0;
        z-index: 10;
    }
    
    .border-bold { border-right: 2px solid #555 !important; }
    
    .status-done { background-color: #e7f5ff; color: #1971c2; font-weight: bold; }   
    .status-ban { background-color: #ffe3e3; color: #c92a2a; font-weight: bold; }    
    .status-visited { background-color: #fff3cd; color: #856404; font-weight: bold; } 
    .status-todo { background-color: #ffffff; color: #adb5bd; }                       
    
    .icon-style { font-size: 14px; margin-right: 2px; }
    
    /* 호수 폰트: 18px */
    .ho-text { 
        font-size: 18px; 
        font-family: sans-serif; 
        font-weight: bold; 
        display: block;      /* 블록 요소로 만들어 줄바꿈 */
        margin-bottom: 4px;  /* 아래 메모와 간격 */
    } 

    /* ▼▼▼ [추가됨] 메모 스타일 ▼▼▼ */
    .memo-text {
        font-size: 11px;
        color: #495057;
        font-weight: normal;
        line-height: 1.2;
        min-height: 10px; /* 비어있어도 공간 확보 */
    }
    
    .entrance-row td {
        background-color: #e9ecef;
        color: #495057;
        text-align: center;
        vertical-align: middle;
        font-size: 12px;
        font-weight: bold;
        height: 35px;
        border-top: 2px solid #000 !important; 
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
        
        # ▼▼▼ [추가됨] 비고(메모) 컬럼 처리 ▼▼▼
        if '비고' not in df.columns: df['비고'] = ''
        else: df['비고'] = df['비고'].fillna('').astype(str)

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
    # ▼▼▼ [수정됨] 비고 컬럼 포함 ▼▼▼
    sub_df['info'] = list(zip(sub_df['동의여부'], sub_df['거주유형'], sub_df['호'], sub_df['비고']))
    pivot = sub_df.pivot_table(index='층', columns='라인', values='info', aggfunc='first')
    pivot = pivot.sort_index(ascending=False) 
    
    total = len(sub_df)
    
    # 1. 찬성 수
    agree_count = len(sub_df[sub_df['동의여부'] == '찬성'])
    
    # 2. 접수 수
    submitted_count = len(sub_df[sub_df['동의여부'].isin(['찬성', '반대'])])
    
    # 3. 동의율
    agree_rate = (agree_count / total * 100) if total > 0 else 0
    
    # 4. 임대 비율
    rented_count = len(sub_df[sub_df['거주유형'] == '임대중'])
    rented_rate = (rented_count / total * 100) if total > 0 else 0
    
    target_dongs = ['102', '104', '106']
    is_corridor = any(target in str(dong_name) for target in target_dongs)
    
    num_cols = len(pivot.columns)
    calculated_width = max(600, num_cols * 80 + 50) 
    
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
            
            # ▼▼▼ [수정됨] 데이터 언패킹 (비고 추가) ▼▼▼
            status, live_type, ho_full, memo_text = cell_data
            
            if status == '찬성':
                cls = "status-done"      
            elif status == '반대':
                cls = "status-ban"       
            elif status == '방문완료':
                cls = "status-visited"   
            else:
                cls = "status-todo"      
            
            icon = "🏠" if live_type == '실거주' else ("👤" if live_type == '임대중' else "")
            
            # ▼▼▼ [수정됨] 호수 아래에 메모 공간 추가 ▼▼▼
            html += f"""
            <td class="apt-cell {cls} {border_class}">
                <span class="icon-style">{icon}</span><span class="ho-text">{ho_full}</span>
                <div class="memo-text">{memo_text}</div>
            </td>
            """
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
cols_num = st.sidebar.slider("한 줄에 동 배치", 1, 5, 2) 

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
        🟨 <b>노란색 (방문완료):</b> 방문하였으나 부재/보류 등<br>
        ⬜ <b>흰색 (미접수):</b> 아직 연락되지 않은 세대
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