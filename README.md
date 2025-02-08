# SilverXSSHunter

SilverXSSHunter - Avtomatik XSS Skanner

## Ümumi Məlumat
SilverXSSHunter, veb tətbiqlərində XSS (Cross-Site Scripting) zəifliklərini avtomatik olaraq aşkar etmək üçün hazırlanmış bir vasitədir. Bu alət, bir çox fərqli payload istifadə edərək XSS zəifliklərini sınayır və tapılan zəiflikləri istifadəçiyə bildirir.

## Xüsusiyyətlər
- WAF (Web Application Firewall) aşkar edilməsi
- Müxtəlif payloadların sınağı
- User-Agent dəstəyi
- Proxy dəstəyi
- Base64 kodlama seçimi
- POST və GET sorğuları üçün dəstək
- Birdən çox hədəf URL faylı dəstəyi

## Tələblər
- Python 3.x
- Selenium
- Requests
- Colorama
- Geckodriver (Firefox üçün)

## Qurulum
```bash
pip install -r requirements.txt
```

## İstifadə
```bash
python silverxsshunter.py -u "http://hedefsayt.com" -p payloadlar.txt -o netice.txt
```

### Əsas Parametrlər
- `-u`, `--url` : Skan üçün hədəf URL.
- `-t`, `--targets` : URL-ləri ehtiva edən faylın yolu.
- `-p`, `--payload` : Payload faylının yolu (mütləqdir).
- `--wait` : Alert gözləmə müddəti (default: 0.5s).
- `-a`, `--useragent` : User-Agent faylının yolu.
- `--data` : POST sorğuları üçün göndəriləcək məlumat (məs: 'username=admin&password=admin').
- `--proxy` : Proxy server (məs: 127.0.0.1:8080).
- `--encode` : Payloadları base64 ilə kodla.
- `-o`, `--output` : Nəticə faylı (məs: netice.txt).

## Nümunələr
- Tək URL ilə skan:
  ```bash
  python silverxsshunter.py -u "http://hedefsayt.com" -p payloadlar.txt
  ```

- Birdən çox URL ilə skan:
  ```bash
  python silverxsshunter.py -t hedefler.txt -p payloadlar.txt
  ```

- Proxy və User-Agent ilə istifadə:
  ```bash
  python silverxsshunter.py -u "http://hedefsayt.com" -p payloadlar.txt --proxy 127.0.0.1:8080 -a useragents.txt
  ```

## Müəllif
**SilverX**
- Telegram: [t.me/silverxvip](https://t.me/silverxvip)

## Xəbərdarlıq
Bu vasitə yalnız tədris və təhlükəsizlik məqsədləri üçün nəzərdə tutulub. Hədəf sistemlərində icazəsiz istifadə qanunsuzdur və cinayət məsuliyyəti yarada bilər. İstifadə etməzdən əvvəl mütləq icazə alın!

