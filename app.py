# import streamlit as st
# import pandas as pd
# import gspread
# from oauth2client.service_account import ServiceAccountCredentials

# # ---------------------------------------------------------
# # 1. 페이지 설정 및 디자인 (CSS)
# # ---------------------------------------------------------
# st.set_page_config(layout="wide", page_title="산호아파트 재건축 사전동의 현황")

# st.markdown("""
# <style>
#     /* 상단 여백 확보 */
#     .block-container { padding-top: 3rem; padding-bottom: 5rem; }
    
#     /* 각 동 카드 디자인 */
#     .dong-card {
#         background-color: white;
#         border: 1px solid #e0e0e0;
#         border-radius: 8px;
#         padding: 0px;
#         margin-bottom: 20px;
#         box-shadow: 0 2px 4px rgba(0,0,0,0.05);
#         overflow: hidden;
#     }
    
#     /* 동 헤더 (제목) 스타일 */
#     .dong-header {
#         background-color: #333;
#         color: white;
#         padding: 12px 5px;       
#         text-align: center;
#         font-weight: bold;
#         font-size: 18px;
#     }
    
#     /* 가로 스크롤 영역 */
#     .table-wrapper {
#         overflow-x: auto; 
#         -webkit-overflow-scrolling: touch;
#         width: 100%;
#         padding-bottom: 5px;
#     }
    
#     /* 테이블 공통 스타일 */
#     .apt-table {
#         width: 100%;
#         min-width: 600px;
#         table-layout: fixed;
#         border-collapse: collapse;
#         border-spacing: 0;
#         font-size: 12px;
#     }
    
#     /* 일반 셀 스타일 */
#     .apt-cell {
#         border: 1px solid #dee2e6;
#         padding: 6px 2px;
#         text-align: center;
#         height: 45px;
#         vertical-align: middle;
#         white-space: nowrap; 
#         overflow: hidden;
#     }

#     /* 층수 표시 셀 (왼쪽 고정) */
#     .floor-cell {
#         width: 45px;             
#         min-width: 45px;
#         background-color: #f1f3f5;
#         color: #495057;
#         font-weight: bold;
#         font-size: 11px;
#         border-right: 2px solid #adb5bd !important;
#         position: sticky;
#         left: 0;
#         z-index: 10;
#     }
    
#     /* 계단식 아파트용 굵은 경계선 */
#     .border-bold { border-right: 2px solid #555 !important; }
    
#     /* ★ 상태별 색상 (응답대기 추가) ★ */
#     .status-agree { background-color: #d1e7dd; color: #0f5132; font-weight: bold; }   /* 초록 */
#     .status-disagree { background-color: #f8d7da; color: #842029; font-weight: bold; } /* 빨강 */
#     .status-waiting { background-color: #fff3cd; color: #856404; font-weight: bold; }  /* 노랑(오렌지) */
#     .status-unknown { background-color: white; color: #ccc; }                          /* 흰색 */
    
#     .icon-style { font-size: 14px; margin-right: 2px; }
#     .ho-text { font-size: 12px; font-family: sans-serif; font-weight: bold; } 
    
#     /* 하단 입구 행 스타일 */
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
#     }
    
#     /* 입구 행의 맨 왼쪽(층수열 아래) 빈칸 처리 */
#     .entrance-empty {
#         background-color: #fff !important;
#         border: none !important;
#         position: sticky;
#         left: 0;
#         z-index: 10;
#     }

#     /* 모바일 안내 문구 */
#     .mobile-hint {
#         font-size: 12px;
#         color: #e03131;
#         font-weight: bold;
#         text-align: right;
#         padding: 5px 10px;
#         background-color: #fff5f5;
#         border-bottom: 1px solid #ffe3e3;
#         display: none;
#     }
    
#     @media only screen and (max-width: 800px) {
#         .mobile-hint { display: block; }
#     }
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
#     # 피벗 테이블
#     sub_df['info'] = list(zip(sub_df['동의여부'], sub_df['거주유형'], sub_df['호']))
#     pivot = sub_df.pivot_table(index='층', columns='라인', values='info', aggfunc='first')
#     pivot = pivot.sort_index(ascending=False) 
    
#     # ★ [수정] 통계 계산 (응답대기 추가)
#     total = len(sub_df)
#     agree = len(sub_df[sub_df['동의여부'] == '찬성'])
#     disagree = len(sub_df[sub_df['동의여부'] == '반대'])
#     waiting = len(sub_df[sub_df['동의여부'] == '응답대기']) # 대기 수 계산
    
#     rate = (agree / total * 100) if total > 0 else 0
    
#     # 복도식 확인
#     target_dongs = ['102', '104', '106']
#     is_corridor = any(target in str(dong_name) for target in target_dongs)
    
#     # 동적 너비 계산
#     num_cols = len(pivot.columns)
#     calculated_width = max(600, num_cols * 60 + 50) 
    
#     # ★ [수정] 헤더 표시 형식 (대기 추가, 색상 구분)
#     # 찬성(노랑), 반대(연한빨강), 대기(연한주황)
#     html = f"""
#     <div class="dong-card">
#         <div class="dong-header">
#             {dong_name}동 
#             <span style="font-size:16px; margin-left:8px; font-weight:normal;">
#                 <span style="color:#FFF176;">(총 {total} 세대</span> | 
#                 <span style="color:#FFF176;">찬성: {agree}</span> | 
#                 <span style="color:#ff8a80;">반대: {disagree}</span> | 
#                 <span style="color:#ffe0b2;">응답대기: {waiting}</span> | 
#                 <span style="color:#FFF176;">동의율: {rate:.0f}%)</span>
#             </span>
#         </div>
#         <div class="mobile-hint">👉 표를 좌우로 밀어서 보세요 👈</div>
#         <div class="table-wrapper">
#             <table class="apt-table" style="min-width: {calculated_width}px;">
#     """
    
#     # [Table Body]
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
            
#             # ★ [수정] 상태별 클래스 매핑 (응답대기 추가)
#             cls = "status-unknown"
#             if status == '찬성': cls = "status-agree"
#             elif status == '반대': cls = "status-disagree"
#             elif status == '응답대기': cls = "status-waiting"  # 여기 추가됨
            
#             icon = "🏠" if live_type == '실거주' else ("👤" if live_type == '임대중' else "")
            
#             html += f'<td class="apt-cell {cls} {border_class}"><span class="icon-style">{icon}</span><span class="ho-text">{ho_full}</span></td>'
#         html += "</tr>"

#     # [Table Footer]
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
    
#     html += "</tr>"
        
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
# cols_num = st.sidebar.slider("한 줄에 동 배치 (PC 추천: 2~3)", 1, 5, 2) 

# if st.sidebar.button("🔄 데이터 새로고침"):
#     st.cache_data.clear()
#     st.rerun()

# if df.empty:
#     st.error("데이터를 불러오지 못했습니다. Google Sheets 연결 상태를 확인해주세요.")
# else:
#     # ★ [수정] 전체 통계 계산 (응답대기 포함)
#     total_cnt = len(df)
#     agree_cnt = len(df[df['동의여부']=='찬성'])
#     disagree_cnt = len(df[df['동의여부']=='반대'])
#     waiting_cnt = len(df[df['동의여부']=='응답대기']) # 대기 카운트
#     total_rate = (agree_cnt / total_cnt * 100) if total_cnt > 0 else 0
    
#     st.title("산호아파트 재건축 사전동의 현황")
    
#     # ★ [수정] 상단 컬럼 6개로 분할 (대기 추가)
#     # 비율: 전체(1) 찬성(1) 반대(1) 대기(1) 율(1.2) 범례(1.8)
#     k1, k2, k3, k4, k5, k6 = st.columns([1, 1, 1, 1, 1.2, 1.8])
    
#     k1.metric("전체 세대", f"{total_cnt}")
#     k2.metric("찬성", f"{agree_cnt}")
#     k3.metric("반대", f"{disagree_cnt}")
#     k4.metric("응답대기", f"{waiting_cnt}") # 회색/중립 느낌
#     k5.metric("전체 동의율 ", f"{total_rate:.1f}%")
    
#     with k6:
#         st.markdown("""
#         <div style="font-size:13px; color:#555; margin-top:0px; border-left:3px solid #ccc; padding-left:10px;">
#         <b>범례</b><br>
#         🟩찬성 🟥반대 🟨대기 <br> 
#         🏠소유주 👤세입자
#         </div>
#         """, unsafe_allow_html=True)
        
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
# 1. 페이지 설정 및 디자인 (CSS)
# ---------------------------------------------------------
st.set_page_config(layout="wide", page_title="산호아파트 재건축 사전동의 현황")

st.markdown("""
<style>
    /* 상단 여백 확보 */
    .block-container { padding-top: 3rem; padding-bottom: 5rem; }
    
    /* 각 동 카드 디자인 */
    .dong-card {
        background-color: white;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 0px;
        margin-bottom: 20px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        overflow: hidden;
    }
    
    /* 동 헤더 (제목) 스타일 */
    .dong-header {
        background-color: #333;
        color: white;
        padding: 15px 5px;       
        text-align: center;
        font-weight: bold;
    }
    
    /* ★ [수정됨] 가로 스크롤 영역: 하단 여백 제거 및 스크롤바 스타일링 */
    .table-wrapper {
        overflow-x: auto; 
        -webkit-overflow-scrolling: touch;
        width: 100%;
        padding-bottom: 0px; /* 5px -> 0px 로 변경하여 흰색 공백 제거 */
        margin-bottom: 0px;
    }
    
    /* 스크롤바 트랙(배경)을 투명하게 설정 */
    .table-wrapper::-webkit-scrollbar {
        height: 6px; /* 높이를 얇게 */
        background: transparent;
    }
    .table-wrapper::-webkit-scrollbar-track {
        background: transparent; 
    }
    .table-wrapper::-webkit-scrollbar-thumb {
        background-color: #ccc; /* 스크롤바 색상 연한 회색 */
        border-radius: 3px;
    }
    
    /* 테이블 공통 스타일 */
    .apt-table {
        width: 100%;
        min-width: 600px;
        table-layout: fixed;
        border-collapse: collapse;
        border-spacing: 0;
        font-size: 12px;
        margin-bottom: 0px; /* 테이블 자체 하단 여백 제거 */
    }
    
    /* 일반 셀 스타일 */
    .apt-cell {
        border: 1px solid #dee2e6;
        padding: 6px 2px;
        text-align: center;
        height: 45px;
        vertical-align: middle;
        white-space: nowrap; 
        overflow: hidden;
    }

    /* 층수 표시 셀 (왼쪽 고정) */
    .floor-cell {
        width: 45px;             
        min-width: 45px;
        background-color: #f1f3f5;
        color: #495057;
        font-weight: bold;
        font-size: 11px;
        border-right: 2px solid #adb5bd !important;
        position: sticky;
        left: 0;
        z-index: 10;
    }
    
    /* 계단식 아파트용 굵은 경계선 */
    .border-bold { border-right: 2px solid #555 !important; }
    
    /* 상태별 색상 */
    .status-agree { background-color: #d1e7dd; color: #0f5132; font-weight: bold; }   /* 초록 */
    .status-disagree { background-color: #f8d7da; color: #842029; font-weight: bold; } /* 빨강 */
    .status-waiting { background-color: #fff3cd; color: #856404; font-weight: bold; }  /* 노랑 */
    .status-unknown { background-color: white; color: #ccc; }                          /* 흰색 */
    
    .icon-style { font-size: 14px; margin-right: 2px; }
    .ho-text { font-size: 12px; font-family: sans-serif; font-weight: bold; } 
    
    /* 하단 입구 행 스타일 */
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
        /* 아래쪽 테두리 없애서 카드 바닥과 밀착 */
        border-bottom: none !important; 
    }
    
    /* 입구 행의 맨 왼쪽(층수열 아래) 빈칸 처리 */
    .entrance-empty {
        background-color: #fff !important;
        border: none !important;
        position: sticky;
        left: 0;
        z-index: 10;
    }

    /* 모바일 안내 문구 */
    .mobile-hint {
        font-size: 12px;
        color: #e03131;
        font-weight: bold;
        text-align: right;
        padding: 5px 10px;
        background-color: #fff5f5;
        border-bottom: 1px solid #ffe3e3;
        display: none;
    }
    
    @media only screen and (max-width: 800px) {
        .mobile-hint { display: block; }
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
    # 피벗 테이블
    sub_df['info'] = list(zip(sub_df['동의여부'], sub_df['거주유형'], sub_df['호']))
    pivot = sub_df.pivot_table(index='층', columns='라인', values='info', aggfunc='first')
    pivot = pivot.sort_index(ascending=False) 
    
    # 통계 계산
    total = len(sub_df)
    agree = len(sub_df[sub_df['동의여부'] == '찬성'])
    disagree = len(sub_df[sub_df['동의여부'] == '반대'])
    waiting = len(sub_df[sub_df['동의여부'] == '응답대기']) 
    
    rate = (agree / total * 100) if total > 0 else 0
    
    # 복도식 확인
    target_dongs = ['102', '104', '106']
    is_corridor = any(target in str(dong_name) for target in target_dongs)
    
    # 동적 너비 계산
    num_cols = len(pivot.columns)
    calculated_width = max(600, num_cols * 80 + 50) 
    
    # ★ [수정] 헤더 색상 변경
    # 찬성: #a5d6a7 (연한 초록)
    # 대기: #e0e0e0 (연한 회색)
    html = f"""
    <div class="dong-card">
        <div class="dong-header">
            <div style="font-size:20px; margin-bottom:5px;">{dong_name}동</div>
            <div style="font-size:15px; font-weight:normal; line-height:1.4;">
                <span style="color:#ffffff;">(총 {total} 세대</span> | 
                <span style="color:#a5d6a7;">찬성: {agree}</span> | 
                <span style="color:#ff8a80;">반대: {disagree}</span> | 
                <span style="color:#FFF176;">응답대기: {waiting}</span> | 
                <span style="color:#ffffff;">동의율: {rate:.0f}%)</span>
            </div>
        </div>
        <div class="mobile-hint">👉 표를 좌우로 밀어서 보세요 👈</div>
        <div class="table-wrapper">
            <table class="apt-table" style="min-width: {calculated_width}px;">
    """
    
    # [Table Body]
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
            
            cls = "status-unknown"
            if status == '찬성': cls = "status-agree"
            elif status == '반대': cls = "status-disagree"
            elif status == '응답대기': cls = "status-waiting"
            
            icon = "🏠" if live_type == '실거주' else ("👤" if live_type == '임대중' else "")
            
            html += f'<td class="apt-cell {cls} {border_class}"><span class="icon-style">{icon}</span><span class="ho-text">{ho_full}</span></td>'
        html += "</tr>"

    # [Table Footer]
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
    
    html += "</tr>"
        
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
cols_num = st.sidebar.slider("한 줄에 동 배치 (PC 추천: 2~3)", 1, 5, 2) 

if st.sidebar.button("🔄 데이터 새로고침"):
    st.cache_data.clear()
    st.rerun()

if df.empty:
    st.error("데이터를 불러오지 못했습니다. Google Sheets 연결 상태를 확인해주세요.")
else:
    total_cnt = len(df)
    agree_cnt = len(df[df['동의여부']=='찬성'])
    disagree_cnt = len(df[df['동의여부']=='반대'])
    waiting_cnt = len(df[df['동의여부']=='응답대기'])
    total_rate = (agree_cnt / total_cnt * 100) if total_cnt > 0 else 0
    
    st.title("산호아파트 재건축 사전동의 현황")
    
    # 상단 지표
    k1, k2, k3, k4, k5, k6 = st.columns([1, 1, 1, 1, 1.2, 1.8])
    
    k1.metric("전체 세대", f"{total_cnt}")
    k2.metric("찬성", f"{agree_cnt}")
    k3.metric("반대", f"{disagree_cnt}")
    k4.metric("응답대기", f"{waiting_cnt}")
    k5.metric("전체 동의율", f"{total_rate:.1f}%")
    
    with k6:
        st.markdown("""
        <div style="font-size:16px; color:#333; margin-top:0px; border-left:4px solid #ccc; padding-left:12px; line-height: 1.5;">
            <strong style="font-size:18px;">범례</strong><br>
            🟩 찬성 &nbsp; 🟥 반대 &nbsp; 🟨 응답대기 <br> 
            🏠 소유주거주 &nbsp; 👤 세입자거주
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