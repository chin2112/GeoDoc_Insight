import subprocess
import sys
import os

def run_command(cmd, description):
    print(f"\n--- [Pipeline Step] {description} ---")
    try:
        # We assume scripts are runnable with python and current PYTHONPATH is correct
        result = subprocess.run([sys.executable] + cmd.split(), check=True, text=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error during {description}: {e}")
        return False

def main():
    # Set PYTHONPATH to project root to ensure imports work
    project_root = os.path.dirname(os.path.abspath(__file__))
    os.environ['PYTHONPATH'] = project_root
    
    steps = [
        ("src/pipeline/geocoding_job.py", "GIS Geocoding (Excel -> Coordinates)"),
        ("src/pipeline/enrich_business_data.py", "Business Enrichment (Classification & District)"),
        ("src/pipeline/analytics_engine.py", "Analytics Engine (Spatial Hotspot Calculation)"),
        ("src/dashboard/data_exporter.py", "Data Publication (DB -> data.js)")
    ]
    
    for script, desc in steps:
        if not run_command(script, desc):
            print("\n[FAIL] Pipeline failed. Please check logs.")
            return

    print("\n[SUCCESS] PIPELINE COMPLETE. Dashboard data is now fresh.")

if __name__ == "__main__":
    main()
