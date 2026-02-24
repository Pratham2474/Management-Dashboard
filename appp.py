import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
from PIL import Image
import os
import base64

# ==================== PAGE CONFIG ====================
st.set_page_config(
    page_title="MY SCHOOL Dashboard",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==================== LOAD BACKGROUND IMAGE ====================
@st.cache_data
def load_background_image():
    if os.path.exists('background.jpg'):
        return 'background.jpg'
    elif os.path.exists('background.png'):
        return 'background.png'
    else:
        return None

bg_image_path = load_background_image()

# ==================== LOAD CUSTOM CSS ====================
def load_css():
    with open('styles.css', 'r') as f:
        return f.read()

custom_css = load_css()
st.markdown(f"<style>{custom_css}</style>", unsafe_allow_html=True)

# ==================== DATA LOADING ====================
@st.cache_data
def load_data():
    teachers_df = pd.read_csv('teachers.csv')
    students_df = pd.read_csv('students.csv')
    performance_df = pd.read_csv('performance.csv')
    return teachers_df, students_df, performance_df

teachers_df, students_df, performance_df = load_data()

# ==================== AUTHENTICATION ====================
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.username = None
    st.session_state.role = None

# ==================== LOGIN PAGE ====================
if not st.session_state.authenticated:
    col_space1, col1, col2, col_space2 = st.columns([0.5, 1, 1, 0.5])
    
    with col1:
        st.markdown("""
            <div class="login-box">
                <div style='text-align: center;'>
                    <div style='font-size: 100px; margin-bottom: 20px; animation: float 3s ease-in-out infinite;'>🎓</div>
                    <h1 class='main-title'>MY SCHOOL</h1>
                    <h2 class='subtitle'>Management Dashboard</h2>
                    <p class='description'>
                        <strong class='highlight-text'>Advanced School Management System</strong><br>
                        Comprehensive Analytics & Performance Tracking<br>
                        Real-time Insights & Data Analytics
                    </p>
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("<div style='padding: 20px;'></div>", unsafe_allow_html=True)
        
        st.markdown("""
            <div class="login-form">
                <h2 class='login-title'>🔐 Login Portal</h2>
        """, unsafe_allow_html=True)
        
        username = st.text_input("👤 Username", placeholder="Enter your username", key="login_username")
        password = st.text_input("🔑 Password", type="password", placeholder="Enter your password", key="login_password")
        role = st.selectbox("👥 Select Role", ["Admin", "Principal", "Teacher"])
        
        if st.button("🔓 Login Now", use_container_width=True):
            USERS = {
                'admin': 'admin123',
                'Pratham2474': 'password123',
                'principal': 'principal123'
            }
            
            if username in USERS and USERS[username] == password:
                st.session_state.authenticated = True
                st.session_state.username = username
                st.session_state.role = role
                st.success("✅ Login successful! Redirecting...")
                st.rerun()
            else:
                st.error("❌ Invalid username or password. Please try again.")
        
        st.markdown("""
                <div style='height: 20px;'></div>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
            <div class="demo-credentials">
                <div class="demo-title">📋 Demo Credentials</div>
                <div class="demo-item"><span class="demo-label">🔹 Admin:</span> admin / admin123</div>
                <div class="demo-item"><span class="demo-label">🔹 User:</span> Pratham2474 / password123</div>
                <div class="demo-item"><span class="demo-label">🔹 Principal:</span> principal / principal123</div>
            </div>
        """, unsafe_allow_html=True)

else:
    # ==================== HEADER ====================
    header_col1, header_col2, header_col3 = st.columns([2, 1, 1])
    
    with header_col1:
        st.markdown("<h1 class='dashboard-title'>🎓 MY SCHOOL Dashboard</h1>", unsafe_allow_html=True)
        st.markdown("<p class='dashboard-subtitle'>📊 Comprehensive Management System</p>", unsafe_allow_html=True)
    
    with header_col3:
        col_logout, col_user = st.columns([1, 1])
        with col_logout:
            if st.button("🚪 Logout"):
                st.session_state.authenticated = False
                st.session_state.username = None
                st.session_state.role = None
                st.rerun()
        
        st.markdown(f"""
            <div class="user-info">
                <div class="user-name">👤 {st.session_state.username.upper()}</div>
                <div class="user-role">Role: {st.session_state.role}</div>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
    st.divider()
    
    # ==================== TABS ====================
    tabs = st.tabs(["📊 Dashboard", "👨‍🏫 Teachers", "🕐 Attendance", "⚠️ Attrition"])
    
    # ========== DASHBOARD TAB ==========
    with tabs[0]:
        st.markdown("## 📊 MS Dashboard Overview")
        st.markdown("_Real-time monitoring of school performance metrics_")
        
        perf = performance_df.copy()
        teachers = teachers_df.copy()
        
        # KPI METRICS
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        
        with col1:
            st.metric("👨‍🏫 Total Teachers", len(teachers), "Staff Members", label_visibility="collapsed")
        
        with col2:
            st.metric("👥 Total Students", len(students_df), "Enrolled", label_visibility="collapsed")
        
        with col3:
            at_risk_count = len(teachers[teachers['Status'] == 'At Risk'])
            st.metric("⚠️ At Risk", at_risk_count, "Teachers", label_visibility="collapsed")
        
        with col4:
            compliance = round(teachers['Compliance_Score'].mean(), 2)
            st.metric("✓ Compliance", compliance, "Out of 10", label_visibility="collapsed")
        
        with col5:
            teaching = round(teachers['Teaching_Score_Internal'].mean(), 2)
            st.metric("📈 Teaching", teaching, "Score", label_visibility="collapsed")
        
        with col6:
            att_rate = round((perf['Attendance'] == 'Present').sum() / len(perf) * 100, 1) if len(perf) > 0 else 0
            st.metric("📊 Attendance", f"{att_rate}%", "Present", label_visibility="collapsed")
        
        st.divider()
        
        # CHARTS
        st.markdown("### 📈 Performance Analytics")
        
        chart_col1, chart_col2 = st.columns(2)
        
        with chart_col1:
            st.markdown("#### Performance Trend (Last 30 Days)")
            perf_trend = perf.sort_values('Date').tail(30)
            trend_data = perf_trend.groupby('Date')['Score'].agg(['mean', 'min', 'max']).reset_index()
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=trend_data['Date'], y=trend_data['mean'],
                mode='lines+markers', name='Average Score',
                line=dict(color='#c500ff', width=4),
                marker=dict(size=8, color='#c500ff'),
                fill='tozeroy', fillcolor='rgba(197, 0, 255, 0.15)'
            ))
            fig.add_trace(go.Scatter(
                x=trend_data['Date'], y=trend_data['max'],
                mode='lines', name='Max Score',
                line=dict(color='#00ff88', width=2, dash='dash')
            ))
            fig.add_trace(go.Scatter(
                x=trend_data['Date'], y=trend_data['min'],
                mode='lines', name='Min Score',
                line=dict(color='#ff006b', width=2, dash='dash')
            ))
            
            fig.update_layout(
                template='plotly_dark', hovermode='x unified',
                height=400, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#bdc3c7', size=11),
                margin=dict(t=30, b=20, l=20, r=20)
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with chart_col2:
            st.markdown("#### Score Distribution Analysis")
            score_dist = {
                'Excellent (90-100)': len(perf[perf['Score'] >= 90]),
                'Good (75-89)': len(perf[(perf['Score'] >= 75) & (perf['Score'] < 90)]),
                'Average (60-74)': len(perf[(perf['Score'] >= 60) & (perf['Score'] < 75)]),
                'Below Average (<60)': len(perf[perf['Score'] < 60])
            }
            
            fig = go.Figure(data=[go.Pie(
                labels=list(score_dist.keys()),
                values=list(score_dist.values()),
                marker=dict(colors=['#00ff88', '#c500ff', '#ff006b', '#ff9500']),
                hole=0.35,
                textinfo='label+percent',
                hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>'
            )])
            
            fig.update_layout(
                template='plotly_dark', height=400, paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#bdc3c7', size=11),
                margin=dict(t=30, b=20, l=20, r=20)
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # MORE ANALYTICS
        st.markdown("### 📚 Subject & Status Analytics")
        
        anal_col1, anal_col2 = st.columns(2)
        
        with anal_col1:
            st.markdown("#### Teachers Distribution by Subject")
            subject_dist = teachers['Subject'].value_counts().sort_values()
            
            fig = go.Figure(data=[go.Bar(
                y=subject_dist.index,
                x=subject_dist.values,
                orientation='h',
                marker=dict(
                    color=subject_dist.values,
                    colorscale='purples',
                    line=dict(color='#c500ff', width=2)
                ),
                text=subject_dist.values,
                textposition='auto',
                hovertemplate='<b>%{y}</b><br>Teachers: %{x}<extra></extra>'
            )])
            
            fig.update_layout(
                template='plotly_dark', height=380, paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#bdc3c7', size=11),
                margin=dict(t=20, b=20, l=100, r=20)
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with anal_col2:
            st.markdown("#### Teacher Status Distribution")
            status_dist = teachers['Status'].value_counts()
            colors_map = {'Active': '#00ff88', 'At Risk': '#ff9500', 'Left': '#ff006b'}
            
            fig = go.Figure(data=[go.Pie(
                labels=status_dist.index,
                values=status_dist.values,
                marker=dict(colors=[colors_map.get(s, '#c500ff') for s in status_dist.index]),
                hole=0.35,
                textinfo='label+value',
                hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>'
            )])
            
            fig.update_layout(
                template='plotly_dark', height=380, paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#bdc3c7', size=11),
                margin=dict(t=20, b=20, l=20, r=20)
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # ATTENDANCE IMPACT
        st.markdown("### 📊 Attendance Impact Analysis")
        
        imp_col1, imp_col2 = st.columns(2)
        
        with imp_col1:
            st.markdown("#### Attendance vs Performance Score")
            attend_impact = perf.groupby('Attendance').agg({'Score': 'mean', 'Late_Count': 'mean'}).reset_index()
            
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=attend_impact['Attendance'],
                y=attend_impact['Score'],
                name='Avg Score',
                marker=dict(color='#c500ff'),
                text=attend_impact['Score'].round(1),
                textposition='auto',
                yaxis='y'
            ))
            
            fig.update_layout(
                template='plotly_dark', height=350, paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#bdc3c7', size=11),
                margin=dict(t=20, b=20, l=20, r=20),
                hovermode='x unified'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with imp_col2:
            st.markdown("#### Late Arrival Trend (30 Days)")
            late_trend = perf.sort_values('Date').tail(30).groupby('Date')['Late_Count'].sum()
            
            fig = go.Figure(data=[go.Scatter(
                x=late_trend.index, y=late_trend.values,
                mode='lines+markers', name='Late Arrivals',
                line=dict(color='#ff9500', width=4),
                marker=dict(size=10, color='#ff9500'),
                fill='tozeroy', fillcolor='rgba(255, 149, 0, 0.15)',
                hovertemplate='<b>%{x}</b><br>Late Count: %{y}<extra></extra>'
            )])
            
            fig.update_layout(
                template='plotly_dark', height=350, paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#bdc3c7', size=11),
                margin=dict(t=20, b=20, l=20, r=20)
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # ========== TEACHERS TAB ==========
    with tabs[1]:
        st.markdown("## 👨‍🏫 Teacher Management System")
        st.markdown("_Search, filter and manage teacher performance data_")
        
        # FILTERS
        filter_col1, filter_col2, filter_col3, filter_col4 = st.columns(4)
        
        with filter_col1:
            search = st.text_input("🔍 Search by Name or ID", placeholder="Type name...")
        
        with filter_col2:
            status_filter = st.selectbox("Filter by Status", ["All", "Active", "At Risk", "Left"])
        
        with filter_col3:
            subject_list = ["All"] + sorted(teachers_df['Subject'].unique().tolist())
            subject_filter = st.selectbox("Filter by Subject", subject_list)
        
        with filter_col4:
            st.write("")
            apply_btn = st.button("🔎 Apply Filters", use_container_width=True)
        
        # FILTER DATA
        filtered_teachers = teachers_df.copy()
        
        if search:
            filtered_teachers = filtered_teachers[
                filtered_teachers['Teacher_Name'].str.lower().str.contains(search.lower(), na=False)
            ]
        
        if status_filter != "All":
            filtered_teachers = filtered_teachers[filtered_teachers['Status'] == status_filter]
        
        if subject_filter != "All":
            filtered_teachers = filtered_teachers[filtered_teachers['Subject'] == subject_filter]
        
        # STATS
        st.markdown("---")
        stat_col1, stat_col2, stat_col3, stat_col4 = st.columns(4)
        
        with stat_col1:
            st.metric("📊 Total Found", len(filtered_teachers))
        
        with stat_col2:
            st.metric("✓ Active", len(filtered_teachers[filtered_teachers['Status'] == 'Active']))
        
        with stat_col3:
            st.metric("⚠️ At Risk", len(filtered_teachers[filtered_teachers['Status'] == 'At Risk']))
        
        with stat_col4:
            st.metric("🚪 Left", len(filtered_teachers[filtered_teachers['Status'] == 'Left']))
        
        # TABLE
        st.markdown("### 📋 Teacher Directory")
        
        if len(filtered_teachers) > 0:
            display_df = filtered_teachers[[
                'Teacher_ID', 'Teacher_Name', 'Subject', 'Total_Experience_Years',
                'Teaching_Score_Internal', 'Compliance_Score', 'Status'
            ]].head(50).copy()
            
            display_df.columns = ['ID', 'Name', 'Subject', 'Experience', 'Teaching Score', 'Compliance', 'Status']
            
            st.dataframe(display_df, use_container_width=True, height=400, hide_index=True)
        else:
            st.warning("❌ No teachers found matching your criteria.")
        
        # TOP PERFORMERS
        st.markdown("---")
        st.markdown("### ⭐ Top 5 Performing Teachers")
        
        top_teachers = teachers_df.nlargest(5, 'Teaching_Score_Internal')
        
        top_cols = st.columns(5)
        for idx, (_, teacher) in enumerate(top_teachers.iterrows()):
            with top_cols[idx]:
                st.markdown(f"""
                    <div class="teacher-card">
                        <img src="{teacher['Avatar_URL']}" class="teacher-avatar">
                        <div class="teacher-name">{teacher['Teacher_Name'][:20]}</div>
                        <div class="teacher-subject">{teacher['Subject']}</div>
                        <div class="teacher-score">{teacher['Teaching_Score_Internal']:.1f}</div>
                        <div class="teacher-label">Teaching Score</div>
                    </div>
                """, unsafe_allow_html=True)
    
    # ========== ATTENDANCE TAB ==========
    with tabs[2]:
        st.markdown("## 🕐 Attendance & Punctuality")
        st.markdown("_Track attendance patterns and late arrivals_")
        
        perf = performance_df.copy()
        
        # KPI METRICS
        kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)
        
        present_rate = round((perf['Attendance'] == 'Present').sum() / len(perf) * 100, 1)
        absent_rate = round((perf['Attendance'] == 'Absent').sum() / len(perf) * 100, 1)
        
        with kpi_col1:
            st.metric("✓ Present Rate", f"{present_rate}%", "Today")
        
        with kpi_col2:
            st.metric("✗ Absent Rate", f"{absent_rate}%", "Today")
        
        with kpi_col3:
            st.metric("⏰ Avg Late Count", f"{perf['Late_Count'].mean():.2f}", "Times/Month")
        
        with kpi_col4:
            st.metric("📊 Max Late Count", int(perf['Late_Count'].max()), "Times")
        
        st.divider()
        
        # ATTENDANCE CHARTS
        att_chart1, att_chart2, att_chart3 = st.columns(3)
        
        with att_chart1:
            st.markdown("#### Attendance Status")
            att_status = perf['Attendance'].value_counts()
            
            fig = go.Figure(data=[go.Pie(
                labels=att_status.index, values=att_status.values,
                marker=dict(colors=['#00ff88', '#ff006b']),
                hole=0.4, textinfo='label+value',
                hovertemplate='<b>%{label}</b><br>Count: %{value}<extra></extra>'
            )])
            
            fig.update_layout(
                template='plotly_dark', height=350, paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#bdc3c7', size=11)
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with att_chart2:
            st.markdown("#### Late Arrival Trend")
            late_analysis = perf.sort_values('Date').tail(30).groupby('Date')['Late_Count'].mean()
            
            fig = go.Figure(data=[go.Scatter(
                x=late_analysis.index, y=late_analysis.values,
                mode='lines+markers', name='Avg Late',
                line=dict(color='#ff9500', width=3),
                marker=dict(size=8, color='#ff9500'),
                fill='tozeroy', fillcolor='rgba(255, 149, 0, 0.15)',
                hovertemplate='<b>%{x}</b><br>Avg Late: %{y:.2f}<extra></extra>'
            )])
            
            fig.update_layout(
                template='plotly_dark', height=350, paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#bdc3c7', size=11)
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with att_chart3:
            st.markdown("#### Performance vs Attendance")
            attend_vs_score = perf.groupby('Attendance').agg({'Score': 'mean'}).reset_index()
            
            fig = go.Figure(data=[go.Bar(
                x=attend_vs_score['Attendance'],
                y=attend_vs_score['Score'],
                marker=dict(
                    color=attend_vs_score['Score'],
                    colorscale='purples',
                    line=dict(color='#c500ff', width=2)
                ),
                text=attend_vs_score['Score'].round(1),
                textposition='auto',
                hovertemplate='<b>%{x}</b><br>Avg Score: %{y:.1f}<extra></extra>'
            )])
            
            fig.update_layout(
                template='plotly_dark', height=350, paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#bdc3c7', size=11)
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # ========== ATTRITION TAB ==========
    with tabs[3]:
        st.markdown("## ⚠️ Attrition & Risk Analysis")
        st.markdown("_Monitor teacher retention and identify at-risk employees_")
        
        t = teachers_df.copy()
        
        # KPI METRICS
        atr_kpi1, atr_kpi2, atr_kpi3, atr_kpi4 = st.columns(4)
        
        at_risk_count = len(t[t['Status'] == 'At Risk'])
        high_risk_count = len(t[t['Attrition_Risk_Score'] >= 4.5])
        
        with atr_kpi1:
            st.metric("👥 Total Teachers", len(t), "Staff")
        
        with atr_kpi2:
            st.metric("⚠️ At Risk", at_risk_count, "Teachers")
        
        with atr_kpi3:
            st.metric("🔴 High Risk", high_risk_count, "Critical")
        
        with atr_kpi4:
            st.metric("📈 Avg Risk Score", f"{t['Attrition_Risk_Score'].mean():.2f}", "Out of 5")
        
        st.divider()
        
        # RISK ANALYSIS CHARTS
        risk_chart1, risk_chart2 = st.columns(2)
        
        with risk_chart1:
            st.markdown("#### Risk Distribution")
            
            risk_dist = {
                'Low': len(t[t['Attrition_Risk_Score'] < 1.5]),
                'Medium': len(t[(t['Attrition_Risk_Score'] >= 1.5) & (t['Attrition_Risk_Score'] < 3.0)]),
                'High': len(t[(t['Attrition_Risk_Score'] >= 3.0) & (t['Attrition_Risk_Score'] < 4.5)]),
                'Critical': len(t[t['Attrition_Risk_Score'] >= 4.5])
            }
            
            fig = go.Figure(data=[go.Pie(
                labels=list(risk_dist.keys()),
                values=list(risk_dist.values()),
                marker=dict(colors=['#00ff88', '#ff9500', '#ff006b', '#c500ff']),
                hole=0.4, textinfo='label+value',
                hovertemplate='<b>%{label}</b><br>Count: %{value}<extra></extra>'
            )])
            
            fig.update_layout(
                template='plotly_dark', height=380, paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#bdc3c7', size=11)
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with risk_chart2:
            st.markdown("#### Teachers by Risk Level")
            
            fig = go.Figure(data=[go.Bar(
                x=['Low', 'Medium', 'High', 'Critical'],
                y=[risk_dist['Low'], risk_dist['Medium'], risk_dist['High'], risk_dist['Critical']],
                marker=dict(color=['#00ff88', '#ff9500', '#ff006b', '#c500ff']),
                text=[risk_dist['Low'], risk_dist['Medium'], risk_dist['High'], risk_dist['Critical']],
                textposition='auto',
                hovertemplate='<b>%{x}</b><br>Count: %{y}<extra></extra>'
            )])
            
            fig.update_layout(
                template='plotly_dark', height=380, paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#bdc3c7', size=11)
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # HIGH RISK TEACHERS
        st.markdown("---")
        st.markdown("### 🚨 High Risk Teachers - Immediate Attention Required")
        
        high_risk_teachers = t[t['Attrition_Risk_Score'] >= 3.5].nlargest(10, 'Attrition_Risk_Score')
        
        if len(high_risk_teachers) > 0:
            hr_display = high_risk_teachers[[
                'Teacher_ID', 'Teacher_Name', 'Subject', 'Attrition_Risk_Score',
                'Compliance_Score', 'Teaching_Score_Internal', 'Late_Count_Current_Month', 'Status'
            ]].copy()
            
            hr_display.columns = ['ID', 'Name', 'Subject', 'Attrition Risk', 'Compliance', 'Teaching Score', 'Late Count', 'Status']
            
            st.dataframe(hr_display, use_container_width=True, height=400, hide_index=True)
            
            st.warning(f"⚠️ {len(high_risk_teachers)} teachers require immediate attention and intervention.")
        else:
            st.success("✅ No high-risk teachers identified! Great work on employee retention.")