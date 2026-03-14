"""
Tüm PDF belgelerini toplu olarak işleyen script
Çıktıları düzenli klasörlere kaydeder
"""

import sys
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')
from pathlib import Path
from dotenv import load_dotenv
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

# .env dosyasını yükle
load_dotenv()

# Proje kök dizinini path'e ekle
sys.path.insert(0, str(Path(__file__).parent))

from src.agents.data_extractor import DataExtractor
from src.config import Config

console = Console()


def organize_output_folders():
    """Çıktı klasörlerini organize et"""
    folders = {
        "regulations": Config.OUTPUT_DIR / "regulations",
        "guidance": Config.OUTPUT_DIR / "guidance",
        "directives": Config.OUTPUT_DIR / "directives",
        "reports": Config.OUTPUT_DIR / "reports"
    }
    
    for folder in folders.values():
        folder.mkdir(parents=True, exist_ok=True)
    
    return folders


def get_output_folder(pdf_name: str, folders: dict) -> Path:
    """PDF adına göre uygun klasörü seç"""
    pdf_lower = pdf_name.lower()
    
    if "regulation" in pdf_lower or "celex" in pdf_lower and "r" in pdf_lower:
        return folders["regulations"]
    elif "guidance" in pdf_lower or "guide" in pdf_lower:
        return folders["guidance"]
    elif "directive" in pdf_lower:
        return folders["directives"]
    else:
        return folders["reports"]


def main():
    """Ana fonksiyon"""
    
    console.print("\n[bold cyan]═══════════════════════════════════════════════════════[/bold cyan]")
    console.print("[bold cyan]📚 TOPLU PDF İŞLEME BAŞLIYOR[/bold cyan]")
    console.print("[bold cyan]═══════════════════════════════════════════════════════[/bold cyan]\n")
    
    # Çıktı klasörlerini organize et
    folders = organize_output_folders()
    console.print(f"📁 Çıktı klasörleri oluşturuldu:")
    for name, path in folders.items():
        console.print(f"   • {name}: {path.name}/")
    console.print()
    
    # Data Extractor oluştur (YENİ ÖZELLİKLERLE)
    console.print(f"🤖 Data Extractor başlatılıyor ({Config.DEFAULT_LLM_PROVIDER.upper()})...")
    extractor = DataExtractor(
        llm_provider=Config.DEFAULT_LLM_PROVIDER,
        api_key=Config.get_api_key(Config.DEFAULT_LLM_PROVIDER),
        use_cache=True,
        cache_ttl_hours=24,
        max_retries=3,
        chunk_size=15000,
        rate_limit_per_minute=10
    )
    console.print("✅ Hazır!\n")
    
    # PDF dosyalarını bul
    pdf_files = list(Config.MEVZUAT_DOCS_DIR.glob("*.pdf"))
    
    if not pdf_files:
        console.print("[red]❌ Hiç PDF dosyası bulunamadı![/red]")
        return
    
    console.print(f"[green]📄 {len(pdf_files)} PDF dosyası bulundu:[/green]")
    for i, pdf in enumerate(pdf_files, 1):
        console.print(f"   {i}. {pdf.name}")
    console.print()
    
    # Her PDF'i işle
    results = []
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        
        for i, pdf_path in enumerate(pdf_files, 1):
            task = progress.add_task(
                f"[cyan]İşleniyor ({i}/{len(pdf_files)}): {pdf_path.name}...", 
                total=None
            )
            
            try:
                # Uygun klasörü seç
                output_folder = get_output_folder(pdf_path.name, folders)
                
                # Çıktı dosya adı
                output_name = pdf_path.stem.replace(" ", "_").lower() + ".json"
                output_path = output_folder / output_name
                
                # PDF'i işle
                result = extractor.process_document(
                    pdf_path=str(pdf_path),
                    output_path=str(output_path)
                )
                
                results.append({
                    "pdf": pdf_path.name,
                    "output": str(output_path.relative_to(Config.OUTPUT_DIR)),
                    "document_name": result.get("document_name", "NULL"),
                    "document_type": result.get("document_type", "NULL"),
                    "publication_date": result.get("publication_date", "NULL"),
                    "status": "✅ Başarılı"
                })
                
                progress.update(task, completed=True)
                
            except Exception as e:
                results.append({
                    "pdf": pdf_path.name,
                    "output": "N/A",
                    "document_name": "ERROR",
                    "document_type": "ERROR",
                    "publication_date": "ERROR",
                    "status": f"❌ Hata: {str(e)[:50]}"
                })
                progress.update(task, completed=True)
    
    # Sonuçları göster
    console.print("\n[bold green]═══════════════════════════════════════════════════════[/bold green]")
    console.print("[bold green]✅ İŞLEME TAMAMLANDI[/bold green]")
    console.print("[bold green]═══════════════════════════════════════════════════════[/bold green]\n")
    
    from rich.table import Table
    
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("PDF Dosyası", style="cyan", width=40)
    table.add_column("Belge Adı", style="yellow", width=35)
    table.add_column("Tip", style="green", width=12)
    table.add_column("Tarih", style="blue", width=12)
    table.add_column("Durum", width=15)
    
    for result in results:
        table.add_row(
            result["pdf"][:37] + "..." if len(result["pdf"]) > 40 else result["pdf"],
            result["document_name"][:32] + "..." if len(result["document_name"]) > 35 else result["document_name"],
            result["document_type"],
            result["publication_date"],
            result["status"]
        )
    
    console.print(table)
    
    # Özet
    console.print(f"\n[bold]📊 ÖZET:[/bold]")
    console.print(f"   • Toplam işlenen: {len(pdf_files)} PDF")
    console.print(f"   • Başarılı: {sum(1 for r in results if '✅' in r['status'])} adet")
    console.print(f"   • Hatalı: {sum(1 for r in results if '❌' in r['status'])} adet")
    console.print(f"\n[bold]💾 Çıktılar:[/bold]")
    console.print(f"   📂 {Config.OUTPUT_DIR.name}/")
    
    # Her klasördeki dosya sayısını göster
    for name, folder in folders.items():
        json_count = len(list(folder.glob("*.json")))
        if json_count > 0:
            console.print(f"      ├── {folder.name}/ ({json_count} dosya)")
            for json_file in folder.glob("*.json"):
                console.print(f"      │   └── {json_file.name}")
    
    console.print("\n[bold green]🎉 Tüm işlemler tamamlandı![/bold green]\n")


if __name__ == "__main__":
    main()
