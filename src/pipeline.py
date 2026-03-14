"""
Main Orchestrator Pipeline - Bridges Agent #1 (Data Extractor) and Agent #2 (Auditor)

This module provides the integration layer between:
- src.agents.data_extractor (Agent #1): Extracts raw JSON from PDFs/Excel
- src.agents.auditor (Agent #2): Performs CBAM compliance audits

Flow:
1. Extract data from document (Agent #1)
2. Map raw JSON to structured InputPayload (Adapter)
3. Run audit calculations (Agent #2)
4. Return comprehensive analysis results
"""

import logging
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
import json

from .agents.data_extractor import DataExtractor
from .agents.auditor import AuditorEngine
from .agents.auditor.models import InputPayload, ProcessInputs, PrecursorInput

# Setup logging
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


class PipelineError(Exception):
    """Custom exception for pipeline errors"""
    pass


def map_extraction_to_payload(raw_data: Dict[str, Any], facility_name: Optional[str] = None) -> InputPayload:
    """
    Maps Agent #1's raw extraction output to Agent #2's InputPayload.
    
    This is the critical adapter that bridges the two systems.
    Handles missing data gracefully with safe defaults.
    
    Args:
        raw_data: Raw JSON output from DataExtractor
        facility_name: Override facility name (optional)
        
    Returns:
        InputPayload object ready for AuditorEngine
        
    Raises:
        PipelineError: If critical fields are missing
    """
    logger.info("🔄 Mapping extraction data to audit payload...")
    
    try:
        # Extract metadata
        metadata = raw_data.get('document_metadata', {})
        filename = metadata.get('filename', 'Unknown Document')
        
        # Extract reporting period
        period_data = raw_data.get('reporting_period', {})
        start_date = period_data.get('start_date')
        end_date = period_data.get('end_date')
        
        # Format reporting period (prefer YYYY-MM format)
        if start_date:
            try:
                reporting_period = datetime.fromisoformat(start_date).strftime('%Y-%m')
            except (ValueError, TypeError):
                reporting_period = "Unknown Period"
        else:
            reporting_period = "Unknown Period"
        
        # Extract production data
        production_data = raw_data.get('production', {})
        production_quantity = production_data.get('quantity', 0.0)
        production_unit = production_data.get('unit', 'ton')
        
        # Handle null production
        if production_quantity is None or production_quantity < 0:
            logger.warning("⚠️  Production quantity is null or negative, defaulting to 0.0")
            production_quantity = 0.0
        
        # Unit conversion (if needed)
        if production_unit and 'kg' in production_unit.lower():
            production_quantity = production_quantity / 1000.0  # kg to ton
            logger.info(f"   Converted production from kg to tons: {production_quantity:.2f}")
        
        # Extract Scope 2 (Electricity)
        scope2_data = raw_data.get('energy_scope_2', {})
        electricity_data = scope2_data.get('electricity', {})
        electricity_mwh = electricity_data.get('total_value', 0.0)
        electricity_unit = electricity_data.get('unit', 'MWh')
        
        # Handle null electricity
        if electricity_mwh is None or electricity_mwh < 0:
            logger.warning("⚠️  Electricity consumption is null or negative, defaulting to 0.0")
            electricity_mwh = 0.0
        
        # Unit conversion (kWh to MWh)
        if electricity_unit and 'kwh' in electricity_unit.lower() and 'mwh' not in electricity_unit.lower():
            electricity_mwh = electricity_mwh / 1000.0
            logger.info(f"   Converted electricity from kWh to MWh: {electricity_mwh:.2f}")
        
        # Extract Scope 1 (Natural Gas & Coal)
        scope1_data = raw_data.get('energy_scope_1', {})
        fuel_data = raw_data.get('fuel_scope_1', {})
        
        # Natural Gas
        natural_gas_m3 = 0.0
        if 'natural_gas' in scope1_data:
            gas_value = scope1_data['natural_gas'].get('value', 0.0)
            natural_gas_m3 = gas_value if gas_value is not None else 0.0
        elif 'natural_gas' in fuel_data:
            gas_value = fuel_data['natural_gas'].get('value', 0.0)
            natural_gas_m3 = gas_value if gas_value is not None else 0.0
        
        # Coal
        coal_tons = 0.0
        if 'coal' in scope1_data:
            coal_value = scope1_data['coal'].get('value', 0.0)
            coal_tons = coal_value if coal_value is not None else 0.0
        elif 'coal' in fuel_data:
            coal_value = fuel_data['coal'].get('value', 0.0)
            coal_tons = coal_value if coal_value is not None else 0.0
        
        # Process Inputs (v2.0) - Usually NOT in invoices, more in technical reports
        process_inputs = None
        if 'process_materials' in raw_data:
            process_data = raw_data['process_materials']
            electrode_consumption = process_data.get('electrode_consumption_ton', 0.0)
            limestone_consumption = process_data.get('limestone_consumption_ton', 0.0)
            
            if electrode_consumption or limestone_consumption:
                process_inputs = ProcessInputs(
                    electrode_consumption_ton=electrode_consumption or 0.0,
                    limestone_consumption_ton=limestone_consumption or 0.0
                )
                logger.info(f"   ✅ Process inputs found: Electrodes={electrode_consumption}, Limestone={limestone_consumption}")
        
        # Precursors (v2.0) - Usually NOT in invoices
        precursors = []
        if 'precursor_materials' in raw_data:
            precursor_list = raw_data['precursor_materials']
            for item in precursor_list:
                precursor = PrecursorInput(
                    material_name=item.get('material_name', 'Unknown'),
                    quantity_ton=item.get('quantity_ton', 0.0),
                    embedded_emissions_factor=item.get('embedded_emissions_factor')
                )
                precursors.append(precursor)
            logger.info(f"   ✅ {len(precursors)} precursor materials found")
        
        # Determine facility name
        if not facility_name:
            # Try to extract from document
            facility_name = raw_data.get('facility_info', {}).get('name')
            if not facility_name:
                facility_name = filename.replace('.pdf', '').replace('_', ' ')
        
        # Ensure facility_name is not None
        if not facility_name:
            facility_name = "Unknown Facility"
        
        # Create InputPayload
        payload = InputPayload(
            facility_name=facility_name,
            facility_id=raw_data.get('facility_info', {}).get('id'),
            reporting_period=reporting_period,
            production_quantity_tons=production_quantity,
            electricity_consumption_mwh=electricity_mwh,
            natural_gas_consumption_m3=natural_gas_m3,
            coal_consumption_tons=coal_tons,
            process_inputs=process_inputs,
            precursors=precursors,
            data_source="agent1_extraction"
        )
        
        logger.info("✅ Mapping complete")
        logger.info(f"   Facility: {facility_name}")
        logger.info(f"   Period: {reporting_period}")
        logger.info(f"   Production: {production_quantity:.2f} tons")
        logger.info(f"   Electricity: {electricity_mwh:.2f} MWh")
        logger.info(f"   Natural Gas: {natural_gas_m3:.2f} m³")
        logger.info(f"   Coal: {coal_tons:.2f} tons")
        
        return payload
        
    except Exception as e:
        logger.error(f"❌ Mapping failed: {str(e)}")
        raise PipelineError(f"Failed to map extraction data to payload: {str(e)}")


def run_analysis(
    file_path: str,
    output_dir: Optional[str] = None,
    facility_name: Optional[str] = None,
    llm_provider: str = "gemini",
    use_cache: bool = True,
    strict_physics: bool = False,
    ets_price_override: Optional[float] = None
) -> Dict[str, Any]:
    """
    Main orchestrator function - runs the complete analysis pipeline.
    
    Args:
        file_path: Path to PDF/Excel/CSV file
        output_dir: Output directory for results (default: output/)
        facility_name: Override facility name
        llm_provider: LLM provider for extraction ("gemini" or "openai")
        use_cache: Enable caching for extraction
        strict_physics: Enable strict physics validation
        ets_price_override: Override EU ETS price for simulation
        
    Returns:
        Complete analysis results including extraction, audit, and summary
        
    Raises:
        PipelineError: If any stage fails
    """
    logger.info("="*80)
    logger.info("🚀 CBAM ANALYSIS PIPELINE - Starting")
    logger.info("="*80)
    
    # Validate input file
    file_path_obj = Path(file_path)
    if not file_path_obj.exists():
        raise PipelineError(f"Input file not found: {file_path}")
    
    logger.info(f"📄 Input File: {file_path_obj.name}")
    logger.info(f"🤖 LLM Provider: {llm_provider.upper()}")
    
    # Setup output directory
    if output_dir is None:
        output_dir = str(Path(__file__).parent.parent / "output" / "pipeline_results")
    
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    try:
        # ====================================================================
        # STAGE 1: Data Extraction (Agent #1)
        # ====================================================================
        logger.info("")
        logger.info("📊 STAGE 1: DATA EXTRACTION (Agent #1)")
        logger.info("-"*80)
        
        extractor = DataExtractor(
            llm_provider=llm_provider,
            use_cache=use_cache,
            cache_ttl_hours=24,
            max_retries=3
        )
        
        # Extract data from document
        text = extractor.extract_text_from_pdf(str(file_path))
        extraction_result = extractor.extract_with_llm(
            text=text,
            use_chunking=True
        )
        
        logger.info("✅ Extraction Complete")
        
        # Save raw extraction
        extraction_output_path = output_path / f"{file_path_obj.stem}_extraction.json"
        with open(extraction_output_path, 'w', encoding='utf-8') as f:
            json.dump(extraction_result, f, indent=2, ensure_ascii=False)
        logger.info(f"💾 Raw extraction saved: {extraction_output_path}")
        
        # ====================================================================
        # STAGE 2: Data Mapping (Adapter)
        # ====================================================================
        logger.info("")
        logger.info("🔄 STAGE 2: DATA MAPPING (Adapter)")
        logger.info("-"*80)
        
        payload = map_extraction_to_payload(extraction_result, facility_name)
        
        # ====================================================================
        # STAGE 3: CBAM Audit (Agent #2)
        # ====================================================================
        logger.info("")
        logger.info("⚖️  STAGE 3: CBAM COMPLIANCE AUDIT (Agent #2)")
        logger.info("-"*80)
        
        auditor = AuditorEngine(
            strict_physics=strict_physics,
            cbam_phase_factor=0.025,  # 2026: 2.5% phase-in
            free_allocation=0.0
        )
        
        audit_result = auditor.audit(
            input_data=payload,
            ets_price_override=ets_price_override
        )
        
        logger.info("✅ Audit Complete")
        
        # Save audit result
        audit_output_path = output_path / f"{file_path_obj.stem}_audit.json"
        with open(audit_output_path, 'w', encoding='utf-8') as f:
            # Convert Pydantic to dict
            audit_dict = audit_result.model_dump(mode='json')
            json.dump(audit_dict, f, indent=2, ensure_ascii=False, default=str)
        logger.info(f"💾 Audit report saved: {audit_output_path}")
        
        # ====================================================================
        # STAGE 4: Summary Report
        # ====================================================================
        logger.info("")
        logger.info("="*80)
        logger.info("📋 FINAL ANALYSIS SUMMARY")
        logger.info("="*80)
        
        print_summary_report(audit_result)
        
        # Compile final results
        final_results = {
            "input_file": str(file_path),
            "processed_at": datetime.now().isoformat(),
            "extraction": extraction_result,
            "audit": audit_dict,
            "summary": {
                "facility": payload.facility_name,
                "period": payload.reporting_period,
                "total_emissions_tco2e": audit_result.emissions.total_emissions,
                "emission_intensity": audit_result.emissions.emission_intensity_per_ton,
                "financial_liability_eur": audit_result.financials.effective_liability_eur,
                "compliance_status": "COMPLIANT" if audit_result.is_compliant else "NON-COMPLIANT",
                "confidence_score": audit_result.confidence_score,
                "anomalies_count": len(audit_result.anomalies)
            }
        }
        
        # Save complete results
        complete_output_path = output_path / f"{file_path_obj.stem}_complete.json"
        with open(complete_output_path, 'w', encoding='utf-8') as f:
            json.dump(final_results, f, indent=2, ensure_ascii=False, default=str)
        
        logger.info("")
        logger.info("="*80)
        logger.info("✅ PIPELINE COMPLETED SUCCESSFULLY")
        logger.info(f"📁 All results saved to: {output_path}")
        logger.info("="*80)
        
        return final_results
        
    except Exception as e:
        logger.error("="*80)
        logger.error(f"❌ PIPELINE FAILED: {str(e)}")
        logger.error("="*80)
        raise PipelineError(f"Pipeline execution failed: {str(e)}")


def print_summary_report(audit_result):
    """Print a formatted summary of the audit results"""
    
    print("")
    print(f"🏭 Facility: {audit_result.input_summary['facility']}")
    print(f"📅 Period: {audit_result.input_summary['period']}")
    print(f"📊 Production: {audit_result.input_summary['production']:.2f} tons")
    print("")
    print("━"*80)
    print("EMISSIONS BREAKDOWN")
    print("━"*80)
    print(f"  Scope 1 (Direct):       {audit_result.emissions.scope_1_direct:.2f} tCO2e")
    print(f"    - Natural Gas:        {audit_result.emissions.natural_gas_emissions:.2f} tCO2e")
    print(f"    - Coal:               {audit_result.emissions.coal_emissions:.2f} tCO2e")
    print(f"  Scope 2 (Indirect):     {audit_result.emissions.scope_2_indirect:.2f} tCO2e")
    print(f"    - Electricity:        {audit_result.emissions.electricity_emissions:.2f} tCO2e")
    
    if audit_result.emissions.process_emissions > 0:
        print(f"  Process Emissions:      {audit_result.emissions.process_emissions:.2f} tCO2e")
    
    if audit_result.emissions.precursor_emissions > 0:
        print(f"  Precursor Emissions:    {audit_result.emissions.precursor_emissions:.2f} tCO2e")
    
    print(f"  ─────────────────────────────────────")
    print(f"  TOTAL:                  {audit_result.emissions.total_emissions:.2f} tCO2e")
    print(f"  Intensity:              {audit_result.emissions.emission_intensity_per_ton:.4f} tCO2e/ton")
    print("")
    print("━"*80)
    print("FINANCIAL IMPACT")
    print("━"*80)
    print(f"  EU ETS Price:           €{audit_result.financials.ets_price_eur_per_ton:.2f}/ton")
    print(f"  Total Liability:        €{audit_result.financials.total_liability_eur:,.2f}")
    print(f"  CBAM Phase-in (2.5%):   €{audit_result.financials.effective_liability_eur:,.2f}")
    print(f"  Cost per ton steel:     €{audit_result.financials.liability_per_ton_steel_eur:.2f}/ton")
    print("")
    print("━"*80)
    print("COMPLIANCE STATUS")
    print("━"*80)
    
    status_icon = "✅" if audit_result.is_compliant else "❌"
    status_text = "COMPLIANT" if audit_result.is_compliant else "NON-COMPLIANT"
    print(f"  Status: {status_icon} {status_text}")
    print(f"  Confidence Score: {audit_result.confidence_score*100:.0f}%")
    print(f"  Anomalies: {len(audit_result.anomalies)}")
    
    if audit_result.anomalies:
        print("")
        print("  Detected Issues:")
        for anomaly in audit_result.anomalies:
            icon = "🔴" if anomaly.level.value == "CRITICAL" else "🟡"
            print(f"    {icon} [{anomaly.level.value}] {anomaly.message}")
    
    if audit_result.compliance_notes:
        print("")
        print("  Notes:")
        for note in audit_result.compliance_notes:
            print(f"    • {note}")
    
    print("")


# CLI Entry Point
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="CBAM Analysis Pipeline - Extract & Audit Industrial Documents"
    )
    parser.add_argument(
        "file_path",
        help="Path to PDF/Excel/CSV file to analyze"
    )
    parser.add_argument(
        "--output-dir",
        help="Output directory for results (default: output/pipeline_results)"
    )
    parser.add_argument(
        "--facility-name",
        help="Override facility name"
    )
    parser.add_argument(
        "--llm",
        choices=["gemini", "openai"],
        default="gemini",
        help="LLM provider for extraction (default: gemini)"
    )
    parser.add_argument(
        "--no-cache",
        action="store_true",
        help="Disable extraction caching"
    )
    parser.add_argument(
        "--strict-physics",
        action="store_true",
        help="Enable strict physics validation (raises on violations)"
    )
    parser.add_argument(
        "--ets-price",
        type=float,
        help="Override EU ETS carbon price (EUR/ton)"
    )
    
    args = parser.parse_args()
    
    try:
        run_analysis(
            file_path=args.file_path,
            output_dir=args.output_dir,
            facility_name=args.facility_name,
            llm_provider=args.llm,
            use_cache=not args.no_cache,
            strict_physics=args.strict_physics,
            ets_price_override=args.ets_price
        )
    except PipelineError as e:
        logger.error(f"Pipeline failed: {e}")
        exit(1)
