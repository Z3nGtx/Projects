import pandas as pd
import streamlit as st

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="College Analytics System",
    page_icon="🎓",
    layout="wide"
)

# ---------------- CUSTOM CSS ----------------
st.markdown("""
<style>
.big-title { font-size: 28px; font-weight: 700; }
.section-title { font-size: 20px; font-weight: 600; margin-top: 20px; }
</style>
""", unsafe_allow_html=True)

# ---------------- TITLE ----------------
st.markdown('<div class="big-title">🎓 College / Coaching Institute Analytics Dashboard</div>', unsafe_allow_html=True)
st.markdown("**Academic Performance & Attendance Monitoring System**")
st.divider()

# ---------------- SIDEBAR ----------------
st.sidebar.header("🔍 Filters")
st.sidebar.markdown("### 📂 Upload Data Files")

# ---------------- FILE UPLOAD ----------------
students_file = st.sidebar.file_uploader(
    "Upload Students File (CSV / Excel)", type=["csv", "xlsx"]
)
marks_file = st.sidebar.file_uploader(
    "Upload Marks File (CSV / Excel)", type=["csv", "xlsx"]
)
attendance_file = st.sidebar.file_uploader(
    "Upload Attendance File (CSV / Excel)", type=["csv", "xlsx"]
)

# ---------------- LOAD DATA FUNCTION ----------------
def load_file(file):
    if file is not None:
        if file.name.endswith(".csv"):
            return pd.read_csv(file)
        else:
            return pd.read_excel(file)
    return None

# ---------------- LOAD DATA ----------------
students = load_file(students_file)
marks = load_file(marks_file)
attendance = load_file(attendance_file)

# Stop app until all required files are uploaded
if students is None or marks is None or attendance is None:
    st.markdown("""
    ### 📂 Upload Your Data to Get Started

    Please upload:
    - 👩‍🎓 **Students file**
    - 📊 **Marks file**
    - 📅 **Attendance file**

    Supported formats: **CSV, Excel**
    """)
    st.stop()

st.success("✅ Data uploaded successfully. Dashboard is ready.")

# ---------------- SIDEBAR FILTER OPTIONS ----------------
course_options = sorted(students["course"].dropna().unique())
batch_options = sorted(students["batch"].dropna().unique())
subject_options = sorted(marks["subject"].dropna().unique())

selected_course = st.sidebar.multiselect("Select Course", course_options, course_options)
selected_batch = st.sidebar.multiselect("Select Batch", batch_options, batch_options)
selected_subject = st.sidebar.multiselect("Select Subject", subject_options, subject_options)

# ---------------- APPLY FILTERS ----------------
filtered_students = students[
    students["course"].isin(selected_course) &
    students["batch"].isin(selected_batch)
]

filtered_marks = marks[
    marks["subject"].isin(selected_subject) &
    marks["student_id"].isin(filtered_students["student_id"])
]

filtered_attendance = attendance[
    attendance["student_id"].isin(filtered_students["student_id"])
]

# ---------------- MARKS ANALYTICS ----------------
avg_marks = filtered_marks.groupby("student_id")["marks"].mean().reset_index()
avg_marks.columns = ["student_id", "avg_marks"]

# ---------------- ATTENDANCE ANALYTICS ----------------
filtered_attendance["present_flag"] = filtered_attendance["status"].apply(
    lambda x: 1 if x == "Present" else 0
)

attendance_pct = (
    filtered_attendance.groupby("student_id")["present_flag"]
    .mean()
    .reset_index()
)
attendance_pct["attendance_pct"] = attendance_pct["present_flag"] * 100
attendance_pct = attendance_pct[["student_id", "attendance_pct"]]

attendance_summary = (
    filtered_attendance
    .groupby(["student_id", "status"])
    .size()
    .unstack(fill_value=0)
    .reset_index()
)

if "Present" not in attendance_summary.columns:
    attendance_summary["Present"] = 0
if "Absent" not in attendance_summary.columns:
    attendance_summary["Absent"] = 0

# ---------------- FINAL MERGE ----------------
final = (
    filtered_students
    .merge(avg_marks, on="student_id", how="left")
    .merge(attendance_pct, on="student_id", how="left")
    .merge(attendance_summary, on="student_id", how="left")
)

final.fillna(0, inplace=True)
final["Present"] = final["Present"].astype(int)
final["Absent"] = final["Absent"].astype(int)

# ---------------- LOGIC COLUMNS ----------------
final["risk"] = final.apply(
    lambda x: "At Risk" if x["avg_marks"] < 40 and x["attendance_pct"] < 75 else "Normal",
    axis=1
)

final["mostly_absent"] = final["attendance_pct"].apply(
    lambda x: "Yes" if x < 50 else "No"
)

final["attendance_display"] = final["attendance_pct"].round(2).astype(str) + " %"

# ---------------- KPI SECTION ----------------
st.markdown('<div class="section-title">📌 Key Academic Indicators</div>', unsafe_allow_html=True)
c1, c2, c3, c4 = st.columns(4)

c1.metric("Total Students", final.shape[0])
c2.metric("Average Marks", round(final["avg_marks"].mean(), 1))
c3.metric("Average Attendance", f"{round(final['attendance_pct'].mean(),1)}%")
c4.metric("At-Risk Students", final[final["risk"] == "At Risk"].shape[0])

# ---------------- CHARTS ----------------
st.markdown('<div class="section-title">📊 Performance Overview</div>', unsafe_allow_html=True)
col5, col6 = st.columns(2)

with col5:
    st.subheader("Average Marks by Student")
    st.bar_chart(final.set_index("name")["avg_marks"])

with col6:
    st.subheader("Attendance Percentage by Student")
    st.bar_chart(final.set_index("name")["attendance_pct"])

# ---------------- MOSTLY ABSENT STUDENTS ----------------
st.markdown('<div class="section-title">🚫 Students Absent Most of the Time</div>', unsafe_allow_html=True)

display_cols = [
    "student_id", "name", "course", "batch",
    "Present", "Absent", "attendance_display", "risk"
]

st.dataframe(
    final[final["mostly_absent"] == "Yes"][display_cols]
    .sort_values("Absent", ascending=False),
    use_container_width=True
)

# ---------------- DETAILED RECORDS ----------------
st.markdown('<div class="section-title">📋 Detailed Student Records</div>', unsafe_allow_html=True)
st.dataframe(final[display_cols], use_container_width=True)

# ---------------- AT-RISK STUDENTS ----------------
st.markdown('<div class="section-title">⚠️ At-Risk Students</div>', unsafe_allow_html=True)
st.dataframe(final[final["risk"] == "At Risk"][display_cols], use_container_width=True)