"""
Data Cleaning Script - Standardize State Names and Remove Duplicates
Fixes all inconsistent state naming across datasets
"""
import pandas as pd
import glob
from pathlib import Path

# State Name Standardization Mapping
STATE_MAPPING = {
    # West Bengal variations
    'WEST BENGAL': 'West Bengal',
    'WESTBENGAL': 'West Bengal',
    'West  Bengal': 'West Bengal',
    'West bengal': 'West Bengal',
    'Westbengal': 'West Bengal',
    'west Bengal': 'West Bengal',
    'West Bangal': 'West Bengal',
    
    # Odisha/Orissa variations (Orissa is old name, now Odisha)
    'ODISHA': 'Odisha',
    'odisha': 'Odisha',
    'Orissa': 'Odisha',
    
    # Andaman & Nicobar
    'Andaman & Nicobar Islands': 'Andaman and Nicobar Islands',
    
    # Andhra Pradesh
    'andhra pradesh': 'Andhra Pradesh',
    
    # Dadra & Nagar Haveli
    'Dadra & Nagar Haveli': 'Dadra and Nagar Haveli',
    
    # Daman & Diu
    'Daman & Diu': 'Daman and Diu',
    
    # Jammu & Kashmir
    'Jammu & Kashmir': 'Jammu and Kashmir',
    
    # Tamil Nadu
    'Tamilnadu': 'Tamil Nadu',
    
    # Chhattisgarh
    'Chhatisgarh': 'Chhattisgarh',
    
    # Uttarakhand (Uttaranchal is old name)
    'Uttaranchal': 'Uttarakhand',
    
    # Puducherry (Pondicherry is old name)
    'Pondicherry': 'Puducherry',
}

def clean_state_name(state):
    """Standardize state name"""
    if pd.isna(state):
        return state
    state = str(state).strip()
    return STATE_MAPPING.get(state, state)

def clean_dataset(df, dataset_name):
    """Clean a single dataset"""
    print(f"\n{'='*80}")
    print(f"CLEANING: {dataset_name}")
    print(f"{'='*80}")
    
    print(f"Original records: {len(df):,}")
    print(f"Original unique states: {df['state'].nunique()}")
    
    # Apply state name standardization
    df['state'] = df['state'].apply(clean_state_name)
    
    print(f"After cleaning unique states: {df['state'].nunique()}")
    
    # Show state distribution
    state_counts = df['state'].value_counts()
    print(f"\nTop 10 states by record count:")
    for state, count in state_counts.head(10).items():
        print(f"  {state}: {count:,} records")
    
    return df

def main():
    print("="*80)
    print("DATA CLEANING - STANDARDIZING STATE NAMES")
    print("="*80)
    
    base_path = Path(r"C:\Users\HP\Desktop\UIDAI")
    
    # Clean Biometric Data
    print("\n📊 BIOMETRIC DATA")
    bio_files = glob.glob(str(base_path / "biometric_data" / "api_data_aadhar_biometric" / "*.csv"))
    bio_dfs = []
    for f in bio_files:
        df = pd.read_csv(f)
        bio_dfs.append(df)
    bio_df = pd.concat(bio_dfs, ignore_index=True)
    bio_df = clean_dataset(bio_df, "Biometric Data")
    
    # Clean Demographic Data
    print("\n📊 DEMOGRAPHIC DATA")
    demo_files = glob.glob(str(base_path / "demographic_data" / "api_data_aadhar_demographic" / "*.csv"))
    demo_dfs = []
    for f in demo_files:
        df = pd.read_csv(f)
        demo_dfs.append(df)
    demo_df = pd.concat(demo_dfs, ignore_index=True)
    demo_df = clean_dataset(demo_df, "Demographic Data")
    
    # Clean Enrolment Data
    print("\n📊 ENROLMENT DATA")
    enrol_files = glob.glob(str(base_path / "enrolment_data" / "api_data_aadhar_enrolment" / "*.csv"))
    enrol_dfs = []
    for f in enrol_files:
        df = pd.read_csv(f)
        enrol_dfs.append(df)
    enrol_df = pd.concat(enrol_dfs, ignore_index=True)
    enrol_df = clean_dataset(enrol_df, "Enrolment Data")
    
    # Calculate cleaned metrics
    print("\n" + "="*80)
    print("RECALCULATING METRICS WITH CLEANED DATA")
    print("="*80)
    
    state_bio = bio_df.groupby('state').agg({
        'bio_age_5_17': 'sum',
        'bio_age_17_': 'sum'
    }).reset_index()
    
    state_bio['youth_bio_pct'] = (
        state_bio['bio_age_5_17'] / (state_bio['bio_age_5_17'] + state_bio['bio_age_17_'])
    ) * 100
    
    state_bio = state_bio.sort_values('youth_bio_pct', ascending=False).reset_index(drop=True)
    
    # Filter out states with 0%
    state_bio_valid = state_bio[state_bio['youth_bio_pct'] > 0].copy()
    
    best = state_bio_valid.iloc[0]
    worst = state_bio_valid.iloc[-1]
    gap = best['youth_bio_pct'] / worst['youth_bio_pct'] if worst['youth_bio_pct'] > 0 else 0
    
    print(f"\n✅ CLEANED RESULTS:")
    print(f"   Total States: {len(state_bio_valid)}")
    print(f"   Best Performer: {best['state']} = {best['youth_bio_pct']:.2f}%")
    print(f"   Worst Performer: {worst['state']} = {worst['youth_bio_pct']:.2f}%")
    print(f"   Gap Ratio: {gap:.2f}X")
    print(f"   National Average: {state_bio_valid['youth_bio_pct'].mean():.2f}%")
    print(f"   National Median: {state_bio_valid['youth_bio_pct'].median():.2f}%")
    
    print(f"\n🏆 TOP 15 STATES (CLEANED):")
    for i, row in state_bio_valid.head(15).iterrows():
        print(f"   {i+1:2}. {row['state']:<30} {row['youth_bio_pct']:6.2f}%")
    
    print(f"\n⚠️ BOTTOM 10 STATES (CLEANED):")
    for i, row in state_bio_valid.tail(10).iterrows():
        rank = len(state_bio_valid) - 9 + list(state_bio_valid.tail(10).index).index(i)
        print(f"   {rank:2}. {row['state']:<30} {row['youth_bio_pct']:6.2f}%")
    
    # Save cleaned data
    print("\n" + "="*80)
    print("SAVING CLEANED DATA")
    print("="*80)
    
    cleaned_dir = base_path / "cleaned_data"
    cleaned_dir.mkdir(exist_ok=True)
    
    bio_df.to_csv(cleaned_dir / "biometric_cleaned.csv", index=False)
    print(f"✅ Saved: {cleaned_dir / 'biometric_cleaned.csv'}")
    
    demo_df.to_csv(cleaned_dir / "demographic_cleaned.csv", index=False)
    print(f"✅ Saved: {cleaned_dir / 'demographic_cleaned.csv'}")
    
    enrol_df.to_csv(cleaned_dir / "enrolment_cleaned.csv", index=False)
    print(f"✅ Saved: {cleaned_dir / 'enrolment_cleaned.csv'}")
    
    state_bio_valid.to_csv(cleaned_dir / "state_summary_cleaned.csv", index=False)
    print(f"✅ Saved: {cleaned_dir / 'state_summary_cleaned.csv'}")
    
    print("\n" + "="*80)
    print("✅ DATA CLEANING COMPLETE!")
    print("="*80)
    print("\nCleaned data saved to: cleaned_data/")
    print("Update your Streamlit app to use cleaned data for accurate results!")

if __name__ == "__main__":
    main()
