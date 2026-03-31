import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import random
from datetime import datetime, timedelta
import json
import time
import pandas as pd

# ==========================================
# 1. UI CONFIGURATION (TRONG SÁNG & ĐỐI XỨNG TUYỆT ĐỐI)
# ==========================================
st.set_page_config(page_title="TOCFL Test System", page_icon="🏫", layout="centered")

st.markdown("""
    <style>
    /* Màu nền chung thân thiện */
    .stApp { background-color: #F0F9FF !important; }
    
    /* Ép font chữ và màu xám đen, căn giữa. KHÔNG ĐỤNG VÀO THẺ SPAN ĐỂ BẢO VỆ ICON */
    p, h1, h2, h3, h4, h5, h6, label, li {
        font-family: 'Nunito', 'Segoe UI', 'Microsoft JhengHei', sans-serif !important;
        color: #0F172A !important;
        text-align: center !important; 
    }

    /* Căn giữa Label của các ô nhập liệu */
    [data-testid="stTextInput"] label, [data-testid="stSelectbox"] label, [data-testid="stNumberInput"] label {
        display: flex !important;
        justify-content: center !important;
        width: 100% !important;
    }

    /* Ô NHẬP LIỆU: Nền trắng, viền xanh nhạt, không có màu đen */
    div[data-baseweb="input"] > div, div[data-baseweb="select"] > div {
        background-color: #FFFFFF !important;
        border: 2px solid #7DD3FC !important;
        border-radius: 15px !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05) !important;
    }
    input, input[type="text"], input[type="password"], input[type="number"] {
        color: #0F172A !important;
        -webkit-text-fill-color: #0F172A !important; 
        font-size: 1.15rem !important;
        font-weight: bold !important;
        padding: 10px !important;
        background-color: transparent !important;
        text-align: center !important; /* Số/chữ gõ vào nằm ở giữa */
    }
    ::placeholder {
        color: #94A3B8 !important;
        -webkit-text-fill-color: #94A3B8 !important;
        opacity: 0.7 !important;
        text-align: center !important;
        font-weight: normal !important;
    }

    /* ĐỔI MÀU CÁC CON SỐ THỐNG KÊ THÀNH MÀU ĐỎ */
    [data-testid="stMetricValue"] {
        color: #DC2626 !important; /* Đỏ rực rỡ */
        font-weight: 900 !important;
    }
    [data-testid="stMetricLabel"] p {
        color: #0F172A !important;
        font-weight: 600 !important;
    }

    /* SỬA LỖI KHUNG XEM GIẢI THÍCH & NÚT DOWNLOAD */
    [data-testid="stExpander"] details summary {
        background-color: #E0F2FE !important; 
        border-radius: 12px !important;
        border: 2px solid #BAE6FD !important;
        padding: 10px !important;
    }
    [data-testid="stExpander"] details summary p { color: #0284C7 !important; font-weight: bold !important; }
    [data-testid="stExpander"] details { background-color: transparent !important; border: none !important; }
    
    [data-testid="stDownloadButton"] button {
        background-color: #10B981 !important; /* Xanh lá */
        border: none !important;
        border-radius: 12px !important;
        height: 3.5rem !important;
        width: 100% !important;
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
    }
    [data-testid="stDownloadButton"] button p { color: #FFFFFF !important; margin: 0 !important; }
    [data-testid="stDownloadButton"] button:hover { background-color: #059669 !important; transform: translateY(-2px); }

    /* ========================================== */
    /* SỬA LỖI DROPDOWN MENU & MULTISELECT BỊ ĐEN */
    /* ========================================== */
    div[data-baseweb="popover"],
    div[data-baseweb="popover"] > div,
    ul[data-baseweb="menu"],
    ul[role="listbox"] {
        background-color: #FFFFFF !important;
    }
    li[role="option"] {
        background-color: #FFFFFF !important;
        color: #000000 !important;
        font-weight: 600 !important;
    }
    li[role="option"]:hover, 
    li[role="option"][aria-selected="true"] {
        background-color: #E0F2FE !important;
        color: #0284C7 !important;
    }
    span[data-baseweb="tag"] {
        background-color: #E0F2FE !important;
        color: #0F172A !important;
        border: 1px solid #7DD3FC !important;
    }
    span[data-baseweb="tag"] span[role="button"] {
        color: #DC2626 !important; 
    }

    /* THẺ CÂU HỎI (CĂN GIỮA, VIỀN TRÊN) */
    .question-card {
        background-color: #FFFFFF;
        padding: 30px;
        border-radius: 20px;
        border: 2px solid #E0F2FE;
        border-top: 8px solid #38BDF8; 
        box-shadow: 0 8px 16px -4px rgba(56, 189, 248, 0.15);
        margin-bottom: 25px;
        color: #000000;
        font-size: 1.4rem;
        font-weight: 700;
        line-height: 1.5;
        text-align: center;
    }

    /* ĐÁP ÁN: THÔNG MINH (NGẮN LÀ 2x2, DÀI LÀ 1 CỘT) */
    div[role="radiogroup"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: wrap !important;
        justify-content: center !important;
        gap: 15px !important;
    }
    .stRadio > div > label {
        flex: 1 1 40% !important;
        min-width: 250px !important; 
        background-color: #FFFFFF !important;
        color: #000000 !important;
        padding: 15px 20px !important;
        border-radius: 12px !important;
        border: 2px solid #E2E8F0 !important;
        cursor: pointer;
        font-weight: 600 !important;
        font-size: 1.15rem !important;
        transition: all 0.2s;
        text-align: center !important;
    }
    .stRadio > div > label:hover {
        background-color: #E0F2FE !important;
        border-color: #38BDF8 !important;
    }

    /* BUTTONS CHUNG: ÉP CĂN GIỮA CHỮ TUYỆT ĐỐI */
    .stButton > button {
        background-color: #38BDF8 !important;
        border-radius: 12px !important;
        height: 3.5rem !important;
        font-size: 1.1rem !important;
        font-weight: 800 !important;
        border: none !important;
        width: 100% !important;
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
    }
    .stButton > button p, .stButton > button span {
        color: #FFFFFF !important;
        margin: 0 !important;
        padding: 0 !important;
        text-align: center !important;
    }
    .stButton > button:hover { opacity: 0.9; transform: translateY(-2px); }
    
    .submit-btn > button { background-color: #34D399 !important; }
    .submit-btn > button:hover { background-color: #10B981 !important; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. GOOGLE SHEETS & CACHING
# ==========================================
@st.cache_resource
def connect_sheets():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    
    try:
        creds = ServiceAccountCredentials.from_json_keyfile_name("key.json", scope)
    except Exception:
        creds_dict = dict(st.secrets["gcp_service_account"])
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        
    return gspread.authorize(creds).open("He_Thong_Thi_TOCFL")

try: 
    sheet = connect_sheets()
except Exception as e:
    st.error(f"System connection failed. Chi tiết lỗi: {e}")
    st.stop()

@st.cache_data(ttl=60)
def fetch_sheet_data(ws_name):
    try: return sheet.worksheet(ws_name).get_all_values()
    except: return []

def fetch_dynamic_data(ws_name):
    try: return sheet.worksheet(ws_name).get_all_values()
    except: return []

def get_exam_config():
    rows = fetch_sheet_data("設定")
    if len(rows) > 1:
        conf = rows[1]
        while len(conf) < 6: conf.append("")
        if not str(conf[5]).strip().isdigit(): conf[5] = 20
        return conf
    return ["開", 30, "1", "123456", "", 20] 

if 'page' not in st.session_state: st.session_state.page = "Login"
if 'answers' not in st.session_state: st.session_state.answers = {}
if 'current_q' not in st.session_state: st.session_state.current_q = 0

def auto_sync_progress():
    try:
        if 'student_info' not in st.session_state or 'exam_data' not in st.session_state: return
        st_id = str(st.session_state.student_info['ID']).strip()
        
        try:
            ws = sheet.worksheet("正在考試")
        except:
            ws = sheet.add_worksheet(title="正在考試", rows="100", cols="5")
            ws.append_row(["學號", "Data"])
            
        data = ws.get_all_values()
        
        found_row = -1
        for i, r in enumerate(data):
            if len(r) > 0 and str(r[0]).strip() == st_id:
                found_row = i + 1; break
                
        state_data = {"exam_data": st.session_state.exam_data, "answers": st.session_state.answers}
        state_json = json.dumps(state_data)
        
        if found_row != -1: 
            ws.update_cell(found_row, 2, state_json)
        else: 
            ws.append_row([st_id, state_json])
    except Exception as e: 
        pass

# ==========================================
# 3. ADMIN DASHBOARD
# ==========================================
def admin_page():
    st.title("📊 系統管理與數據中心 (Admin Dashboard)")
    conf = get_exam_config()
    
    tab1, tab2, tab3 = st.tabs(["⚙️ 考場設定 (Settings)", "📡 即時監考 (Live Monitor)", "📈 成績統計 (Statistics)"])
    
    with tab1:
        st.markdown("<h3 style='margin-top:20px;'>考場參數設定 (Exam Settings)</h3>", unsafe_allow_html=True)
        sv_rows = fetch_sheet_data("學生名單")[1:]
        all_classes = sorted(list(set([r[0] for r in sv_rows if len(r)>0 and r[0].strip()!=""])))
        current_allowed = [c.strip() for c in (conf[4].split(",") if len(conf)>4 and conf[4] else []) if c.strip() in all_classes]
        
        col1, col2, col3 = st.columns(3)
        with col1: status = st.selectbox("狀態 (Status)", ["開", "關"], index=0 if conf[0]=="開" else 1)
        with col2: time_limit = st.number_input("考試時間 - 分鐘 (Time - Min)", value=int(conf[1]))
        with col3: week = st.text_input("測驗週數 (Week)", value=str(conf[2]))
        
        col4, col5 = st.columns([1, 2])
        with col4: num_q = st.number_input("考試題數 (Number of Questions)", min_value=1, max_value=200, value=int(conf[5]))
        with col5: allowed_classes = st.multiselect("允許考試的班級 (Allowed Classes):", all_classes, default=current_allowed)
        
        st.info(f"💡 系統將自動抽取 **{num_q}** 題，每題配分為 **{round(100/num_q, 2)}** 分。")
        
        if st.button("💾 儲存設定 (Save)", use_container_width=True):
            allowed_str = ",".join(allowed_classes)
            try:
                sheet.worksheet("設定").update('A2:F2', [[status, time_limit, week, conf[3], allowed_str, num_q]])
            except:
                ws_set = sheet.worksheet("設定")
                ws_set.update_cell(2, 1, status)
                ws_set.update_cell(2, 2, time_limit)
                ws_set.update_cell(2, 3, week)
                ws_set.update_cell(2, 4, conf[3])
                ws_set.update_cell(2, 5, allowed_str)
                ws_set.update_cell(2, 6, num_q)
                
            st.cache_data.clear()
            st.success("✅ 設定已更新！(Settings Updated)")
            time.sleep(1); st.rerun()

    with tab2:
        st.markdown("<h3 style='margin-top:20px;'>正在考試學生 (Students in Progress)</h3>", unsafe_allow_html=True)
        active_data = fetch_dynamic_data("正在考試")
        
        monitor_list = []
        for r in active_data:
            if len(r) > 0 and str(r[0]).strip() != "" and "學號" not in str(r[0]) and "ID" not in str(r[0]):
                s_id = str(r[0]).strip()
                s_info = next((sv for sv in sv_rows if str(sv[1]).strip() == s_id), ["", s_id, "", "Unknown"])
                
                answered = 0
                total_for_student = int(conf[5])
                
                if len(r) > 1 and str(r[1]).strip() != "":
                    try:
                        state_dict = json.loads(r[1])
                        ans_dict = state_dict.get("answers", {})
                        answered = len([v for v in ans_dict.values() if str(v).strip() not in ["None", ""]])
                        total_for_student = len(state_dict.get("exam_data", []))
                    except: pass
                    
                monitor_list.append({
                    "班級 (Class)": s_info[0], "學號 (ID)": s_id,
                    "姓名 (Name)": s_info[3], "進度 (Progress)": f"{answered} / {total_for_student} 題"
                })
        
        if len(monitor_list) > 0:
            # Tạo DataFrame và đẩy STT (index) bắt đầu từ 1
            df_monitor = pd.DataFrame(monitor_list)
            df_monitor.index = df_monitor.index + 1
            st.dataframe(df_monitor, use_container_width=True)
        else:
            st.info("目前沒有學生 (No students currently taking the exam).")
            
        if st.button("🔄 刷新 (Refresh)", use_container_width=True): 
            st.rerun()

    with tab3:
        st.markdown(f"<h3 style='margin-top:20px;'>第 {conf[2]} 週成績統計 (Week {conf[2]} Statistics)</h3>", unsafe_allow_html=True)
        kq_rows = fetch_dynamic_data("考試結果")
        if len(kq_rows) > 1:
            df = pd.DataFrame(kq_rows[1:], columns=kq_rows[0])
            df_week = df[df.iloc[:, 1] == f"第 {conf[2]} 週"] 
            
            if not df_week.empty:
                # Tự động dò tìm cột điểm
                score_col_idx = 7 # Mặc định là cột thứ 8
                for idx, col_name in enumerate(df.columns):
                    if '分' in str(col_name) or 'score' in str(col_name).lower():
                        score_col_idx = idx
                        break
                
                # Giải quyết lỗi định dạng số phẩy của Google Sheets (vd: 16,7 -> 16.7)
                raw_scores = df_week.iloc[:, score_col_idx].astype(str).str.replace(',', '.')
                scores = pd.to_numeric(raw_scores, errors='coerce').dropna()
                
                if not scores.empty:
                    c1, c2, c3, c4 = st.columns(4)
                    c1.metric("已考次數 (Total Exams)", f"{len(scores)}")
                    c2.metric("平均分 (Average)", f"{scores.mean():.1f}")
                    c3.metric("最高分 (Highest)", f"{scores.max():.1f}")
                    c4.metric("最低分 (Lowest)", f"{scores.min():.1f}")
                    
                    csv_data = df_week.to_csv(index=False).encode('utf-8-sig')
                    st.download_button(label="📥 下載成績單 (Download CSV)", data=csv_data, file_name=f"TOCFL_Results_Week_{conf[2]}.csv", mime="text/csv")
                else:
                    st.info("本週的數據沒有有效分數 (No valid scores found for this week).")
            else: 
                st.info("本週尚無成績 (No results for this week yet).")
        else:
            st.info("系統尚未有任何考試成績 (System has no exam records yet).")

    st.markdown("---")
    if st.button("登出 (Logout)", use_container_width=True): 
        st.session_state.page = "Login"
        st.rerun()

# ==========================================
# 4. EXAM PAGE
# ==========================================
def exam_page():
    sv = st.session_state.student_info
    conf = get_exam_config()
    
    if 'end_time' not in st.session_state:
        st.session_state.end_time = datetime.now() + timedelta(minutes=int(conf[1]))
    
    target_timestamp = int(st.session_state.end_time.timestamp())
    now_timestamp = int(datetime.now().timestamp())
    remaining = target_timestamp - now_timestamp
    
    if remaining <= 0:
        finish_exam(sv, conf[2])
        st.rerun()

    st.components.v1.html(
        f"""
        <div style="display: flex; justify-content: center; align-items: center; font-family: 'Segoe UI', sans-serif;">
            <div id="timer" style="background: #FFFFFF; padding: 10px 30px; border-radius: 30px; box-shadow: 0 4px 10px rgba(0,0,0,0.05); font-size: 1.8rem; font-weight: 900; color: #F43F5E; border: 3px solid #FFE4E6; text-align: center;">
                --:--
            </div>
        </div>
        <script>
        var targetTime = {target_timestamp};
        var elem = document.getElementById('timer');
        setInterval(function() {{
            var now = Math.floor(Date.now() / 1000);
            var timeLeft = targetTime - now;
            if (timeLeft <= 0) {{ elem.innerHTML = "時間到 (Time's up)"; }} 
            else {{
                var m = Math.floor(timeLeft / 60);
                var s = timeLeft % 60;
                elem.innerHTML = "⏰ " + (m < 10 ? "0" + m : m) + ":" + (s < 10 ? "0" + s : s);
            }}
        }}, 1000);
        </script>
        """, height=75
    )

    total_q = len(st.session_state.exam_data)
    curr_idx = st.session_state.current_q
    
    st.markdown(f"""
        <div style='background: #FFFFFF; padding: 20px; border-radius: 15px; margin-bottom: 20px; border: 2px solid #E0F2FE;'>
            <h3 style='margin:0; color: #0284C7; text-align: center;'>🎒 TOCFL - 第 {conf[2]} 週 (Week {conf[2]})</h3>
            <p style='margin: 5px 0 0 0; color: #64748B; text-align: center;'>姓名: <b>{sv['EN']}</b> | 學號: {sv['ID']} | 班級: {sv['Lop']}</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.progress((curr_idx + 1) / total_q)
    st.markdown(f"<p style='text-align: center; color: #64748B; font-weight: bold;'>題目 (Question): {curr_idx + 1} / {total_q}</p>", unsafe_allow_html=True)

    row = st.session_state.exam_data[curr_idx]
    st.markdown(f'<div class="question-card">📝 第 {curr_idx + 1} 題：<br><span style="font-weight: normal; color: #000000;">{row[1]}</span></div>', unsafe_allow_html=True)
    
    saved_ans = st.session_state.answers.get(str(curr_idx))
    
    if len(row) > 2 and row[2].strip() != "":
        opts = [f"A. {row[2]}", f"B. {row[3]}", f"C. {row[4]}", f"D. {row[5]}"]
        idx = None
        if saved_ans:
            for opt_idx, opt_val in enumerate(opts):
                if saved_ans.startswith(opt_val[0]): idx = opt_idx
        
        choice = st.radio("Select Answer", opts, key=f"radio_{curr_idx}", index=idx, label_visibility="collapsed")
        st.session_state.answers[str(curr_idx)] = choice
    else:
        text_ans = st.text_input("Fill in", value=saved_ans if saved_ans else "", key=f"text_{curr_idx}", placeholder="✍️ 請輸入答案...", label_visibility="collapsed")
        st.session_state.answers[str(curr_idx)] = text_ans

    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if curr_idx > 0:
            if st.button("⬅️ 上一題 (Previous)", use_container_width=True):
                st.session_state.current_q -= 1
                auto_sync_progress()
                st.rerun()
    with col2:
        if curr_idx < total_q - 1:
            if st.button("下一題 (Next) ➡️", use_container_width=True):
                st.session_state.current_q += 1
                auto_sync_progress()
                st.rerun()
        else:
            st.markdown('<div class="submit-btn">', unsafe_allow_html=True)
            if st.button("🚀 提交試卷 (Submit)", use_container_width=True):
                finish_exam(sv, conf[2])
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

def finish_exam(sv, week):
    auto_sync_progress()
    total_q = len(st.session_state.exam_data)
    points_per_q = 100.0 / total_q if total_q > 0 else 0
    score = 0.0
    logs = []
    quoc_tich = str(sv.get('QuocTich', '')).strip().lower()

    for i, row in enumerate(st.session_state.exam_data):
        correct = str(row[6]).strip().upper() if len(row) > 6 else ""
        ans = st.session_state.answers.get(str(i))
        
        choice = "未作答"
        if ans and str(ans).strip() != "None":
            choice = str(ans)[0].upper() if ". " in str(ans) else str(ans).strip().upper()
            
        if choice == correct: score += points_per_q
        else: 
            exp_cn = row[7] if len(row) > 7 else "無"
            exp_vn = row[8] if len(row) > 8 and str(row[8]).strip() != "" else exp_cn
            exp_id = row[9] if len(row) > 9 and str(row[9]).strip() != "" else exp_cn
            exp_th = row[10] if len(row) > 10 and str(row[10]).strip() != "" else exp_cn
            
            if any(k in quoc_tich for k in ["việt", "越", "vn"]): final_exp = exp_vn
            elif any(k in quoc_tich for k in ["indo", "印", "id"]): final_exp = exp_id
            elif any(k in quoc_tich for k in ["thái", "泰", "th"]): final_exp = exp_th
            else: final_exp = exp_cn

            logs.append(f"❌ 第 {i+1} 題 ({row[1]}) \n您的答案 (Your Answer): {choice} | ✅ 正確答案 (Correct): {correct} \n💡 解析 (Explanation): {final_exp}")
    
    score = round(score, 1)
    if score.is_integer(): score = int(score)

    tw_time = datetime.utcnow() + timedelta(hours=8)

    sheet.worksheet("考試結果").append_row([
        tw_time.strftime("%Y-%m-%d %H:%M"), f"第 {week} 週", sv['Lop'], sv['ID'], 
        sv['CN'], sv['EN'], sv['QuocTich'], score
    ]) 
    
    try:
        ws_temp = sheet.worksheet("正在考試")
        cell = ws_temp.find(str(sv['ID']))
        try:
            ws_temp.delete_rows(cell.row)
        except:
            ws_temp.delete_row(cell.row)
    except: pass
    
    st.session_state.final_score = score
    st.session_state.final_logs = logs
    st.session_state.page = "Result"

# ==========================================
# 5. LOGIN & LOGIC
# ==========================================
if st.session_state.page == "Login":
    st.markdown("<br><br>", unsafe_allow_html=True) 
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<h2 style='color: #0284C7; font-weight: 900; text-align: center; margin-top: 30px;'>🏫 華語文測驗系統 <span style='font-size:1.5rem; color:#64748B;'>TOCFL Test System</span></h2>", unsafe_allow_html=True)
        st.write("")
        
        st_id = st.text_input("學號 (Student ID):", placeholder="Ex: 1141313801")
        
        if st.button("🌟 登入 (Login)", use_container_width=True):
            if st_id:
                sv_rows = fetch_sheet_data("學生名單")[1:]
                sv = None
                for r in sv_rows:
                    if len(r) > 1 and str(r[1]).strip() == st_id.strip():
                        sv = {"Lop": r[0], "ID": r[1], "CN": r[2], "EN": r[3], "QuocTich": r[5] if len(r)>5 else "Unknown"}
                        break
                
                if sv:
                    conf = get_exam_config()
                    if conf[0] != "開":
                        st.error("💤 系統關閉中 (System is currently closed).")
                    else:
                        allowed_classes = [c.strip() for c in (conf[4].split(",") if len(conf)>4 and conf[4] else [])]
                        if len(allowed_classes) > 0 and sv['Lop'] not in allowed_classes:
                            st.error(f"🚷 您的班級尚未開放 (Your class is not allowed yet).")
                        else:
                            st.session_state.student_info = sv
                            st.session_state.answers = {}
                            st.session_state.current_q = 0
                            
                            is_resumed = False
                            temp_data = fetch_dynamic_data("正在考試")
                            for r in temp_data:
                                if r and len(r) > 0 and str(r[0]).strip() == str(sv['ID']).strip():
                                    try:
                                        state_dict = json.loads(r[1])
                                        st.session_state.exam_data = state_dict.get("exam_data", [])
                                        st.session_state.answers = state_dict.get("answers", {})
                                        st.info("🔄 已恢復上次進度！(Progress restored!)")
                                        is_resumed = True
                                    except: pass
                                    break
                            
                            if not is_resumed:
                                all_q = fetch_sheet_data("題庫")[1:]
                                num_q = int(conf[5])
                                st.session_state.exam_data = random.sample(all_q, min(num_q, len(all_q)))
                            
                            auto_sync_progress()
                            time.sleep(1)
                            st.session_state.page = "Exam"
                            st.rerun()
                else: st.error("🤷‍♂️ 找不到此學號 (Student ID not found).")
            else: st.warning("⚠️ 請輸入學號 (Please enter your ID).")

        st.markdown("<br><br>", unsafe_allow_html=True)
        with st.expander("🔐 系統管理員 (Admin Login)"):
            pw = st.text_input("密碼 (Password)", type="password", max_chars=10)
            if len(pw) == 10:
                if st.button("進入後台 (Enter Dashboard)", use_container_width=True): 
                    conf = get_exam_config()
                    if len(conf) > 1 and pw == str(conf[3]):
                        st.session_state.page = "Admin"
                        st.rerun()
                    else:
                        st.error("❌ 密碼錯誤 (Sai mật khẩu, vui lòng thử lại!)")
            elif len(pw) > 0:
                st.info(f"Đang nhập... ({len(pw)}/10)")

elif st.session_state.page == "Result":
    st.balloons()
    st.markdown("<h1>🎉 測驗完成 (Exam Completed)!</h1>", unsafe_allow_html=True)
    
    score = st.session_state.final_score
    msg = "太厲害了 (Excellent)！💯" if score >= 80 else "繼續加油 (Keep going)！💪"
    
    st.markdown(f"""
        <div style='background-color: #FFFFFF; border: 4px dashed #38BDF8; border-radius: 30px; padding: 40px; text-align: center; margin: 30px auto; max-width: 500px;'>
            <h3 style='color: #0284C7; margin: 0;'>你的得分 (Your Score)</h3>
            <h1 style='color: #F43F5E; font-size: 5rem; font-weight: 900; margin: 10px 0;'>{score}</h1>
            <h4 style='color: #000000;'>{msg}</h4>
        </div>
    """, unsafe_allow_html=True)
    
    with st.expander("🔍 查看錯題解析 (Review Mistakes)"):
        if st.session_state.final_logs:
            for log in st.session_state.final_logs: st.error(log)
        else: st.success("🌟 完美！一題都沒錯。(Perfect! No mistakes.)")
            
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        if st.button("🏠 回首頁 (Back to Home)", use_container_width=True): 
            st.session_state.clear()
            st.rerun()

elif st.session_state.page == "Admin": admin_page()
elif st.session_state.page == "Exam": exam_page()
