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
    
    /* ★ 핵심 1: 가로 스크롤 영역 */
    .table-wrapper {
        overflow-x: auto; 
        -webkit-overflow-scrolling: touch;
        width: 100%;
        padding-bottom: 10px; /* 스크롤바 터치하기 편하게 여백 */
    }
    
    /* ★ 핵심 2: 테이블 스타일 (CSS에서 width 강제 지정) */
    .apt-table {
        /* width: 100%;  <- 이거 삭제함 (화면에 맞추지 마!) */
        border-collapse: collapse;
        font-size: 12px;
        table-layout: fixed; /* 칸 너비 균등 분배 */
    }
    
    /* 셀 스타일 */
    .apt-cell {
        border: 1px solid #dee2e6;
        padding: 6px 2px; /* 여백을 좀 더 줌 */
        text-align: center;
        height: 45px; /* 높이도 시원하게 */
        vertical-align: middle;
        white-space: nowrap; 
        overflow: hidden;
    }
    
    .border-bold { border-right: 2px solid #555 !important; }
    
    /* 상태별 색상 */
    .status-agree { background-color: #d1e7dd; color: #0f5132; font-weight: bold; }
    .status-disagree { background-color: #f8d7da; color: #842029; font-weight: bold; }
    .status-unknown { background-color: white; color: #ccc; }
    
    .icon-style { font-size: 14px; margin-right: 2px; }
    .ho-text { font-size: 12px; font-family: sans-serif; font-weight: bold; } 
    
    /* 입구 행 */
    .entrance-row td {
        background-color: #f1f3f5;
        color: #495057;
        text-align: center;
        vertical-align: middle;
        font-size: 12px;
        font-weight: bold;
        height: 30px;
        border-top: 2px solid #555;
        border-right: 1px solid #dee2e6;
        border-left: 1px solid #dee2e6;
    }
    
    /* 모바일 안내 문구 */
    .mobile-hint {
        font-size: 12px;
        color: #e03131; /* 빨간색으로 눈에 띄게 */
        font-weight: bold;
        text-align: right;
        padding: 5px 10px;
        background-color: #fff5f5;
        border-bottom: 1px solid #ffe3e3;
        display: none;
    }
    
    @media only screen and (max-width: 600px) {
        .mobile-hint { display: block; }
        /* 모바일에서 글씨 작게 하던 코드 삭제! 이제 PC랑 똑같이 큼직하게 나옵니다. */
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
# 3. HTML 생성 함수 (여기가 중요!)
# ---------------------------------------------------------
def generate_dong_html(sub_df, dong_name):
    sub_df['info'] = list(zip(sub_df['동의여부'], sub_df['거주유형'], sub_df['호']))
    pivot = sub_df.pivot_table(index='층', columns='라인', values='info', aggfunc='first')
    pivot = pivot.sort_index(ascending=False) 
    
    total = len(sub_df)
    agree = len(sub_df[sub_df['동의여부'] == '찬성'])
    rate = (agree / total * 100) if total > 0 else 0
    
    # ★ 여기서 width: 800px를 직접 박아버립니다. (절대 무시 못함) ★
    html = f"""
    <div class="dong-card">
        <div class="dong-header">
            {dong_name}동 <span style="font-size:0.85em; opacity:0.9; font-weight:normal;">(총 {total}세대 | {rate:.0f}%)</span>
        </div>
        <div class="mobile-hint">👉 표를 좌우로 밀어서 보세요 👈</div>
        <div class="table-wrapper">
            <table class="apt-table" style="width: 800px !important;">
    """
    
    for floor, row in pivot.iterrows():
        html += "<tr>"
        for idx, line in enumerate(pivot.columns):
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
            
            # 모바일에서도 아이콘 옆에 배치 (공간 충분하므로)
            html += f'<td class="apt-cell {cls} {border_class}"><span class="icon-style">{icon}</span><span class="ho-text">{ho_full}</span></td>'
        html += "</tr>"

    html += '<tr class="entrance-row">'
    num_cols = len(pivot.columns)
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
# 4. 메인 화면
# ---------------------------------------------------------
st.sidebar.header("설정")
cols_num = st.sidebar.slider("한 줄에 동 배치 (모바일은 1 추천)", 1, 5, 2) 

if st.sidebar.button("🔄 데이터 새로고침"):
    st.cache_data.clear()
    st.rerun()

if df.empty:
    st.error("데이터 로딩 실패")
else:
    total_cnt = len(df)
    agree_cnt = len(df[df['동의여부']=='찬성'])
    total_rate = (agree_cnt / total_cnt * 100) if total_cnt > 0 else 0
    
    st.title("🏙️ 산호아파트 재건축 현황판")
    
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("전체", f"{total_cnt}", delta="세대")
    k2.metric("찬성", f"{agree_cnt}", delta="세대")
    k3.metric("율", f"{total_rate:.1f}%")
    
    with k4:
        st.markdown("""
        <div style="font-size:12px; color:#555; margin-top:5px;">
        🟩찬성 🟥반대 <br> 🏠실거주 👤임대
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