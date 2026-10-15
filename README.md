# Otel Rezervasyon ve Konaklama Yönetim Sistemi

Veritabanı Yönetim Sistemleri dersi projesi.

## Grup Üyeleri
- Usame Hamada

## Kurulum
1. Sanal ortamı oluşturun ve aktif edin:
   `python -m venv venv`
   `source venv/Scripts/activate`

2. Kütüphaneleri yükleyin:
   `pip install django mysqlclient python-dotenv`

3. `.env` dosyasını oluşturup veritabanı ayarlarını ekleyin.

4. Veritabanını oluşturup projeyi çalıştırın:
   `python manage.py makemigrations`
   `python manage.py migrate`
   `python manage.py runserver`
