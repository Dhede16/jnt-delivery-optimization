"""
Runner aplikasi SwiftRoute by J&T - Alokasi Multi-Kurir KNN & Optimasi ACO
Jalankan file ini dengan: python run.py
"""
import sys
import webbrowser
from pathlib import Path
import uvicorn

if __name__ == "__main__":
    backend_dir = Path(__file__).resolve().parent / "backend"
    sys.path.insert(0, str(backend_dir))

    print("=" * 70)
    print("  [>>] SwiftRoute by J&T - Sistem Alokasi Paket Multi-Kurir KNN & Optimasi Rute ACO")
    print("  [>>] J&T Express Samarinda")
    print("=" * 70)
    print("  [==] Aplikasi dapat diakses di: http://localhost:8000")
    print("  [==] Dokumentasi API Swagger : http://localhost:8000/docs")
    print("=" * 70)

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=False, app_dir=str(backend_dir))

