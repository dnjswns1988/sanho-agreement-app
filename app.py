# import streamlit as st
# import pandas as pd
# import gspread
# from oauth2client.service_account import ServiceAccountCredentials
#
# # ---------------------------------------------------------
# # 1. 페이지 설정 및 디자인
# # ---------------------------------------------------------
# st.set_page_config(layout="wide", page_title="산호아파트 동의 현황")
#
# st.markdown("""
# <style>
#     .block-container { padding-top: 1rem; padding-bottom: 5rem; }
#
#     .dong-card {
#         background-color: white;
#         border: 1px solid #e0e0e0;
#         border-radius: 8px;
#         padding: 0px;
#         margin-bottom: 20px;
#         box-shadow: 0 2px 4px rgba(0,0,0,0.05);
#         overflow: hidden;
#     }
#
#     .dong-header {
#         background-color: #333;
#         color: white;
#         padding: 8px 5px;
#         text-align: center;
#         font-weight: bold;
#         font-size: 15px;
#     }
#
#     /* 테이블 스타일 */
#     .apt-table {
#         width: 100%;
#         table-layout: fixed; /* 칸 너비 균등 분할 */
#         border-collapse: collapse;
#         font-size: 12px;
#     }
#
#     .apt-table td {
#         border: 1px solid #dee2e6;
#         padding: 4px 1px;
#         text-align: center;
#         height: 40px;
#         vertical-align: middle;
#         white-space: nowrap;
#         overflow: hidden;
#     }
#
#     /* ★ 입구 구분용 굵은 선 (검은색에 가깝게) */
#     .border-bold {
#         border-right: 3px solid #444 !important;
#     }
#
#     /* 상태별 색상 */
#     .status-agree { background-color: #d1e7dd; color: #0f5132; font-weight: bold; }
#     .status-disagree { background-color: #f8d7da; color: #842029; font-weight: bold; }
#     .status-unknown { background-color: white; color: #ccc; }
#
#     /* 아이콘 스타일 */
#     .icon-style { font-size: 12px; margin-right: 2px; }
#     .ho-text { font-size: 11px; font-family: sans-serif; }
#
# </style>
# """, unsafe_allow_html=True)
#
#
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
#
#         df['동'] = df['동'].astype(str)
#         df['호'] = df['호'].astype(str)
#         if '동의여부' not in df.columns: df['동의여부'] = '미조사'
#         if '거주유형' not in df.columns: df['거주유형'] = ''
#
#         def get_floor_line(h):
#             try:
#                 # 3자리 이상 (101, 1105 등)
#                 if len(h) >= 3:
#                     return int(h[:-2]), int(h[-2:])
#                 return 0, 0
#             except:
#                 return 0, 0
#
#         df['층'], df['라인'] = zip(*df['호'].apply(get_floor_line))
#         return df
#     except Exception as e:
#         return pd.DataFrame()
#
#
# df = load_data()
#
#
# # ---------------------------------------------------------
# # 3. HTML 생성 함수 (입구 구분 로직 수정)
# # ---------------------------------------------------------
# def generate_dong_html(sub_df, dong_name):
#     # 피벗 테이블 생성
#     sub_df['info'] = list(zip(sub_df['동의여부'], sub_df['거주유형'], sub_df['호']))
#     pivot = sub_df.pivot_table(index='층', columns='라인', values='info', aggfunc='first')
#     pivot = pivot.sort_index(ascending=False)
#
#     total = len(sub_df)
#     agree = len(sub_df[sub_df['동의여부'] == '찬성'])
#     rate = (agree / total * 100) if total > 0 else 0
#
#     html = f"""
#     <div class="dong-card">
#         <div class="dong-header">
#             {dong_name}동 <span style="font-size:0.85em; opacity:0.9; font-weight:normal;">(총 {total}세대 | {rate:.0f}%)</span>
#         </div>
#         <table class="apt-table">
#     """
#
#     for floor, row in pivot.iterrows():
#         html += "<tr>"
#         # ★ 핵심 로직 변경: enumerate를 써서 '순서'대로 2칸씩 끊기
#         # columns에는 [1, 2, 3, 5, 6, 7...] 이렇게 4가 빠진 상태로 들어옵니다.
#         # 인덱스(idx)가 0, 1, 2, 3, 4, 5... 로 붙으므로
#         # idx 1(2번째), idx 3(4번째), idx 5(6번째) 칸 뒤에 선을 그으면 됩니다.
#         for idx, line in enumerate(pivot.columns):
#             # 2번째, 4번째, 6번째... 칸마다 우측 굵은 선 적용
#             border_class = "border-bold" if (idx + 1) % 2 == 0 else ""
#
#             cell_data = row[line]
#             if not isinstance(cell_data, tuple):
#                 html += f'<td class="{border_class}"></td>'
#                 continue
#
#             status, live_type, ho_full = cell_data
#
#             cls = "status-unknown"
#             if status == '찬성':
#                 cls = "status-agree"
#             elif status == '반대':
#                 cls = "status-disagree"
#
#             icon = ""
#             if live_type == '실거주':
#                 icon = "🏠"
#             elif live_type == '임대중':
#                 icon = "👤"
#
#             html += f'<td class="{cls} {border_class}"><span class="icon-style">{icon}</span><span class="ho-text">{ho_full}</span></td>'
#         html += "</tr>"
#
#     html += "</table></div>"
#     return html
#
#
# # ---------------------------------------------------------
# # 4. 메인 화면
# # ---------------------------------------------------------
# st.sidebar.header("설정")
# cols_num = st.sidebar.slider("한 줄에 몇 개 동씩 볼까요?", 1, 5, 3)
#
# if st.sidebar.button("🔄 데이터 새로고침"):
#     st.cache_data.clear()
#     st.rerun()
#
# if df.empty:
#     st.error("데이터 로딩 실패")
# else:
#     total_cnt = len(df)
#     agree_cnt = len(df[df['동의여부'] == '찬성'])
#     total_rate = (agree_cnt / total_cnt * 100) if total_cnt > 0 else 0
#
#     st.title("🏙️ 산호아파트 재건축 현황판")
#
#     k1, k2, k3, k4 = st.columns(4)
#     k1.metric("전체 세대", f"{total_cnt}", delta="세대")
#     k2.metric("동의 완료", f"{agree_cnt}", delta="세대")
#     k3.metric("전체 동의율", f"{total_rate:.1f}%")
#
#     with k4:
#         st.caption("범례")
#         st.markdown("""
#         <span style='background:#d1e7dd; padding:2px 5px; font-size:11px; font-weight:bold; color:#0f5132;'>찬성</span>
#         <span style='background:#f8d7da; padding:2px 5px; font-size:11px; font-weight:bold; color:#842029;'>반대</span>
#         <span style='font-size:11px;'> (굵은 선: 입구 구분)</span>
#         """, unsafe_allow_html=True)
#
#     st.divider()
#
#     dongs = sorted(df['동'].unique())
#
#     for i in range(0, len(dongs), cols_num):
#         cols = st.columns(cols_num)
#         chunk = dongs[i:i + cols_num]
#
#         for idx, dong_name in enumerate(chunk):
#             with cols[idx]:
#                 sub_df = df[df['동'] == dong_name]
#                 st.markdown(generate_dong_html(sub_df, dong_name), unsafe_allow_html=True)


import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# ---------------------------------------------------------
# 1. 페이지 설정 및 디자인
# ---------------------------------------------------------
st.set_page_config(layout="wide", page_title="산호아파트 동의 현황")

st.markdown("""
<style>
    /* 상단 여백 확보 (제목 잘림 방지) */
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
        background-color: #333;
        color: white;
        padding: 8px 5px;
        text-align: center;
        font-weight: bold;
        font-size: 15px;
    }

    /* 테이블 스타일 */
    .apt-table {
        width: 100%;
        table-layout: fixed;
        border-collapse: collapse;
        font-size: 12px;
    }

    /* 아파트 호수 셀 */
    .apt-cell {
        border: 1px solid #dee2e6;
        padding: 4px 1px;
        text-align: center;
        height: 40px;
        vertical-align: middle;
        white-space: nowrap;
        overflow: hidden;
    }

    /* 입구 구분용 세로 굵은 선 (검은색에 가깝게) */
    .border-bold { border-right: 2px solid #555 !important; }

    /* 상태별 색상 */
    .status-agree { background-color: #d1e7dd; color: #0f5132; font-weight: bold; }
    .status-disagree { background-color: #f8d7da; color: #842029; font-weight: bold; }
    .status-unknown { background-color: white; color: #ccc; }

    .icon-style { font-size: 12px; margin-right: 2px; }
    .ho-text { font-size: 11px; font-family: sans-serif; } 

    /* ★ 수정됨: 깔끔한 입구 표시 바 (회색 배경) */
    .entrance-row td {
        background-color: #f1f3f5; /* 아주 연한 회색 */
        color: #495057;            /* 진한 회색 글씨 */
        text-align: center;
        vertical-align: middle;
        font-size: 11px;
        font-weight: bold;
        height: 25px;              /* 높이를 얇게 */
        border-top: 2px solid #555; /* 위쪽에 굵은 선을 주어 건물과 구분 */
        border-right: 1px solid #dee2e6;
        border-left: 1px solid #dee2e6;
    }

    /* 입구 행 사이의 간격 띄우기 (선택사항) */
    .spacer-cell { border: none !important; background: white !important; }

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
            except:
                return 0, 0

        df['층'], df['라인'] = zip(*df['호'].apply(get_floor_line))
        return df
    except Exception as e:
        return pd.DataFrame()


df = load_data()


# ---------------------------------------------------------
# 3. HTML 생성 함수 (디자인 변경)
# ---------------------------------------------------------
def generate_dong_html(sub_df, dong_name):
    sub_df['info'] = list(zip(sub_df['동의여부'], sub_df['거주유형'], sub_df['호']))
    pivot = sub_df.pivot_table(index='층', columns='라인', values='info', aggfunc='first')
    pivot = pivot.sort_index(ascending=False)

    total = len(sub_df)
    agree = len(sub_df[sub_df['동의여부'] == '찬성'])
    rate = (agree / total * 100) if total > 0 else 0

    html = f"""
    <div class="dong-card">
        <div class="dong-header">
            {dong_name}동 <span style="font-size:0.85em; opacity:0.9; font-weight:normal;">(총 {total}세대 | {rate:.0f}%)</span>
        </div>
        <table class="apt-table">
    """

    # 층별 호수 그리기
    for floor, row in pivot.iterrows():
        html += "<tr>"
        for idx, line in enumerate(pivot.columns):
            # 2칸마다 세로 줄 긋기
            border_class = "border-bold" if (idx + 1) % 2 == 0 else ""
            cell_data = row[line]

            if not isinstance(cell_data, tuple):
                html += f'<td class="apt-cell {border_class}"></td>'
                continue

            status, live_type, ho_full = cell_data
            cls = "status-unknown"
            if status == '찬성':
                cls = "status-agree"
            elif status == '반대':
                cls = "status-disagree"
            icon = "🏠" if live_type == '실거주' else ("👤" if live_type == '임대중' else "")

            html += f'<td class="apt-cell {cls} {border_class}"><span class="icon-style">{icon}</span><span class="ho-text">{ho_full}</span></td>'
        html += "</tr>"

    # ★ 수정됨: 깔끔한 하단 입구 바 그리기
    html += '<tr class="entrance-row">'
    num_cols = len(pivot.columns)
    i = 0
    while i < num_cols:
        # 2개씩 묶어서 '입구' 표시
        if i + 1 < num_cols:
            # 여기서는 세로선 border-bold를 쓰지 않고 자체 CSS border를 따름
            html += """<td colspan="2">입구</td>"""
            i += 2
        else:
            # 홀수 칸이 남을 경우
            html += "<td></td>"
            i += 1
    html += "</tr>"

    html += "</table></div>"
    return html


# ---------------------------------------------------------
# 4. 메인 화면
# ---------------------------------------------------------
st.sidebar.header("설정")
cols_num = st.sidebar.slider("한 줄에 몇 개 동씩 볼까요?", 1, 5, 3)

if st.sidebar.button("🔄 데이터 새로고침"):
    st.cache_data.clear()
    st.rerun()

if df.empty:
    st.error("데이터 로딩 실패")
else:
    total_cnt = len(df)
    agree_cnt = len(df[df['동의여부'] == '찬성'])
    total_rate = (agree_cnt / total_cnt * 100) if total_cnt > 0 else 0

    st.title("🏙️ 산호아파트 재건축 현황판")

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("전체 세대", f"{total_cnt}", delta="세대")
    k2.metric("동의 완료", f"{agree_cnt}", delta="세대")
    k3.metric("전체 동의율", f"{total_rate:.1f}%")

    with k4:
        st.caption("범례")
        st.markdown("""
        <span style='background:#d1e7dd; padding:2px 5px; font-size:11px; font-weight:bold; color:#0f5132;'>찬성</span>
        <span style='background:#f8d7da; padding:2px 5px; font-size:11px; font-weight:bold; color:#842029;'>반대</span><br>
        <span style='font-size:11px; color:#555;'>하단 회색 바: 공동 현관(입구)</span>
        """, unsafe_allow_html=True)

    st.divider()

    dongs = sorted(df['동'].unique())

    for i in range(0, len(dongs), cols_num):
        cols = st.columns(cols_num)
        chunk = dongs[i:i + cols_num]

        for idx, dong_name in enumerate(chunk):
            with cols[idx]:
                sub_df = df[df['동'] == dong_name]
                st.markdown(generate_dong_html(sub_df, dong_name), unsafe_allow_html=True)