# AgeLens public sürüm kontrol listesi

Repo görünürlüğünü public yapmadan önce aşağıdaki kontroller
tamamlanmalıdır.

## Güvenlik kontrolü

Repo kökünde çalıştırın:

```powershell
python scripts/preflight_repository.py .
```

Çıktının `PREFLIGHT PASSED` olması gerekir.

Kontrol; ham ve katılımcı düzeyindeki veri uzantılarını, hassas veri
klasörlerini, yaygın gizli anahtar biçimlerini, kişisel mutlak kullanıcı
yollarını, bozuk ZIP dosyalarını ve 50 MiB üzerindeki dosyaları reddeder.

## Notebook çıktıları

Public notebook kopyalarında yalnızca çalıştırma çıktılarında görünen
mutlak yerel proje yolları `<PROJECT_ROOT>` olarak değiştirilmiştir.
Kaynak kod hücreleri değiştirilmemiştir.

Governed ve public notebook SHA-256 eşlemesi:

```text
release/public_notebook_sanitization.json
release/public_notebook_inventory.csv
```

## Veri sınırı

Public repo şunları içermez:

- ham NHANES dosyaları;
- public-use mortality fixed-width kaynak dosyaları;
- interim veya processed katılımcı düzeyi dosyaları;
- yetkilendirilmiş mortality cohort Parquet dosyası;
- cause-specific mortality çıktıları.

## Görünürlük

Güvenlik kontrolü geçmeden repo görünürlüğü değiştirilmemelidir.
