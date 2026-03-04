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

# ==================== LOAD CUSTOM CSS ====================
def load_css():
    """Load external CSS file"""
    try:
        with open('styles.css', 'r') as f:
            return f.read()
    except FileNotFoundError:
        st.error("❌ styles.css file not found!")
        return ""

custom_css = load_css()
st.markdown(f"<style>{custom_css}</style>", unsafe_allow_html=True)

# ==================== DATA LOADING ====================

@st.cache_data
def load_data():
    """Load all required data files"""
    try:
        teachers_df = pd.read_csv('teachers.csv')
        students_df = pd.read_csv('students.csv')
        performance_df = pd.read_csv('performance.csv')
        teacher_credentials = pd.read_csv('teacher_login_credentials.csv')
        return teachers_df, students_df, performance_df, teacher_credentials
    except FileNotFoundError as e:
        st.error(f"❌ Error loading data files: {e}")
        return None, None, None, None

teachers_df, students_df, performance_df, teacher_credentials = load_data()

# ==================== HELPER FUNCTIONS ====================

def filter_non_null_info(data_dict):
    """Remove null/empty values from dictionary"""
    return {k: v for k, v in data_dict.items() if pd.notna(v) and v != '' and str(v).lower() != 'nan'}

def create_radar_chart(teacher):
    """Create a radar chart for teacher performance"""
    categories = ['TD Estimated', 'TD Current', 'CCA', 'Stakeholder']
    values = [
        teacher['Teaching_Score_External'] if pd.notna(teacher['Teaching_Score_External']) else 0,
        teacher['Teaching_Score_Internal'] if pd.notna(teacher['Teaching_Score_Internal']) else 0,
        teacher['Contribution_CoCurricular_%'] if pd.notna(teacher['Contribution_CoCurricular_%']) else 0,
        (teacher['Alignment_Head_Rating'] + teacher['Alignment_Peer_Rating'] + 
         teacher['Alignment_Student_Rating'] + teacher['Alignment_Parent_Rating']) / 4 * 20
    ]
    
    fig = go.Figure(data=go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        name='Performance',
        line=dict(color='#00ff88', width=3),
        fillcolor='rgba(0, 255, 136, 0.2)'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                tickfont=dict(color='#bdc3c7', size=10),
                gridcolor='rgba(197, 0, 255, 0.2)'
            ),
            angularaxis=dict(tickfont=dict(color='#bdc3c7', size=10))
        ),
        template='plotly_dark',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#bdc3c7'),
        height=400,
        showlegend=False,
        margin=dict(l=60, r=60, t=60, b=60)
    )
    
    return fig

# ==================== AUTHENTICATION ====================
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.username = None
    st.session_state.role = None
    st.session_state.teacher_id = None

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
                'principal': 'principal123'
            }
            
            if role in ["Admin", "Principal"]:
                if username in USERS and USERS[username] == password:
                    st.session_state.authenticated = True
                    st.session_state.username = username
                    st.session_state.role = role
                    st.session_state.teacher_id = None
                    st.success("✅ Login successful! Redirecting...")
                    st.rerun()
                else:
                    st.error("❌ Invalid username or password. Please try again.")
            
            elif role == "Teacher":
                teacher_creds = teacher_credentials[teacher_credentials['username'] == username]
                if len(teacher_creds) > 0:
                    stored_password = teacher_creds.iloc[0]['password']
                    if str(stored_password) == str(password):
                        st.session_state.authenticated = True
                        st.session_state.username = username
                        st.session_state.role = role
                        st.session_state.teacher_id = teacher_creds.iloc[0]['Teacher_ID']
                        st.success("✅ Login successful! Redirecting...")
                        st.rerun()
                    else:
                        st.error("❌ Invalid password. Please try again.")
                else:
                    st.error("❌ Username not found. Please contact administration.")
        
        st.markdown("""
                <div style='height: 20px;'></div>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
            <div class="demo-credentials">
                <div class="demo-title">📋 Demo Credentials</div>
                <div class="demo-item"><span class="demo-label">🔹 Admin:</span> admin / admin123</div>
                <div class="demo-item"><span class="demo-label">🔹 Principal:</span> principal / principal123</div>
                <div class="demo-item"><span class="demo-label">🔹 Teacher:</span> T001 / 9593</div>
                <div class="demo-item"><span class="demo-label">🔹 Teacher:</span> T002 / 4663</div>
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
                st.session_state.teacher_id = None
                st.rerun()
        
        st.markdown(f"""
            <div class="user-info">
                <div class="user-name">👤 {st.session_state.username.upper()}</div>
                <div class="user-role">Role: {st.session_state.role}</div>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
    st.divider()
    
    # ==================== DYNAMIC TABS ====================
    if st.session_state.role in ["Admin", "Principal"]:
        tabs = st.tabs(["📊 Dashboard", "👨‍🏫 Teachers", "🕐 Attendance", "⚠️ Attrition"])
        teacher_role = False
    else:
        tabs = st.tabs(["👤 My Profile"])
        teacher_role = True
    
    # ========== DASHBOARD TAB ==========
    if not teacher_role:
        with tabs[0]:
            st.markdown("## 📊 MS Dashboard Overview")
            st.markdown("_Real-time monitoring of school performance metrics_")
            
            perf = performance_df.copy()
            teachers = teachers_df.copy()
            
            # KPI METRICS
            col1, col2, col3, col4, col5, col6 = st.columns(6)
            
            with col1:
                st.metric("👨‍🏫 Total Teachers", len(teachers), "Staff Members")
            
            with col2:
                st.metric("👥 Total Students", len(students_df), "Enrolled")
            
            with col3:
                at_risk_count = len(teachers[teachers['Status'] == 'At Risk'])
                st.metric("⚠️ At Risk", at_risk_count, "Teachers")
            
            with col4:
                compliance = round(teachers['Compliance_Score'].mean(), 2)
                st.metric("✓ Compliance", compliance, "Out of 10")
            
            with col5:
                teaching = round(teachers['Teaching_Score_Internal'].mean(), 2)
                st.metric("📈 Teaching", teaching, "Score")
            
            with col6:
                att_rate = round((perf['Attendance'] == 'Present').sum() / len(perf) * 100, 1) if len(perf) > 0 else 0
                st.metric("📊 Attendance", f"{att_rate}%", "Present")
            
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
            filter_col1, filter_col2, filter_col3, filter_col4, filter_col5 = st.columns(5)
            
            with filter_col1:
                search = st.text_input("🔍 Search by Name or ID", placeholder="Type name...")
            
            with filter_col2:
                status_filter = st.selectbox("Filter by Status", ["All", "Active", "At Risk", "Left"])
            
            with filter_col3:
                subject_list = ["All"] + sorted(teachers_df['Subject'].unique().tolist())
                subject_filter = st.selectbox("Filter by Subject", subject_list)

            with filter_col4:
                Qualification_list = ["All"] + sorted(teachers_df['Qualification'].unique().tolist())
                Qualification_filter = st.selectbox("Filter by Qualification", Qualification_list)

            with filter_col5:
                st.write("")
                apply_btn = st.button("🔎 Apply Filters", use_container_width=True)
            
            # FILTER DATA
            filtered_teachers = teachers_df.copy()
            
            if search:
                filtered_teachers = filtered_teachers[
                    (filtered_teachers['Teacher_Name'].str.lower().str.contains(search.lower(), na=False)) |
                    (filtered_teachers['Teacher_ID'].str.lower().str.contains(search.lower(), na=False))
                ]
            
            if status_filter != "All":
                filtered_teachers = filtered_teachers[filtered_teachers['Status'] == status_filter]
            
            if subject_filter != "All":
                filtered_teachers = filtered_teachers[filtered_teachers['Subject'] == subject_filter]

            if Qualification_filter != "All":
                filtered_teachers = filtered_teachers[filtered_teachers['Qualification'] == Qualification_filter]
            
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
                    'Teacher_ID', 'Teacher_Name', 'Subject','Qualification', 'Total_Experience_Years',
                    'Teaching_Score_Internal', 'Compliance_Score', 'Status'
                ]].head(50).copy()
                
                display_df.columns = ['ID', 'Name', 'Subject','Qualification', 'Experience', 'Teaching Score', 'Compliance', 'Status']
                
                st.dataframe(display_df, use_container_width=True, height=400, hide_index=True)

                csv = filtered_teachers.to_csv(index=False).encode('utf-8')

                st.download_button(
                    label="⬇️ Download Filtered Data (CSV)",
                    data=csv,
                    file_name="filtered_teachers.csv",
                    mime="text/csv",
                    use_container_width=True)

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
            
            high_risk_teachers = t[(t['Attrition_Risk_Score'] >= 3.5) & 
                                   (t['Status'] == "At Risk")].nlargest(10, 'Attrition_Risk_Score')
            
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
    
    # ========== TEACHER PROFILE TAB (Only for Teachers) ==========
        # ========== TEACHER PROFILE TAB (Enhanced with more columns) ==========
    else:
        with tabs[0]:
            st.markdown("## 👤 My Profile")
            st.markdown("_Your personal teaching profile and performance analytics_")
            
            # Get current teacher's data using teacher_id
            current_teacher_data = teachers_df[teachers_df['Teacher_ID'] == st.session_state.teacher_id]
            
            if len(current_teacher_data) > 0:
                teacher = current_teacher_data.iloc[0]
                
                # ==================== PROFILE HEADER ====================
                profile_col1, profile_col2, profile_col3 = st.columns([1, 2, 1])
                
                with profile_col1:
                    st.markdown(f"""
                        <div style='text-align: center; padding: 20px;'>
                            <img src="{teacher['Avatar_URL']}" style='width: 150px; height: 150px; border-radius: 50%; border: 4px solid #c500ff;'>
                        </div>
                    """, unsafe_allow_html=True)
                
                with profile_col2:
                    st.markdown(f"""
                        <div style='padding: 20px;'>
                            <h2 style='color: #c500ff; margin: 0;'>{teacher['Teacher_Name']}</h2>
                            <p style='color: #00ff88; font-size: 18px; margin: 5px 0;'>📚 {teacher['Subject']}</p>
                            <p style='color: #bdc3c7; margin: 10px 0;'>🆔 ID: {teacher['Teacher_ID']}</p>
                            <p style='color: #bdc3c7; margin: 5px 0;'>📍 Status: 
                                <span style='color: #00ff88;'>{teacher['Status']}</span>
                            </p>
                            <p style='color: #bdc3c7; margin: 5px 0;'>🎓 Qualification: 
                                <span style='color: #ff9500;'>{teacher['Qualification']}</span>
                            </p>
                        </div>
                    """, unsafe_allow_html=True)
                
                with profile_col3:
                    st.markdown(f"""
                        <div style='text-align: center; padding: 20px; background: rgba(197, 0, 255, 0.1); border-radius: 10px; border: 1px solid #c500ff;'>
                            <div style='font-size: 12px; color: #bdc3c7;'>Total Experience</div>
                            <div style='font-size: 32px; color: #c500ff; font-weight: bold;'>{teacher['Total_Experience_Years']}</div>
                            <div style='font-size: 12px; color: #bdc3c7;'>Years</div>
                            <div style='margin-top: 15px; padding-top: 15px; border-top: 1px solid rgba(197, 0, 255, 0.5);'>
                                <div style='font-size: 12px; color: #bdc3c7;'>At Current School</div>
                                <div style='font-size: 24px; color: #00ff88; font-weight: bold;'>{teacher['Experience_Current_School_Years']}</div>
                                <div style='font-size: 12px; color: #bdc3c7;'>Years</div>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                
                st.divider()
                
                # ==================== KEY METRICS ====================
                st.markdown("### 📊 Performance Metrics")
                
                metric_col1, metric_col2, metric_col3, metric_col4, metric_col5 = st.columns(5)
                
                with metric_col1:
                    st.metric(
                        "📈 Internal Teaching Score",
                        f"{teacher['Teaching_Score_Internal']:.1f}",
                        "Out of 100",
                        label_visibility="collapsed"
                    )
                
                with metric_col2:
                    st.metric(
                        "📊 External Teaching Score",
                        f"{teacher['Teaching_Score_External']:.1f}",
                        "Out of 100",
                        label_visibility="collapsed"
                    )
                
                with metric_col3:
                    st.metric(
                        "✓ Compliance Score",
                        f"{teacher['Compliance_Score']:.1f}",
                        "Out of 10",
                        label_visibility="collapsed"
                    )
                
                with metric_col4:
                    st.metric(
                        "⚠️ Attrition Risk",
                        f"{teacher['Attrition_Risk_Score']:.1f}",
                        "Out of 5",
                        label_visibility="collapsed"
                    )
                
                with metric_col5:
                    st.metric(
                        "📅 Late This Month",
                        int(teacher['Late_Count_Current_Month']),
                        "Times",
                        label_visibility="collapsed"
                    )
                
                st.divider()
                
                # ==================== CLASSES & SECTIONS ====================
                st.markdown("### 📚 Assignment Information")
                
                classes_sections_col1, classes_sections_col2, classes_sections_col3 = st.columns(3)
                
                with classes_sections_col1:
                    st.markdown(f"""
                        <div style='background: rgba(0, 255, 136, 0.1); padding: 20px; border-radius: 8px; border-left: 4px solid #00ff88;'>
                            <b style='color: #00ff88;'>📖 Classes Taught</b><br>
                            <p style='color: #c500ff; font-size: 24px; margin: 8px 0; font-weight: bold;'>{teacher['Classes_Taught']}</p>
                        </div>
                    """, unsafe_allow_html=True)
                
                with classes_sections_col2:
                    st.markdown(f"""
                        <div style='background: rgba(255, 149, 0, 0.1); padding: 20px; border-radius: 8px; border-left: 4px solid #ff9500;'>
                            <b style='color: #ff9500;'>👥 Sections Taught</b><br>
                            <p style='color: #c500ff; font-size: 24px; margin: 8px 0; font-weight: bold;'>{teacher['Sections_Taught']}</p>
                        </div>
                    """, unsafe_allow_html=True)
                
                with classes_sections_col3:
                    st.markdown(f"""
                        <div style='background: rgba(197, 0, 255, 0.1); padding: 20px; border-radius: 8px; border-left: 4px solid #c500ff;'>
                            <b style='color: #c500ff;'>📋 Subject</b><br>
                            <p style='color: #00ff88; font-size: 20px; margin: 8px 0; font-weight: bold;'>{teacher['Subject']}</p>
                        </div>
                    """, unsafe_allow_html=True)
                
                st.divider()
                
                # ==================== PROFESSIONAL DEVELOPMENT ====================
                st.markdown("### 🎓 Professional Development")
                
                prof_dev_col1, prof_dev_col2, prof_dev_col3 = st.columns(3)
                
                with prof_dev_col1:
                    st.markdown(f"""
                        <div style='background: rgba(0, 255, 136, 0.1); padding: 20px; border-radius: 8px; border-left: 4px solid #00ff88;'>
                            <b style='color: #00ff88;'>📚 Training Hours</b><br>
                            <p style='color: #c500ff; font-size: 28px; margin: 8px 0; font-weight: bold;'>{teacher['Training_Hours_Completed']}</p>
                            <p style='color: #bdc3c7; font-size: 12px;'>Hours Completed</p>
                        </div>
                    """, unsafe_allow_html=True)
                
                with prof_dev_col2:
                    completion_rate = teacher['Assignment_Completion_Rate_%']
                    st.markdown(f"""
                        <div style='background: rgba(197, 0, 255, 0.1); padding: 20px; border-radius: 8px; border-left: 4px solid #c500ff;'>
                            <b style='color: #c500ff;'>✅ Assignment Completion</b><br>
                            <p style='color: #00ff88; font-size: 28px; margin: 8px 0; font-weight: bold;'>{completion_rate:.1f}%</p>
                        </div>
                    """, unsafe_allow_html=True)
                
                with prof_dev_col3:
                    st.markdown(f"""
                        <div style='background: rgba(255, 149, 0, 0.1); padding: 20px; border-radius: 8px; border-left: 4px solid #ff9500;'>
                            <b style='color: #ff9500;'>🎯 Co-Curricular</b><br>
                            <p style='color: #c500ff; font-size: 28px; margin: 8px 0; font-weight: bold;'>{teacher['Contribution_CoCurricular_%']:.1f}%</p>
                            <p style='color: #bdc3c7; font-size: 12px;'>Contribution</p>
                        </div>
                    """, unsafe_allow_html=True)
                
                st.divider()
                
                # ==================== ALIGNMENT RATINGS ====================
                st.markdown("### ⭐ Alignment & Rating Scores")
                
                alignment_col1, alignment_col2, alignment_col3 = st.columns(3)
                
                with alignment_col1:
                    head_rating = teacher['Alignment_Head_Rating']
                    peer_rating = teacher['Alignment_Peer_Rating']
                    st.markdown(f"""
                        <div style='background: rgba(0, 255, 136, 0.1); padding: 20px; border-radius: 8px;'>
                            <b style='color: #00ff88;'>👔 Head Rating</b><br>
                            <div style='font-size: 24px; color: #c500ff; margin: 8px 0; font-weight: bold;'>{head_rating}/5</div>
                            <div style='color: #bdc3c7; font-size: 12px;'>{'⭐' * int(head_rating)}</div>
                        </div>
                    """, unsafe_allow_html=True)
                
                with alignment_col2:
                    student_rating = teacher['Alignment_Student_Rating']
                    st.markdown(f"""
                        <div style='background: rgba(197, 0, 255, 0.1); padding: 20px; border-radius: 8px;'>
                            <b style='color: #c500ff;'>👨‍🎓 Student Rating</b><br>
                            <div style='font-size: 24px; color: #00ff88; margin: 8px 0; font-weight: bold;'>{student_rating}/5</div>
                            <div style='color: #bdc3c7; font-size: 12px;'>{'⭐' * int(student_rating)}</div>
                        </div>
                    """, unsafe_allow_html=True)
                
                with alignment_col3:
                    parent_rating = teacher['Alignment_Parent_Rating']
                    st.markdown(f"""
                        <div style='background: rgba(255, 149, 0, 0.1); padding: 20px; border-radius: 8px;'>
                            <b style='color: #ff9500;'>👨‍👩‍👧‍👦 Parent Rating</b><br>
                            <div style='font-size: 24px; color: #c500ff; margin: 8px 0; font-weight: bold;'>{parent_rating}/5</div>
                            <div style='color: #bdc3c7; font-size: 12px;'>{'⭐' * int(parent_rating)}</div>
                        </div>
                    """, unsafe_allow_html=True)
                
                st.divider()
                
                # ==================== PERSONAL INFORMATION ====================
                st.markdown("### 👤 Personal Information")
                
                personal_col1, personal_col2, personal_col3 = st.columns(3)
                
                with personal_col1:
                    dob = teacher.get('Date_of_Birth', 'N/A')
                    st.markdown(f"""
                        <div style='background: rgba(0, 255, 136, 0.1); padding: 15px; border-radius: 8px; border-left: 4px solid #00ff88;'>
                            <b style='color: #00ff88;'>🎂 Date of Birth</b><br>
                            <p style='color: #bdc3c7; margin: 8px 0;'>{dob}</p>
                        </div>
                    """, unsafe_allow_html=True)
                
                with personal_col2:
                    qualification = teacher['Qualification']
                    st.markdown(f"""
                        <div style='background: rgba(197, 0, 255, 0.1); padding: 15px; border-radius: 8px; border-left: 4px solid #c500ff;'>
                            <b style='color: #c500ff;'>🎓 Qualification</b><br>
                            <p style='color: #00ff88; margin: 8px 0;'>{qualification}</p>
                        </div>
                    """, unsafe_allow_html=True)
                
                with personal_col3:
                    status = teacher['Status']
                    status_color = "#00ff88" if status == "Active" else "#ff006b" if status == "At Risk" else "#ff9500"
                    st.markdown(f"""
                        <div style='background: rgba({status_color}, 0.1); padding: 15px; border-radius: 8px; border-left: 4px solid {status_color};'>
                            <b style='color: {status_color};'>📊 Current Status</b><br>
                            <p style='color: #bdc3c7; margin: 8px 0;'>{status}</p>
                        </div>
                    """, unsafe_allow_html=True)
                
                st.divider()
                
                # ==================== PERFORMANCE VISUALIZATION ====================
                st.markdown("### 📈 Performance Overview")
                
                perf_viz_col1, perf_viz_col2 = st.columns(2)
                
                with perf_viz_col1:
                    st.markdown("#### Teaching Score Comparison")
                    
                    internal_score = teacher['Teaching_Score_Internal']
                    external_score = teacher['Teaching_Score_External']
                    
                    scores_df = pd.DataFrame({
                        'Score Type': ['Internal Assessment', 'External Assessment'],
                        'Score': [internal_score, external_score]
                    })
                    
                    fig = go.Figure(data=[
                        go.Bar(
                            x=scores_df['Score Type'],
                            y=scores_df['Score'],
                            marker=dict(color=['#c500ff', '#00ff88']),
                            text=scores_df['Score'],
                            textposition='auto',
                            hovertemplate='<b>%{x}</b><br>Score: %{y:.1f}<extra></extra>'
                        )
                    ])
                    
                    fig.update_layout(
                        template='plotly_dark',
                        height=350,
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        font=dict(color='#bdc3c7', size=11),
                        margin=dict(t=20, b=20, l=20, r=20),
                        yaxis=dict(range=[0, 100])
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                with perf_viz_col2:
                    st.markdown("#### Rating Scores Summary")
                    
                    ratings_data = pd.DataFrame({
                        'Rater': ['Head', 'Peer', 'Student', 'Parent'],
                        'Rating': [
                            teacher['Alignment_Head_Rating'],
                            teacher['Alignment_Peer_Rating'],
                            teacher['Alignment_Student_Rating'],
                            teacher['Alignment_Parent_Rating']
                        ]
                    })
                    
                    fig = go.Figure(data=[
                        go.Bar(
                            x=ratings_data['Rater'],
                            y=ratings_data['Rating'],
                            marker=dict(color=['#c500ff', '#00ff88', '#ff006b', '#ff9500']),
                            text=ratings_data['Rating'],
                            textposition='auto',
                            hovertemplate='<b>%{x}</b><br>Rating: %{y:.1f}/5<extra></extra>'
                        )
                    ])
                    
                    fig.update_layout(
                        template='plotly_dark',
                        height=350,
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        font=dict(color='#bdc3c7', size=11),
                        margin=dict(t=20, b=20, l=20, r=20),
                        yaxis=dict(range=[0, 5])
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                st.divider()
                
                # ==================== RISK ASSESSMENT ====================
                st.markdown("### ⚠️ Your Risk Assessment")
                
                risk_col1, risk_col2 = st.columns(2)
                
                with risk_col1:
                    risk_score = teacher['Attrition_Risk_Score']
                    if risk_score >= 4.5:
                        risk_status = "🚨 Critical"
                        risk_color = "#c500ff"
                        risk_message = "Immediate action required. Please contact HR."
                    elif risk_score >= 3:
                        risk_status = "⚠️ High"
                        risk_color = "#ff006b"
                        risk_message = "We recommend discussing your concerns with management."
                    elif risk_score >= 1.5:
                        risk_status = "ℹ️ Medium"
                        risk_color = "#ff9500"
                        risk_message = "Monitor your performance and engagement levels."
                    else:
                        risk_status = "✅ Low"
                        risk_color = "#00ff88"
                        risk_message = "Keep up the excellent work!"
                    
                    st.markdown(f"""
                        <div style='background: rgba({risk_color}, 0.1); padding: 20px; border-radius: 8px; border: 2px solid {risk_color};'>
                            <h4 style='color: {risk_color}; margin-top: 0;'>Risk Score: {risk_score:.2f}/5</h4>
                            <p style='color: #bdc3c7;'>{risk_message}</p>
                        </div>
                    """, unsafe_allow_html=True)
                
                with risk_col2:
                    st.markdown(f"""
                        <div style='background: rgba(197, 0, 255, 0.1); padding: 20px; border-radius: 8px; border: 1px solid #c500ff;'>
                            <h4 style='color: #c500ff; margin-top: 0;'>📊 Quick Stats</h4>
                            <ul style='color: #bdc3c7; margin: 10px 0;'>
                                <li>Late Count: <b style='color: #ff9500;'>{int(teacher['Late_Count_Current_Month'])} times</b></li>
                                <li>Assignment Completion: <b style='color: #00ff88;'>{teacher['Assignment_Completion_Rate_%']:.1f}%</b></li>
                                <li>Training Hours: <b style='color: #c500ff;'>{teacher['Training_Hours_Completed']}</b></li>
                                <li>Co-Curricular Contribution: <b style='color: #ff006b;'>{teacher['Contribution_CoCurricular_%']:.1f}%</b></li>
                            </ul>
                        </div>
                    """, unsafe_allow_html=True)
                
                st.divider()
                
                # ==================== DETAILED INFORMATION TABLE ====================
                st.markdown("### 📋 Complete Profile Summary")
                
                summary_data = {
                    "Metric": [
                        "Teacher ID",
                        "Name",
                        "Subject",
                        "Qualification",
                        "Date of Birth",
                        "Current Status",
                        "Total Experience (Years)",
                        "Experience at Current School (Years)",
                        "Classes Taught",
                        "Sections Taught",
                        "Compliance Score",
                        "Internal Teaching Score",
                        "External Teaching Score",
                        "Training Hours Completed",
                        "Assignment Completion Rate",
                        "Co-Curricular Contribution",
                        "Head Rating",
                        "Peer Rating",
                        "Student Rating",
                        "Parent Rating",
                        "Late Count (Current Month)",
                        "Attrition Risk Score"
                    ],
                    "Value": [
                        teacher['Teacher_ID'],
                        teacher['Teacher_Name'],
                        teacher['Subject'],
                        teacher['Qualification'],
                        teacher['Date_of_Birth'],
                        teacher['Status'],
                        f"{teacher['Total_Experience_Years']} years",
                        f"{teacher['Experience_Current_School_Years']} years",
                        teacher['Classes_Taught'],
                        teacher['Sections_Taught'],
                        f"{teacher['Compliance_Score']:.2f}/10",
                        f"{teacher['Teaching_Score_Internal']:.2f}/100",
                        f"{teacher['Teaching_Score_External']:.2f}/100",
                        f"{teacher['Training_Hours_Completed']} hours",
                        f"{teacher['Assignment_Completion_Rate_%']:.2f}%",
                        f"{teacher['Contribution_CoCurricular_%']:.2f}%",
                        f"{teacher['Alignment_Head_Rating']:.1f}/5",
                        f"{teacher['Alignment_Peer_Rating']:.1f}/5",
                        f"{teacher['Alignment_Student_Rating']:.1f}/5",
                        f"{teacher['Alignment_Parent_Rating']:.1f}/5",
                        int(teacher['Late_Count_Current_Month']),
                        f"{teacher['Attrition_Risk_Score']:.2f}/5"
                    ]
                }
                
                summary_df = pd.DataFrame(summary_data)
                st.dataframe(summary_df, use_container_width=True, hide_index=True)
            
            else:
                st.error("❌ Unable to load your profile. Please contact administration.")
