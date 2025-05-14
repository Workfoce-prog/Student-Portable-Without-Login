
import streamlit as st
import pandas as pd
from datetime import datetime
import os

st.set_page_config(page_title="StratAI Unified Student Portal", layout="wide")
st.title("🔐 LOG IN TO STUDENT PORTAL")

# Upload option
uploaded_file = st.sidebar.file_uploader("Upload custom student CSV", type="csv")
demo_mode = st.sidebar.checkbox("🚀 Enable Demo Mode (no login)", value=False)

if uploaded_file:
    df_students = pd.read_csv(uploaded_file)
    st.sidebar.success("✅ Custom dataset loaded.")
else:
    df_students = pd.read_csv("student_services_full_data.csv")

df_academic = pd.read_csv("academic_info.csv")

# Choose student
if demo_mode:
    selected_id = str(df_students["StudentID"].iloc[0])
else:
    student_ids = df_students["StudentID"].astype(str).tolist()
    selected_id = st.text_input("Enter Student ID")

if demo_mode or (selected_id and selected_id in df_students["StudentID"].astype(str).tolist()):
    student = df_students[df_students["StudentID"].astype(str) == selected_id].iloc[0]
    academic = df_academic[df_academic["StudentID"] == int(selected_id)].iloc[0]

    st.success(f"Welcome, {student['Name']}!")

    tabs = st.tabs([
        "🏠 Dashboard", "📚 Academic Info", "💰 Financial Center",
        "🧠 Wellness & Career", "👨‍👩‍👧 Family Portal", "👤 Profile",
        "📘 Payment History", "🔍 Browse Students"
    ])

    with tabs[0]:
        st.subheader("Dashboard")
        col1, col2, col3 = st.columns(3)
        col1.metric("GPA", student.GPA)
        col2.metric("Career Readiness", student.CareerReadinessScore)
        col3.metric("Outstanding Tuition", f"${student.TotalTuitionDue - student.AmountPaid:,.2f}")

    with tabs[1]:
        st.subheader("Academic Info")
        st.write(f"**Academic Standing:** {academic.AcademicStanding}")
        st.write(f"**Current Credits:** {academic.CurrentCredits}")
        st.code(academic.CourseSchedule)

    with tabs[2]:
        st.subheader("Tuition Payment")
        balance = float(student.TotalTuitionDue - student.AmountPaid)
        amount = st.number_input("Enter Payment Amount", 0.0, float(balance), step=10.0)
        method = st.selectbox("Payment Method", ["Credit Card", "Bank Transfer", "Cash"])
        note = st.text_input("Reference Note")
        if st.button("Submit Payment"):
            receipt_id = f"R-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            log = {
                "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "StudentID": student.StudentID,
                "Name": student.Name,
                "Amount": amount,
                "Method": method,
                "ReceiptID": receipt_id,
                "Note": note
            }
            log_df = pd.DataFrame([log])
            if os.path.exists("payments_log.csv"):
                old = pd.read_csv("payments_log.csv")
                log_df = pd.concat([old, log_df], ignore_index=True)
            log_df.to_csv("payments_log.csv", index=False)
            st.success(f"Payment submitted. Receipt ID: {receipt_id}")

    with tabs[3]:
        st.subheader("Wellness & Career Readiness")
        col1, col2 = st.columns(2)
        col1.metric("Wellness Score", student.WellnessScore)
        col2.metric("Career Score", student.CareerReadinessScore)
        st.bar_chart(pd.DataFrame({
            "Wellness": [student.WellnessScore],
            "Career": [student.CareerReadinessScore]
        }, index=[student.Name]))

    with tabs[4]:
        st.subheader("Family Portal")
        st.write(f"Parent Email: {student.ParentEmail}")
        st.write(f"RAG Status: {student.RAGStatus}")
        st.write(f"Paid: ${student.AmountPaid}, GPA: {student.GPA}")

    with tabs[5]:
        st.subheader("Profile Overview")
        st.json({
            "Name": student.Name,
            "Student ID": int(student.StudentID),
            "Email": f"{student.Name.lower().split()[0]}@university.edu",
            "Program": "Bachelor of Arts",
            "Standing": academic.AcademicStanding
        })

    with tabs[6]:
        st.subheader("Payment History")
        if os.path.exists("payments_log.csv"):
            logs = pd.read_csv("payments_log.csv")
            logs = logs[logs["StudentID"] == student.StudentID]
            if not logs.empty:
                st.dataframe(logs.sort_values(by="Timestamp", ascending=False), use_container_width=True)
            else:
                st.info("No payment history.")
        else:
            st.info("Payment log unavailable.")

    with tabs[7]:
        st.subheader("Browse All Students")
        st.dataframe(df_students, use_container_width=True)

else:
    st.warning("Enter a valid Student ID to access the portal.")
