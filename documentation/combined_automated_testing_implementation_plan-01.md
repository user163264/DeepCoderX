{
  `path`: `/Users/admin/Documents/DeepCoderX/documentation/combined_automated_testing_implementation_plan.md`,
  `edits`: [
    {
      `newText`: `        # Get baseline performance
        cursor.execute(\"\"\"
            SELECT provider, query_category, AVG(execution_time_ms) as avg_time, COUNT(*) as count
            FROM test_results
            WHERE timestamp BETWEEN date('now', '-{} days') AND date('now', '-{} days')
            AND success = true
            GROUP BY provider, query_category
            HAVING count >= 5
        \"\"\".format(comparison_days + baseline_days, comparison_days))
        
        baseline_performance = {(row[0], row[1]): (row[2], row[3]) for row in cursor.fetchall()}
        conn.close()
        
        # Detect regressions
        regressions = []
        for (provider, category), (recent_time, recent_count) in recent_performance.items():
            if (provider, category) in baseline_performance:
                baseline_time, baseline_count = baseline_performance[(provider, category)]
                
                # Calculate regression percentage
                regression_percent = ((recent_time - baseline_time) / baseline_time) * 100
                
                # Consider it a regression if >20% slower with significant sample size
                if regression_percent > 20 and recent_count >= 5 and baseline_count >= 5:
                    regressions.append(PerformanceRegression(
                        provider=provider,
                        query_category=category,
                        avg_time_before=baseline_time,
                        avg_time_after=recent_time,
                        regression_percent=regression_percent,
                        sample_size=min(recent_count, baseline_count)
                    ))
                    
        return regressions
        
    def generate_quality_report(self, days: int = 7) -> Dict[str, any]:
        \"\"\"Generate comprehensive quality report for specified time period\"\"\"
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Overall statistics
        cursor.execute(\"\"\"
            SELECT 
                provider,
                COUNT(*) as total_queries,
                SUM(CASE WHEN success = true THEN 1 ELSE 0 END) as successful_queries,
                AVG(quality_score) as avg_quality,
                AVG(execution_time_ms) as avg_response_time,
                SUM(CASE WHEN hallucination_detected = true THEN 1 ELSE 0 END) as hallucinations
            FROM test_results
            WHERE timestamp > date('now', '-{} days')
            GROUP BY provider
        \"\"\".format(days))
        
        provider_stats = {}
        for row in cursor.fetchall():
            provider, total, successful, avg_quality, avg_time, hallucinations = row
            provider_stats[provider] = {
                \"total_queries\": total,
                \"successful_queries\": successful,
                \"success_rate\": successful / total if total > 0 else 0,
                \"avg_quality_score\": avg_quality or 0,
                \"avg_response_time_ms\": avg_time or 0,
                \"hallucination_count\": hallucinations,
                \"hallucination_rate\": hallucinations / total if total > 0 else 0
            }
            
        conn.close()
        
        return {
            \"report_period_days\": days,
            \"generated_at\": datetime.now().isoformat(),
            \"provider_statistics\": provider_stats,
            \"hallucination_alerts\": self.detect_hallucinations(days),
            \"performance_regressions\": self.detect_performance_regressions()
        }
```

---

## Phase 3: Real-Time Monitoring Dashboard (Week 3)

### 3.1 Analysis Dashboard Implementation

**File:** `dashboard/analysis_dashboard.py`

```python
import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json

from analysis.behavior_analyzer import BehaviorAnalyzer
from database.data_importer import TestDataImporter

class AnalysisDashboard:
    \"\"\"Real-time analysis dashboard for DeepCoderX testing results\"\"\"
    
    def __init__(self, db_path: str = \"data/test_results.db\"):
        self.db_path = db_path
        self.analyzer = BehaviorAnalyzer(db_path)
        
    def run(self):
        \"\"\"Launch Streamlit dashboard\"\"\"
        st.set_page_config(
            page_title=\"DeepCoderX Analysis Dashboard\",
            page_icon=\"🤖\",
            layout=\"wide\"
        )
        
        st.title(\"🤖 DeepCoderX Model Behavior Analysis Dashboard\")
        
        # Sidebar configuration
        st.sidebar.header(\"Dashboard Configuration\")
        analysis_days = st.sidebar.slider(\"Analysis Period (Days)\", 1, 30, 7)
        auto_refresh = st.sidebar.checkbox(\"Auto Refresh (30s)\", value=True)
        
        if auto_refresh:
            st.rerun()
            
        # Main dashboard tabs
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            \"📊 Overview\", \"🚨 Alerts\", \"📈 Performance\", \"🎯 Quality\", \"🔍 Detailed Analysis\"
        ])
        
        with tab1:
            self._render_overview_tab(analysis_days)
            
        with tab2:
            self._render_alerts_tab(analysis_days)
            
        with tab3:
            self._render_performance_tab(analysis_days)
            
        with tab4:
            self._render_quality_tab(analysis_days)
            
        with tab5:
            self._render_detailed_analysis_tab(analysis_days)
            
    def _render_overview_tab(self, days: int):
        \"\"\"Render main overview dashboard\"\"\"
        
        # Load recent test statistics
        conn = sqlite3.connect(self.db_path)
        
        # Provider statistics
        provider_stats = pd.read_sql_query(f\"\"\"
            SELECT 
                provider,
                COUNT(*) as total_tests,
                AVG(quality_score) as avg_quality,
                AVG(execution_time_ms) as avg_response_time,
                SUM(CASE WHEN success = true THEN 1 ELSE 0 END) * 100.0 / COUNT(*) as success_rate
            FROM test_results
            WHERE timestamp > date('now', '-{days} days')
            GROUP BY provider
        \"\"\", conn)
        
        conn.close()
        
        # Display key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_tests = provider_stats['total_tests'].sum()
            st.metric(\"Total Tests\", f\"{total_tests:,}\")
            
        with col2:
            avg_quality = provider_stats['avg_quality'].mean()
            st.metric(\"Average Quality\", f\"{avg_quality:.3f}\")
            
        with col3:
            avg_time = provider_stats['avg_response_time'].mean()
            st.metric(\"Avg Response Time\", f\"{avg_time:.0f}ms\")
            
        with col4:
            avg_success = provider_stats['success_rate'].mean()
            st.metric(\"Success Rate\", f\"{avg_success:.1f}%\")
            
        # Provider comparison charts
        col1, col2 = st.columns(2)
        
        with col1:
            fig_quality = px.bar(
                provider_stats, 
                x='provider', 
                y='avg_quality',
                title=\"Average Quality Score by Provider\",
                color='avg_quality',
                color_continuous_scale='Viridis'
            )
            st.plotly_chart(fig_quality, use_container_width=True)
            
        with col2:
            fig_time = px.bar(
                provider_stats,
                x='provider',
                y='avg_response_time', 
                title=\"Average Response Time by Provider\",
                color='avg_response_time',
                color_continuous_scale='Plasma'
            )
            st.plotly_chart(fig_time, use_container_width=True)
            
    def _render_alerts_tab(self, days: int):
        \"\"\"Render alerts and issues dashboard\"\"\"
        
        st.header(\"🚨 Current Alerts and Issues\")
        
        # Get hallucination alerts
        hallucinations = self.analyzer.detect_hallucinations(days)
        
        if hallucinations:
            st.warning(f\"⚠️ {len(hallucinations)} potential hallucinations detected\")
            
            for alert in hallucinations[:10]:  # Show top 10
                with st.expander(f\"🚨 {alert.provider}: '{alert.query}' (Confidence: {alert.confidence:.2f})\"):
                    st.write(f\"**Response:** {alert.response}\")
                    st.write(f\"**Timestamp:** {alert.timestamp}\")
                    st.write(f\"**Interaction ID:** {alert.interaction_id}\")
        else:
            st.success(\"✅ No hallucinations detected in the selected period\")
            
        # Performance regressions
        regressions = self.analyzer.detect_performance_regressions()
        
        if regressions:
            st.warning(f\"📉 {len(regressions)} performance regressions detected\")
            
            regression_data = []
            for reg in regressions:
                regression_data.append({
                    \"Provider\": reg.provider,
                    \"Category\": reg.query_category,
                    \"Before (ms)\": f\"{reg.avg_time_before:.0f}\",
                    \"After (ms)\": f\"{reg.avg_time_after:.0f}\",
                    \"Regression %\": f\"{reg.regression_percent:.1f}%\",
                    \"Sample Size\": reg.sample_size
                })
                
            st.dataframe(pd.DataFrame(regression_data))
        else:
            st.success(\"✅ No performance regressions detected\")
            
    def _render_performance_tab(self, days: int):
        \"\"\"Render performance analysis dashboard\"\"\"
        
        st.header(\"📈 Performance Analysis\")
        
        conn = sqlite3.connect(self.db_path)
        
        # Response time trends
        time_trends = pd.read_sql_query(f\"\"\"
            SELECT 
                DATE(timestamp) as test_date,
                provider,
                AVG(execution_time_ms) as avg_response_time,
                COUNT(*) as test_count
            FROM test_results
            WHERE timestamp > date('now', '-{days} days')
            AND success = true
            GROUP BY DATE(timestamp), provider
            ORDER BY test_date
        \"\"\", conn)
        
        if not time_trends.empty:
            fig_trends = px.line(
                time_trends,
                x='test_date',
                y='avg_response_time',
                color='provider',
                title=\"Response Time Trends Over Time\",
                markers=True
            )
            st.plotly_chart(fig_trends, use_container_width=True)
            
        # Category performance breakdown
        category_perf = pd.read_sql_query(f\"\"\"
            SELECT 
                query_category,
                provider,
                AVG(execution_time_ms) as avg_time,
                COUNT(*) as test_count
            FROM test_results
            WHERE timestamp > date('now', '-{days} days')
            AND success = true
            GROUP BY query_category, provider
        \"\"\", conn)
        
        if not category_perf.empty:
            fig_category = px.box(
                category_perf,
                x='query_category',
                y='avg_time',
                color='provider',
                title=\"Response Time Distribution by Category\"
            )
            st.plotly_chart(fig_category, use_container_width=True)
            
        conn.close()
        
    def _render_quality_tab(self, days: int):
        \"\"\"Render quality analysis dashboard\"\"\"
        
        st.header(\"🎯 Quality Analysis\")
        
        # Quality report
        quality_report = self.analyzer.generate_quality_report(days)
        
        # Display provider quality statistics
        quality_data = []
        for provider, stats in quality_report[\"provider_statistics\"].items():
            quality_data.append({
                \"Provider\": provider,
                \"Total Tests\": stats[\"total_queries\"],
                \"Success Rate\": f\"{stats['success_rate']:.1%}\",
                \"Avg Quality\": f\"{stats['avg_quality_score']:.3f}\",
                \"Hallucination Rate\": f\"{stats['hallucination_rate']:.1%}\",
                \"Avg Response Time\": f\"{stats['avg_response_time_ms']:.0f}ms\"
            })
            
        st.dataframe(pd.DataFrame(quality_data))
        
        # Semantic zone accuracy
        zone_accuracy = self.analyzer.analyze_semantic_routing_accuracy(days)
        
        if zone_accuracy:
            st.subheader(\"🎯 Semantic Zone Detection Accuracy\")
            
            accuracy_data = []
            for provider, data in zone_accuracy.items():
                accuracy_data.append({
                    \"Provider\": provider,
                    \"Overall Accuracy\": f\"{data['accuracy']:.1%}\",
                    \"Avg Confidence\": f\"{data['avg_confidence']:.3f}\",
                    \"Total Classifications\": data['total']
                })
                
            st.dataframe(pd.DataFrame(accuracy_data))
            
    def _render_detailed_analysis_tab(self, days: int):
        \"\"\"Render detailed analysis and raw data view\"\"\"
        
        st.header(\"🔍 Detailed Analysis\")
        
        # Query builder for custom analysis
        st.subheader(\"Custom Query Builder\")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            selected_provider = st.selectbox(\"Provider\", [\"All\", \"dual\", \"local\", \"deepseek\", \"openai\"])
            
        with col2:
            selected_category = st.selectbox(\"Category\", [\"All\", \"conversational\", \"commands\", \"code_gen\", \"semantic\", \"edge\"])
            
        with col3:
            min_quality = st.slider(\"Minimum Quality Score\", 0.0, 1.0, 0.0)
            
        # Build query
        conn = sqlite3.connect(self.db_path)
        query = f\"\"\"
            SELECT 
                timestamp,
                provider,
                query_category,
                query,
                response_content,
                quality_score,
                execution_time_ms,
                success,
                hallucination_detected
            FROM test_results
            WHERE timestamp > date('now', '-{days} days')
            AND quality_score >= {min_quality}
        \"\"\"
        
        if selected_provider != \"All\":
            query += f\" AND provider = '{selected_provider}'\"
            
        if selected_category != \"All\":
            query += f\" AND query_category = '{selected_category}'\"
            
        query += \" ORDER BY timestamp DESC LIMIT 100\"
        
        results = pd.read_sql_query(query, conn)
        conn.close()
        
        if not results.empty:
            st.dataframe(results)
            
            # Download option
            csv = results.to_csv(index=False)
            st.download_button(
                label=\"Download CSV\",
                data=csv,
                file_name=f\"deepcoderx_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv\",
                mime=\"text/csv\"
            )
        else:
            st.info(\"No results found for the selected criteria\")

# Streamlit app entry point
if __name__ == \"__main__\":
    dashboard = AnalysisDashboard()
    dashboard.run()
```

### 3.2 Automated Report Generation

**File:** `reports/report_generator.py`

```python
import json
import jinja2
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List

from analysis.behavior_analyzer import BehaviorAnalyzer

class ReportGenerator:
    \"\"\"Generate automated reports for DeepCoderX testing results\"\"\"
    
    def __init__(self, db_path: str = \"data/test_results.db\"):
        self.analyzer = BehaviorAnalyzer(db_path)
        self.template_dir = Path(__file__).parent / \"templates\"
        self.output_dir = Path(\"reports/output\")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize Jinja2 environment
        self.jinja_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(self.template_dir)
        )
        
    def generate_daily_summary(self, date: datetime = None) -> str:
        \"\"\"Generate daily summary report\"\"\"
        
        if date is None:
            date = datetime.now()
            
        # Generate comprehensive quality report
        quality_report = self.analyzer.generate_quality_report(days=1)
        
        # Additional daily metrics
        hallucinations = self.analyzer.detect_hallucinations(days=1)
        regressions = self.analyzer.detect_performance_regressions(comparison_days=1)
        
        report_data = {
            \"report_date\": date.strftime(\"%Y-%m-%d\"),
            \"generated_at\": datetime.now().isoformat(),
            \"quality_report\": quality_report,
            \"hallucination_count\": len(hallucinations),
            \"regression_count\": len(regressions),
            \"hallucinations\": hallucinations[:5],  # Top 5
            \"regressions\": regressions[:5]  # Top 5
        }
        
        # Render HTML report
        template = self.jinja_env.get_template(\"daily_summary.html\")
        html_content = template.render(**report_data)
        
        # Save report
        output_file = self.output_dir / f\"daily_summary_{date.strftime('%Y%m%d')}.html\"
        with open(output_file, 'w') as f:
            f.write(html_content)
            
        return str(output_file)
        
    def generate_weekly_analysis(self, weeks_back: int = 1) -> str:
        \"\"\"Generate weekly analysis report\"\"\"
        
        end_date = datetime.now()
        start_date = end_date - timedelta(weeks=weeks_back)
        
        # Weekly metrics
        quality_report = self.analyzer.generate_quality_report(days=7 * weeks_back)
        consistency_scores = {}
        
        # Test common queries for consistency
        common_queries = [\"hello\", \"pwd\", \"ls\", \"create a simple script\"]
        for query in common_queries:
            consistency_scores[query] = self.analyzer.measure_consistency(query, days=7 * weeks_back)
            
        report_data = {
            \"report_period\": f\"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}\",
            \"generated_at\": datetime.now().isoformat(),
            \"quality_report\": quality_report,
            \"consistency_analysis\": consistency_scores,
            \"hallucinations\": self.analyzer.detect_hallucinations(days=7 * weeks_back),
            \"regressions\": self.analyzer.detect_performance_regressions()
        }
        
        # Render report
        template = self.jinja_env.get_template(\"weekly_analysis.html\")
        html_content = template.render(**report_data)
        
        # Save report
        output_file = self.output_dir / f\"weekly_analysis_{end_date.strftime('%Y%m%d')}.html\"
        with open(output_file, 'w') as f:
            f.write(html_content)
            
        return str(output_file)
        
    def generate_provider_comparison(self, days: int = 7) -> str:
        \"\"\"Generate detailed provider comparison report\"\"\"
        
        quality_report = self.analyzer.generate_quality_report(days)
        zone_accuracy = self.analyzer.analyze_semantic_routing_accuracy(days)
        
        # Build comparison matrix
        providers = list(quality_report[\"provider_statistics\"].keys())
        comparison_matrix = {}
        
        for provider in providers:
            stats = quality_report[\"provider_statistics\"][provider]
            accuracy = zone_accuracy.get(provider, {})
            
            comparison_matrix[provider] = {
                **stats,
                \"zone_accuracy\": accuracy.get(\"accuracy\", 0),
                \"zone_confidence\": accuracy.get(\"avg_confidence\", 0)
            }
            
        report_data = {
            \"analysis_period_days\": days,
            \"generated_at\": datetime.now().isoformat(),
            \"provider_comparison\": comparison_matrix,
            \"recommendations\": self._generate_recommendations(comparison_matrix)
        }
        
        # Render report
        template = self.jinja_env.get_template(\"provider_comparison.html\")
        html_content = template.render(**report_data)
        
        # Save report
        output_file = self.output_dir / f\"provider_comparison_{datetime.now().strftime('%Y%m%d')}.html\"
        with open(output_file, 'w') as f:
            f.write(html_content)
            
        return str(output_file)
        
    def _generate_recommendations(self, comparison_matrix: Dict) -> List[str]:
        \"\"\"Generate recommendations based on analysis\"\"\"
        
        recommendations = []
        
        # Find best/worst performers
        providers_by_quality = sorted(
            comparison_matrix.items(),
            key=lambda x: x[1]['avg_quality_score'],
            reverse=True
        )
        
        best_provider = providers_by_quality[0][0]
        worst_provider = providers_by_quality[-1][0]
        
        recommendations.append(
            f\"🏆 **Best Overall Quality**: {best_provider} with {providers_by_quality[0][1]['avg_quality_score']:.3f} average quality score\"
        )
        
        if len(providers_by_quality) > 1:
            recommendations.append(
                f\"⚠️ **Needs Improvement**: {worst_provider} with {providers_by_quality[-1][1]['avg_quality_score']:.3f} average quality score\"
            )
            
        # Hallucination analysis
        high_hallucination_providers = [
            provider for provider, stats in comparison_matrix.items()
            if stats['hallucination_rate'] > 0.05  # >5% hallucination rate
        ]
        
        if high_hallucination_providers:
            recommendations.append(
                f\"🚨 **High Hallucination Rate**: {', '.join(high_hallucination_providers)} need prompt optimization\"
            )
            
        # Performance analysis
        slow_providers = [
            provider for provider, stats in comparison_matrix.items()
            if stats['avg_response_time_ms'] > 5000  # >5 seconds
        ]
        
        if slow_providers:
            recommendations.append(
                f\"🐌 **Performance Optimization Needed**: {', '.join(slow_providers)} have slow response times\"
            )
            
        return recommendations
```

### 3.3 Alert System Implementation

**File:** `monitoring/alert_system.py`

```python
import smtplib
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from typing import List, Dict
from dataclasses import dataclass

from analysis.behavior_analyzer import BehaviorAnalyzer, HallucinationAlert, PerformanceRegression

@dataclass
class AlertConfiguration:
    enabled: bool = True
    quality_threshold: float = 0.7
    response_time_threshold: float = 10000  # ms
    hallucination_threshold: int = 5  # count per day
    regression_threshold: float = 20.0  # percent increase
    email_notifications: bool = False
    email_recipients: List[str] = None
    check_interval_minutes: int = 30
    
class AlertSystem:
    \"\"\"Automated alerting system for DeepCoderX quality issues\"\"\"
    
    def __init__(self, config: AlertConfiguration, db_path: str = \"data/test_results.db\"):
        self.config = config
        self.analyzer = BehaviorAnalyzer(db_path)
        self.last_check = datetime.now() - timedelta(days=1)
        
    def check_and_alert(self) -> Dict[str, List]:
        \"\"\"Check for issues and send alerts if necessary\"\"\"
        
        current_time = datetime.now()
        alerts_sent = {
            \"hallucination_alerts\": [],
            \"performance_alerts\": [],
            \"quality_alerts\": []
        }
        
        if not self.config.enabled:
            return alerts_sent
            
        # Check for hallucinations
        hallucinations = self.analyzer.detect_hallucinations(days=1)
        if len(hallucinations) >= self.config.hallucination_threshold:
            alert_message = self._create_hallucination_alert(hallucinations)
            alerts_sent[\"hallucination_alerts\"].append(alert_message)
            
            if self.config.email_notifications:
                self._send_email_alert(\"🚨 DeepCoderX Hallucination Alert\", alert_message)
                
        # Check for performance regressions
        regressions = self.analyzer.detect_performance_regressions()
        critical_regressions = [
            r for r in regressions 
            if r.regression_percent >= self.config.regression_threshold
        ]
        
        if critical_regressions:
            alert_message = self._create_regression_alert(critical_regressions)
            alerts_sent[\"performance_alerts\"].append(alert_message)
            
            if self.config.email_notifications:
                self._send_email_alert(\"📉 DeepCoderX Performance Regression Alert\", alert_message)
                
        # Check overall quality degradation
        quality_report = self.analyzer.generate_quality_report(days=1)
        low_quality_providers = [
            provider for provider, stats in quality_report[\"provider_statistics\"].items()
            if stats[\"avg_quality_score\"] < self.config.quality_threshold
        ]
        
        if low_quality_providers:
            alert_message = self._create_quality_alert(low_quality_providers, quality_report)
            alerts_sent[\"quality_alerts\"].append(alert_message)
            
            if self.config.email_notifications:
                self._send_email_alert(\"⚠️ DeepCoderX Quality Degradation Alert\", alert_message)
                
        self.last_check = current_time
        return alerts_sent
        
    def _create_hallucination_alert(self, hallucinations:`,
      `oldText`: `        # Get baseline performance
        cursor.execute(\"\"\"
            SELECT provider, query_category, AVG(execution_time_ms) as avg_time, COUNT(*) as count
            FROM test_results
            WHERE timestamp BETWEEN date('now', '-{} days') AND date('now', '-{} days')
            AND success = true
            GROUP BY provider,`
    }
  ],
  `dryRun`: false
}






{
  `edits`: [
    {
      `newText`: `    def _create_hallucination_alert(self, hallucinations: List[HallucinationAlert]) -> str:
        \"\"\"Create hallucination alert message\"\"\"
        
        message = f\"🚨 HALLUCINATION ALERT: {len(hallucinations)} potential hallucinations detected\
\
\"
        
        for i, alert in enumerate(hallucinations[:5], 1):
            message += f\"{i}. Provider: {alert.provider}\
\"
            message += f\"   Query: '{alert.query}'\
\"
            message += f\"   Response: {alert.response[:100]}...\
\"
            message += f\"   Confidence: {alert.confidence:.2f}\
\"
            message += f\"   Time: {alert.timestamp}\
\
\"
            
        if len(hallucinations) > 5:
            message += f\"... and {len(hallucinations) - 5} more\
\"
            
        return message
        
    def _create_regression_alert(self, regressions: List[PerformanceRegression]) -> str:
        \"\"\"Create performance regression alert message\"\"\"
        
        message = f\"📉 PERFORMANCE REGRESSION ALERT: {len(regressions)} critical regressions detected\
\
\"
        
        for i, reg in enumerate(regressions, 1):
            message += f\"{i}. Provider: {reg.provider}\
\"
            message += f\"   Category: {reg.query_category}\
\"
            message += f\"   Before: {reg.avg_time_before:.0f}ms\
\"
            message += f\"   After: {reg.avg_time_after:.0f}ms\
\"
            message += f\"   Regression: {reg.regression_percent:.1f}%\
\
\"
            
        return message
        
    def _create_quality_alert(self, providers: List[str], quality_report: Dict) -> str:
        \"\"\"Create quality degradation alert message\"\"\"
        
        message = f\"⚠️ QUALITY DEGRADATION ALERT: {len(providers)} providers below threshold\
\
\"
        
        for provider in providers:
            stats = quality_report[\"provider_statistics\"][provider]
            message += f\"Provider: {provider}\
\"
            message += f\"   Quality Score: {stats['avg_quality_score']:.3f}\
\"
            message += f\"   Success Rate: {stats['success_rate']:.1%}\
\"
            message += f\"   Hallucination Rate: {stats['hallucination_rate']:.1%}\
\
\"
            
        return message
        
    def _send_email_alert(self, subject: str, message: str):
        \"\"\"Send email alert to configured recipients\"\"\"
        
        if not self.config.email_recipients:
            return
            
        try:
            # Configure your email settings here
            smtp_server = \"smtp.gmail.com\"  # Update with your SMTP server
            smtp_port = 587
            sender_email = \"your-email@gmail.com\"  # Update with your email
            sender_password = \"your-app-password\"  # Update with your app password
            
            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = \", \".join(self.config.email_recipients)
            msg['Subject'] = subject
            
            msg.attach(MIMEText(message, 'plain'))
            
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(sender_email, sender_password)
            text = msg.as_string()
            server.sendmail(sender_email, self.config.email_recipients, text)
            server.quit()
            
            print(f\"📧 Alert email sent: {subject}\")
            
        except Exception as e:
            print(f\"❌ Failed to send email alert: {e}\")
            
    def run_continuous_monitoring(self):
        \"\"\"Run continuous monitoring with configured intervals\"\"\"
        
        import time
        
        print(f\"🔍 Starting continuous monitoring (check every {self.config.check_interval_minutes} minutes)\")
        
        while True:
            try:
                alerts = self.check_and_alert()
                
                total_alerts = sum(len(alert_list) for alert_list in alerts.values())
                if total_alerts > 0:
                    print(f\"⚠️ {total_alerts} alerts generated at {datetime.now()}\")
                else:
                    print(f\"✅ No issues detected at {datetime.now()}\")
                    
            except Exception as e:
                print(f\"❌ Error during monitoring check: {e}\")
                
            # Wait for next check
            time.sleep(self.config.check_interval_minutes * 60)
```

---

## Phase 4: Advanced Analytics and Optimization (Week 4)

### 4.1 Historical Trend Analysis

**File:** `analysis/trend_analyzer.py`

```python
import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
from dataclasses import dataclass
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score

@dataclass
class TrendAnalysis:
    metric: str
    provider: str
    trend_direction: str  # 'improving', 'declining', 'stable'
    slope: float
    r_squared: float
    prediction_7_days: float
    confidence: str  # 'high', 'medium', 'low'
    
class TrendAnalyzer:
    \"\"\"Analyze historical trends and predict future performance\"\"\"
    
    def __init__(self, db_path: str = \"data/test_results.db\"):
        self.db_path = db_path
        
    def analyze_quality_trends(self, days: int = 30) -> List[TrendAnalysis]:
        \"\"\"Analyze quality score trends over time\"\"\"
        
        conn = sqlite3.connect(self.db_path)
        
        # Get daily quality averages
        df = pd.read_sql_query(f\"\"\"
            SELECT 
                DATE(timestamp) as date,
                provider,
                AVG(quality_score) as avg_quality,
                COUNT(*) as sample_size
            FROM test_results
            WHERE timestamp > date('now', '-{days} days')
            AND quality_score IS NOT NULL
            GROUP BY DATE(timestamp), provider
            HAVING sample_size >= 5
            ORDER BY date
        \"\"\", conn)
        
        conn.close()
        
        trends = []
        
        for provider in df['provider'].unique():
            provider_data = df[df['provider'] == provider].copy()
            
            if len(provider_data) < 7:  # Need at least a week of data
                continue
                
            # Prepare data for regression
            provider_data['date_ordinal'] = pd.to_datetime(provider_data['date']).map(datetime.toordinal)
            X = provider_data[['date_ordinal']]
            y = provider_data['avg_quality']
            
            # Fit linear regression
            model = LinearRegression()
            model.fit(X, y)
            
            # Calculate metrics
            y_pred = model.predict(X)
            slope = model.coef_[0]
            r_squared = r2_score(y, y_pred)
            
            # Predict 7 days ahead
            future_date = datetime.now() + timedelta(days=7)
            future_ordinal = future_date.toordinal()
            prediction = model.predict([[future_ordinal]])[0]
            
            # Determine trend direction and confidence
            if abs(slope) < 0.001:  # Very small slope
                direction = 'stable'
            elif slope > 0:
                direction = 'improving'
            else:
                direction = 'declining'
                
            # Confidence based on R-squared
            if r_squared > 0.7:
                confidence = 'high'
            elif r_squared > 0.4:
                confidence = 'medium'
            else:
                confidence = 'low'
                
            trends.append(TrendAnalysis(
                metric='quality_score',
                provider=provider,
                trend_direction=direction,
                slope=slope,
                r_squared=r_squared,
                prediction_7_days=prediction,
                confidence=confidence
            ))
            
        return trends
        
    def analyze_performance_trends(self, days: int = 30) -> List[TrendAnalysis]:
        \"\"\"Analyze response time trends over time\"\"\"
        
        conn = sqlite3.connect(self.db_path)
        
        # Get daily performance averages
        df = pd.read_sql_query(f\"\"\"
            SELECT 
                DATE(timestamp) as date,
                provider,
                AVG(execution_time_ms) as avg_response_time,
                COUNT(*) as sample_size
            FROM test_results
            WHERE timestamp > date('now', '-{days} days')
            AND success = true
            GROUP BY DATE(timestamp), provider
            HAVING sample_size >= 5
            ORDER BY date
        \"\"\", conn)
        
        conn.close()
        
        trends = []
        
        for provider in df['provider'].unique():
            provider_data = df[df['provider'] == provider].copy()
            
            if len(provider_data) < 7:
                continue
                
            # Prepare data for regression
            provider_data['date_ordinal'] = pd.to_datetime(provider_data['date']).map(datetime.toordinal)
            X = provider_data[['date_ordinal']]
            y = provider_data['avg_response_time']
            
            # Fit linear regression
            model = LinearRegression()
            model.fit(X, y)
            
            # Calculate metrics
            y_pred = model.predict(X)
            slope = model.coef_[0]
            r_squared = r2_score(y, y_pred)
            
            # Predict 7 days ahead
            future_date = datetime.now() + timedelta(days=7)
            future_ordinal = future_date.toordinal()
            prediction = model.predict([[future_ordinal]])[0]
            
            # Determine trend direction (for performance, lower is better)
            if abs(slope) < 50:  # Less than 50ms change per day
                direction = 'stable'
            elif slope > 0:
                direction = 'declining'  # Getting slower
            else:
                direction = 'improving'  # Getting faster
                
            # Confidence based on R-squared
            if r_squared > 0.7:
                confidence = 'high'
            elif r_squared > 0.4:
                confidence = 'medium'
            else:
                confidence = 'low'
                
            trends.append(TrendAnalysis(
                metric='response_time',
                provider=provider,
                trend_direction=direction,
                slope=slope,
                r_squared=r_squared,
                prediction_7_days=prediction,
                confidence=confidence
            ))
            
        return trends
        
    def detect_seasonal_patterns(self, days: int = 90) -> Dict[str, Dict[str, float]]:
        \"\"\"Detect seasonal patterns in usage and performance\"\"\"
        
        conn = sqlite3.connect(self.db_path)
        
        # Get hourly patterns
        hourly_data = pd.read_sql_query(f\"\"\"
            SELECT 
                strftime('%H', timestamp) as hour,
                provider,
                AVG(execution_time_ms) as avg_response_time,
                AVG(quality_score) as avg_quality,
                COUNT(*) as test_count
            FROM test_results
            WHERE timestamp > date('now', '-{days} days')
            GROUP BY strftime('%H', timestamp), provider
            ORDER BY hour
        \"\"\", conn)
        
        # Get daily patterns
        daily_data = pd.read_sql_query(f\"\"\"
            SELECT 
                strftime('%w', timestamp) as day_of_week,
                provider,
                AVG(execution_time_ms) as avg_response_time,
                AVG(quality_score) as avg_quality,
                COUNT(*) as test_count
            FROM test_results
            WHERE timestamp > date('now', '-{days} days')
            GROUP BY strftime('%w', timestamp), provider
            ORDER BY day_of_week
        \"\"\", conn)
        
        conn.close()
        
        patterns = {}
        
        # Analyze hourly patterns
        for provider in hourly_data['provider'].unique():
            provider_hourly = hourly_data[hourly_data['provider'] == provider]
            
            if len(provider_hourly) >= 12:  # At least half a day of data
                peak_hour = provider_hourly.loc[provider_hourly['test_count'].idxmax(), 'hour']
                lowest_hour = provider_hourly.loc[provider_hourly['test_count'].idxmin(), 'hour']
                
                patterns[provider] = {
                    'peak_usage_hour': int(peak_hour),
                    'lowest_usage_hour': int(lowest_hour),
                    'hourly_variance': provider_hourly['test_count'].var(),
                    'quality_variance_by_hour': provider_hourly['avg_quality'].var() if 'avg_quality' in provider_hourly else 0
                }
                
        return patterns
        
    def generate_trend_report(self, days: int = 30) -> Dict[str, any]:
        \"\"\"Generate comprehensive trend analysis report\"\"\"
        
        quality_trends = self.analyze_quality_trends(days)
        performance_trends = self.analyze_performance_trends(days)
        seasonal_patterns = self.detect_seasonal_patterns(days * 3)  # Longer period for seasonal analysis
        
        # Summarize trends
        trend_summary = {
            'quality_trends': {
                'improving': [t for t in quality_trends if t.trend_direction == 'improving'],
                'declining': [t for t in quality_trends if t.trend_direction == 'declining'],
                'stable': [t for t in quality_trends if t.trend_direction == 'stable']
            },
            'performance_trends': {
                'improving': [t for t in performance_trends if t.trend_direction == 'improving'],
                'declining': [t for t in performance_trends if t.trend_direction == 'declining'],
                'stable': [t for t in performance_trends if t.trend_direction == 'stable']
            },
            'seasonal_patterns': seasonal_patterns
        }
        
        # Generate insights
        insights = self._generate_trend_insights(trend_summary)
        
        return {
            'analysis_period_days': days,
            'generated_at': datetime.now().isoformat(),
            'trend_summary': trend_summary,
            'insights': insights,
            'recommendations': self._generate_trend_recommendations(trend_summary)
        }
        
    def _generate_trend_insights(self, trend_summary: Dict) -> List[str]:
        \"\"\"Generate insights from trend analysis\"\"\"
        
        insights = []
        
        # Quality insights
        improving_quality = len(trend_summary['quality_trends']['improving'])
        declining_quality = len(trend_summary['quality_trends']['declining'])
        
        if improving_quality > declining_quality:
            insights.append(f\"📈 Overall quality is improving: {improving_quality} providers showing improvement vs {declining_quality} declining\")
        elif declining_quality > improving_quality:
            insights.append(f\"📉 Quality concerns: {declining_quality} providers declining vs {improving_quality} improving\")
        else:
            insights.append(f\"📊 Quality trends are mixed: equal numbers improving and declining\")
            
        # Performance insights
        improving_performance = len(trend_summary['performance_trends']['improving'])
        declining_performance = len(trend_summary['performance_trends']['declining'])
        
        if improving_performance > declining_performance:
            insights.append(f\"⚡ Performance is improving: {improving_performance} providers getting faster\")
        elif declining_performance > improving_performance:
            insights.append(f\"🐌 Performance degradation: {declining_performance} providers getting slower\")
            
        # Seasonal insights
        if trend_summary['seasonal_patterns']:
            high_variance_providers = [
                provider for provider, patterns in trend_summary['seasonal_patterns'].items()
                if patterns.get('hourly_variance', 0) > 100
            ]
            
            if high_variance_providers:
                insights.append(f\"🕐 High usage variance detected in: {', '.join(high_variance_providers)}\")
                
        return insights
        
    def _generate_trend_recommendations(self, trend_summary: Dict) -> List[str]:
        \"\"\"Generate recommendations based on trend analysis\"\"\"
        
        recommendations = []
        
        # Quality recommendations
        declining_quality_providers = [t.provider for t in trend_summary['quality_trends']['declining'] if t.confidence in ['high', 'medium']]
        
        if declining_quality_providers:
            recommendations.append(
                f\"🔧 Immediate attention needed: {', '.join(declining_quality_providers)} showing consistent quality decline - review prompts and model parameters\"
            )
            
        # Performance recommendations
        declining_performance_providers = [t.provider for t in trend_summary['performance_trends']['declining'] if t.confidence in ['high', 'medium']]
        
        if declining_performance_providers:
            recommendations.append(
                f\"⚡ Performance optimization needed: {', '.join(declining_performance_providers)} showing response time increases - consider resource allocation or model optimization\"
            )
            
        # Seasonal recommendations
        if trend_summary['seasonal_patterns']:
            peak_hours = {}
            for provider, patterns in trend_summary['seasonal_patterns'].items():
                peak_hour = patterns.get('peak_usage_hour')
                if peak_hour is not None:
                    if peak_hour not in peak_hours:
                        peak_hours[peak_hour] = []
                    peak_hours[peak_hour].append(provider)
                    
            if peak_hours:
                recommendations.append(
                    f\"📊 Consider resource scaling during peak hours: {dict(peak_hours)}\"
                )
                
        return recommendations
```

### 4.2 Predictive Analysis Implementation

**File:** `analysis/predictive_analyzer.py`

```python
import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, accuracy_score
from sklearn.preprocessing import LabelEncoder
import joblib
from pathlib import Path

@dataclass
class QualityPrediction:
    query: str
    provider: str
    predicted_quality: float
    confidence_interval: Tuple[float, float]
    prediction_confidence: float
    factors: Dict[str, float]
    
@dataclass
class FailurePrediction:
    query: str
    provider: str
    failure_probability: float
    risk_factors: List[str]
    recommendations: List[str]
    
class PredictiveAnalyzer:
    \"\"\"Predictive analysis for model behavior and performance\"\"\"
    
    def __init__(self, db_path: str = \"data/test_results.db\"):
        self.db_path = db_path
        self.models_dir = Path(\"models/predictive\")
        self.models_dir.mkdir(parents=True, exist_ok=True)
        
        # Model storage
        self.quality_models = {}
        self.failure_models = {}
        self.label_encoders = {}
        
    def train_quality_prediction_models(self, days: int = 60) -> Dict[str, float]:
        \"\"\"Train models to predict response quality\"\"\"
        
        conn = sqlite3.connect(self.db_path)
        
        # Load training data
        df = pd.read_sql_query(f\"\"\"
            SELECT 
                provider,
                query_category,
                LENGTH(query) as query_length,
                execution_time_ms,
                tokens_used,
                model_used,
                semantic_zone_detected,
                zone_confidence,
                response_length,
                contains_code,
                contains_tool_calls,
                strftime('%H', timestamp) as hour_of_day,
                strftime('%w', timestamp) as day_of_week,
                quality_score
            FROM test_results
            WHERE timestamp > date('now', '-{days} days')
            AND quality_score IS NOT NULL
            AND success = true
        \"\"\", conn)
        
        conn.close()
        
        if len(df) < 100:  # Need minimum data for training
            raise ValueError(f\"Insufficient data for training: {len(df)} records\")
            
        # Prepare features
        categorical_columns = ['provider', 'query_category', 'model_used', 'semantic_zone_detected']
        
        # Encode categorical variables
        for col in categorical_columns:
            if col not in self.label_encoders:
                self.label_encoders[col] = LabelEncoder()
            df[f'{col}_encoded'] = self.label_encoders[col].fit_transform(df[col].astype(str))
            
        # Select features
        feature_columns = [
            'provider_encoded', 'query_category_encoded', 'query_length',
            'execution_time_ms', 'tokens_used', 'model_used_encoded',
            'semantic_zone_detected_encoded', 'zone_confidence',
            'response_length', 'contains_code', 'contains_tool_calls',
            'hour_of_day', 'day_of_week'
        ]
        
        X = df[feature_columns]
        y = df['quality_score']
        
        # Train models for each provider
        model_scores = {}
        
        for provider in df['provider'].unique():
            provider_mask = df['provider'] == provider
            X_provider = X[provider_mask]
            y_provider = y[provider_mask]
            
            if len(X_provider) < 50:  # Skip providers with insufficient data
                continue
                
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X_provider, y_provider, test_size=0.2, random_state=42
            )
            
            # Train model
            model = RandomForestRegressor(n_estimators=100, random_state=42)
            model.fit(X_train, y_train)
            
            # Evaluate
            y_pred = model.predict(X_test)
            mse = mean_squared_error(y_test, y_pred)
            
            # Store model
            self.quality_models[provider] = model
            model_scores[provider] = 1 - mse  # Convert MSE to a \"score\"
            
            # Save model
            model_path = self.models_dir / f\"quality_model_{provider}.joblib\"
            joblib.dump(model, model_path)
            
        # Save label encoders
        for col, encoder in self.label_encoders.items():
            encoder_path = self.models_dir / f\"label_encoder_{col}.joblib\"
            joblib.dump(encoder, encoder_path)
            
        return model_scores
        
    def predict_query_quality(self, query: str, provider: str, category: str = \"general\") -> Optional[QualityPrediction]:
        \"\"\"Predict quality score for a specific query and provider\"\"\"
        
        if provider not in self.quality_models:
            # Try to load model
            try:
                model_path = self.models_dir / f\"quality_model_{provider}.joblib\"
                self.quality_models[provider] = joblib.load(model_path)
            except FileNotFoundError:
                return None
                
        model = self.quality_models[provider]
        
        # Prepare features (simplified for prediction)
        features = {
            'provider_encoded': self._encode_value('provider', provider),
            'query_category_encoded': self._encode_value('query_category', category),
            'query_length': len(query),
            'execution_time_ms': 2000,  # Estimated average
            'tokens_used': len(query.split()) * 1.3,  # Rough estimate
            'model_used_encoded': self._encode_value('model_used', 'Llama-3.2-3B'),
            'semantic_zone_detected_encoded': self._encode_value('semantic_zone_detected', 'conversational'),
            'zone_confidence': 0.8,  # Default confidence
            'response_length': 100,  # Estimated average
            'contains_code': 1 if 'code' in query.lower() or 'script' in query.lower() else 0,
            'contains_tool_calls': 1 if 'file' in query.lower() or 'read' in query.lower() else 0,
            'hour_of_day': datetime.now().hour,
            'day_of_week': datetime.now().weekday()
        }
        
        # Create feature vector
        feature_vector = np.array([[features[col] for col in [
            'provider_encoded', 'query_category_encoded', 'query_length',
            'execution_time_ms', 'tokens_used', 'model_used_encoded',
            'semantic_zone_detected_encoded', 'zone_confidence',
            'response_length', 'contains_code', 'contains_tool_calls',
            'hour_of_day', 'day_of_week'
        ]]])
        
        # Predict
        predicted_quality = model.predict(feature_vector)[0]
        
        # Calculate confidence interval (simplified)
        # For Random Forest, we can use the standard deviation of tree predictions
        tree_predictions = [tree.predict(feature_vector)[0] for tree in model.estimators_]
        confidence_interval = (
            np.percentile(tree_predictions, 10),
            np.percentile(tree_predictions, 90)
        )
        
        prediction_confidence = 1.0 - (np.std(tree_predictions) / np.mean(tree_predictions))
        
        # Feature importance (simplified)
        feature_importance = dict(zip([
            'provider', 'category', 'query_length', 'exec_time', 'tokens',
            'model', 'semantic_zone', 'zone_conf', 'response_len',
            'has_code', 'has_tools', 'hour', 'day'
        ], model.feature_importances_))
        
        return QualityPrediction(
            query=query,
            provider=provider,
            predicted_quality=predicted_quality,
            confidence_interval=confidence_interval,
            prediction_confidence=prediction_confidence,
            factors=feature_importance
        )
        
    def train_failure_prediction_models(self, days: int = 60) -> Dict[str, float]:
        \"\"\"Train models to predict query failures\"\"\"
        
        conn = sqlite3.connect(self.db_path)
        
        # Load training data including failures
        df = pd.read_sql_query(f\"\"\"
            SELECT 
                provider,
                query_category,
                LENGTH(query) as query_length,
                semantic_zone_detected,
                zone_confidence,
                strftime('%H', timestamp) as hour_of_day,
                strftime('%w', timestamp) as day_of_week,
                CASE WHEN success = true THEN 0 ELSE 1 END as failure
            FROM test_results
            WHERE timestamp > date('now', '-{days} days')
        \"\"\", conn)
        
        conn.close()
        
        if len(df) < 100:
            raise ValueError(f\"Insufficient data for training: {len(df)} records\")
            
        # Prepare features
        categorical_columns = ['provider', 'query_category', 'semantic_zone_detected']
        
        for col in categorical_columns:
            if col not in self.label_encoders:
                self.label_encoders[col] = LabelEncoder()
            df[f'{col}_encoded'] = self.label_encoders[col].fit_transform(df[col].astype(str))
            
        feature_columns = [
            'provider_encoded', 'query_category_encoded', 'query_length',
            'semantic_zone_detected_encoded', 'zone_confidence',
            'hour_of_day', 'day_of_week'
        ]
        
        X = df[feature_columns]
        y = df['failure']
        
        # Train models for each provider
        model_scores = {}
        
        for provider in df['provider'].unique():
            provider_mask = df['provider'] == provider
            X_provider = X[provider_mask]
            y_provider = y[provider_mask]
            
            if len(X_provider) < 30 or y_provider.sum() < 5:  # Need some failures to learn from
                continue
                
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X_provider, y_provider, test_size=0.2, random_state=42, stratify=y_provider
            )
            
            # Train model
            model = RandomForestClassifier(n_estimators=100, random_state=42, class_weight='balanced')
            model.fit(X_train, y_train)
            
            # Evaluate
            y_pred =`
    }
  ],
  `dryRun`: false
}