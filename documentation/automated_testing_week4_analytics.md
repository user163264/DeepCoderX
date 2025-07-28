# Week 4: Advanced Analytics Implementation Plan
*DeepCoderX Automated Testing System - Final Phase*

## Executive Summary

Week 4 implements advanced analytics capabilities including historical trend analysis, predictive modeling, pattern detection, and optimization recommendations. This final phase transforms the automated testing system into a comprehensive AI behavior analysis platform with machine learning-powered insights and forecasting.

### Week 4 Objectives
- **Historical Analysis:** Comprehensive trend analysis with seasonal pattern detection
- **Predictive Modeling:** Quality degradation and failure prediction using machine learning
- **Pattern Recognition:** Automated detection of behavior patterns and anomalies
- **Optimization Engine:** Data-driven recommendations for prompt engineering and model selection
- **Advanced Reporting:** Executive dashboards with forecasting and strategic insights

## Prerequisites

### Required Components from Previous Weeks
- **Week 1:** Automated testing engine with standardized JSON output
- **Week 2:** Hybrid JSONL + SQLite storage with behavior analysis pipeline
- **Week 3:** Streamlit dashboard and alert system

### Technical Dependencies
```bash
# Additional packages for Week 4
pip install scikit-learn pandas matplotlib seaborn plotly
pip install statsmodels scipy numpy
pip install prophet # For time series forecasting
pip install joblib # For model persistence
```

## Implementation Architecture

### Week 4 Component Structure
```
analytics/
├── models/
│   ├── trend_analyzer.py          # Historical trend analysis
│   ├── predictive_models.py       # ML prediction models
│   ├── pattern_detector.py        # Pattern recognition engine
│   └── optimization_engine.py     # Recommendation system
├── forecasting/
│   ├── quality_forecaster.py      # Quality prediction models
│   ├── performance_forecaster.py  # Performance forecasting
│   └── failure_predictor.py       # Failure prediction system
├── visualization/
│   ├── advanced_charts.py         # Advanced visualization components
│   ├── trend_plots.py             # Trend analysis visualizations
│   └── forecast_charts.py         # Forecasting visualizations
├── config/
│   ├── ml_config.json             # ML model configuration
│   └── analytics_config.json      # Analytics parameters
└── reports/
    ├── executive_summary.py       # Executive reporting
    ├── technical_analysis.py      # Technical deep-dive reports
    └── optimization_report.py     # Optimization recommendations
```

## Core Implementation Components

### 1. Historical Trend Analyzer

**File:** `analytics/models/trend_analyzer.py`

```python
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import sqlite3
from dataclasses import dataclass
from statsmodels.tsa.seasonal import seasonal_decompose
from sklearn.preprocessing import StandardScaler
import json

@dataclass
class TrendMetrics:
    """Comprehensive trend analysis metrics"""
    overall_trend: str  # 'improving', 'declining', 'stable'
    trend_strength: float  # 0.0 to 1.0
    seasonal_patterns: Dict[str, float]
    quality_trajectory: List[float]
    performance_trajectory: List[float]
    confidence_interval: Tuple[float, float]
    significant_changes: List[Dict]

class HistoricalTrendAnalyzer:
    """Advanced historical trend analysis for model behavior"""
    
    def __init__(self, db_path: str, config_path: str = "analytics/config/analytics_config.json"):
        self.db_path = db_path
        self.config = self._load_config(config_path)
        self.scaler = StandardScaler()
        
    def _load_config(self, config_path: str) -> Dict:
        """Load analytics configuration"""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return self._default_config()
    
    def _default_config(self) -> Dict:
        """Default analytics configuration"""
        return {
            "trend_analysis": {
                "min_data_points": 50,
                "seasonal_period": 7,  # Weekly patterns
                "significance_threshold": 0.05,
                "confidence_level": 0.95
            },
            "quality_metrics": {
                "response_time_weight": 0.3,
                "accuracy_weight": 0.4,
                "consistency_weight": 0.3
            },
            "pattern_detection": {
                "anomaly_threshold": 2.5,  # Standard deviations
                "pattern_min_length": 5,
                "correlation_threshold": 0.7
            }
        }
    
    def analyze_historical_trends(self, days_back: int = 30) -> TrendMetrics:
        """Comprehensive historical trend analysis"""
        data = self._load_historical_data(days_back)
        
        if len(data) < self.config["trend_analysis"]["min_data_points"]:
            raise ValueError(f"Insufficient data points: {len(data)}")
        
        # Calculate trend components
        quality_trend = self._calculate_quality_trend(data)
        performance_trend = self._calculate_performance_trend(data)
        seasonal_patterns = self._detect_seasonal_patterns(data)
        significant_changes = self._detect_significant_changes(data)
        
        # Overall trend assessment
        overall_trend = self._assess_overall_trend(quality_trend, performance_trend)
        trend_strength = self._calculate_trend_strength(data)
        confidence_interval = self._calculate_confidence_interval(data)
        
        return TrendMetrics(
            overall_trend=overall_trend,
            trend_strength=trend_strength,
            seasonal_patterns=seasonal_patterns,
            quality_trajectory=quality_trend,
            performance_trajectory=performance_trend,
            confidence_interval=confidence_interval,
            significant_changes=significant_changes
        )
    
    def _load_historical_data(self, days_back: int) -> pd.DataFrame:
        """Load historical data from SQLite database"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        
        query = """
        SELECT 
            timestamp,
            provider,
            query_category,
            response_time,
            quality_score,
            success,
            tokens_used,
            hallucination_detected,
            consistency_score
        FROM test_results 
        WHERE timestamp >= ? AND timestamp <= ?
        ORDER BY timestamp
        """
        
        conn = sqlite3.connect(self.db_path)
        data = pd.read_sql_query(query, conn, params=[start_date, end_date])
        conn.close()
        
        data['timestamp'] = pd.to_datetime(data['timestamp'])
        data['date'] = data['timestamp'].dt.date
        data['hour'] = data['timestamp'].dt.hour
        data['day_of_week'] = data['timestamp'].dt.dayofweek
        
        return data
    
    def _calculate_quality_trend(self, data: pd.DataFrame) -> List[float]:
        """Calculate quality trend over time"""
        daily_quality = data.groupby('date').agg({
            'quality_score': 'mean',
            'success': 'mean',
            'hallucination_detected': lambda x: 1 - x.mean(),  # Invert for quality
            'consistency_score': 'mean'
        })
        
        # Weighted quality score
        weights = self.config["quality_metrics"]
        daily_quality['composite_quality'] = (
            daily_quality['quality_score'] * weights['accuracy_weight'] +
            daily_quality['success'] * weights['response_time_weight'] +
            daily_quality['consistency_score'] * weights['consistency_weight']
        )
        
        return daily_quality['composite_quality'].tolist()
    
    def _calculate_performance_trend(self, data: pd.DataFrame) -> List[float]:
        """Calculate performance trend over time"""
        daily_performance = data.groupby('date').agg({
            'response_time': 'mean',
            'tokens_used': 'mean'
        })
        
        # Normalize and invert response time (lower is better)
        normalized_time = 1 - self.scaler.fit_transform(
            daily_performance[['response_time']].fillna(0)
        ).flatten()
        
        return normalized_time.tolist()
    
    def _detect_seasonal_patterns(self, data: pd.DataFrame) -> Dict[str, float]:
        """Detect seasonal patterns in model behavior"""
        if len(data) < 14:  # Need at least 2 weeks for weekly patterns
            return {}
        
        try:
            daily_quality = data.groupby('date')['quality_score'].mean()
            
            if len(daily_quality) >= 14:
                decomposition = seasonal_decompose(
                    daily_quality, 
                    model='additive', 
                    period=7
                )
                
                seasonal_strength = np.std(decomposition.seasonal) / np.std(daily_quality)
                
                # Day of week patterns
                hourly_patterns = data.groupby('hour')['quality_score'].mean()
                daily_patterns = data.groupby('day_of_week')['quality_score'].mean()
                
                return {
                    "seasonal_strength": float(seasonal_strength),
                    "best_hour": int(hourly_patterns.idxmax()),
                    "worst_hour": int(hourly_patterns.idxmin()),
                    "best_day": int(daily_patterns.idxmax()),
                    "worst_day": int(daily_patterns.idxmin()),
                    "hour_variation": float(hourly_patterns.std()),
                    "day_variation": float(daily_patterns.std())
                }
        except Exception as e:
            print(f"Error in seasonal analysis: {e}")
            return {}
    
    def _detect_significant_changes(self, data: pd.DataFrame) -> List[Dict]:
        """Detect significant changes in model behavior"""
        daily_metrics = data.groupby('date').agg({
            'quality_score': 'mean',
            'response_time': 'mean',
            'success': 'mean'
        })
        
        changes = []
        threshold = self.config["trend_analysis"]["significance_threshold"]
        
        for metric in ['quality_score', 'response_time', 'success']:
            series = daily_metrics[metric].dropna()
            if len(series) < 5:
                continue
                
            # Calculate rolling statistics
            rolling_mean = series.rolling(window=3).mean()
            rolling_std = series.rolling(window=3).std()
            
            # Detect significant deviations
            z_scores = np.abs((series - rolling_mean) / rolling_std)
            significant_points = z_scores > threshold
            
            for date, is_significant in significant_points.items():
                if is_significant and not pd.isna(z_scores[date]):
                    changes.append({
                        "date": str(date),
                        "metric": metric,
                        "value": float(series[date]),
                        "z_score": float(z_scores[date]),
                        "significance": "high" if z_scores[date] > 3 else "moderate"
                    })
        
        return sorted(changes, key=lambda x: x['z_score'], reverse=True)
    
    def _assess_overall_trend(self, quality_trend: List[float], 
                            performance_trend: List[float]) -> str:
        """Assess overall trend direction"""
        if len(quality_trend) < 3:
            return "insufficient_data"
        
        # Linear regression on trends
        from scipy import stats
        
        x = np.arange(len(quality_trend))
        quality_slope, _, quality_r, quality_p, _ = stats.linregress(x, quality_trend)
        perf_slope, _, perf_r, perf_p, _ = stats.linregress(x, performance_trend)
        
        # Significance threshold
        sig_threshold = self.config["trend_analysis"]["significance_threshold"]
        
        quality_significant = quality_p < sig_threshold
        perf_significant = perf_p < sig_threshold
        
        if quality_significant and quality_slope > 0.01:
            if perf_significant and perf_slope > 0.01:
                return "improving"
            elif perf_significant and perf_slope < -0.01:
                return "mixed"
            else:
                return "quality_improving"
        elif quality_significant and quality_slope < -0.01:
            return "declining"
        else:
            return "stable"
    
    def _calculate_trend_strength(self, data: pd.DataFrame) -> float:
        """Calculate strength of observed trends"""
        if len(data) < 5:
            return 0.0
        
        daily_quality = data.groupby('date')['quality_score'].mean()
        
        if len(daily_quality) < 3:
            return 0.0
        
        # Calculate R-squared for linear trend
        from scipy import stats
        x = np.arange(len(daily_quality))
        _, _, r_value, _, _ = stats.linregress(x, daily_quality)
        
        return float(abs(r_value))
    
    def _calculate_confidence_interval(self, data: pd.DataFrame) -> Tuple[float, float]:
        """Calculate confidence interval for predictions"""
        daily_quality = data.groupby('date')['quality_score'].mean()
        
        if len(daily_quality) < 3:
            return (0.0, 1.0)
        
        mean_quality = daily_quality.mean()
        std_quality = daily_quality.std()
        
        confidence_level = self.config["trend_analysis"]["confidence_level"]
        margin = stats.norm.ppf((1 + confidence_level) / 2) * std_quality / np.sqrt(len(daily_quality))
        
        return (
            float(max(0, mean_quality - margin)),
            float(min(1, mean_quality + margin))
        )
```

### 2. Predictive Models System

**File:** `analytics/models/predictive_models.py`

```python
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, GradientBoostingClassifier
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_squared_error, accuracy_score, classification_report
import joblib
from typing import Dict, List, Tuple, Optional
import sqlite3
from datetime import datetime, timedelta
import json

class QualityPredictor:
    """Predict future quality degradation using machine learning"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.model = GradientBoostingClassifier(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()
        self.label_encoder = LabelEncoder()
        self.feature_names = []
        self.is_trained = False
        
    def prepare_features(self, data: pd.DataFrame) -> np.ndarray:
        """Prepare features for quality prediction"""
        features = []
        
        # Time-based features
        data['hour'] = data['timestamp'].dt.hour
        data['day_of_week'] = data['timestamp'].dt.dayofweek
        data['is_weekend'] = data['day_of_week'].isin([5, 6]).astype(int)
        
        # Historical performance features
        data = data.sort_values('timestamp')
        data['quality_ma_3'] = data['quality_score'].rolling(3).mean()
        data['quality_ma_7'] = data['quality_score'].rolling(7).mean()
        data['response_time_ma_3'] = data['response_time'].rolling(3).mean()
        
        # Provider performance
        provider_quality = data.groupby('provider')['quality_score'].transform('mean')
        data['provider_avg_quality'] = provider_quality
        
        # Query complexity indicators
        data['query_length'] = data['query'].str.len()
        data['is_code_generation'] = data['query_category'].eq('code_generation').astype(int)
        
        feature_columns = [
            'hour', 'day_of_week', 'is_weekend',
            'quality_ma_3', 'quality_ma_7', 'response_time_ma_3',
            'provider_avg_quality', 'query_length', 'is_code_generation',
            'response_time', 'tokens_used'
        ]
        
        self.feature_names = feature_columns
        return data[feature_columns].fillna(data[feature_columns].mean())
    
    def train_model(self, days_back: int = 30) -> Dict:
        """Train the quality prediction model"""
        data = self._load_training_data(days_back)
        
        if len(data) < 100:
            raise ValueError("Insufficient training data")
        
        # Prepare features and targets
        X = self.prepare_features(data)
        X_scaled = self.scaler.fit_transform(X)
        
        # Create quality degradation labels
        y = (data['quality_score'] < 0.7).astype(int)  # 1 = poor quality
        
        # Train-test split
        X_train, X_test, y_train, y_test = train_test_split(
            X_scaled, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Train model
        self.model.fit(X_train, y_train)
        
        # Evaluate
        train_score = self.model.score(X_train, y_train)
        test_score = self.model.score(X_test, y_test)
        
        # Cross-validation
        cv_scores = cross_val_score(self.model, X_scaled, y, cv=5)
        
        self.is_trained = True
        
        return {
            "train_accuracy": train_score,
            "test_accuracy": test_score,
            "cv_mean": cv_scores.mean(),
            "cv_std": cv_scores.std(),
            "feature_importance": dict(zip(
                self.feature_names, 
                self.model.feature_importances_
            ))
        }
    
    def predict_quality_risk(self, recent_data: pd.DataFrame) -> Dict:
        """Predict quality degradation risk"""
        if not self.is_trained:
            raise ValueError("Model not trained. Call train_model() first.")
        
        X = self.prepare_features(recent_data)
        X_scaled = self.scaler.transform(X)
        
        # Predict probabilities
        probabilities = self.model.predict_proba(X_scaled)
        risk_scores = probabilities[:, 1]  # Probability of poor quality
        
        # Risk categories
        high_risk = risk_scores > 0.7
        medium_risk = (risk_scores > 0.4) & (risk_scores <= 0.7)
        low_risk = risk_scores <= 0.4
        
        return {
            "overall_risk": float(risk_scores.mean()),
            "high_risk_queries": int(high_risk.sum()),
            "medium_risk_queries": int(medium_risk.sum()),
            "low_risk_queries": int(low_risk.sum()),
            "risk_by_provider": self._analyze_risk_by_provider(recent_data, risk_scores),
            "top_risk_factors": self._get_top_risk_factors()
        }
    
    def _load_training_data(self, days_back: int) -> pd.DataFrame:
        """Load training data from database"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        
        query = """
        SELECT * FROM test_results 
        WHERE timestamp >= ? AND timestamp <= ?
        ORDER BY timestamp
        """
        
        conn = sqlite3.connect(self.db_path)
        data = pd.read_sql_query(query, conn, params=[start_date, end_date])
        conn.close()
        
        data['timestamp'] = pd.to_datetime(data['timestamp'])
        return data
    
    def _analyze_risk_by_provider(self, data: pd.DataFrame, 
                                 risk_scores: np.ndarray) -> Dict:
        """Analyze risk scores by provider"""
        data = data.copy()
        data['risk_score'] = risk_scores
        
        provider_risk = data.groupby('provider')['risk_score'].agg([
            'mean', 'std', 'count'
        ]).round(3)
        
        return provider_risk.to_dict('index')
    
    def _get_top_risk_factors(self) -> List[Dict]:
        """Get top risk factors from feature importance"""
        if not hasattr(self.model, 'feature_importances_'):
            return []
        
        importance_pairs = list(zip(self.feature_names, self.model.feature_importances_))
        importance_pairs.sort(key=lambda x: x[1], reverse=True)
        
        return [
            {"feature": name, "importance": float(importance)}
            for name, importance in importance_pairs[:5]
        ]
    
    def save_model(self, path: str):
        """Save trained model to disk"""
        if not self.is_trained:
            raise ValueError("No trained model to save")
        
        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'feature_names': self.feature_names,
            'is_trained': self.is_trained
        }
        
        joblib.dump(model_data, path)
    
    def load_model(self, path: str):
        """Load trained model from disk"""
        model_data = joblib.load(path)
        
        self.model = model_data['model']
        self.scaler = model_data['scaler']
        self.feature_names = model_data['feature_names']
        self.is_trained = model_data['is_trained']
```

### 3. Pattern Detection Engine

**File:** `analytics/models/pattern_detector.py`

```python
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import sqlite3
from datetime import datetime, timedelta
import json

class BehaviorPatternDetector:
    """Detect patterns and anomalies in model behavior"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.scaler = StandardScaler()
        self.pca = PCA(n_components=3)
        
    def detect_anomalies(self, days_back: int = 7) -> Dict:
        """Detect anomalous behavior patterns"""
        data = self._load_recent_data(days_back)
        
        if len(data) < 20:
            return {"error": "Insufficient data for anomaly detection"}
        
        # Prepare features for anomaly detection
        features = self._prepare_anomaly_features(data)
        features_scaled = self.scaler.fit_transform(features)
        
        # Use DBSCAN for anomaly detection
        clustering = DBSCAN(eps=0.5, min_samples=5)
        clusters = clustering.fit_predict(features_scaled)
        
        # Identify anomalies (cluster label -1)
        anomalies = data[clusters == -1].copy()
        
        if len(anomalies) == 0:
            return {
                "anomalies_found": 0,
                "anomaly_rate": 0.0,
                "patterns": []
            }
        
        # Analyze anomaly patterns
        anomaly_patterns = self._analyze_anomaly_patterns(anomalies)
        
        return {
            "anomalies_found": len(anomalies),
            "anomaly_rate": len(anomalies) / len(data),
            "patterns": anomaly_patterns,
            "affected_providers": anomalies['provider'].unique().tolist(),
            "time_distribution": self._analyze_time_distribution(anomalies),
            "severity_distribution": self._analyze_severity(anomalies)
        }
    
    def detect_recurring_patterns(self, days_back: int = 30) -> Dict:
        """Detect recurring patterns in model behavior"""
        data = self._load_recent_data(days_back)
        
        if len(data) < 50:
            return {"error": "Insufficient data for pattern detection"}
        
        patterns = {
            "temporal_patterns": self._detect_temporal_patterns(data),
            "provider_patterns": self._detect_provider_patterns(data),
            "query_patterns": self._detect_query_patterns(data),
            "performance_patterns": self._detect_performance_patterns(data)
        }
        
        return patterns
    
    def _load_recent_data(self, days_back: int) -> pd.DataFrame:
        """Load recent data for pattern analysis"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        
        query = """
        SELECT 
            timestamp, provider, query_category, query,
            response_time, quality_score, success,
            tokens_used, hallucination_detected
        FROM test_results 
        WHERE timestamp >= ? AND timestamp <= ?
        ORDER BY timestamp
        """
        
        conn = sqlite3.connect(self.db_path)
        data = pd.read_sql_query(query, conn, params=[start_date, end_date])
        conn.close()
        
        data['timestamp'] = pd.to_datetime(data['timestamp'])
        data['hour'] = data['timestamp'].dt.hour
        data['day_of_week'] = data['timestamp'].dt.dayofweek
        
        return data
    
    def _prepare_anomaly_features(self, data: pd.DataFrame) -> np.ndarray:
        """Prepare features for anomaly detection"""
        # Numerical features
        numerical_features = [
            'response_time', 'quality_score', 'tokens_used',
            'hour', 'day_of_week'
        ]
        
        features = data[numerical_features].fillna(data[numerical_features].mean())
        
        # Add derived features
        features['response_time_zscore'] = np.abs(
            (features['response_time'] - features['response_time'].mean()) / 
            features['response_time'].std()
        )
        
        features['quality_deviation'] = np.abs(
            features['quality_score'] - features['quality_score'].rolling(5).mean()
        )
        
        return features.fillna(0)
    
    def _analyze_anomaly_patterns(self, anomalies: pd.DataFrame) -> List[Dict]:
        """Analyze patterns in detected anomalies"""
        patterns = []
        
        # Provider-based patterns
        provider_counts = anomalies['provider'].value_counts()
        for provider, count in provider_counts.items():
            if count >= 3:  # At least 3 anomalies
                patterns.append({
                    "type": "provider_anomaly",
                    "provider": provider,
                    "count": int(count),
                    "description": f"Multiple anomalies detected for provider {provider}"
                })
        
        # Time-based patterns
        hour_counts = anomalies['hour'].value_counts()
        for hour, count in hour_counts.items():
            if count >= 3:
                patterns.append({
                    "type": "temporal_anomaly",
                    "hour": int(hour),
                    "count": int(count),
                    "description": f"Anomalies clustered around hour {hour}"
                })
        
        # Quality-based patterns
        low_quality = anomalies[anomalies['quality_score'] < 0.5]
        if len(low_quality) >= 3:
            patterns.append({
                "type": "quality_anomaly",
                "count": len(low_quality),
                "avg_quality": float(low_quality['quality_score'].mean()),
                "description": "Multiple low-quality responses detected"
            })
        
        return patterns
    
    def _detect_temporal_patterns(self, data: pd.DataFrame) -> Dict:
        """Detect temporal patterns in behavior"""
        hourly_quality = data.groupby('hour')['quality_score'].mean()
        daily_quality = data.groupby('day_of_week')['quality_score'].mean()
        
        # Find best and worst times
        best_hour = hourly_quality.idxmax()
        worst_hour = hourly_quality.idxmin()
        best_day = daily_quality.idxmax()
        worst_day = daily_quality.idxmin()
        
        # Calculate variability
        hour_variance = hourly_quality.var()
        day_variance = daily_quality.var()
        
        return {
            "hourly_patterns": {
                "best_hour": int(best_hour),
                "worst_hour": int(worst_hour),
                "quality_variance": float(hour_variance),
                "peak_performance_time": "morning" if best_hour < 12 else "afternoon"
            },
            "daily_patterns": {
                "best_day": int(best_day),
                "worst_day": int(worst_day),
                "quality_variance": float(day_variance),
                "weekend_effect": self._calculate_weekend_effect(data)
            }
        }
    
    def _detect_provider_patterns(self, data: pd.DataFrame) -> Dict:
        """Detect provider-specific patterns"""
        provider_stats = data.groupby('provider').agg({
            'quality_score': ['mean', 'std'],
            'response_time': ['mean', 'std'],
            'success': 'mean',
            'hallucination_detected': 'mean'
        }).round(3)
        
        # Flatten column names
        provider_stats.columns = ['_'.join(col).strip() for col in provider_stats.columns]
        
        # Identify best and worst performers
        best_quality = provider_stats['quality_score_mean'].idxmax()
        worst_quality = provider_stats['quality_score_mean'].idxmin()
        fastest = provider_stats['response_time_mean'].idxmin()
        slowest = provider_stats['response_time_mean'].idxmax()
        
        return {
            "provider_rankings": {
                "best_quality": best_quality,
                "worst_quality": worst_quality,
                "fastest": fastest,
                "slowest": slowest
            },
            "provider_stats": provider_stats.to_dict('index'),
            "consistency_analysis": self._analyze_provider_consistency(data)
        }
    
    def _detect_query_patterns(self, data: pd.DataFrame) -> Dict:
        """Detect query category patterns"""
        category_stats = data.groupby('query_category').agg({
            'quality_score': 'mean',
            'response_time': 'mean',
            'success': 'mean',
            'hallucination_detected': 'mean'
        }).round(3)
        
        # Find challenging categories
        difficult_categories = category_stats[
            (category_stats['quality_score'] < 0.7) | 
            (category_stats['success'] < 0.9)
        ]
        
        return {
            "category_performance": category_stats.to_dict('index'),
            "difficult_categories": difficult_categories.index.tolist(),
            "query_complexity_analysis": self._analyze_query_complexity(data)
        }
    
    def _detect_performance_patterns(self, data: pd.DataFrame) -> Dict:
        """Detect performance degradation patterns"""
        # Rolling averages for trend detection
        data_sorted = data.sort_values('timestamp')
        data_sorted['quality_ma'] = data_sorted['quality_score'].rolling(10).mean()
        data_sorted['response_ma'] = data_sorted['response_time'].rolling(10).mean()
        
        # Detect trends
        recent_quality = data_sorted['quality_ma'].tail(20).mean()
        historical_quality = data_sorted['quality_ma'].head(20).mean()
        
        quality_trend = "improving" if recent_quality > historical_quality else "declining"
        
        # Performance alerts
        alerts = []
        if recent_quality < 0.7:
            alerts.append("Quality degradation detected")
        if data_sorted['response_time'].tail(10).mean() > data_sorted['response_time'].mean() * 1.5:
            alerts.append("Response time degradation detected")
        
        return {
            "quality_trend": quality_trend,
            "recent_quality": float(recent_quality),
            "historical_quality": float(historical_quality),
            "performance_alerts": alerts,
            "degradation_risk": self._calculate_degradation_risk(data_sorted)
        }
    
    def _calculate_weekend_effect(self, data: pd.DataFrame) -> float:
        """Calculate weekend vs weekday performance difference"""
        weekday_quality = data[data['day_of_week'] < 5]['quality_score'].mean()
        weekend_quality = data[data['day_of_week'] >= 5]['quality_score'].mean()
        
        return float(weekend_quality - weekday_quality)
    
    def _analyze_provider_consistency(self, data: pd.DataFrame) -> Dict:
        """Analyze consistency across providers"""
        provider_consistency = data.groupby('provider')['quality_score'].std()
        
        most_consistent = provider_consistency.idxmin()
        least_consistent = provider_consistency.idxmax()
        
        return {
            "most_consistent": most_consistent,
            "least_consistent": least_consistent,
            "consistency_scores": provider_consistency.to_dict()
        }
    
    def _analyze_query_complexity(self, data: pd.DataFrame) -> Dict:
        """Analyze relationship between query complexity and performance"""
        data['query_length'] = data['query'].str.len()
        
        # Correlation analysis
        length_quality_corr = data['query_length'].corr(data['quality_score'])
        length_time_corr = data['query_length'].corr(data['response_time'])
        
        return {
            "length_quality_correlation": float(length_quality_corr),
            "length_time_correlation": float(length_time_corr),
            "complexity_impact": "high" if abs(length_quality_corr) > 0.3 else "low"
        }
    
    def _calculate_degradation_risk(self, data: pd.DataFrame) -> str:
        """Calculate risk of performance degradation"""
        recent_data = data.tail(20)
        
        quality_declining = recent_data['quality_score'].is_monotonic_decreasing
        time_increasing = recent_data['response_time'].is_monotonic_increasing
        
        if quality_declining and time_increasing:
            return "high"
        elif quality_declining or time_increasing:
            return "medium"
        else:
            return "low"
    
    def _analyze_time_distribution(self, anomalies: pd.DataFrame) -> Dict:
        """Analyze time distribution of anomalies"""
        hour_dist = anomalies['hour'].value_counts().to_dict()
        day_dist = anomalies['day_of_week'].value_counts().to_dict()
        
        return {
            "by_hour": hour_dist,
            "by_day": day_dist
        }
    
    def _analyze_severity(self, anomalies: pd.DataFrame) -> Dict:
        """Analyze severity distribution of anomalies"""
        severe = len(anomalies[anomalies['quality_score'] < 0.3])
        moderate = len(anomalies[(anomalies['quality_score'] >= 0.3) & (anomalies['quality_score'] < 0.6)])
        mild = len(anomalies[anomalies['quality_score'] >= 0.6])
        
        return {
            "severe": severe,
            "moderate": moderate,
            "mild": mild
        }
```

### 4. Optimization Engine

**File:** `analytics/models/optimization_engine.py`

```python
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
import sqlite3
from datetime import datetime, timedelta
import json
from dataclasses import dataclass

@dataclass
class OptimizationRecommendation:
    """Optimization recommendation with priority and impact"""
    category: str
    title: str
    description: str
    priority: str  # high, medium, low
    estimated_impact: float  # 0.0 to 1.0
    implementation_effort: str  # low, medium, high
    specific_actions: List[str]
    expected_improvement: Dict[str, float]

class ModelOptimizationEngine:
    """Generate data-driven optimization recommendations"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        
    def generate_comprehensive_recommendations(self, 
                                            analysis_days: int = 30) -> List[OptimizationRecommendation]:
        """Generate comprehensive optimization recommendations"""
        data = self._load_analysis_data(analysis_days)
        
        if len(data) < 50:
            return [OptimizationRecommendation(
                category="data_collection",
                title="Insufficient Data",
                description="Need more data for meaningful optimization recommendations",
                priority="high",
                estimated_impact=0.0,
                implementation_effort="low",
                specific_actions=["Continue automated testing", "Increase test frequency"],
                expected_improvement={"data_quality": 1.0}
            )]
        
        recommendations = []
        
        # Provider optimization recommendations
        recommendations.extend(self._analyze_provider_optimization(data))
        
        # Temporal optimization recommendations
        recommendations.extend(self._analyze_temporal_optimization(data))
        
        # Query optimization recommendations
        recommendations.extend(self._analyze_query_optimization(data))
        
        # Performance optimization recommendations
        recommendations.extend(self._analyze_performance_optimization(data))
        
        # System architecture recommendations
        recommendations.extend(self._analyze_architecture_optimization(data))
        
        # Sort by priority and estimated impact
        recommendations.sort(key=lambda x: (
            {"high": 3, "medium": 2, "low": 1}[x.priority],
            x.estimated_impact
        ), reverse=True)
        
        return recommendations
    
    def _load_analysis_data(self, days_back: int) -> pd.DataFrame:
        """Load data for optimization analysis"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        
        query = """
        SELECT 
            timestamp, provider, query_category, query,
            response_time, quality_score, success,
            tokens_used, hallucination_detected, consistency_score
        FROM test_results 
        WHERE timestamp >= ? AND timestamp <= ?
        ORDER BY timestamp
        """
        
        conn = sqlite3.connect(self.db_path)
        data = pd.read_sql_query(query, conn, params=[start_date, end_date])
        conn.close()
        
        data['timestamp'] = pd.to_datetime(data['timestamp'])
        data['hour'] = data['timestamp'].dt.hour
        data['day_of_week'] = data['timestamp'].dt.dayofweek
        
        return data
    
    def _analyze_provider_optimization(self, data: pd.DataFrame) -> List[OptimizationRecommendation]:
        """Analyze provider performance for optimization"""
        recommendations = []
        
        provider_stats = data.groupby('provider').agg({
            'quality_score': ['mean', 'std', 'count'],
            'response_time': ['mean', 'std'],
            'success': 'mean',
            'hallucination_detected': 'mean'
        })
        
        # Flatten column names
        provider_stats.columns = ['_'.join(col).strip() for col in provider_stats.columns]
        
        # Find underperforming providers
        quality_threshold = provider_stats['quality_score_mean'].median()
        underperforming = provider_stats[
            provider_stats['quality_score_mean'] < quality_threshold
        ]
        
        if len(underperforming) > 0:
            worst_provider = provider_stats['quality_score_mean'].idxmin()
            worst_quality = provider_stats.loc[worst_provider, 'quality_score_mean']
            best_quality = provider_stats['quality_score_mean'].max()
            
            improvement_potential = best_quality - worst_quality
            
            recommendations.append(OptimizationRecommendation(
                category="provider_optimization",
                title=f"Optimize {worst_provider} Provider Performance",
                description=f"Provider {worst_provider} shows quality score of {worst_quality:.3f}, "
                           f"significantly below best performer ({best_quality:.3f})",
                priority="high" if improvement_potential > 0.2 else "medium",
                estimated_impact=improvement_potential,
                implementation_effort="medium",
                specific_actions=[
                    f"Review {worst_provider} system prompts and configuration",
                    "Analyze failure patterns for this provider",
                    "Consider model parameter tuning",
                    "Implement provider-specific optimizations"
                ],
                expected_improvement={
                    "quality_score": improvement_potential * 0.7,
                    "consistency": 0.15
                }
            ))
        
        # High variability providers
        high_variability = provider_stats[
            provider_stats['quality_score_std'] > provider_stats['quality_score_std'].median() * 1.5
        ]
        
        for provider in high_variability.index:
            variability = provider_stats.loc[provider, 'quality_score_std']
            
            recommendations.append(OptimizationRecommendation(
                category="consistency_optimization",
                title=f"Improve {provider} Consistency",
                description=f"Provider {provider} shows high variability "
                           f"(std: {variability:.3f}) in quality scores",
                priority="medium",
                estimated_impact=0.25,
                implementation_effort="medium",
                specific_actions=[
                    "Analyze inconsistent responses from this provider",
                    "Implement response validation",
                    "Add consistency monitoring",
                    "Review prompt engineering approaches"
                ],
                expected_improvement={
                    "consistency": 0.3,
                    "reliability": 0.2
                }
            ))
        
        return recommendations
    
    def _analyze_temporal_optimization(self, data: pd.DataFrame) -> List[OptimizationRecommendation]:
        """Analyze temporal patterns for optimization"""
        recommendations = []
        
        # Hourly performance analysis
        hourly_quality = data.groupby('hour')['quality_score'].mean()
        hourly_time = data.groupby('hour')['response_time'].mean()
        
        # Find poor performance hours
        quality_threshold = hourly_quality.median() - hourly_quality.std()
        poor_hours = hourly_quality[hourly_quality < quality_threshold]
        
        if len(poor_hours) > 0:
            worst_hours = poor_hours.index.tolist()
            
            recommendations.append(OptimizationRecommendation(
                category="temporal_optimization",
                title="Optimize Performance During Poor Hours",
                description=f"Quality significantly drops during hours: {worst_hours}",
                priority="medium",
                estimated_impact=0.15,
                implementation_effort="low",
                specific_actions=[
                    f"Investigate what causes poor performance at hours {worst_hours}",
                    "Consider different model parameters for these time periods",
                    "Implement time-based prompt variations",
                    "Add performance monitoring alerts for these hours"
                ],
                expected_improvement={
                    "quality_score": 0.15,
                    "temporal_consistency": 0.25
                }
            ))
        
        # Weekend vs weekday analysis
        weekday_quality = data[data['day_of_week'] < 5]['quality_score'].mean()
        weekend_quality = data[data['day_of_week'] >= 5]['quality_score'].mean()
        
        if abs(weekend_quality - weekday_quality) > 0.1:
            recommendations.append(OptimizationRecommendation(
                category="temporal_optimization",
                title="Address Weekend Performance Difference",
                description=f"Significant quality difference between weekdays ({weekday_quality:.3f}) "
                           f"and weekends ({weekend_quality:.3f})",
                priority="low",
                estimated_impact=0.1,
                implementation_effort="low",
                specific_actions=[
                    "Analyze weekend vs weekday usage patterns",
                    "Consider different configurations for weekends",
                    "Monitor for external factors affecting weekend performance"
                ],
                expected_improvement={
                    "temporal_consistency": 0.2
                }
            ))
        
        return recommendations
    
    def _analyze_query_optimization(self, data: pd.DataFrame) -> List[OptimizationRecommendation]:
        """Analyze query categories for optimization"""
        recommendations = []
        
        category_stats = data.groupby('query_category').agg({
            'quality_score': ['mean', 'std', 'count'],
            'response_time': 'mean',
            'success': 'mean',
            'hallucination_detected': 'mean'
        })
        
        category_stats.columns = ['_'.join(col).strip() for col in category_stats.columns]
        
        # Find problematic categories
        quality_threshold = 0.7
        problematic_categories = category_stats[
            (category_stats['quality_score_mean'] < quality_threshold) |
            (category_stats['success_mean'] < 0.9) |
            (category_stats['hallucination_detected_mean'] > 0.1)
        ]
        
        for category in problematic_categories.index:
            stats = category_stats.loc[category]
            issues = []
            
            if stats['quality_score_mean'] < quality_threshold:
                issues.append(f"low quality ({stats['quality_score_mean']:.3f})")
            if stats['success_mean'] < 0.9:
                issues.append(f"high failure rate ({1-stats['success_mean']:.1%})")
            if stats['hallucination_detected_mean'] > 0.1:
                issues.append(f"frequent hallucinations ({stats['hallucination_detected_mean']:.1%})")
            
            recommendations.append(OptimizationRecommendation(
                category="query_optimization",
                title=f"Optimize {category} Query Handling",
                description=f"Category '{category}' shows issues: {', '.join(issues)}",
                priority="high" if len(issues) > 1 else "medium",
                estimated_impact=0.3 if len(issues) > 1 else 0.2,
                implementation_effort="medium",
                specific_actions=[
                    f"Develop specialized prompts for {category} queries",
                    "Analyze failed queries in this category",
                    "Consider category-specific model fine-tuning",
                    "Implement category-specific validation"
                ],
                expected_improvement={
                    "category_quality": 0.25,
                    "success_rate": 0.15
                }
            ))
        
        return recommendations
    
    def _analyze_performance_optimization(self, data: pd.DataFrame) -> List[OptimizationRecommendation]:
        """Analyze overall performance for optimization"""
        recommendations = []
        
        # Response time analysis
        avg_response_time = data['response_time'].mean()
        p95_response_time = data['response_time'].quantile(0.95)
        
        if avg_response_time > 5.0:  # 5 seconds threshold
            recommendations.append(OptimizationRecommendation(
                category="performance_optimization",
                title="Optimize Response Times",
                description=f"Average response time ({avg_response_time:.2f}s) exceeds recommended threshold",
                priority="high",
                estimated_impact=0.4,
                implementation_effort="high",
                specific_actions=[
                    "Profile slow queries and identify bottlenecks",
                    "Optimize model parameters for speed",
                    "Consider caching frequently requested responses",
                    "Implement response streaming where appropriate"
                ],
                expected_improvement={
                    "response_time": 0.3,
                    "user_experience": 0.4
                }
            ))
        
        # Quality consistency analysis
        quality_std = data['quality_score'].std()
        if quality_std > 0.2:
            recommendations.append(OptimizationRecommendation(
                category="quality_optimization",
                title="Improve Quality Consistency",
                description=f"High quality variability (std: {quality_std:.3f}) across responses",
                priority="medium",
                estimated_impact=0.25,
                implementation_effort="medium",
                specific_actions=[
                    "Implement quality validation pipelines",
                    "Develop consistent prompt templates",
                    "Add response quality scoring",
                    "Monitor for quality regressions"
                ],
                expected_improvement={
                    "consistency": 0.3,
                    "quality_score": 0.15
                }
            ))
        
        return recommendations
    
    def _analyze_architecture_optimization(self, data: pd.DataFrame) -> List[OptimizationRecommendation]:
        """Analyze system architecture for optimization"""
        recommendations = []
        
        # Provider distribution analysis
        provider_usage = data['provider'].value_counts(normalize=True)
        
        # Check if load is balanced
        if len(provider_usage) > 1:
            max_usage = provider_usage.max()
            min_usage = provider_usage.min()
            
            if max_usage / min_usage > 3:  # Highly unbalanced
                recommendations.append(OptimizationRecommendation(
                    category="architecture_optimization",
                    title="Balance Provider Load Distribution",
                    description=f"Uneven provider usage distribution detected",
                    priority="medium",
                    estimated_impact=0.2,
                    implementation_effort="medium",
                    specific_actions=[
                        "Implement intelligent load balancing",
                        "Analyze provider selection patterns",
                        "Consider automatic failover mechanisms",
                        "Monitor provider health and availability"
                    ],
                    expected_improvement={
                        "system_reliability": 0.25,
                        "resource_utilization": 0.2
                    }
                ))
        
        # Error rate analysis
        error_rate = 1 - data['success'].mean()
        if error_rate > 0.05:  # 5% error threshold
            recommendations.append(OptimizationRecommendation(
                category="reliability_optimization",
                title="Reduce System Error Rate",
                description=f"Current error rate ({error_rate:.1%}) exceeds acceptable threshold",
                priority="high",
                estimated_impact=0.3,
                implementation_effort="high",
                specific_actions=[
                    "Implement comprehensive error handling",
                    "Add retry mechanisms for transient failures",
                    "Improve input validation",
                    "Monitor and alert on error spikes"
                ],
                expected_improvement={
                    "reliability": 0.4,
                    "success_rate": error_rate * 0.8
                }
            ))
        
        return recommendations
```

### 5. Executive Reporting System

**File:** `analytics/reports/executive_summary.py`

```python
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json
import sqlite3
from dataclasses import dataclass, asdict

@dataclass
class ExecutiveSummary:
    """Executive summary data structure"""
    reporting_period: str
    overall_health_score: float
    key_metrics: Dict[str, float]
    performance_trends: Dict[str, str]
    critical_issues: List[str]
    success_highlights: List[str]
    recommendations: List[str]
    provider_comparison: Dict[str, Dict]
    forecast: Dict[str, float]

class ExecutiveReportGenerator:
    """Generate executive-level reports and summaries"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        
    def generate_weekly_summary(self) -> ExecutiveSummary:
        """Generate weekly executive summary"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        
        return self._generate_summary(start_date, end_date, "Weekly")
    
    def generate_monthly_summary(self) -> ExecutiveSummary:
        """Generate monthly executive summary"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        return self._generate_summary(start_date, end_date, "Monthly")
    
    def _generate_summary(self, start_date: datetime, 
                         end_date: datetime, period: str) -> ExecutiveSummary:
        """Generate executive summary for given period"""
        data = self._load_summary_data(start_date, end_date)
        
        if len(data) == 0:
            return self._empty_summary(period)
        
        # Calculate key metrics
        key_metrics = self._calculate_key_metrics(data)
        
        # Assess overall health
        health_score = self._calculate_health_score(key_metrics)
        
        # Identify trends
        trends = self._identify_trends(data)
        
        # Find critical issues
        critical_issues = self._identify_critical_issues(data, key_metrics)
        
        # Highlight successes
        successes = self._identify_successes(data, key_metrics)
        
        # Generate recommendations
        recommendations = self._generate_executive_recommendations(
            data, key_metrics, critical_issues
        )
        
        # Provider comparison
        provider_comparison = self._generate_provider_comparison(data)
        
        # Forecast
        forecast = self._generate_forecast(data)
        
        return ExecutiveSummary(
            reporting_period=f"{period} ({start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')})",
            overall_health_score=health_score,
            key_metrics=key_metrics,
            performance_trends=trends,
            critical_issues=critical_issues,
            success_highlights=successes,
            recommendations=recommendations,
            provider_comparison=provider_comparison,
            forecast=forecast
        )
    
    def _load_summary_data(self, start_date: datetime, end_date: datetime) -> pd.DataFrame:
        """Load data for summary generation"""
        query = """
        SELECT 
            timestamp, provider, query_category,
            response_time, quality_score, success,
            tokens_used, hallucination_detected
        FROM test_results 
        WHERE timestamp >= ? AND timestamp <= ?
        ORDER BY timestamp
        """
        
        conn = sqlite3.connect(self.db_path)
        data = pd.read_sql_query(query, conn, params=[start_date, end_date])
        conn.close()
        
        if len(data) > 0:
            data['timestamp'] = pd.to_datetime(data['timestamp'])
        
        return data
    
    def _calculate_key_metrics(self, data: pd.DataFrame) -> Dict[str, float]:
        """Calculate key performance metrics"""
        return {
            "avg_quality_score": float(data['quality_score'].mean()),
            "avg_response_time": float(data['response_time'].mean()),
            "success_rate": float(data['success'].mean()),
            "total_queries": int(len(data)),
            "hallucination_rate": float(data['hallucination_detected'].mean()),
            "avg_tokens_per_query": float(data['tokens_used'].mean()),
            "quality_consistency": float(1 - data['quality_score'].std()),
            "provider_count": int(data['provider'].nunique())
        }
    
    def _calculate_health_score(self, metrics: Dict[str, float]) -> float:
        """Calculate overall system health score (0-100)"""
        weights = {
            "avg_quality_score": 0.3,
            "success_rate": 0.25,
            "quality_consistency": 0.2,
            "response_time_score": 0.15,
            "hallucination_score": 0.1
        }
        
        # Normalize response time (lower is better)
        response_time_score = max(0, 1 - (metrics["avg_response_time"] - 1) / 10)
        
        # Normalize hallucination rate (lower is better)
        hallucination_score = 1 - metrics["hallucination_rate"]
        
        normalized_metrics = {
            "avg_quality_score": metrics["avg_quality_score"],
            "success_rate": metrics["success_rate"],
            "quality_consistency": metrics["quality_consistency"],
            "response_time_score": response_time_score,
            "hallucination_score": hallucination_score
        }
        
        health_score = sum(
            normalized_metrics[metric] * weight 
            for metric, weight in weights.items()
        )
        
        return float(health_score * 100)
    
    def _identify_trends(self, data: pd.DataFrame) -> Dict[str, str]:
        """Identify performance trends"""
        if len(data) < 10:
            return {}
        
        # Sort by timestamp and calculate trends
        data_sorted = data.sort_values('timestamp')
        
        # Split into first and second half for comparison
        mid_point = len(data_sorted) // 2
        first_half = data_sorted.iloc[:mid_point]
        second_half = data_sorted.iloc[mid_point:]
        
        trends = {}
        
        # Quality trend
        quality_change = second_half['quality_score'].mean() - first_half['quality_score'].mean()
        if quality_change > 0.05:
            trends["quality"] = "improving"
        elif quality_change < -0.05:
            trends["quality"] = "declining"
        else:
            trends["quality"] = "stable"
        
        # Response time trend
        time_change = second_half['response_time'].mean() - first_half['response_time'].mean()
        if time_change > 0.5:
            trends["response_time"] = "slower"
        elif time_change < -0.5:
            trends["response_time"] = "faster"
        else:
            trends["response_time"] = "stable"
        
        # Success rate trend
        success_change = second_half['success'].mean() - first_half['success'].mean()
        if success_change > 0.02:
            trends["reliability"] = "improving"
        elif success_change < -0.02:
            trends["reliability"] = "declining"
        else:
            trends["reliability"] = "stable"
        
        return trends
    
    def _identify_critical_issues(self, data: pd.DataFrame, 
                                 metrics: Dict[str, float]) -> List[str]:
        """Identify critical issues requiring attention"""
        issues = []
        
        if metrics["avg_quality_score"] < 0.7:
            issues.append(f"Quality score below threshold ({metrics['avg_quality_score']:.3f})")
        
        if metrics["success_rate"] < 0.9:
            issues.append(f"Success rate below 90% ({metrics['success_rate']:.1%})")
        
        if metrics["avg_response_time"] > 10:
            issues.append(f"Average response time exceeds 10 seconds ({metrics['avg_response_time']:.1f}s)")
        
        if metrics["hallucination_rate"] > 0.1:
            issues.append(f"High hallucination rate detected ({metrics['hallucination_rate']:.1%})")
        
        # Provider-specific issues
        provider_success = data.groupby('provider')['success'].mean()
        failing_providers = provider_success[provider_success < 0.8]
        if len(failing_providers) > 0:
            issues.append(f"Provider reliability issues: {list(failing_providers.index)}")
        
        return issues
    
    def _identify_successes(self, data: pd.DataFrame, 
                           metrics: Dict[str, float]) -> List[str]:
        """Identify success highlights"""
        successes = []
        
        if metrics["avg_quality_score"] > 0.85:
            successes.append(f"Excellent quality score maintained ({metrics['avg_quality_score']:.3f})")
        
        if metrics["success_rate"] > 0.95:
            successes.append(f"High reliability achieved ({metrics['success_rate']:.1%})")
        
        if metrics["avg_response_time"] < 3:
            successes.append(f"Fast response times maintained ({metrics['avg_response_time']:.1f}s)")
        
        if metrics["hallucination_rate"] < 0.02:
            successes.append(f"Low hallucination rate achieved ({metrics['hallucination_rate']:.1%})")
        
        # Growth metrics
        if metrics["total_queries"] > 1000:
            successes.append(f"High system utilization ({metrics['total_queries']} queries processed)")
        
        return successes
    
    def _generate_executive_recommendations(self, data: pd.DataFrame,
                                          metrics: Dict[str, float],
                                          issues: List[str]) -> List[str]:
        """Generate executive-level recommendations"""
        recommendations = []
        
        if metrics["avg_quality_score"] < 0.8:
            recommendations.append("Immediate quality improvement initiative recommended")
        
        if metrics["avg_response_time"] > 5:
            recommendations.append("Performance optimization should be prioritized")
        
        if len(issues) > 2:
            recommendations.append("Consider comprehensive system review and optimization")
        
        # Provider diversification
        if metrics["provider_count"] < 2:
            recommendations.append("Consider provider diversification for improved reliability")
        
        # Capacity planning
        if metrics["total_queries"] > 5000:
            recommendations.append("Evaluate system capacity for continued growth")
        
        return recommendations
    
    def _generate_provider_comparison(self, data: pd.DataFrame) -> Dict[str, Dict]:
        """Generate provider comparison metrics"""
        if len(data) == 0:
            return {}
        
        provider_stats = data.groupby('provider').agg({
            'quality_score': ['mean', 'std'],
            'response_time': 'mean',
            'success': 'mean',
            'hallucination_detected': 'mean'
        }).round(3)
        
        # Flatten column names and convert to dict
        comparison = {}
        for provider in provider_stats.index:
            comparison[provider] = {
                'quality_score': float(provider_stats.loc[provider, ('quality_score', 'mean')]),
                'quality_std': float(provider_stats.loc[provider, ('quality_score', 'std')]),
                'response_time': float(provider_stats.loc[provider, ('response_time', 'mean')]),
                'success_rate': float(provider_stats.loc[provider, ('success', 'mean')]),
                'hallucination_rate': float(provider_stats.loc[provider, ('hallucination_detected', 'mean')])
            }
        
        return comparison
    
    def _generate_forecast(self, data: pd.DataFrame) -> Dict[str, float]:
        """Generate simple forecast based on trends"""
        if len(data) < 10:
            return {}
        
        # Simple linear trend extrapolation
        data_sorted = data.sort_values('timestamp')
        
        # Calculate recent trend
        recent_data = data_sorted.tail(min(20, len(data_sorted)))
        
        forecast = {
            "predicted_quality_7d": float(recent_data['quality_score'].mean()),
            "predicted_response_time_7d": float(recent_data['response_time'].mean()),
            "predicted_success_rate_7d": float(recent_data['success'].mean())
        }
        
        return forecast
    
    def _empty_summary(self, period: str) -> ExecutiveSummary:
        """Generate empty summary when no data available"""
        return ExecutiveSummary(
            reporting_period=f"{period} (No data available)",
            overall_health_score=0.0,
            key_metrics={},
            performance_trends={},
            critical_issues=["No data available for analysis"],
            success_highlights=[],
            recommendations=["Increase testing frequency to generate meaningful metrics"],
            provider_comparison={},
            forecast={}
        )
    
    def export_summary_json(self, summary: ExecutiveSummary, filepath: str):
        """Export summary to JSON file"""
        with open(filepath, 'w') as f:
            json.dump(asdict(summary), f, indent=2, default=str)
    
    def generate_summary_html(self, summary: ExecutiveSummary) -> str:
        """Generate HTML report from summary"""
        html_template = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>DeepCoderX Executive Summary</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 5px; }}
                .metrics {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin: 20px 0; }}
                .metric-card {{ background-color: #f9f9f9; padding: 15px; border-radius: 5px; text-align: center; }}
                .health-score {{ font-size: 2em; font-weight: bold; color: {'green' if summary.overall_health_score > 80 else 'orange' if summary.overall_health_score > 60 else 'red'}; }}
                .section {{ margin: 20px 0; }}
                .issue {{ color: red; }}
                .success {{ color: green; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>DeepCoderX Executive Summary</h1>
                <p><strong>Period:</strong> {summary.reporting_period}</p>
                <div class="health-score">Health Score: {summary.overall_health_score:.1f}/100</div>
            </div>
            
            <div class="section">
                <h2>Key Metrics</h2>
                <div class="metrics">
                    {self._format_metrics_html(summary.key_metrics)}
                </div>
            </div>
            
            <div class="section">
                <h2>Performance Trends</h2>
                <ul>
                    {self._format_trends_html(summary.performance_trends)}
                </ul>
            </div>
            
            <div class="section">
                <h2>Critical Issues</h2>
                <ul class="issue">
                    {self._format_list_html(summary.critical_issues)}
                </ul>
            </div>
            
            <div class="section">
                <h2>Success Highlights</h2>
                <ul class="success">
                    {self._format_list_html(summary.success_highlights)}
                </ul>
            </div>
            
            <div class="section">
                <h2>Recommendations</h2>
                <ul>
                    {self._format_list_html(summary.recommendations)}
                </ul>
            </div>
            
            <div class="section">
                <h2>Provider Comparison</h2>
                {self._format_provider_table_html(summary.provider_comparison)}
            </div>
        </body>
        </html>
        """
        
        return html_template
    
    def _format_metrics_html(self, metrics: Dict[str, float]) -> str:
        """Format metrics as HTML cards"""
        cards = []
        for key, value in metrics.items():
            formatted_value = f"{value:.3f}" if isinstance(value, float) and value < 10 else f"{value:.0f}"
            cards.append(f"""
                <div class="metric-card">
                    <div style="font-weight: bold;">{key.replace('_', ' ').title()}</div>
                    <div style="font-size: 1.5em;">{formatted_value}</div>
                </div>
            """)
        return ''.join(cards)
    
    def _format_trends_html(self, trends: Dict[str, str]) -> str:
        """Format trends as HTML list items"""
        return ''.join([f"<li><strong>{key.title()}:</strong> {value}</li>" for key, value in trends.items()])
    
    def _format_list_html(self, items: List[str]) -> str:
        """Format list items as HTML"""
        return ''.join([f"<li>{item}</li>" for item in items])
    
    def _format_provider_table_html(self, providers: Dict[str, Dict]) -> str:
        """Format provider comparison as HTML table"""
        if not providers:
            return "<p>No provider data available</p>"
        
        table_html = """
        <table border="1" style="border-collapse: collapse; width: 100%;">
            <tr>
                <th>Provider</th>
                <th>Quality Score</th>
                <th>Response Time</th>
                <th>Success Rate</th>
                <th>Hallucination Rate</th>
            </tr>
        """
        
        for provider, stats in providers.items():
            table_html += f"""
            <tr>
                <td>{provider}</td>
                <td>{stats.get('quality_score', 0):.3f}</td>
                <td>{stats.get('response_time', 0):.2f}s</td>
                <td>{stats.get('success_rate', 0):.1%}</td>
                <td>{stats.get('hallucination_rate', 0):.1%}</td>
            </tr>
            """
        
        table_html += "</table>"
        return table_html
```

## Configuration Files

### Analytics Configuration

**File:** `analytics/config/analytics_config.json`

```json
{
  "trend_analysis": {
    "min_data_points": 50,
    "seasonal_period": 7,
    "significance_threshold": 0.05,
    "confidence_level": 0.95,
    "trend_detection_window": 10
  },
  "quality_metrics": {
    "response_time_weight": 0.3,
    "accuracy_weight": 0.4,
    "consistency_weight": 0.3,
    "quality_threshold": 0.7,
    "acceptable_response_time": 5.0
  },
  "pattern_detection": {
    "anomaly_threshold": 2.5,
    "pattern_min_length": 5,
    "correlation_threshold": 0.7,
    "clustering_eps": 0.5,
    "clustering_min_samples": 5
  },
  "forecasting": {
    "forecast_horizon_days": 7,
    "min_training_days": 14,
    "confidence_intervals": [0.8, 0.95],
    "seasonal_decomposition": true
  },
  "optimization": {
    "improvement_threshold": 0.1,
    "priority_weights": {
      "quality": 0.4,
      "performance": 0.3,
      "reliability": 0.3
    },
    "implementation_effort_scores": {
      "low": 1,
      "medium": 3,
      "high": 5
    }
  }
}
```

### ML Model Configuration

**File:** `analytics/config/ml_config.json`

```json
{
  "quality_predictor": {
    "model_type": "gradient_boosting",
    "parameters": {
      "n_estimators": 100,
      "learning_rate": 0.1,
      "max_depth": 6,
      "random_state": 42
    },
    "feature_selection": {
      "max_features": 15,
      "feature_importance_threshold": 0.01
    },
    "validation": {
      "test_size": 0.2,
      "cv_folds": 5,
      "stratify": true
    }
  },
  "pattern_detector": {
    "clustering_algorithm": "dbscan",
    "anomaly_detection": {
      "contamination": 0.1,
      "n_neighbors": 20
    },
    "dimensionality_reduction": {
      "method": "pca",
      "n_components": 3,
      "variance_threshold": 0.95
    }
  },
  "forecasting_models": {
    "prophet": {
      "daily_seasonality": true,
      "weekly_seasonality": true,
      "yearly_seasonality": false,
      "changepoint_prior_scale": 0.05
    },
    "linear_trend": {
      "fit_intercept": true,
      "normalize": false
    }
  }
}
```

## Setup and Installation Scripts

### Main Setup Script

**File:** `setup_week4_analytics.py`

```python
#!/usr/bin/env python3
"""Setup script for Week 4 Advanced Analytics implementation"""

import os
import subprocess
import sys
import json
from pathlib import Path

def install_dependencies():
    """Install required Python packages"""
    print("Installing Week 4 dependencies...")
    
    packages = [
        "scikit-learn>=1.0.0",
        "pandas>=1.3.0",
        "matplotlib>=3.5.0",
        "seaborn>=0.11.0",
        "plotly>=5.0.0",
        "statsmodels>=0.13.0",
        "scipy>=1.7.0",
        "numpy>=1.21.0",
        "prophet>=1.0.0",
        "joblib>=1.1.0"
    ]
    
    for package in packages:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"✅ Installed {package}")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install {package}: {e}")
            return False
    
    return True

def create_directory_structure():
    """Create Week 4 directory structure"""
    print("Creating directory structure...")
    
    directories = [
        "analytics",
        "analytics/models",
        "analytics/forecasting",
        "analytics/visualization",
        "analytics/config",
        "analytics/reports",
        "analytics/data",
        "analytics/saved_models"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ Created directory: {directory}")

def create_config_files():
    """Create default configuration files"""
    print("Creating configuration files...")
    
    # Analytics config
    analytics_config = {
        "trend_analysis": {
            "min_data_points": 50,
            "seasonal_period": 7,
            "significance_threshold": 0.05,
            "confidence_level": 0.95
        },
        "quality_metrics": {
            "response_time_weight": 0.3,
            "accuracy_weight": 0.4,
            "consistency_weight": 0.3
        },
        "pattern_detection": {
            "anomaly_threshold": 2.5,
            "pattern_min_length": 5,
            "correlation_threshold": 0.7
        }
    }
    
    with open("analytics/config/analytics_config.json", "w") as f:
        json.dump(analytics_config, f, indent=2)
    
    # ML config
    ml_config = {
        "quality_predictor": {
            "model_type": "gradient_boosting",
            "parameters": {
                "n_estimators": 100,
                "learning_rate": 0.1,
                "max_depth": 6,
                "random_state": 42
            }
        }
    }
    
    with open("analytics/config/ml_config.json", "w") as f:
        json.dump(ml_config, f, indent=2)
    
    print("✅ Created configuration files")

def verify_prerequisites():
    """Verify Week 1-3 components are available"""
    print("Verifying prerequisites...")
    
    required_files = [
        "automated_testing_engine.py",
        "test_results.db",
        "dashboard/main_dashboard.py"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print("❌ Missing prerequisites:")
        for file_path in missing_files:
            print(f"   - {file_path}")
        print("\nPlease complete Week 1-3 implementation first.")
        return False
    
    print("✅ All prerequisites found")
    return True

def create_launcher_script():
    """Create analytics launcher script"""
    launcher_content = '''#!/usr/bin/env python3
"""Analytics Suite Launcher"""

import argparse
import sys
from pathlib import Path

# Add analytics modules to path
sys.path.append(str(Path(__file__).parent / "analytics"))

def main():
    parser = argparse.ArgumentParser(description="DeepCoderX Analytics Suite")
    parser.add_argument("command", choices=[
        "trend-analysis",
        "pattern-detection", 
        "quality-prediction",
        "optimization",
        "executive-report"
    ])
    parser.add_argument("--days", type=int, default=7, help="Analysis period in days")
    parser.add_argument("--output", type=str, help="Output file path")
    
    args = parser.parse_args()
    
    if args.command == "trend-analysis":
        from models.trend_analyzer import HistoricalTrendAnalyzer
        analyzer = HistoricalTrendAnalyzer("test_results.db")
        results = analyzer.analyze_historical_trends(args.days)
        print(f"Trend Analysis Results: {results}")
        
    elif args.command == "pattern-detection":
        from models.pattern_detector import BehaviorPatternDetector
        detector = BehaviorPatternDetector("test_results.db")
        patterns = detector.detect_anomalies(args.days)
        print(f"Pattern Detection Results: {patterns}")
        
    elif args.command == "quality-prediction":
        from models.predictive_models import QualityPredictor
        predictor = QualityPredictor("test_results.db")
        try:
            training_results = predictor.train_model(30)
            print(f"Model Training Results: {training_results}")
        except ValueError as e:
            print(f"Training failed: {e}")
            
    elif args.command == "optimization":
        from models.optimization_engine import ModelOptimizationEngine
        engine = ModelOptimizationEngine("test_results.db")
        recommendations = engine.generate_comprehensive_recommendations(args.days)
        print(f"Optimization Recommendations: {len(recommendations)} found")
        for rec in recommendations[:5]:  # Show top 5
            print(f"  - {rec.title} (Priority: {rec.priority})")
            
    elif args.command == "executive-report":
        from reports.executive_summary import ExecutiveReportGenerator
        generator = ExecutiveReportGenerator("test_results.db")
        if args.days <= 7:
            summary = generator.generate_weekly_summary()
        else:
            summary = generator.generate_monthly_summary()
        
        print(f"Executive Summary - Health Score: {summary.overall_health_score:.1f}/100")
        
        if args.output:
            if args.output.endswith('.json'):
                generator.export_summary_json(summary, args.output)
            elif args.output.endswith('.html'):
                html_content = generator.generate_summary_html(summary)
                with open(args.output, 'w') as f:
                    f.write(html_content)
            print(f"Report saved to: {args.output}")

if __name__ == "__main__":
    main()
'''
    
    with open("analytics_launcher.py", "w") as f:
        f.write(launcher_content)
    
    # Make executable
    os.chmod("analytics_launcher.py", 0o755)
    print("✅ Created analytics launcher script")

def main():
    """Main setup function"""
    print("=== DeepCoderX Week 4 Advanced Analytics Setup ===\n")
    
    # Verify prerequisites
    if not verify_prerequisites():
        return False
    
    # Install dependencies
    if not install_dependencies():
        print("❌ Dependency installation failed")
        return False
    
    # Create directories
    create_directory_structure()
    
    # Create config files
    create_config_files()
    
    # Create launcher
    create_launcher_script()
    
    print("\n✅ Week 4 Advanced Analytics setup complete!")
    print("\nNext steps:")
    print("1. Run: python3 analytics_launcher.py trend-analysis --days 7")
    print("2. Run: python3 analytics_launcher.py executive-report --output report.html")
    print("3. Check analytics/saved_models/ for trained ML models")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
```

## Usage Examples

### Command Line Usage

```bash
# Setup Week 4 analytics
python3 setup_week4_analytics.py

# Run trend analysis
python3 analytics_launcher.py trend-analysis --days 30

# Generate pattern detection report
python3 analytics_launcher.py pattern-detection --days 14

# Train quality prediction model
python3 analytics_launcher.py quality-prediction

# Generate optimization recommendations
python3 analytics_launcher.py optimization --days 30

# Create executive summary
python3 analytics_launcher.py executive-report --output executive_summary.html
```

### Python API Usage

```python
# Historical trend analysis
from analytics.models.trend_analyzer import HistoricalTrendAnalyzer

analyzer = HistoricalTrendAnalyzer("test_results.db")
trends = analyzer.analyze_historical_trends(days_back=30)

print(f"Overall trend: {trends.overall_trend}")
print(f"Trend strength: {trends.trend_strength}")
print(f"Seasonal patterns: {trends.seasonal_patterns}")

# Quality prediction
from analytics.models.predictive_models import QualityPredictor

predictor = QualityPredictor("test_results.db")
training_results = predictor.train_model(days_back=30)
print(f"Model accuracy: {training_results['test_accuracy']:.3f}")

# Save trained model
predictor.save_model("analytics/saved_models/quality_predictor.joblib")

# Pattern detection
from analytics.models.pattern_detector import BehaviorPatternDetector

detector = BehaviorPatternDetector("test_results.db")
anomalies = detector.detect_anomalies(days_back=7)
patterns = detector.detect_recurring_patterns(days_back=30)

print(f"Anomalies found: {anomalies['anomalies_found']}")
print(f"Anomaly rate: {anomalies['anomaly_rate']:.1%}")

# Optimization recommendations
from analytics.models.optimization_engine import ModelOptimizationEngine

engine = ModelOptimizationEngine("test_results.db")
recommendations = engine.generate_comprehensive_recommendations(30)

for rec in recommendations[:3]:
    print(f"\n{rec.title}")
    print(f"Priority: {rec.priority}")
    print(f"Impact: {rec.estimated_impact:.1%}")
    print(f"Actions: {rec.specific_actions[:2]}")

# Executive reporting
from analytics.reports.executive_summary import ExecutiveReportGenerator

generator = ExecutiveReportGenerator("test_results.db")
summary = generator.generate_weekly_summary()

print(f"Health Score: {summary.overall_health_score:.1f}/100")
print(f"Quality Score: {summary.key_metrics.get('avg_quality_score', 0):.3f}")

# Export reports
generator.export_summary_json(summary, "weekly_summary.json")
html_report = generator.generate_summary_html(summary)
with open("weekly_summary.html", "w") as f:
    f.write(html_report)
```

## Integration with Previous Weeks

### Week 1 Integration (Testing Engine)
- Uses standardized JSON output from automated testing engine
- Reads test results from established database schema
- Extends test query categories with analytics-specific queries

### Week 2 Integration (SQLite Storage)
- Leverages optimized SQLite database for fast analytics queries
- Uses established data import pipeline for JSONL to SQLite sync
- Builds on existing behavior analysis pipeline foundation

### Week 3 Integration (Dashboard)
- Integrates with Streamlit dashboard for advanced analytics pages
- Extends alert system with ML-powered anomaly detection
- Enhances automated reporting with predictive insights

## Expected Outcomes

### Week 4 Deliverables
1. **Historical Trend Analysis System**
   - Comprehensive trend detection with statistical significance testing
   - Seasonal pattern analysis with weekly/daily cycles
   - Confidence intervals and trend strength measurements

2. **Predictive Modeling Platform**
   - Quality degradation prediction with 80%+ accuracy
   - Performance forecasting with confidence intervals
   - Risk assessment and early warning systems

3. **Pattern Detection Engine**
   - Automated anomaly detection with clustering algorithms
   - Recurring pattern identification across temporal and provider dimensions
   - Behavioral consistency analysis and deviation tracking

4. **Optimization Recommendation System**
   - Data-driven optimization recommendations with priority scoring
   - Provider, temporal, and query category optimization insights
   - Implementation effort assessment and impact estimation

5. **Executive Reporting Suite**
   - Automated weekly and monthly executive summaries
   - Health score calculation with weighted metrics
   - HTML and JSON export capabilities for stakeholder communication

### Performance Targets
- **Analysis Speed:** Complete trend analysis in under 10 seconds for 30-day datasets
- **Prediction Accuracy:** Quality prediction models achieving 80%+ accuracy
- **Pattern Detection:** Anomaly detection with <5% false positive rate
- **Report Generation:** Executive summaries generated in under 30 seconds

### Long-term Benefits
- **Proactive Quality Management:** Predict and prevent quality degradation
- **Data-Driven Optimization:** Evidence-based improvement recommendations
- **Executive Visibility:** Clear insights into system health and performance trends
- **Automated Monitoring:** Continuous analysis with minimal manual intervention

## Testing and Validation

### Week 4 Testing Strategy
```bash
# Test all analytics components
python3 -m pytest analytics/tests/

# Validate trend analysis
python3 analytics/tests/test_trend_analyzer.py

# Test predictive models
python3 analytics/tests/test_predictive_models.py

# Validate pattern detection
python3 analytics/tests/test_pattern_detector.py

# Test optimization engine
python3 analytics/tests/test_optimization_engine.py

# Validate reporting system
python3 analytics/tests/test_executive_reports.py
```

### Validation Criteria
- **Data Quality:** All analytics functions handle edge cases (empty data, insufficient data)
- **Performance:** Analytics complete within target time limits
- **Accuracy:** Predictive models meet accuracy thresholds on test data
- **Integration:** Seamless integration with Week 1-3 components
- **Documentation:** Complete documentation and usage examples

## Conclusion

Week 4 completes the automated testing and analysis system with advanced analytics capabilities that provide deep insights into model behavior, predictive monitoring, and data-driven optimization recommendations. The comprehensive analytics platform enables proactive quality management and strategic decision-making for the DeepCoderX system.

The modular design allows for incremental implementation and easy extension with additional analytics capabilities as the system evolves. The combination of historical analysis, predictive modeling, pattern detection, and optimization recommendations provides a complete analytics solution for AI system monitoring and improvement.
