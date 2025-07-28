# Automated Testing Week 3: Dashboard and Reporting Implementation

## Week 3 Overview: Real-Time Monitoring Dashboard

**Objective:** Create comprehensive real-time monitoring dashboard with automated reporting and alert system for DeepCoderX model behavior analysis.

**Prerequisites:** 
- Week 1 Foundation: Automated testing engine operational
- Week 2 SQLite Integration: Hybrid JSONL + SQLite storage working
- Enhanced logging system capturing model interactions

**Deliverables:**
- Real-time Streamlit dashboard with interactive visualizations
- Automated daily/weekly report generation system
- Alert system with email notifications and threshold monitoring
- Provider comparison interface with performance metrics
- Historical trend visualization and quality tracking
- Export capabilities for analysis and presentation

---

## Technical Architecture

### Dashboard Components
```
Dashboard Frontend (Streamlit)
├── Real-time Metrics Panel
├── Provider Comparison Charts  
├── Quality Trend Analysis
├── Performance Monitoring
├── Alert Management Interface
└── Report Generation Tools

Backend Services
├── Data Aggregation Engine
├── Alert Processing System
├── Report Generation Pipeline
├── Notification Service
└── Export Manager
```

### Data Flow Architecture
```
SQLite Database → Aggregation Engine → Dashboard Components
                              ↓
                      Alert System → Email Notifications
                              ↓
                      Report Generator → PDF/HTML Reports
```

---

## Implementation Phase 1: Core Dashboard Infrastructure

### 1.1 Streamlit Dashboard Foundation

**File:** `dashboard/main_dashboard.py`

```python
import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
from pathlib import Path

class DeepCoderXDashboard:
    def __init__(self):
        self.db_path = "logs/model_interactions/test_results.db"
        self.setup_page_config()
        
    def setup_page_config(self):
        st.set_page_config(
            page_title="DeepCoderX Model Analytics",
            page_icon="🤖",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
    def run(self):
        # Sidebar navigation
        st.sidebar.title("🤖 DeepCoderX Analytics")
        page = st.sidebar.selectbox(
            "Select View",
            ["Overview", "Provider Comparison", "Quality Trends", 
             "Performance Metrics", "Alert Management", "Reports"]
        )
        
        # Main content based on selection
        if page == "Overview":
            self.render_overview()
        elif page == "Provider Comparison":
            self.render_provider_comparison()
        elif page == "Quality Trends":
            self.render_quality_trends()
        elif page == "Performance Metrics":
            self.render_performance_metrics()
        elif page == "Alert Management":
            self.render_alert_management()
        elif page == "Reports":
            self.render_reports()
    
    def get_database_connection(self):
        """Get SQLite database connection with error handling"""
        try:
            conn = sqlite3.connect(self.db_path)
            return conn
        except Exception as e:
            st.error(f"Database connection failed: {e}")
            return None
    
    def render_overview(self):
        st.title("📊 DeepCoderX Model Analytics Overview")
        
        # Real-time metrics in columns
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            self.render_metric_card("Total Tests", self.get_total_tests(), "🧪")
        with col2:
            self.render_metric_card("Success Rate", f"{self.get_success_rate():.1f}%", "✅")
        with col3:
            self.render_metric_card("Avg Response Time", f"{self.get_avg_response_time():.2f}s", "⚡")
        with col4:
            self.render_metric_card("Active Alerts", self.get_active_alerts(), "🚨")
        
        # Recent activity timeline
        st.subheader("📈 Recent Activity (Last 24 Hours)")
        self.render_activity_timeline()
        
        # Provider performance comparison
        st.subheader("🔀 Provider Performance Summary")
        self.render_provider_summary()
    
    def render_metric_card(self, title, value, icon):
        st.metric(label=f"{icon} {title}", value=value)
    
    def get_total_tests(self):
        conn = self.get_database_connection()
        if not conn:
            return 0
        
        query = "SELECT COUNT(*) FROM test_results WHERE timestamp >= datetime('now', '-24 hours')"
        result = pd.read_sql_query(query, conn)
        conn.close()
        return result.iloc[0, 0]
    
    def get_success_rate(self):
        conn = self.get_database_connection()
        if not conn:
            return 0.0
        
        query = """
        SELECT 
            (COUNT(CASE WHEN success = 1 THEN 1 END) * 100.0 / COUNT(*)) as success_rate
        FROM test_results 
        WHERE timestamp >= datetime('now', '-24 hours')
        """
        result = pd.read_sql_query(query, conn)
        conn.close()
        return result.iloc[0, 0] if result.iloc[0, 0] else 0.0
    
    def get_avg_response_time(self):
        conn = self.get_database_connection()
        if not conn:
            return 0.0
        
        query = """
        SELECT AVG(response_time) as avg_time
        FROM test_results 
        WHERE timestamp >= datetime('now', '-24 hours')
        """
        result = pd.read_sql_query(query, conn)
        conn.close()
        return result.iloc[0, 0] if result.iloc[0, 0] else 0.0
    
    def get_active_alerts(self):
        # Placeholder for alert system integration
        return 0
    
    def render_activity_timeline(self):
        conn = self.get_database_connection()
        if not conn:
            st.error("Cannot load activity timeline - database unavailable")
            return
        
        query = """
        SELECT 
            datetime(timestamp) as time,
            provider,
            query_category,
            success,
            response_time
        FROM test_results 
        WHERE timestamp >= datetime('now', '-24 hours')
        ORDER BY timestamp DESC
        LIMIT 100
        """
        
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        if df.empty:
            st.info("No recent activity to display")
            return
        
        # Create timeline chart
        fig = px.scatter(
            df, 
            x='time', 
            y='response_time',
            color='provider',
            symbol='success',
            size_max=10,
            title="Response Time Timeline by Provider"
        )
        
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    def render_provider_summary(self):
        conn = self.get_database_connection()
        if not conn:
            st.error("Cannot load provider summary - database unavailable")
            return
        
        query = """
        SELECT 
            provider,
            COUNT(*) as total_tests,
            AVG(response_time) as avg_response_time,
            (COUNT(CASE WHEN success = 1 THEN 1 END) * 100.0 / COUNT(*)) as success_rate,
            AVG(quality_score) as avg_quality
        FROM test_results 
        WHERE timestamp >= datetime('now', '-7 days')
        GROUP BY provider
        ORDER BY total_tests DESC
        """
        
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        if df.empty:
            st.info("No provider data available")
            return
        
        st.dataframe(
            df.round(2),
            use_container_width=True,
            hide_index=True
        )

if __name__ == "__main__":
    dashboard = DeepCoderXDashboard()
    dashboard.run()
```

### 1.2 Provider Comparison Interface

**Enhancement to dashboard:** `render_provider_comparison()` method

```python
def render_provider_comparison(self):
    st.title("🔀 Provider Performance Comparison")
    
    # Time range selector
    time_range = st.selectbox(
        "Select Time Range",
        ["Last 24 Hours", "Last 7 Days", "Last 30 Days", "All Time"]
    )
    
    time_filter = self.get_time_filter(time_range)
    
    # Provider metrics comparison
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Response Time Comparison")
        self.render_response_time_comparison(time_filter)
    
    with col2:
        st.subheader("✅ Success Rate Comparison")
        self.render_success_rate_comparison(time_filter)
    
    # Quality metrics by category
    st.subheader("🎯 Quality Scores by Query Category")
    self.render_quality_by_category(time_filter)
    
    # Detailed provider analysis table
    st.subheader("📋 Detailed Provider Analysis")
    self.render_detailed_provider_table(time_filter)

def get_time_filter(self, time_range):
    """Convert time range selection to SQL filter"""
    filters = {
        "Last 24 Hours": "datetime('now', '-24 hours')",
        "Last 7 Days": "datetime('now', '-7 days')",
        "Last 30 Days": "datetime('now', '-30 days')",
        "All Time": "datetime('1970-01-01')"
    }
    return filters.get(time_range, filters["Last 7 Days"])

def render_response_time_comparison(self, time_filter):
    conn = self.get_database_connection()
    if not conn:
        return
    
    query = f"""
    SELECT 
        provider,
        AVG(response_time) as avg_response_time,
        MIN(response_time) as min_response_time,
        MAX(response_time) as max_response_time
    FROM test_results 
    WHERE timestamp >= {time_filter}
    GROUP BY provider
    """
    
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    if not df.empty:
        fig = px.bar(
            df, 
            x='provider', 
            y='avg_response_time',
            title="Average Response Time by Provider"
        )
        st.plotly_chart(fig, use_container_width=True)

def render_success_rate_comparison(self, time_filter):
    conn = self.get_database_connection()
    if not conn:
        return
    
    query = f"""
    SELECT 
        provider,
        (COUNT(CASE WHEN success = 1 THEN 1 END) * 100.0 / COUNT(*)) as success_rate
    FROM test_results 
    WHERE timestamp >= {time_filter}
    GROUP BY provider
    """
    
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    if not df.empty:
        fig = px.pie(
            df, 
            values='success_rate', 
            names='provider',
            title="Success Rate Distribution"
        )
        st.plotly_chart(fig, use_container_width=True)
```

---

## Implementation Phase 2: Alert System

### 2.1 Alert Configuration and Management

**File:** `dashboard/alert_system.py`

```python
import sqlite3
import smtplib
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import List, Dict, Optional
import logging

@dataclass
class AlertRule:
    id: str
    name: str
    condition: str
    threshold: float
    severity: str  # 'low', 'medium', 'high', 'critical'
    enabled: bool
    notification_channels: List[str]
    cooldown_minutes: int

@dataclass
class Alert:
    id: str
    rule_id: str
    message: str
    severity: str
    timestamp: datetime
    acknowledged: bool
    resolved: bool

class AlertSystem:
    def __init__(self, db_path: str, config_path: str):
        self.db_path = db_path
        self.config_path = config_path
        self.rules = self.load_alert_rules()
        self.setup_logging()
    
    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('logs/alert_system.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def load_alert_rules(self) -> List[AlertRule]:
        """Load alert rules from configuration file"""
        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)
            
            rules = []
            for rule_data in config.get('alert_rules', []):
                rule = AlertRule(**rule_data)
                rules.append(rule)
            
            return rules
        except Exception as e:
            self.logger.error(f"Failed to load alert rules: {e}")
            return self.get_default_alert_rules()
    
    def get_default_alert_rules(self) -> List[AlertRule]:
        """Default alert rules for system monitoring"""
        return [
            AlertRule(
                id="high_failure_rate",
                name="High Failure Rate",
                condition="success_rate < threshold",
                threshold=80.0,
                severity="high",
                enabled=True,
                notification_channels=["email"],
                cooldown_minutes=30
            ),
            AlertRule(
                id="slow_response_time",
                name="Slow Response Time",
                condition="avg_response_time > threshold",
                threshold=10.0,
                severity="medium",
                enabled=True,
                notification_channels=["email"],
                cooldown_minutes=15
            ),
            AlertRule(
                id="model_hallucination",
                name="Model Hallucination Detected",
                condition="hallucination_score > threshold",
                threshold=0.5,
                severity="critical",
                enabled=True,
                notification_channels=["email"],
                cooldown_minutes=5
            ),
            AlertRule(
                id="provider_unavailable",
                name="Provider Unavailable",
                condition="provider_success_rate < threshold",
                threshold=10.0,
                severity="critical",
                enabled=True,
                notification_channels=["email"],
                cooldown_minutes=60
            )
        ]
    
    def check_alerts(self):
        """Check all enabled alert rules against current data"""
        for rule in self.rules:
            if not rule.enabled:
                continue
            
            try:
                if self.evaluate_alert_condition(rule):
                    self.trigger_alert(rule)
            except Exception as e:
                self.logger.error(f"Error checking alert rule {rule.id}: {e}")
    
    def evaluate_alert_condition(self, rule: AlertRule) -> bool:
        """Evaluate if alert condition is met"""
        conn = sqlite3.connect(self.db_path)
        
        # Check if alert is in cooldown
        if self.is_in_cooldown(rule):
            return False
        
        try:
            if rule.id == "high_failure_rate":
                return self.check_failure_rate(conn, rule.threshold)
            elif rule.id == "slow_response_time":
                return self.check_response_time(conn, rule.threshold)
            elif rule.id == "model_hallucination":
                return self.check_hallucination_rate(conn, rule.threshold)
            elif rule.id == "provider_unavailable":
                return self.check_provider_availability(conn, rule.threshold)
            else:
                return False
        finally:
            conn.close()
    
    def check_failure_rate(self, conn, threshold: float) -> bool:
        """Check if overall failure rate exceeds threshold"""
        query = """
        SELECT 
            (COUNT(CASE WHEN success = 1 THEN 1 END) * 100.0 / COUNT(*)) as success_rate
        FROM test_results 
        WHERE timestamp >= datetime('now', '-1 hour')
        """
        
        cursor = conn.execute(query)
        result = cursor.fetchone()
        
        if result and result[0] is not None:
            success_rate = result[0]
            return success_rate < threshold
        
        return False
    
    def check_response_time(self, conn, threshold: float) -> bool:
        """Check if average response time exceeds threshold"""
        query = """
        SELECT AVG(response_time) as avg_time
        FROM test_results 
        WHERE timestamp >= datetime('now', '-30 minutes')
        """
        
        cursor = conn.execute(query)
        result = cursor.fetchone()
        
        if result and result[0] is not None:
            avg_time = result[0]
            return avg_time > threshold
        
        return False
    
    def check_hallucination_rate(self, conn, threshold: float) -> bool:
        """Check if hallucination rate exceeds threshold"""
        query = """
        SELECT AVG(hallucination_score) as avg_hallucination
        FROM test_results 
        WHERE timestamp >= datetime('now', '-1 hour')
        AND hallucination_score IS NOT NULL
        """
        
        cursor = conn.execute(query)
        result = cursor.fetchone()
        
        if result and result[0] is not None:
            avg_hallucination = result[0]
            return avg_hallucination > threshold
        
        return False
    
    def check_provider_availability(self, conn, threshold: float) -> bool:
        """Check if any provider success rate is below threshold"""
        query = """
        SELECT 
            provider,
            (COUNT(CASE WHEN success = 1 THEN 1 END) * 100.0 / COUNT(*)) as success_rate
        FROM test_results 
        WHERE timestamp >= datetime('now', '-30 minutes')
        GROUP BY provider
        """
        
        cursor = conn.execute(query)
        results = cursor.fetchall()
        
        for provider, success_rate in results:
            if success_rate < threshold:
                return True
        
        return False
    
    def is_in_cooldown(self, rule: AlertRule) -> bool:
        """Check if alert rule is in cooldown period"""
        conn = sqlite3.connect(self.db_path)
        
        query = """
        SELECT timestamp FROM alerts 
        WHERE rule_id = ? 
        ORDER BY timestamp DESC 
        LIMIT 1
        """
        
        cursor = conn.execute(query, (rule.id,))
        result = cursor.fetchone()
        conn.close()
        
        if not result:
            return False
        
        last_alert_time = datetime.fromisoformat(result[0])
        cooldown_end = last_alert_time + timedelta(minutes=rule.cooldown_minutes)
        
        return datetime.now() < cooldown_end
    
    def trigger_alert(self, rule: AlertRule):
        """Trigger alert and send notifications"""
        alert_id = f"{rule.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        alert = Alert(
            id=alert_id,
            rule_id=rule.id,
            message=f"Alert: {rule.name} - Threshold {rule.threshold} exceeded",
            severity=rule.severity,
            timestamp=datetime.now(),
            acknowledged=False,
            resolved=False
        )
        
        # Store alert in database
        self.store_alert(alert)
        
        # Send notifications
        for channel in rule.notification_channels:
            self.send_notification(alert, channel)
        
        self.logger.warning(f"Alert triggered: {alert.message}")
    
    def store_alert(self, alert: Alert):
        """Store alert in database"""
        conn = sqlite3.connect(self.db_path)
        
        query = """
        INSERT INTO alerts (id, rule_id, message, severity, timestamp, acknowledged, resolved)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        
        conn.execute(query, (
            alert.id, alert.rule_id, alert.message, alert.severity,
            alert.timestamp.isoformat(), alert.acknowledged, alert.resolved
        ))
        conn.commit()
        conn.close()
    
    def send_notification(self, alert: Alert, channel: str):
        """Send alert notification via specified channel"""
        if channel == "email":
            self.send_email_notification(alert)
        elif channel == "webhook":
            self.send_webhook_notification(alert)
        # Add other notification channels as needed
    
    def send_email_notification(self, alert: Alert):
        """Send email notification for alert"""
        try:
            # Email configuration (should be in config file)
            smtp_server = "smtp.gmail.com"
            smtp_port = 587
            email_user = "your-email@gmail.com"
            email_password = "your-app-password"
            recipient = "admin@yourcompany.com"
            
            msg = MIMEMultipart()
            msg['From'] = email_user
            msg['To'] = recipient
            msg['Subject'] = f"DeepCoderX Alert: {alert.severity.upper()}"
            
            body = f"""
            Alert Details:
            - ID: {alert.id}
            - Message: {alert.message}
            - Severity: {alert.severity}
            - Timestamp: {alert.timestamp}
            
            Please check the DeepCoderX dashboard for more details.
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(email_user, email_password)
            text = msg.as_string()
            server.sendmail(email_user, recipient, text)
            server.quit()
            
            self.logger.info(f"Email notification sent for alert {alert.id}")
            
        except Exception as e:
            self.logger.error(f"Failed to send email notification: {e}")
```

### 2.2 Alert Configuration File

**File:** `config/alert_config.json`

```json
{
    "alert_rules": [
        {
            "id": "high_failure_rate",
            "name": "High Failure Rate",
            "condition": "success_rate < threshold",
            "threshold": 80.0,
            "severity": "high",
            "enabled": true,
            "notification_channels": ["email"],
            "cooldown_minutes": 30
        },
        {
            "id": "slow_response_time",
            "name": "Slow Response Time",
            "condition": "avg_response_time > threshold",
            "threshold": 10.0,
            "severity": "medium",
            "enabled": true,
            "notification_channels": ["email"],
            "cooldown_minutes": 15
        },
        {
            "id": "model_hallucination",
            "name": "Model Hallucination Detected",
            "condition": "hallucination_score > threshold",
            "threshold": 0.5,
            "severity": "critical",
            "enabled": true,
            "notification_channels": ["email"],
            "cooldown_minutes": 5
        },
        {
            "id": "provider_unavailable",
            "name": "Provider Unavailable",
            "condition": "provider_success_rate < threshold",
            "threshold": 10.0,
            "severity": "critical",
            "enabled": true,
            "notification_channels": ["email"],
            "cooldown_minutes": 60
        },
        {
            "id": "quality_degradation",
            "name": "Quality Score Degradation",
            "condition": "avg_quality_score < threshold",
            "threshold": 0.7,
            "severity": "medium",
            "enabled": true,
            "notification_channels": ["email"],
            "cooldown_minutes": 45
        }
    ],
    "notification_settings": {
        "email": {
            "smtp_server": "smtp.gmail.com",
            "smtp_port": 587,
            "username": "your-email@gmail.com",
            "password": "your-app-password",
            "recipients": ["admin@yourcompany.com", "dev@yourcompany.com"]
        },
        "webhook": {
            "url": "https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK",
            "enabled": false
        }
    },
    "alert_retention_days": 30
}
```

---

## Implementation Phase 3: Automated Report Generation

### 3.1 Report Generation Engine

**File:** `dashboard/report_generator.py`

```python
import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import seaborn as sns
from jinja2 import Template
import pdfkit
from pathlib import Path
import json
import logging

class ReportGenerator:
    def __init__(self, db_path: str, output_dir: str = "reports"):
        self.db_path = db_path
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.setup_logging()
    
    def setup_logging(self):
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def generate_daily_report(self, date: datetime = None):
        """Generate comprehensive daily report"""
        if date is None:
            date = datetime.now() - timedelta(days=1)
        
        report_data = self.collect_daily_data(date)
        
        # Generate HTML report
        html_report = self.create_html_report(report_data, "daily")
        html_file = self.output_dir / f"daily_report_{date.strftime('%Y%m%d')}.html"
        
        with open(html_file, 'w') as f:
            f.write(html_report)
        
        # Generate PDF report
        pdf_file = self.output_dir / f"daily_report_{date.strftime('%Y%m%d')}.pdf"
        self.convert_html_to_pdf(html_file, pdf_file)
        
        self.logger.info(f"Daily report generated: {pdf_file}")
        return pdf_file
    
    def generate_weekly_report(self, week_start: datetime = None):
        """Generate comprehensive weekly report"""
        if week_start is None:
            week_start = datetime.now() - timedelta(days=7)
        
        report_data = self.collect_weekly_data(week_start)
        
        # Generate HTML report
        html_report = self.create_html_report(report_data, "weekly")
        html_file = self.output_dir / f"weekly_report_{week_start.strftime('%Y%m%d')}.html"
        
        with open(html_file, 'w') as f:
            f.write(html_report)
        
        # Generate PDF report
        pdf_file = self.output_dir / f"weekly_report_{week_start.strftime('%Y%m%d')}.pdf"
        self.convert_html_to_pdf(html_file, pdf_file)
        
        self.logger.info(f"Weekly report generated: {pdf_file}")
        return pdf_file
    
    def collect_daily_data(self, date: datetime) -> dict:
        """Collect all data needed for daily report"""
        conn = sqlite3.connect(self.db_path)
        
        start_date = date.strftime('%Y-%m-%d 00:00:00')
        end_date = date.strftime('%Y-%m-%d 23:59:59')
        
        # Overall metrics
        overall_query = f"""
        SELECT 
            COUNT(*) as total_tests,
            AVG(response_time) as avg_response_time,
            (COUNT(CASE WHEN success = 1 THEN 1 END) * 100.0 / COUNT(*)) as success_rate,
            AVG(quality_score) as avg_quality_score,
            AVG(hallucination_score) as avg_hallucination_score
        FROM test_results 
        WHERE timestamp BETWEEN '{start_date}' AND '{end_date}'
        """
        
        overall_df = pd.read_sql_query(overall_query, conn)
        
        # Provider breakdown
        provider_query = f"""
        SELECT 
            provider,
            COUNT(*) as total_tests,
            AVG(response_time) as avg_response_time,
            (COUNT(CASE WHEN success = 1 THEN 1 END) * 100.0 / COUNT(*)) as success_rate,
            AVG(quality_score) as avg_quality_score
        FROM test_results 
        WHERE timestamp BETWEEN '{start_date}' AND '{end_date}'
        GROUP BY provider
        """
        
        provider_df = pd.read_sql_query(provider_query, conn)
        
        # Category analysis
        category_query = f"""
        SELECT 
            query_category,
            COUNT(*) as total_tests,
            AVG(response_time) as avg_response_time,
            (COUNT(CASE WHEN success = 1 THEN 1 END) * 100.0 / COUNT(*)) as success_rate,
            AVG(quality_score) as avg_quality_score
        FROM test_results 
        WHERE timestamp BETWEEN '{start_date}' AND '{end_date}'
        GROUP BY query_category
        """
        
        category_df = pd.read_sql_query(category_query, conn)
        
        # Hourly trends
        hourly_query = f"""
        SELECT 
            strftime('%H', timestamp) as hour,
            COUNT(*) as test_count,
            AVG(response_time) as avg_response_time,
            (COUNT(CASE WHEN success = 1 THEN 1 END) * 100.0 / COUNT(*)) as success_rate
        FROM test_results 
        WHERE timestamp BETWEEN '{start_date}' AND '{end_date}'
        GROUP BY hour
        ORDER BY hour
        """
        
        hourly_df = pd.read_sql_query(hourly_query, conn)
        
        # Error analysis
        error_query = f"""
        SELECT 
            error_message,
            COUNT(*) as error_count
        FROM test_results 
        WHERE timestamp BETWEEN '{start_date}' AND '{end_date}'
        AND success = 0
        AND error_message IS NOT NULL
        GROUP BY error_message
        ORDER BY error_count DESC
        LIMIT 10
        """
        
        error_df = pd.read_sql_query(error_query, conn)
        
        conn.close()
        
        return {
            'date': date,
            'overall': overall_df.to_dict('records')[0] if not overall_df.empty else {},
            'providers': provider_df.to_dict('records'),
            'categories': category_df.to_dict('records'),
            'hourly_trends': hourly_df.to_dict('records'),
            'errors': error_df.to_dict('records')
        }
    
    def collect_weekly_data(self, week_start: datetime) -> dict:
        """Collect all data needed for weekly report"""
        conn = sqlite3.connect(self.db_path)
        
        week_end = week_start + timedelta(days=7)
        start_date = week_start.strftime('%Y-%m-%d 00:00:00')
        end_date = week_end.strftime('%Y-%m-%d 23:59:59')
        
        # Weekly trends
        daily_query = f"""
        SELECT 
            DATE(timestamp) as date,
            COUNT(*) as total_tests,
            AVG(response_time) as avg_response_time,
            (COUNT(CASE WHEN success = 1 THEN 1 END) * 100.0 / COUNT(*)) as success_rate,
            AVG(quality_score) as avg_quality_score
        FROM test_results 
        WHERE timestamp BETWEEN '{start_date}' AND '{end_date}'
        GROUP BY DATE(timestamp)
        ORDER BY date
        """
        
        daily_df = pd.read_sql_query(daily_query, conn)
        
        # Provider comparison over week
        provider_weekly_query = f"""
        SELECT 
            provider,
            DATE(timestamp) as date,
            COUNT(*) as total_tests,
            AVG(response_time) as avg_response_time,
            (COUNT(CASE WHEN success = 1 THEN 1 END) * 100.0 / COUNT(*)) as success_rate
        FROM test_results 
        WHERE timestamp BETWEEN '{start_date}' AND '{end_date}'
        GROUP BY provider, DATE(timestamp)
        ORDER BY date, provider
        """
        
        provider_weekly_df = pd.read_sql_query(provider_weekly_query, conn)
        
        conn.close()
        
        # Calculate week-over-week changes
        previous_week_start = week_start - timedelta(days=7)
        previous_week_data = self.get_weekly_comparison_data(previous_week_start)
        
        return {
            'week_start': week_start,
            'week_end': week_end,
            'daily_trends': daily_df.to_dict('records'),
            'provider_weekly': provider_weekly_df.to_dict('records'),
            'previous_week_comparison': previous_week_data
        }
    
    def get_weekly_comparison_data(self, week_start: datetime) -> dict:
        """Get comparison data for previous week"""
        conn = sqlite3.connect(self.db_path)
        
        week_end = week_start + timedelta(days=7)
        start_date = week_start.strftime('%Y-%m-%d 00:00:00')
        end_date = week_end.strftime('%Y-%m-%d 23:59:59')
        
        query = f"""
        SELECT 
            COUNT(*) as total_tests,
            AVG(response_time) as avg_response_time,
            (COUNT(CASE WHEN success = 1 THEN 1 END) * 100.0 / COUNT(*)) as success_rate,
            AVG(quality_score) as avg_quality_score
        FROM test_results 
        WHERE timestamp BETWEEN '{start_date}' AND '{end_date}'
        """
        
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        return df.to_dict('records')[0] if not df.empty else {}
    
    def create_html_report(self, data: dict, report_type: str) -> str:
        """Create HTML report from data"""
        if report_type == "daily":
            template_str = self.get_daily_report_template()
        else:
            template_str = self.get_weekly_report_template()
        
        template = Template(template_str)
        return template.render(**data)
    
    def get_daily_report_template(self) -> str:
        """HTML template for daily report"""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>DeepCoderX Daily Report - {{ date.strftime('%Y-%m-%d') }}</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; }
                .header { background-color: #f8f9fa; padding: 20px; border-radius: 8px; }
                .metric-card { 
                    background-color: #e9ecef; 
                    padding: 15px; 
                    margin: 10px 0; 
                    border-radius: 5px; 
                }
                .table { width: 100%; border-collapse: collapse; margin: 20px 0; }
                .table th, .table td { 
                    border: 1px solid #dee2e6; 
                    padding: 12px; 
                    text-align: left; 
                }
                .table th { background-color: #e9ecef; }
                .success { color: #28a745; }
                .warning { color: #ffc107; }
                .danger { color: #dc3545; }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🤖 DeepCoderX Daily Report</h1>
                <h2>{{ date.strftime('%A, %B %d, %Y') }}</h2>
            </div>
            
            <h3>📊 Overall Performance</h3>
            <div class="metric-card">
                <strong>Total Tests:</strong> {{ overall.total_tests or 0 }}<br>
                <strong>Success Rate:</strong> 
                <span class="{% if overall.success_rate >= 90 %}success{% elif overall.success_rate >= 70 %}warning{% else %}danger{% endif %}">
                    {{ "%.1f"|format(overall.success_rate or 0) }}%
                </span><br>
                <strong>Average Response Time:</strong> {{ "%.2f"|format(overall.avg_response_time or 0) }}s<br>
                <strong>Average Quality Score:</strong> {{ "%.2f"|format(overall.avg_quality_score or 0) }}<br>
            </div>
            
            <h3>🔀 Provider Performance</h3>
            <table class="table">
                <thead>
                    <tr>
                        <th>Provider</th>
                        <th>Tests</th>
                        <th>Success Rate</th>
                        <th>Avg Response Time</th>
                        <th>Quality Score</th>
                    </tr>
                </thead>
                <tbody>
                    {% for provider in providers %}
                    <tr>
                        <td>{{ provider.provider }}</td>
                        <td>{{ provider.total_tests }}</td>
                        <td>{{ "%.1f"|format(provider.success_rate) }}%</td>
                        <td>{{ "%.2f"|format(provider.avg_response_time) }}s</td>
                        <td>{{ "%.2f"|format(provider.avg_quality_score) }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
            
            <h3>📋 Query Category Analysis</h3>
            <table class="table">
                <thead>
                    <tr>
                        <th>Category</th>
                        <th>Tests</th>
                        <th>Success Rate</th>
                        <th>Avg Response Time</th>
                        <th>Quality Score</th>
                    </tr>
                </thead>
                <tbody>
                    {% for category in categories %}
                    <tr>
                        <td>{{ category.query_category }}</td>
                        <td>{{ category.total_tests }}</td>
                        <td>{{ "%.1f"|format(category.success_rate) }}%</td>
                        <td>{{ "%.2f"|format(category.avg_response_time) }}s</td>
                        <td>{{ "%.2f"|format(category.avg_quality_score) }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
            
            {% if errors %}
            <h3>⚠️ Error Analysis</h3>
            <table class="table">
                <thead>
                    <tr>
                        <th>Error Message</th>
                        <th>Count</th>
                    </tr>
                </thead>
                <tbody>
                    {% for error in errors %}
                    <tr>
                        <td>{{ error.error_message }}</td>
                        <td>{{ error.error_count }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
            {% endif %}
            
            <div style="margin-top: 40px; text-align: center; color: #6c757d;">
                <small>Generated on {{ datetime.now().strftime('%Y-%m-%d %H:%M:%S') }}</small>
            </div>
        </body>
        </html>
        """
    
    def get_weekly_report_template(self) -> str:
        """HTML template for weekly report"""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>DeepCoderX Weekly Report - {{ week_start.strftime('%Y-%m-%d') }}</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; }
                .header { background-color: #f8f9fa; padding: 20px; border-radius: 8px; }
                .metric-card { 
                    background-color: #e9ecef; 
                    padding: 15px; 
                    margin: 10px 0; 
                    border-radius: 5px; 
                }
                .table { width: 100%; border-collapse: collapse; margin: 20px 0; }
                .table th, .table td { 
                    border: 1px solid #dee2e6; 
                    padding: 12px; 
                    text-align: left; 
                }
                .table th { background-color: #e9ecef; }
                .trend-up { color: #28a745; }
                .trend-down { color: #dc3545; }
                .trend-same { color: #6c757d; }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🤖 DeepCoderX Weekly Report</h1>
                <h2>{{ week_start.strftime('%B %d') }} - {{ week_end.strftime('%B %d, %Y') }}</h2>
            </div>
            
            <h3>📈 Daily Trends</h3>
            <table class="table">
                <thead>
                    <tr>
                        <th>Date</th>
                        <th>Tests</th>
                        <th>Success Rate</th>
                        <th>Avg Response Time</th>
                        <th>Quality Score</th>
                    </tr>
                </thead>
                <tbody>
                    {% for day in daily_trends %}
                    <tr>
                        <td>{{ day.date }}</td>
                        <td>{{ day.total_tests }}</td>
                        <td>{{ "%.1f"|format(day.success_rate) }}%</td>
                        <td>{{ "%.2f"|format(day.avg_response_time) }}s</td>
                        <td>{{ "%.2f"|format(day.avg_quality_score) }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
            
            <div style="margin-top: 40px; text-align: center; color: #6c757d;">
                <small>Generated on {{ datetime.now().strftime('%Y-%m-%d %H:%M:%S') }}</small>
            </div>
        </body>
        </html>
        """
    
    def convert_html_to_pdf(self, html_file: Path, pdf_file: Path):
        """Convert HTML report to PDF"""
        try:
            options = {
                'page-size': 'A4',
                'margin-top': '0.75in',
                'margin-right': '0.75in',
                'margin-bottom': '0.75in',
                'margin-left': '0.75in',
                'encoding': "UTF-8",
                'no-outline': None
            }
            
            pdfkit.from_file(str(html_file), str(pdf_file), options=options)
            
        except Exception as e:
            self.logger.error(f"Failed to convert HTML to PDF: {e}")
```

---

## Implementation Phase 4: Deployment and Configuration

### 4.1 Dashboard Launcher Script

**File:** `launch_dashboard.py`

```python
#!/usr/bin/env python3
"""
DeepCoderX Dashboard Launcher
Starts the complete monitoring dashboard with all components
"""

import subprocess
import sys
import time
import threading
from pathlib import Path
import logging

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__)

def check_dependencies():
    """Check if all required dependencies are installed"""
    required_packages = [
        'streamlit',
        'plotly',
        'pandas',
        'sqlite3',
        'jinja2',
        'pdfkit'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"Missing required packages: {missing_packages}")
        print("Install with: pip install " + " ".join(missing_packages))
        return False
    
    return True

def start_alert_system():
    """Start the alert monitoring system"""
    logger = setup_logging()
    
    try:
        from dashboard.alert_system import AlertSystem
        
        alert_system = AlertSystem(
            db_path="logs/model_interactions/test_results.db",
            config_path="config/alert_config.json"
        )
        
        logger.info("Starting alert monitoring system...")
        
        while True:
            alert_system.check_alerts()
            time.sleep(60)  # Check every minute
            
    except Exception as e:
        logger.error(f"Alert system error: {e}")

def start_dashboard():
    """Start the Streamlit dashboard"""
    logger = setup_logging()
    
    try:
        logger.info("Starting Streamlit dashboard...")
        
        # Start Streamlit dashboard
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            "dashboard/main_dashboard.py",
            "--server.port", "8501",
            "--server.address", "localhost"
        ])
        
    except Exception as e:
        logger.error(f"Dashboard startup error: {e}")

def main():
    logger = setup_logging()
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Create necessary directories
    Path("logs/model_interactions").mkdir(parents=True, exist_ok=True)
    Path("reports").mkdir(exist_ok=True)
    Path("config").mkdir(exist_ok=True)
    
    logger.info("🚀 Starting DeepCoderX Dashboard...")
    
    # Start alert system in background thread
    alert_thread = threading.Thread(target=start_alert_system, daemon=True)
    alert_thread.start()
    
    # Start dashboard (blocking)
    start_dashboard()

if __name__ == "__main__":
    main()
```

### 4.2 Installation and Setup Script

**File:** `setup_dashboard.py`

```python
#!/usr/bin/env python3
"""
DeepCoderX Dashboard Setup Script
Installs dependencies and configures the monitoring dashboard
"""

import subprocess
import sys
import json
from pathlib import Path

def install_dependencies():
    """Install required Python packages"""
    packages = [
        "streamlit>=1.28.0",
        "plotly>=5.17.0", 
        "pandas>=2.0.0",
        "jinja2>=3.1.0",
        "pdfkit>=1.0.0",
        "smtplib-ssl"
    ]
    
    print("📦 Installing dashboard dependencies...")
    
    for package in packages:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"✅ Installed {package}")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install {package}: {e}")
            return False
    
    return True

def create_directory_structure():
    """Create necessary directory structure"""
    directories = [
        "dashboard",
        "reports", 
        "config",
        "logs/model_interactions"
    ]
    
    print("📁 Creating directory structure...")
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ Created {directory}/")

def create_default_config():
    """Create default configuration files"""
    
    # Alert configuration
    alert_config = {
        "alert_rules": [
            {
                "id": "high_failure_rate",
                "name": "High Failure Rate",
                "condition": "success_rate < threshold",
                "threshold": 80.0,
                "severity": "high",
                "enabled": True,
                "notification_channels": ["email"],
                "cooldown_minutes": 30
            },
            {
                "id": "slow_response_time", 
                "name": "Slow Response Time",
                "condition": "avg_response_time > threshold",
                "threshold": 10.0,
                "severity": "medium",
                "enabled": True,
                "notification_channels": ["email"],
                "cooldown_minutes": 15
            }
        ],
        "notification_settings": {
            "email": {
                "smtp_server": "smtp.gmail.com",
                "smtp_port": 587,
                "username": "your-email@gmail.com",
                "password": "your-app-password",
                "recipients": ["admin@yourcompany.com"]
            }
        },
        "alert_retention_days": 30
    }
    
    config_file = Path("config/alert_config.json")
    with open(config_file, 'w') as f:
        json.dump(alert_config, f, indent=2)
    
    print(f"✅ Created {config_file}")

def setup_database_schema():
    """Set up database schema for alerts"""
    import sqlite3
    
    db_path = "logs/model_interactions/test_results.db"
    conn = sqlite3.connect(db_path)
    
    # Create alerts table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS alerts (
            id TEXT PRIMARY KEY,
            rule_id TEXT NOT NULL,
            message TEXT NOT NULL,
            severity TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            acknowledged BOOLEAN DEFAULT FALSE,
            resolved BOOLEAN DEFAULT FALSE
        )
    """)
    
    conn.commit()
    conn.close()
    
    print("✅ Database schema configured")

def main():
    print("🚀 Setting up DeepCoderX Dashboard...")
    
    # Install dependencies
    if not install_dependencies():
        print("❌ Failed to install dependencies")
        sys.exit(1)
    
    # Create directories
    create_directory_structure()
    
    # Create configuration
    create_default_config()
    
    # Setup database
    setup_database_schema()
    
    print("\n🎉 Dashboard setup complete!")
    print("\nNext steps:")
    print("1. Update config/alert_config.json with your email settings")
    print("2. Run: python3 launch_dashboard.py")
    print("3. Open browser to: http://localhost:8501")

if __name__ == "__main__":
    main()
```

---

## Usage Instructions

### 1. Initial Setup
```bash
# Install dashboard components
python3 setup_dashboard.py

# Configure email alerts (optional)
nano config/alert_config.json
```

### 2. Launch Dashboard
```bash
# Start complete monitoring system
python3 launch_dashboard.py

# Dashboard will be available at: http://localhost:8501
```

### 3. Generate Reports
```bash
# Generate daily report
python3 -c "
from dashboard.report_generator import ReportGenerator
rg = ReportGenerator('logs/model_interactions/test_results.db')
rg.generate_daily_report()
"

# Generate weekly report  
python3 -c "
from dashboard.report_generator import ReportGenerator
rg = ReportGenerator('logs/model_interactions/test_results.db')
rg.generate_weekly_report()
"
```

### 4. Alert Management
```bash
# Test alert system
python3 -c "
from dashboard.alert_system import AlertSystem
alert_system = AlertSystem(
    'logs/model_interactions/test_results.db',
    'config/alert_config.json'
)
alert_system.check_alerts()
"
```

---

## Expected Outcomes

### Dashboard Features
✅ **Real-time Monitoring:** Live metrics and performance tracking  
✅ **Provider Comparison:** Side-by-side performance analysis  
✅ **Quality Trends:** Historical quality score tracking  
✅ **Interactive Visualizations:** Plotly-powered charts and graphs  
✅ **Export Capabilities:** PDF and HTML report generation  

### Alert System  
✅ **Proactive Monitoring:** Automatic threshold-based alerting  
✅ **Email Notifications:** Instant alert delivery via email  
✅ **Cooldown Management:** Prevents alert spam with smart timing  
✅ **Multiple Severity Levels:** Critical, high, medium, low priorities  
✅ **Configurable Rules:** Customizable alert conditions and thresholds  

### Report Generation
✅ **Automated Reports:** Daily and weekly report generation  
✅ **Comprehensive Analysis:** Performance, quality, and error analysis  
✅ **Professional Formatting:** HTML and PDF output with charts  
✅ **Historical Tracking:** Week-over-week and trend analysis  
✅ **Executive Summary:** High-level metrics for stakeholders  

## Integration Status

**Week 1 + 2 Dependencies:** Requires completed automated testing engine and SQLite integration  
**Configuration:** Uses existing enhanced logging infrastructure and API automation  
**Deployment:** Streamlit-based for easy deployment and accessibility  
**Scalability:** Designed for production use with proper error handling and monitoring  

---

## Week 3 Status: IMPLEMENTATION READY

The Week 3 Dashboard and Reporting implementation plan provides comprehensive real-time monitoring capabilities with automated alerting and professional report generation. All components are designed to integrate seamlessly with the existing DeepCoderX infrastructure and provide immediate value for model behavior monitoring and analysis.

**Next Priority:** Begin Week 3 implementation following this detailed plan, or proceed to Week 4 Advanced Analytics planning.