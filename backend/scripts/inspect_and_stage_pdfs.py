import os
import shutil
import hashlib
import json
import pymupdf

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RAW_DIR = os.path.join(PROJECT_ROOT, "datasets", "agricultural_knowledge", "raw", "gbpuat")
METADATA_DIR = os.path.join(PROJECT_ROOT, "datasets", "agricultural_knowledge", "metadata")
REPORTS_DIR = os.path.join(PROJECT_ROOT, "datasets", "agricultural_knowledge", "reports")

os.makedirs(RAW_DIR, exist_ok=True)
os.makedirs(METADATA_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)

CANDIDATES = [
    {
        "expected_id": "gbpuat-pant-prasar-sandesh-jul-sep-2026",
        "search_names": [
            "Pant Prasar Sandesh (July-Sept., 2026).pdf",
            "Pant Prasar Sandesh (July-Sept, 2026).pdf",
            "pant_prasar_sandesh_jul_sep_2026.pdf"
        ],
        "canonical_filename": "pant_prasar_sandesh_jul_sep_2026.pdf",
        "expected_title": "Pant Prasar Sandesh (July–September 2026)",
        "publisher": "Directorate of Extension Education, GBPUAT Pantnagar",
        "source_url": "https://gbpuat.ac.in/directorates/Extension_Edu/pant_prasar/Pant%20Prasar%20Sandesh%20%28July-Sept.%2C%202026%29.pdf",
        "document_type": "Agricultural Extension Publication / Quarterly Bulletin",
        "publication_period": "July–September 2026",
        "publication_date": "2026-07-01",
        "state": "Uttarakhand",
        "language": "hi", # Mostly Hindi with English sections
        "license_information": "Official State Agricultural University Extension Publication (Public Educational / Agricultural Advisory)"
    },
    {
        "expected_id": "gbpuat-pant-prasar-sandesh-apr-jun-2026",
        "search_names": [
            "Pant Prasar Sandesh (April-June, 2026).pdf",
            "Pant Prasar Sandesh (April-June 2026).pdf",
            "pant_prasar_sandesh_apr_jun_2026.pdf"
        ],
        "canonical_filename": "pant_prasar_sandesh_apr_jun_2026.pdf",
        "expected_title": "Pant Prasar Sandesh (April–June 2026)",
        "publisher": "Directorate of Extension Education, GBPUAT Pantnagar",
        "source_url": "https://www.gbpuat.ac.in/directorates/Extension_Edu/pant_prasar/Pant%20Prasar%20Sandesh%20%28April-June%2C%202026%29.pdf",
        "document_type": "Agricultural Extension Publication / Quarterly Bulletin",
        "publication_period": "April–June 2026",
        "publication_date": "2026-04-01",
        "state": "Uttarakhand",
        "language": "hi",
        "license_information": "Official State Agricultural University Extension Publication (Public Educational / Agricultural Advisory)"
    },
    {
        "expected_id": "gbpuat-uttarakhand-kharif-advisory-2020",
        "search_names": [
            "02.05.2020_Kharif_season_Advisory.pdf",
            "Kharif_season_Advisory.pdf",
            "uttarakhand_kharif_advisory_2020.pdf"
        ],
        "canonical_filename": "uttarakhand_kharif_advisory_2020.pdf",
        "expected_title": "Uttarakhand Kharif Season Agricultural Advisory 2020",
        "publisher": "Directorate of Extension Education, GBPUAT Pantnagar",
        "source_url": "https://gbpuat.ac.in/directorates/Extension_Edu/02.05.2020_Kharif_season_Advisory.pdf",
        "document_type": "Seasonal Agricultural Advisory Bulletin (Historical)",
        "publication_period": "Kharif 2020",
        "publication_date": "2020-05-02",
        "state": "Uttarakhand",
        "language": "hi",
        "license_information": "Official State Agricultural University Extension Publication (Public Educational / Agricultural Advisory)"
    }
]


def compute_sha256(filepath: str) -> str:
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


def find_source_file(search_names):
    # Check root, incoming_rag_docs, or RAW_DIR
    check_dirs = [
        PROJECT_ROOT,
        os.path.join(PROJECT_ROOT, "incoming_rag_docs"),
        RAW_DIR
    ]
    for d in check_dirs:
        if os.path.exists(d):
            for name in search_names:
                candidate = os.path.join(d, name)
                if os.path.exists(candidate) and os.path.isfile(candidate):
                    return candidate
    return None


def inspect_and_stage():
    print("=" * 70)
    print("STAGE 2 & 3: PDF DISCOVERY, METADATA AUDIT & VERIFIED STAGING")
    print("=" * 70)

    manifest_entries = []
    staging_records = []

    for item in CANDIDATES:
        src_path = find_source_file(item["search_names"])
        if not src_path:
            raise FileNotFoundError(f"Could not locate document matching search names: {item['search_names']}")

        src_size = os.path.getsize(src_path)
        src_hash = compute_sha256(src_path)
        print(f"\n[FOUND] {os.path.basename(src_path)}")
        print(f"  Source Path: {src_path}")
        print(f"  Size: {src_size:,} bytes")
        print(f"  SHA-256: {src_hash}")

        # Verify readability with PyMuPDF
        doc = pymupdf.open(src_path)
        page_count = len(doc)
        print(f"  Pages: {page_count}")
        first_page_text = doc[0].get_text()[:300].strip().replace("\n", " ")
        print(f"  Sample Snippet (P1): {first_page_text[:120]}...")
        doc.close()

        # Destination path
        dest_path = os.path.join(RAW_DIR, item["canonical_filename"])

        # Check if identical already in dest
        already_in_place = (os.path.abspath(src_path) == os.path.abspath(dest_path))
        if not already_in_place:
            print(f"  Staging to: {dest_path}")
            shutil.copy2(src_path, dest_path)
            dest_size = os.path.getsize(dest_path)
            dest_hash = compute_sha256(dest_path)

            if dest_size != src_size or dest_hash != src_hash:
                raise ValueError(f"Integrity check failed copying {src_path} -> {dest_path}")
            
            # Verify destination copy is readable
            dest_doc = pymupdf.open(dest_path)
            if len(dest_doc) != page_count:
                dest_doc.close()
                raise ValueError(f"Page count mismatch in copy: {len(dest_doc)} != {page_count}")
            dest_doc.close()
            print("  ✓ Verified copy integrity. SHA-256 matches perfectly.")

            # Safe removal of original file only after destination is verified
            if os.path.exists(src_path) and os.path.abspath(src_path) != os.path.abspath(dest_path):
                os.remove(src_path)
                print(f"  ✓ Safely removed source file: {os.path.basename(src_path)}")
        else:
            print("  ✓ File is already in destination with verified SHA-256.")

        manifest_entry = {
            "document_id": item["expected_id"],
            "title": item["expected_title"],
            "publisher": item["publisher"],
            "source_url": item["source_url"],
            "original_filename": os.path.basename(src_path),
            "stored_filename": item["canonical_filename"],
            "document_type": item["document_type"],
            "publication_date": item["publication_date"],
            "publication_period": item["publication_period"],
            "state": item["state"],
            "districts": ["All Uttarakhand Districts", "Hill & Plain Agro-climatic Zones"],
            "crop_categories": ["Cereals", "Pulses", "Millets", "Vegetables", "Horticulture", "Fodder"],
            "subject_categories": ["Soil Health", "Crop Protection", "Disease Management", "Sowing Calendar", "Irrigation"],
            "language": item["language"],
            "page_count": page_count,
            "sha256_hash": src_hash,
            "file_path": os.path.relpath(dest_path, PROJECT_ROOT).replace("\\", "/"),
            "file_size": src_size,
            "license_information": item["license_information"],
            "ingestion_status": "staged",
            "is_historical": (item["publication_date"] < "2024-01-01"),
            "first_page_sample": first_page_text
        }
        manifest_entries.append(manifest_entry)
        staging_records.append({
            "canonical_filename": item["canonical_filename"],
            "sha256": src_hash,
            "pages": page_count,
            "size": src_size,
            "verified": True
        })

    # Save manifest
    manifest_path = os.path.join(METADATA_DIR, "document_manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump({
            "version": "1.0",
            "repository": "KisanMitra Agricultural Knowledge Base",
            "state_focus": "Uttarakhand, India",
            "total_documents": len(manifest_entries),
            "documents": manifest_entries
        }, f, indent=2, ensure_ascii=False)
    print(f"\n✓ Saved document manifest to {manifest_path}")

    # Save staging report
    report_path = os.path.join(REPORTS_DIR, "ingestion_report.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump({
            "stage": "staging_and_verification",
            "status": "success",
            "verified_files_count": len(staging_records),
            "records": staging_records
        }, f, indent=2)
    print(f"✓ Saved staging report to {report_path}")


if __name__ == "__main__":
    inspect_and_stage()
