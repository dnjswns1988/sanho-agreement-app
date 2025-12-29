# import streamlit as st
# import pandas as pd
# import gspread
# from oauth2client.service_account import ServiceAccountCredentials

# # ---------------------------------------------------------
# # 1. 페이지 설정 및 디자인
# # ---------------------------------------------------------
# st.set_page_config(layout="wide", page_title="산호아파트 재건축 사전동의 현황")

# st.markdown("""
# <style>
#     /* 상단 여백 확보 */
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
#         background-color: #333;
#         color: white;
#         padding: 8px 5px;
#         text-align: center;
#         font-weight: bold;
#         font-size: 15px;
#     }
    
#     /* 가로 스크롤 영역 */
#     .table-wrapper {
#         overflow-x: auto; 
#         -webkit-overflow-scrolling: touch;
#         width: 100%;
#         padding-bottom: 5px;
#     }
    
#     /* 테이블 기본 스타일 */
#     .apt-table {
#         width: 100%;
#         min-width: 600px; /* 복도식은 라인이 많아 좁을 수 있으므로 조정 가능 */
#         table-layout: fixed;
#         border-collapse: collapse;
#         font-size: 12px;
#     }
    
#     /* 셀 스타일 */
#     .apt-cell {
#         border: 1px solid #dee2e6;
#         padding: 6px 2px;
#         text-align: center;
#         height: 45px;
#         vertical-align: middle;
#         white-space: nowrap; 
#         overflow: hidden;
#     }
    
#     /* 계단식 전용: 두 라인마다 굵은 선 */
#     .border-bold { border-right: 2px solid #555 !important; }
    
#     /* 상태별 색상 */
#     .status-agree { background-color: #d1e7dd; color: #0f5132; font-weight: bold; }
#     .status-disagree { background-color: #f8d7da; color: #842029; font-weight: bold; }
#     .status-unknown { background-color: white; color: #ccc; }
    
#     .icon-style { font-size: 14px; margin-right: 2px; }
#     .ho-text { font-size: 12px; font-family: sans-serif; font-weight: bold; } 
    
#     /* 입구 행 */
#     .entrance-row td {
#         background-color: #f1f3f5;
#         color: #495057;
#         text-align: center;
#         vertical-align: middle;
#         font-size: 12px;
#         font-weight: bold;
#         height: 30px;
#         border-top: 2px solid #555;
#         border-right: 1px solid #dee2e6;
#         border-left: 1px solid #dee2e6;
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
# # 3. HTML 생성 함수 (복도식 로직 추가)
# # ---------------------------------------------------------
# def generate_dong_html(sub_df, dong_name):
#     sub_df['info'] = list(zip(sub_df['동의여부'], sub_df['거주유형'], sub_df['호']))
#     pivot = sub_df.pivot_table(index='층', columns='라인', values='info', aggfunc='first')
#     pivot = pivot.sort_index(ascending=False) 
    
#     total = len(sub_df)
#     agree = len(sub_df[sub_df['동의여부'] == '찬성'])
#     rate = (agree / total * 100) if total > 0 else 0
    
#     # ★ 복도식 아파트인지 확인 (문자열 비교)
#     is_corridor = str(dong_name) in ['102', '104', '106']
    
#     html = f"""
#     <div class="dong-card">
#         <div class="dong-header">
#             {dong_name}동 <span style="font-size:0.85em; opacity:0.9; font-weight:normal;">(총 {total}세대 | {rate:.0f}%)</span>
#         </div>
#         <div class="mobile-hint">👉 표를 좌우로 밀어서 보세요 👈</div>
#         <div class="table-wrapper">
#             <table class="apt-table">
#     """
    
#     # 3-1. 호실 배치 (본문)
#     for floor, row in pivot.iterrows():
#         html += "<tr>"
#         for idx, line in enumerate(pivot.columns):
#             # ★ 복도식은 굵은 경계선 없음, 계단식만 2개마다 적용
#             if is_corridor:
#                 border_class = ""
#             else:
#                 border_class = "border-bold" if (idx + 1) % 2 == 0 else ""
            
#             cell_data = row[line] 
            
#             if not isinstance(cell_data, tuple):
#                 html += f'<td class="apt-cell {border_class}"></td>'
#                 continue
            
#             status, live_type, ho_full = cell_data
#             cls = "status-unknown"
#             if status == '찬성': cls = "status-agree"
#             elif status == '반대': cls = "status-disagree"
#             icon = "🏠" if live_type == '실거주' else ("👤" if live_type == '임대중' else "")
            
#             html += f'<td class="apt-cell {cls} {border_class}"><span class="icon-style">{icon}</span><span class="ho-text">{ho_full}</span></td>'
#         html += "</tr>"

#     # 3-2. 입구 (Footer)
#     html += '<tr class="entrance-row">'
#     num_cols = len(pivot.columns)
    
#     # ★ 복도식: 전체를 하나로 통합 (colspan = 전체 컬럼 수)
#     if is_corridor:
#         html += f"""<td colspan="{num_cols}">공동 현관 (복도식)</td>"""
    
#     # ★ 계단식: 2개씩 묶어서 입구 표시
#     else:
#         i = 0
#         while i < num_cols:
#             if i + 1 < num_cols:
#                 html += """<td colspan="2">입구</td>"""
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
#     st.error("데이터 로딩 실패")
# else:
#     total_cnt = len(df)
#     agree_cnt = len(df[df['동의여부']=='찬성'])
#     total_rate = (agree_cnt / total_cnt * 100) if total_cnt > 0 else 0
    
#     st.title("산호아파트 재건축 사전동의 현황")
    
#     k1, k2, k3, k4 = st.columns(4)
#     k1.metric("전체", f"{total_cnt}", delta="세대")
#     k2.metric("찬성", f"{agree_cnt}", delta="세대")
#     k3.metric("전체 동의율", f"{total_rate:.1f}%")
    
#     with k4:
#         st.markdown("""
#         <div style="font-size:12px; color:#555; margin-top:5px;">
#         🟩찬성 🟥반대 <br> 🏠집주인실거주 👤세입자거주
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
    
    /* 동 헤더 (제목) 스타일 - 글자 키움 */
    .dong-header {
        background-color: #333;
        color: white;
        padding: 12px 5px;       
        text-align: center;
        font-weight: bold;
        font-size: 18px;         /* 제목 크기 확대 */
    }
    
    /* 가로 스크롤 영역 */
    .table-wrapper {
        overflow-x: auto; 
        -webkit-overflow-scrolling: touch;
        width: 100%;
        padding-bottom: 5px;
    }
    
    /* 테이블 공통 스타일 */
    .apt-table {
        width: 100%;
        min-width: 600px;        /* 너무 좁아지지 않게 방어 */
        table-layout: fixed;
        border-collapse: collapse;
        border-spacing: 0;
        font-size: 12px;
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

    /* ★ 층수 표시 셀 (왼쪽 고정) ★ */
    .floor-cell {
        width: 45px;             
        min-width: 45px;
        background-color: #f1f3f5; /* 연한 회색 배경 */
        color: #495057;
        font-weight: bold;
        font-size: 11px;
        border-right: 2px solid #adb5bd !important; /* 구분선 진하게 */
        
        /* 스크롤 시 왼쪽 고정 (Sticky) */
        position: sticky;
        left: 0;
        z-index: 10;
    }
    
    /* 계단식 아파트용 굵은 경계선 */
    .border-bold { border-right: 2px solid #555 !important; }
    
    /* 상태별 색상 */
    .status-agree { background-color: #d1e7dd; color: #0f5132; font-weight: bold; }
    .status-disagree { background-color: #f8d7da; color: #842029; font-weight: bold; }
    .status-unknown { background-color: white; color: #ccc; }
    
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
    
    /* 화면 폭이 800px 이하일 때만 안내 문구 표시 */
    @media only screen and (max-width: 800px) {
        .mobile-hint { display: block; }
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. 데이터 로드 (구글 시트 연동)
# ---------------------------------------------------------
@st.cache_data(ttl=60)
def load_data():
    try:
        # Streamlit Secrets에서 인증 정보 가져오기
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        creds_dict = st.secrets["gcp_service_account"]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        client = gspread.authorize(creds)
        
        # 구글 시트 열기 (파일명: sanho_db, 시트명: data)
        sheet = client.open("sanho_db").worksheet("data")
        data = sheet.get_all_records()
        df = pd.DataFrame(data)

        # 데이터 전처리
        df['동'] = df['동'].astype(str)
        df['호'] = df['호'].astype(str)
        if '동의여부' not in df.columns: df['동의여부'] = '미조사'
        if '거주유형' not in df.columns: df['거주유형'] = ''
        
        # 호수에서 층과 라인 분리 함수
        def get_floor_line(h):
            try:
                # 예: 1501 -> 15층, 1호 / 101 -> 1층, 1호
                if len(h) >= 3: return int(h[:-2]), int(h[-2:])
                return 0, 0
            except: return 0, 0
            
        df['층'], df['라인'] = zip(*df['호'].apply(get_floor_line))
        return df
    except Exception as e:
        # 에러 발생 시 빈 데이터프레임 반환 (화면에 에러 메시지 대신 빈 화면)
        return pd.DataFrame()

df = load_data()

# ---------------------------------------------------------
# 3. HTML 생성 함수 (핵심 로직)
# ---------------------------------------------------------
def generate_dong_html(sub_df, dong_name):
    # 피벗 테이블 생성 (층 x 라인)
    sub_df['info'] = list(zip(sub_df['동의여부'], sub_df['거주유형'], sub_df['호']))
    pivot = sub_df.pivot_table(index='층', columns='라인', values='info', aggfunc='first')
    pivot = pivot.sort_index(ascending=False) 
    
    total = len(sub_df)
    agree = len(sub_df[sub_df['동의여부'] == '찬성'])
    rate = (agree / total * 100) if total > 0 else 0
    
    # 복도식 아파트 확인
    target_dongs = ['102', '104', '106']
    is_corridor = any(target in str(dong_name) for target in target_dongs)
    
    # ★ [핵심 수정] 동적 너비 계산
    # 라인(열) 개수를 셉니다.
    num_cols = len(pivot.columns)
    
    # "라인 수 * 60px"과 "기본 600px" 중 더 큰 값을 표의 최소 너비로 설정
    # 예: 복도식이 15라인이면 15 * 60 = 900px까지 늘어남 -> 4자리 숫자 안 잘림
    calculated_width = max(600, num_cols * 60 + 50) # 50은 층수 표시열 여분
    
    html = f"""
    <div class="dong-card">
        <div class="dong-header">
            {dong_name}동 
            <span style="font-size:16px; color:#FFF176; margin-left:8px; font-weight:normal;">
                (총 {total}세대 | {rate:.0f}%)
            </span>
        </div>
        <div class="mobile-hint">👉 표를 좌우로 밀어서 보세요 👈</div>
        <div class="table-wrapper">
            <table class="apt-table" style="min-width: {calculated_width}px;">
    """
    
    # [Table Body] 호실 배치
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
            icon = "🏠" if live_type == '실거주' else ("👤" if live_type == '임대중' else "")
            
            html += f'<td class="apt-cell {cls} {border_class}"><span class="icon-style">{icon}</span><span class="ho-text">{ho_full}</span></td>'
        html += "</tr>"

    # [Table Footer] 입구 표시
    html += '<tr class="entrance-row">'
    html += '<td class="entrance-empty"></td>'
    
    if is_corridor:
        html += f"""<td colspan="{num_cols}">공동 현관 (복도식)</td>"""
    else:
        i = 0
        while i < num_cols:
            if i + 1 < num_cols:
                html += """<td colspan="2">입구</td>"""
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
# 4. 메인 화면 구성
# ---------------------------------------------------------
# 사이드바 설정
st.sidebar.header("설정")
cols_num = st.sidebar.slider("한 줄에 동 배치 (PC 추천: 2~3)", 1, 5, 2) 

if st.sidebar.button("🔄 데이터 새로고침"):
    st.cache_data.clear()
    st.rerun()

# 데이터 로딩 확인
if df.empty:
    st.error("데이터를 불러오지 못했습니다. Google Sheets 연결 상태를 확인해주세요.")
else:
    # 전체 통계 계산
    total_cnt = len(df)
    agree_cnt = len(df[df['동의여부']=='찬성'])
    total_rate = (agree_cnt / total_cnt * 100) if total_cnt > 0 else 0
    
    # 제목 및 상단 지표
    st.title("산호아파트 재건축 사전동의 현황")
    
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("전체 세대", f"{total_cnt}", delta="세대")
    k2.metric("찬성 세대", f"{agree_cnt}", delta="세대")
    k3.metric("전체 동의율", f"{total_rate:.1f}%")
    
    with k4:
        st.markdown("""
        <div style="font-size:13px; color:#555; margin-top:5px; border-left:3px solid #ccc; padding-left:10px;">
        <b>범례 안내</b><br>
        🟩 찬성 &nbsp; 🟥 반대 <br> 
        🏠 소유주 &nbsp; 👤 세입자
        </div>
        """, unsafe_allow_html=True)
        
    st.divider()
    
    # 동별 반복 출력
    dongs = sorted(df['동'].unique())
    
    for i in range(0, len(dongs), cols_num):
        cols = st.columns(cols_num)
        chunk = dongs[i:i+cols_num]
        
        for idx, dong_name in enumerate(chunk):
            with cols[idx]:
                sub_df = df[df['동'] == dong_name]
                st.markdown(generate_dong_html(sub_df, dong_name), unsafe_allow_html=True)