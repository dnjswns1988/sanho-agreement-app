# ##공용 버전
# import streamlit as st
# import pandas as pd
# import gspread
# from oauth2client.service_account import ServiceAccountCredentials

# # ---------------------------------------------------------
# # 0. [보안] 비밀번호 설정 함수
# # ---------------------------------------------------------
# def check_password():
#     """로그인 기능을 구현하여 아무나 볼 수 없게 합니다."""
#     if "password_correct" not in st.session_state:
#         st.session_state.password_correct = False

#     if st.session_state.password_correct:
#         return True

#     st.markdown("### 🔒 관계자 전용 페이지")
#     password = st.text_input("비밀번호를 입력하세요", type="password")
    
#     # 비밀번호 설정 (원하는 비밀번호로 변경하세요 예: "sanho1234")
#     if st.button("로그인"):
#         if password == "sanho2325":  # 실제 운영시엔 복잡한 비밀번호 권장
#             st.session_state.password_correct = True
#             st.rerun()
#         else:
#             st.error("비밀번호가 틀렸습니다.")
#     return False

# # ---------------------------------------------------------
# # 1. 페이지 설정 및 디자인 (CSS)
# # ---------------------------------------------------------
# st.set_page_config(layout="wide", page_title="산호아파트 동의서 접수 현황")

# # ★ 비밀번호 체크 (통과 못하면 여기서 코드 중단)
# if not check_password():
#     st.stop()

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
#         background-color: #495057; /* 중립적인 진한 회색 */
#         color: white;
#         padding: 15px 5px;       
#         text-align: center;
#         font-weight: bold;
#     }
    
#     /* 가로 스크롤 영역 */
#     .table-wrapper {
#         overflow-x: auto; 
#         -webkit-overflow-scrolling: touch;
#         width: 100%;
#         padding-bottom: 0px;
#         margin-bottom: 0px;
#     }
    
#     /* 스크롤바 트랙 투명 설정 */
#     .table-wrapper::-webkit-scrollbar { height: 6px; background: transparent; }
#     .table-wrapper::-webkit-scrollbar-track { background: transparent; }
#     .table-wrapper::-webkit-scrollbar-thumb { background-color: #ccc; border-radius: 3px; }
    
#     /* 테이블 공통 스타일 */
#     .apt-table {
#         width: 100%;
#         min-width: 600px;
#         table-layout: fixed;
#         border-collapse: collapse;
#         border-spacing: 0;
#         font-size: 12px;
#         margin-bottom: 0px;
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

#     /* 층수 표시 셀 */
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
    
#     /* ★ [법적 안전 조치] 상태별 색상 변경 (찬반 구분 제거) */
#     /* 접수완료 (찬성/반대 모두 포함) -> 차분한 파란색 */
#     .status-done { background-color: #e7f5ff; color: #1971c2; font-weight: bold; }   
    
#     /* 미접수 (방문 필요 대상) -> 흰색 또는 연한 노랑 */
#     .status-todo { background-color: #ffffff; color: #adb5bd; }  
    
#     /* 아이콘 스타일 */
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
#         border-bottom: none !important; 
#     }
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
#         # Streamlit Cloud 배포 시 secrets 사용 권장
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
    
#     # ★ [통계] 동별 통계는 '접수율'로만 표시 (찬/반 상세 수치는 동별 카드에서 제거)
#     total = len(sub_df)
#     # 찬성+반대 모두 '접수'로 처리
#     submitted_count = len(sub_df[sub_df['동의여부'].isin(['찬성', '반대'])])
#     submitted_rate = (submitted_count / total * 100) if total > 0 else 0
    
#     # 복도식 확인
#     target_dongs = ['102', '104', '106']
#     is_corridor = any(target in str(dong_name) for target in target_dongs)
    
#     # 동적 너비 계산
#     num_cols = len(pivot.columns)
#     calculated_width = max(600, num_cols * 80 + 50) 
    
#     html = f"""
#     <div class="dong-card">
#         <div class="dong-header">
#             <div style="font-size:20px; margin-bottom:5px;">{dong_name}동</div>
#             <div style="font-size:14px; font-weight:normal;">
#                 총 {total} 세대 중 
#                 <span style="color:#74c0fc; font-weight:bold;">{submitted_count}세대 접수</span>
#                 (접수율: {submitted_rate:.1f}%)
#             </div>
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
            
#             # ★ [핵심 수정] 찬성/반대 정보를 제거하고 '접수됨/미접수'로만 표현
#             # 찬성이든 반대든 서류를 냈으면 'status-done'
#             if status in ['찬성', '반대']:
#                 cls = "status-done"  # 파란색 (의사표시 완료)
#             else:
#                 cls = "status-todo"  # 흰색 (미접수, 방문 필요)
            
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
#     # 전체 통계 (관리 차원에서 전체 찬/반 비율은 상단에 표시하되, 개별 동에서는 숨김)
#     total_cnt = len(df)
#     agree_cnt = len(df[df['동의여부']=='찬성'])
#     disagree_cnt = len(df[df['동의여부']=='반대'])
#     waiting_cnt = len(df[df['동의여부']=='응답대기'])
    
#     # 총 접수(의사표현)된 수
#     submitted_total = agree_cnt + disagree_cnt
#     submit_rate = (submitted_total / total_cnt * 100) if total_cnt > 0 else 0
#     agree_rate = (agree_cnt / total_cnt * 100) if total_cnt > 0 else 0
    
#     st.title("산호아파트 동의서 접수 현황판")
    
#     # 상단 지표 (전체적인 경향만 파악)
#     k1, k2, k3, k4 = st.columns(4)
    
#     k1.metric("전체 세대", f"{total_cnt}세대")
#     k2.metric("접수 완료", f"{submitted_total}세대")
#     k3.metric("미접수 (대상)", f"{waiting_cnt}세대")
#     # 찬성률은 전체 통계로만 작게 표시 (법적 안전장치)
#     k4.metric("현재 동의율", f"{agree_rate:.1f}%", help="전체 세대 대비 찬성표 비율입니다.")
    
#     st.markdown("""
#     <div style="font-size:14px; color:#555; margin-top:10px; padding:10px; background-color:#f8f9fa; border-radius:5px;">
#         <strong>[범례 가이드]</strong><br>
#         🟦 <b>파란색 (접수완료):</b> 동의서를 제출했거나 의사를 확실히 밝힌 세대 (방문 불필요)<br> 
#         ⬜ <b>흰색 (미접수):</b> 아직 의사가 확인되지 않은 세대 (우선 방문 대상)
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
    
#     /* 1. 파란색 (접수완료): 찬성/반대 */
#     .status-done { background-color: #e7f5ff; color: #1971c2; font-weight: bold; }   
    
#     /* 2. 노란색 (답변대기): 응답대기 상태 */
#     .status-waiting { background-color: #fff3cd; color: #856404; font-weight: bold; }  
    
#     /* 3. 흰색 (미접수): 데이터 없음 */
#     .status-todo { background-color: #ffffff; color: #adb5bd; }  
    
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
#     submitted_count = len(sub_df[sub_df['동의여부'].isin(['찬성', '반대'])])
#     submitted_rate = (submitted_count / total * 100) if total > 0 else 0
    
#     # ★ [추가] 임대중 비율 계산
#     rented_count = len(sub_df[sub_df['거주유형'] == '임대중'])
#     rented_rate = (rented_count / total * 100) if total > 0 else 0
    
#     target_dongs = ['102', '104', '106']
#     is_corridor = any(target in str(dong_name) for target in target_dongs)
    
#     num_cols = len(pivot.columns)
#     calculated_width = max(600, num_cols * 80 + 50) 
    
#     # ★ [수정] 헤더에 임대 비율 표시 (연한 회색 작은 글씨)
#     html = f"""
#     <div class="dong-card">
#         <div class="dong-header">
#             <div style="font-size:20px; margin-bottom:5px;">{dong_name}동</div>
#             <div style="font-size:14px; font-weight:normal;">
#                 총 {total} 세대 중 
#                 <span style="color:#74c0fc; font-weight:bold;">{submitted_count}세대 접수</span>
#                 (접수율: {submitted_rate:.1f}%)<br>
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
            
#             if status in ['찬성', '반대']:
#                 cls = "status-done"      
#             elif status == '응답대기':
#                 cls = "status-waiting"   
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
#     waiting_cnt = len(df[df['동의여부']=='응답대기'])
    
#     submitted_total = agree_cnt + disagree_cnt
#     agree_rate = (agree_cnt / total_cnt * 100) if total_cnt > 0 else 0
    
#     # 미접수(아무것도 없는 상태) 계산
#     todo_cnt = total_cnt - submitted_total - waiting_cnt
    
#     st.title("산호 사전동의 현황")
    
#     # 상단 지표
#     k1, k2, k3, k4 = st.columns(4)
    
#     k1.metric("전체 세대", f"{total_cnt}세대")
#     k2.metric("접수 완료", f"{submitted_total}세대")
    
#     k3.metric("답변 대기중", f"{waiting_cnt}세대")
    
#     k4.metric("현재 동의율", f"{agree_rate:.1f}%")
    
#     st.markdown("""
#     <div style="font-size:14px; color:#555; margin-top:10px; padding:10px; background-color:#f8f9fa; border-radius:5px;">
#         <strong>[범례 가이드]</strong><br>
#         🟦 <b>파란색 (접수완료):</b> 찬/반 의사를 밝힌 세대<br> 
#         🟨 <b>노란색 (답변대기중):</b> 소유자에 연락했으나 미회신 세대<br>
#         ⬜ <b>흰색 (미접수):</b> 미연락 세대
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
    
    .apt-cell {
        border: 1px solid #dee2e6;
        padding: 6px 2px;
        text-align: center;
        height: 45px;
        vertical-align: middle;
        white-space: nowrap; 
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
        position: sticky;
        left: 0;
        z-index: 10;
    }
    
    .border-bold { border-right: 2px solid #555 !important; }
    
    /* ★ [상태별 색상 정의] ★ */
    .status-done { background-color: #e7f5ff; color: #1971c2; font-weight: bold; }   /* 파란색 (찬성) */
    .status-ban { background-color: #ffe3e3; color: #c92a2a; font-weight: bold; }    /* 빨간색 (반대/연락금지) */
    .status-waiting { background-color: #fff3cd; color: #856404; font-weight: bold; } /* 노란색 (응답대기) */
    .status-todo { background-color: #ffffff; color: #adb5bd; }                       /* 흰색 (미접수) */
    
    .icon-style { font-size: 14px; margin-right: 2px; }
    .ho-text { font-size: 12px; font-family: sans-serif; font-weight: bold; } 
    
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
    
    # 1. 찬성 수 (동의율 계산용 분자)
    agree_count = len(sub_df[sub_df['동의여부'] == '찬성'])
    
    # 2. ★ 접수 수 (찬성 + 반대) -> 화면 표시용
    submitted_count = len(sub_df[sub_df['동의여부'].isin(['찬성', '반대'])])
    
    # 3. 동의율 (찬성 / 전체) -> 화면 표시용
    agree_rate = (agree_count / total * 100) if total > 0 else 0
    
    # 4. 임대 비율
    rented_count = len(sub_df[sub_df['거주유형'] == '임대중'])
    rented_rate = (rented_count / total * 100) if total > 0 else 0
    
    target_dongs = ['102', '104', '106']
    is_corridor = any(target in str(dong_name) for target in target_dongs)
    
    num_cols = len(pivot.columns)
    calculated_width = max(600, num_cols * 80 + 50) 
    
    # ★ [수정됨] "XX 세대 접수 (동의율: XX%)" 로직 적용
    # 접수: submitted_count (찬+반)
    # 동의율: agree_rate (찬/전체)
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
                cls = "status-done"      # 파란색
            elif status == '반대':
                cls = "status-ban"       # 빨간색 (연락금지)
            elif status == '응답대기':
                cls = "status-waiting"   # 노란색
            else:
                cls = "status-todo"      # 흰색
            
            icon = "🏠" if live_type == '실거주' else ("👤" if live_type == '임대중' else "")
            
            html += f'<td class="apt-cell {cls} {border_class}"><span class="icon-style">{icon}</span><span class="ho-text">{ho_full}</span></td>'
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
    waiting_cnt = len(df[df['동의여부']=='응답대기'])
    
    # 동의율 (전체 중 찬성 비율)
    agree_rate = (agree_cnt / total_cnt * 100) if total_cnt > 0 else 0
    
    st.title("산호 사전동의 현황")
    
    k1, k2, k3, k4, k5 = st.columns(5)
    
    k1.metric("전체 세대", f"{total_cnt}세대")
    k2.metric("동의 세대", f"{agree_cnt}세대")
    k3.metric("🚫 연락|방문 금지", f"{disagree_cnt}세대")
    k4.metric("답변 대기중", f"{waiting_cnt}세대")
    k5.metric("동의율", f"{agree_rate:.1f}%")
    
    st.markdown("""
    <div style="font-size:14px; color:#555; margin-top:10px; padding:10px; background-color:#f8f9fa; border-radius:5px;">
        <strong>[범례 가이드]</strong><br>
        🟦 <b>파란색 (동의):</b> 동의 의사 밝힌 세대<br> 
        🟥 <b>빨간색 (연락금지):</b> 연락 및 방문 금지 세대<br>
        🟨 <b>노란색 (답변대기중):</b> 소유자에 연락했으나 미회신 세대<br>
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