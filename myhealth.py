import streamlit as st
import pandas as pd
import datetime
import os
from zoneinfo import ZoneInfo

st.set_page_config(page_title="초인류 프로젝트", layout="wide")

# -------------------------------
# 데이터 파일 경로 설정 (로컬/클라우드 분기)
# -------------------------------
desktop = os.path.join(os.path.expanduser("~"), "OneDrive", "바탕 화면")
if os.path.exists(desktop):  # 로컬 환경 (윈도우 바탕화면)
    data_dir = os.path.join(desktop, "myhealth")
else:  # 클라우드 환경 (Streamlit Cloud 등)
    data_dir = "."

os.makedirs(data_dir, exist_ok=True)
DATA_FILE = os.path.join(data_dir, "health_records.csv")

# -------------------------------
# 초기 세팅
# -------------------------------
categories = ["아침루틴", "점심루틴", "저녁루틴", "공부집중", "체력", "식단"]

if "records" not in st.session_state:
    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE)
        if not df.empty:
            df["date"] = pd.to_datetime(
                df["date"], format="%Y-%m-%d %H:%M:%S", errors="coerce"
            )
            st.session_state.records = df.to_dict("records")
        else:
            st.session_state.records = []
    else:
        st.session_state.records = []

if "page" not in st.session_state:
    st.session_state.page = "main"
if "tasks" not in st.session_state:
    st.session_state.tasks = {
        "아침루틴": ["물 1컵 마시기", "가벼운 스트레칭 5분", "아침 햇빛 쬐기"],
        "점심루틴": ["천천히 식사하기", "식후 가벼운 산책", "과식하지 않기"],
        "저녁루틴": ["저녁 7시 이전 식사", "20분 산책", "전자기기 줄이고 독서"],
        "공부집중": ["딥 워크 90분", "포모도로 25분 × 4", "복습 30분"],
        "체력": ["푸시업 30개", "스쿼트 30개", "조깅 20분"],
        "식단": ["단백질 보충", "야채 섭취", "가공식품 줄이기"],
    }

# -------------------------------
# 저장 함수
# -------------------------------
def save_records():
    if st.session_state.records:
        df = pd.DataFrame(st.session_state.records)
        df["date"] = pd.to_datetime(df["date"], errors="coerce")

        # timezone 처리
        if df["date"].dt.tz is None:
            df["date"] = df["date"].dt.tz_localize("Asia/Seoul")
        else:
            df["date"] = df["date"].dt.tz_convert("Asia/Seoul")

        # 저장은 문자열로
        df["date"] = df["date"].dt.strftime("%Y-%m-%d %H:%M:%S")
        df.to_csv(DATA_FILE, index=False)

# -------------------------------
# CSS
# -------------------------------
st.markdown(
    """
    <style>
    .task-row {
        display: flex;
        align-items: center;
        margin-bottom: -6px;
    }
    div.stButton > button:first-child {
        padding: 0px 4px;
        font-size: 12px;
        line-height: 1;
        height: 22px;
        margin-left: 4px;
    }
    .block-container {
        padding-top: 1rem;
        padding-bottom: 0rem;
        padding-left: 1rem;
        padding-right: 1rem;
    }
    html, body, [class^="css"] {
        overflow: hidden !important;
    }
    section[data-testid="stSidebar"] {
        overflow: hidden !important;
        min-width: 320px;
        max-width: 320px;
    }
    section[data-testid="stSidebar"] > div {
        overflow: hidden !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# -------------------------------
# 사이드바 : 제목 + 건강 상태 + 입력
# -------------------------------
with st.sidebar:
    st.title("💪 초인류 프로젝트")

    # 건강 상태 표시
    st.markdown("---")

    if st.session_state.records:
        latest = st.session_state.records[-1]
        date_str = pd.to_datetime(latest["date"]).strftime("%m월 %d일 %H:%M")
        st.markdown(
            f"<span style='font-size:16px; font-weight:bold'>📌 건강 상태 ({date_str} 기준)</span>",
            unsafe_allow_html=True,
        )

        # 몸무게
        st.markdown(f"- ⚖️ 몸무게: {latest['weight']:.1f} kg")

        # 혈압 + 상태 판정
        sys, dia = latest["systolic"], latest["diastolic"]
        if sys < 90 or dia < 60:
            bp_status = "<span style='color:blue'>저혈압</span>"
        elif sys >= 140 or dia >= 90:
            bp_status = "<span style='color:red'>고혈압</span>"
        else:
            bp_status = "<span style='color:green'>정상</span>"
        st.markdown(f"- ❤️ 혈압: {sys}/{dia} mmHg ({bp_status})", unsafe_allow_html=True)

        # 수면시간 + 상태 판정
        sleep = latest.get("sleep", None)
        if sleep is not None:
            if sleep < 6:
                sleep_status = "<span style='color:red'>부족</span>"
            elif 6 <= sleep <= 9:
                sleep_status = "<span style='color:green'>정상</span>"
            else:
                sleep_status = "<span style='color:orange'>과다</span>"
            st.markdown(
                f"- 😴 수면시간: {sleep} 시간 ({sleep_status})", unsafe_allow_html=True
            )

        # BMI + 상태 판정
        height = 168
        bmi = latest["weight"] / ((height / 100) ** 2)
        if bmi < 18.5:
            bmi_status = "<span style='color:blue'>저체중</span>"
        elif bmi < 25:
            bmi_status = "<span style='color:green'>정상</span>"
        elif bmi < 30:
            bmi_status = "<span style='color:orange'>과체중</span>"
        else:
            bmi_status = "<span style='color:red'>비만</span>"
        st.markdown(f"- 📊 BMI: {bmi:.1f} ({bmi_status})", unsafe_allow_html=True)
    else:
        st.info("아직 건강 기록이 없습니다. 아래에서 입력하세요.")

    # 건강 기록 입력
    st.markdown("---")
    st.subheader("📋 건강 기록 입력")

    now = datetime.datetime.now(ZoneInfo("Asia/Seoul"))
    col1, col2 = st.columns(2)
    with col1:
        weight = st.number_input(
            "몸무게 (kg)", min_value=30.0, max_value=200.0, step=0.1, value=73.0
        )
        sleep = st.number_input(
            "수면 시간 (h)", min_value=0.0, max_value=24.0, step=0.5, value=7.0
        )
    with col2:
        systolic = st.number_input(
            "수축기 혈압 (mmHg)", min_value=80, max_value=200, step=1, value=120
        )
        diastolic = st.number_input(
            "이완기 혈압 (mmHg)", min_value=50, max_value=130, step=1, value=80
        )

    if st.button("✅ 건강 기록 저장"):
        new_record = {
            "date": now.strftime("%Y-%m-%d %H:%M:%S"),
            "weight": round(weight, 1),
            "systolic": systolic,
            "diastolic": diastolic,
            "sleep": sleep,
        }
        st.session_state.records.append(new_record)
        save_records()
        st.success("기록이 저장되었습니다!")

    if st.button("📊 변화 그래프 보기"):
        st.session_state.page = "graph"
    if st.button("🏠 대시보드로 돌아가기"):
        st.session_state.page = "main"

# -------------------------------
# 메인 페이지
# -------------------------------
if st.session_state.page == "main":
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### ✅ 오늘의 할 일 체크리스트")

    checked, total = 0, 0
    cols = st.columns(3)

    for i, category in enumerate(categories):
        with cols[i % 3]:
            st.subheader(category)
            for j, task in enumerate(st.session_state.tasks[category]):
                col_task, col_del = st.columns([6, 1])
                with col_task:
                    if st.checkbox(task, key=f"{category}_{j}"):
                        checked += 1
                with col_del:
                    if st.button("❌", key=f"del_{category}_{j}"):
                        st.session_state.tasks[category].remove(task)
                        st.rerun()
                total += 1

            col_in, col_add = st.columns([5, 1])
            with col_in:
                new_task = st.text_input(
                    f"{category} 새 항목",
                    key=f"new_{category}",
                    label_visibility="collapsed",
                    placeholder="추가할 일 입력",
                )
            with col_add:
                if st.button("➕", key=f"add_{category}"):
                    if new_task:
                        st.session_state.tasks[category].append(new_task)
                        st.rerun()

    progress = checked / total if total > 0 else 0
    st.subheader("📊 오늘의 달성률")
    st.progress(progress)
    st.write(f"오늘 달성률: **{progress*100:.1f}%**")

# -------------------------------
# 그래프 페이지
# -------------------------------
elif st.session_state.page == "graph":
    st.title("📊 나의 건강 변화 추이")
    df = pd.DataFrame(st.session_state.records)

    if df.empty:
        st.warning("아직 기록이 없습니다. 좌측에서 건강 기록을 입력하세요.")
    else:
        df["date"] = pd.to_datetime(
            df["date"], format="%Y-%m-%d %H:%M:%S", errors="coerce"
        )
        df = df.sort_values("date").set_index("date")

        st.subheader("⚖️ 몸무게 변화")
        st.line_chart(df["weight"])

        st.subheader("❤️ 혈압 변화 (수축기/이완기)")
        st.line_chart(df[["systolic", "diastolic"]])

        st.subheader("😴 수면시간 변화")
        st.line_chart(df["sleep"])
