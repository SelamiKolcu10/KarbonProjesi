"""
Pipeline Demo - Complete CBAM Analysis Workflow
Demonstrates the full integration of Agent #1 and Agent #2
"""

import sys
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')
from pathlib import Path
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.pipeline import run_analysis, PipelineError

# Enable detailed logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def main():
    """Run a demo analysis"""
    
    # Example: Analyze a factory document
    # You can replace this with your actual document path
    demo_file = project_root / "mevzuat_docs" / "CELEX_32023R0956_EN_TXT.pdf"
    
    # Check if file exists
    if not demo_file.exists():
        print(f"⚠️  Demo file not found: {demo_file}")
        print("Please provide a valid document path.")
        return
    
    try:
        print("\n" + "="*80)
        print("🏭 CBAM PIPELINE DEMONSTRATION")
        print("="*80)
        print(f"\n📄 Analyzing: {demo_file.name}\n")
        
        # Run the complete pipeline
        results = run_analysis(
            file_path=str(demo_file),
            facility_name="Demo Steel Factory",
            llm_provider="gemini",  # or "openai"
            use_cache=True,
            strict_physics=False,
            ets_price_override=None  # Use default price
        )
        
        # Print summary
        print("\n" + "="*80)
        print("✅ ANALYSIS COMPLETE!")
        print("="*80)
        print(f"\nTotal Emissions: {results['summary']['total_emissions_tco2e']:.2f} tCO2e")
        print(f"Financial Liability: €{results['summary']['financial_liability_eur']:,.2f}")
        print(f"Compliance: {results['summary']['compliance_status']}")
        print(f"Confidence: {results['summary']['confidence_score']*100:.0f}%")
        
        if results['summary']['anomalies_count'] > 0:
            print(f"\n⚠️  {results['summary']['anomalies_count']} anomalies detected")
        
        print(f"\n📁 Detailed results saved to: output/pipeline_results/")
        
    except PipelineError as e:
        print(f"\n❌ Pipeline Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
