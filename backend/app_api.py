"""
Youth Transition Crisis - Backend API
Flask REST API for Aadhaar Youth Biometric Analysis
"""

from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
import pandas as pd
import numpy as np
from pathlib import Path
import glob
from datetime import datetime

app = Flask(__name__, static_folder='../frontend', static_url_path='')
CORS(app)  # Enable CORS for frontend access

# State Name Standardization
STATE_MAPPING = {
    'WEST BENGAL': 'West Bengal', 'WESTBENGAL': 'West Bengal', 'West  Bengal': 'West Bengal',
    'West bengal': 'West Bengal', 'Westbengal': 'West Bengal', 'west Bengal': 'West Bengal',
    'West Bangal': 'West Bengal', 'ODISHA': 'Odisha', 'odisha': 'Odisha', 'Orissa': 'Odisha',
    'Andaman & Nicobar Islands': 'Andaman and Nicobar Islands', 'andhra pradesh': 'Andhra Pradesh',
    'Dadra & Nagar Haveli': 'Dadra and Nagar Haveli', 'Daman & Diu': 'Daman and Diu',
    'Jammu & Kashmir': 'Jammu and Kashmir', 'Tamilnadu': 'Tamil Nadu', 'Chhatisgarh': 'Chhattisgarh',
    'Uttaranchal': 'Uttarakhand', 'Pondicherry': 'Puducherry',
}

def clean_state_name(state):
    """Standardize state name"""
    if pd.isna(state):
        return state
    state = str(state).strip()
    return STATE_MAPPING.get(state, state)

# Global data cache
data_cache = {}

def load_data():
    """Load and cache all data"""
    if data_cache:
        return data_cache
    
    base_path = Path(__file__).parent.parent
    cleaned_path = base_path / "cleaned_data"
    
    # Try cleaned data first
    if (cleaned_path / "biometric_cleaned.csv").exists():
        bio_df = pd.read_csv(cleaned_path / "biometric_cleaned.csv")
        demo_df = pd.read_csv(cleaned_path / "demographic_cleaned.csv")
        enrol_df = pd.read_csv(cleaned_path / "enrolment_cleaned.csv")
    else:
        # Load raw data
        bio_files = glob.glob(str(base_path / "biometric_data" / "api_data_aadhar_biometric" / "*.csv"))
        demo_files = glob.glob(str(base_path / "demographic_data" / "api_data_aadhar_demographic" / "*.csv"))
        enrol_files = glob.glob(str(base_path / "enrolment_data" / "api_data_aadhar_enrolment" / "*.csv"))
        
        bio_df = pd.concat([pd.read_csv(f) for f in bio_files], ignore_index=True)
        demo_df = pd.concat([pd.read_csv(f) for f in demo_files], ignore_index=True)
        enrol_df = pd.concat([pd.read_csv(f) for f in enrol_files], ignore_index=True)
        
        # Clean state names
        bio_df['state'] = bio_df['state'].apply(clean_state_name)
        demo_df['state'] = demo_df['state'].apply(clean_state_name)
        enrol_df['state'] = enrol_df['state'].apply(clean_state_name)
    
    # Parse dates
    bio_df['date'] = pd.to_datetime(bio_df['date'], format='%d-%m-%Y')
    demo_df['date'] = pd.to_datetime(demo_df['date'], format='%d-%m-%Y')
    enrol_df['date'] = pd.to_datetime(enrol_df['date'], format='%d-%m-%Y')
    
    data_cache['bio'] = bio_df
    data_cache['demo'] = demo_df
    data_cache['enrol'] = enrol_df
    
    return data_cache

def calculate_metrics():
    """Calculate all metrics"""
    data = load_data()
    bio_df = data['bio']
    demo_df = data['demo']
    enrol_df = data['enrol']
    
    # State-level aggregation
    state_bio = bio_df.groupby('state').agg({
        'bio_age_5_17': 'sum',
        'bio_age_17_': 'sum'
    }).reset_index()
    
    state_bio['youth_bio_pct'] = (
        state_bio['bio_age_5_17'] / (state_bio['bio_age_5_17'] + state_bio['bio_age_17_'])
    ) * 100
    
    state_demo = demo_df.groupby('state').agg({
        'demo_age_5_17': 'sum',
        'demo_age_17_': 'sum'
    }).reset_index()
    
    state_demo['youth_demo_pct'] = (
        state_demo['demo_age_5_17'] / (state_demo['demo_age_5_17'] + state_demo['demo_age_17_'])
    ) * 100
    
    state_summary = state_bio.merge(state_demo, on='state', how='outer')
    
    state_enrol = enrol_df.groupby('state').agg({
        'age_5_17': 'sum',
        'age_18_greater': 'sum'
    }).reset_index()
    
    state_summary = state_summary.merge(state_enrol, on='state', how='outer')
    state_summary = state_summary.sort_values('youth_bio_pct', ascending=False).reset_index(drop=True)
    
    # Risk categorization
    def categorize_risk(pct):
        if pd.isna(pct):
            return 'Unknown'
        elif pct >= 60:
            return 'Exemplary'
        elif pct >= 50:
            return 'Good'
        elif pct >= 45:
            return 'Moderate'
        elif pct >= 40:
            return 'At Risk'
        else:
            return 'Critical'
    
    state_summary['risk_category'] = state_summary['youth_bio_pct'].apply(categorize_risk)
    
    # Monthly trends
    bio_df['month'] = bio_df['date'].dt.to_period('M')
    monthly = bio_df.groupby('month').agg({
        'bio_age_5_17': 'sum',
        'bio_age_17_': 'sum'
    }).reset_index()
    
    monthly['youth_bio_pct'] = (
        monthly['bio_age_5_17'] / (monthly['bio_age_5_17'] + monthly['bio_age_17_'])
    ) * 100
    
    monthly['month_str'] = monthly['month'].astype(str)
    
    return state_summary, monthly

@app.route('/')
def index():
    """Serve the main HTML page"""
    return send_from_directory('../frontend', 'index.html')

@app.route('/api/overview')
def get_overview():
    """Get overview statistics"""
    state_summary, monthly = calculate_metrics()
    data = load_data()
    
    best = state_summary.iloc[0].to_dict()
    worst = state_summary.iloc[-1].to_dict()
    gap = best['youth_bio_pct'] / worst['youth_bio_pct']
    
    critical_count = len(state_summary[state_summary['risk_category'] == 'Critical'])
    at_risk_count = len(state_summary[state_summary['risk_category'] == 'At Risk'])
    
    return jsonify({
        'total_records': len(data['bio']) + len(data['demo']) + len(data['enrol']),
        'num_states': len(state_summary),
        'num_districts': data['bio']['district'].nunique(),
        'num_pincodes': data['bio']['pincode'].nunique(),
        'best_state': best['state'],
        'best_percentage': round(best['youth_bio_pct'], 1),
        'worst_state': worst['state'],
        'worst_percentage': round(worst['youth_bio_pct'], 1),
        'gap': round(gap, 1),
        'national_avg': round(state_summary['youth_bio_pct'].mean(), 1),
        'critical_states': critical_count,
        'at_risk_states': at_risk_count,
        'analysis_date': datetime.now().strftime('%B %d, %Y')
    })

@app.route('/api/states')
def get_states():
    """Get all state data"""
    state_summary, _ = calculate_metrics()
    return jsonify(state_summary.to_dict('records'))

@app.route('/api/monthly')
def get_monthly():
    """Get monthly trends"""
    _, monthly = calculate_metrics()
    return jsonify(monthly.to_dict('records'))

@app.route('/api/risk-distribution')
def get_risk_distribution():
    """Get risk category distribution"""
    state_summary, _ = calculate_metrics()
    risk_counts = state_summary['risk_category'].value_counts().to_dict()
    return jsonify(risk_counts)

@app.route('/api/top-performers/<int:n>')
def get_top_performers(n):
    """Get top N performing states"""
    state_summary, _ = calculate_metrics()
    top_n = state_summary.head(n)
    return jsonify(top_n.to_dict('records'))

@app.route('/api/bottom-performers/<int:n>')
def get_bottom_performers(n):
    """Get bottom N performing states"""
    state_summary, _ = calculate_metrics()
    bottom_n = state_summary.tail(n)
    return jsonify(bottom_n.to_dict('records'))

@app.route('/api/state/<state_name>')
def get_state_detail(state_name):
    """Get details for specific state"""
    state_summary, _ = calculate_metrics()
    state_data = state_summary[state_summary['state'] == state_name]
    
    if len(state_data) == 0:
        return jsonify({'error': 'State not found'}), 404
    
    return jsonify(state_data.iloc[0].to_dict())

if __name__ == '__main__':
    print("Loading data...")
    load_data()
    print("Data loaded successfully!")
    print("\nStarting Flask server...")
    print("Backend API: http://localhost:5000")
    print("API Endpoints:")
    print("  GET /api/overview - Overview statistics")
    print("  GET /api/states - All state data")
    print("  GET /api/monthly - Monthly trends")
    print("  GET /api/risk-distribution - Risk category counts")
    print("  GET /api/top-performers/<n> - Top N states")
    print("  GET /api/bottom-performers/<n> - Bottom N states")
    print("  GET /api/state/<name> - Specific state details")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
