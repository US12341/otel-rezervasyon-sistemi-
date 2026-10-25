import os
import django
import random
from datetime import date, datetime, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from django.db import connection
from hotel.models import (
    OdaTipi, Oda, SezonFiyati, Misafir, Personel, Kullanici,
    Rezervasyon, Konaklama, EkHizmet, KonaklamaHizmeti, Odeme, TemizlikKaydi
)

def verileri_temizle():
    with connection.cursor() as cursor:
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
        tablolar = [
            'islem_log', 'temizlik_kaydi', 'odeme', 'konaklama_hizmeti',
            'ek_hizmet', 'konaklama', 'rezervasyon', 'kullanici',
            'personel', 'misafir', 'sezon_fiyati', 'oda', 'oda_tipi'
        ]
        for t in tablolar:
            cursor.execute(f"TRUNCATE TABLE {t};")
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")

def calistir():
    verileri_temizle()

    tipler = [
        OdaTipi.objects.create(tip_adi='Standart Tek Kisilik', kapasite=1, aciklama='Sehir manzarali standart oda', temel_fiyat=1200.00),
        OdaTipi.objects.create(tip_adi='Standart Cift Kisilik', kapasite=2, aciklama='Cift kisilik yatakli balkonlu oda', temel_fiyat=1800.00),
        OdaTipi.objects.create(tip_adi='Aile Odasi', kapasite=4, aciklama='Genis aile odasi', temel_fiyat=2800.00),
        OdaTipi.objects.create(tip_adi='Suit Oda', kapasite=2, aciklama='Deniz manzarali jakuzili suit', temel_fiyat=4500.00),
    ]

    for t in tipler:
        SezonFiyati.objects.create(
            oda_tipi=t,
            baslangic_tarihi=date(2026, 6, 1),
            bitis_tarihi=date(2026, 9, 15),
            gecelik_fiyat=float(t.temel_fiyat) * 1.35
        )
        SezonFiyati.objects.create(
            oda_tipi=t,
            baslangic_tarihi=date(2026, 9, 16),
            bitis_tarihi=date(2026, 12, 31),
            gecelik_fiyat=float(t.temel_fiyat) * 1.15
        )

    odalar = []
    for kat in range(1, 5):
        for no in range(1, 6):
            oda_no = f"{kat}0{no}"
            tip = tipler[(no - 1) % len(tipler)]
            odalar.append(Oda.objects.create(oda_numarasi=oda_no, kat=kat, oda_tipi=tip, durum='bos'))

    personeller = [
        Personel.objects.create(ad='Ahmet', soyad='Yilmaz', gorev='Yonetici', ise_giris_tarihi=date(2023, 3, 10)),
        Personel.objects.create(ad='Zeynep', soyad='Kaya', gorev='Resepsiyon', ise_giris_tarihi=date(2024, 5, 15)),
        Personel.objects.create(ad='Mehmet', soyad='Demir', gorev='Resepsiyon', ise_giris_tarihi=date(2024, 8, 1)),
        Personel.objects.create(ad='Fatma', soyad='Celik', gorev='Kat Gorevlisi', ise_giris_tarihi=date(2024, 2, 20)),
        Personel.objects.create(ad='Mustafa', soyad='Sahin', gorev='Kat Gorevlisi', ise_giris_tarihi=date(2025, 1, 12)),
    ]

    isimler = ['Ali', 'Veli', 'Ayse', 'Elif', 'Burak', 'Emre', 'Selin', 'Deniz', 'Cem', 'Gizem', 'Hakan', 'Sinan', 'Derya', 'Pinar', 'Oguz', 'Kaan', 'Merve', 'Buse', 'Tolga', 'Serkan']
    soyisimler = ['Ozturk', 'Aydin', 'Ozdemir', 'Arslan', 'Dogan', 'Kilic', 'Aslan', 'Cetin', 'Kara', 'Koc', 'Kurt', 'Ozkan', 'Simsek', 'Polat', 'Korkmaz']

    misafirler = []
    for i in range(1, 56):
        ad = random.choice(isimler)
        soyad = random.choice(soyisimler)
        m = Misafir.objects.create(
            ad=ad,
            soyad=soyad,
            tc_pasaport_no=str(10000000000 + i * 13579),
            telefon=f"053{random.randint(10000000, 99999999)}",
            eposta=f"{ad.lower()}.{soyad.lower()}{i}@mail.com",
            dogum_tarihi=date(random.randint(1975, 2003), random.randint(1, 12), random.randint(1, 28))
        )
        misafirler.append(m)

    Kullanici.objects.create(kullanici_adi='admin', sifre='1234', rol='yonetici', personel=personeller[0])
    Kullanici.objects.create(kullanici_adi='resepsiyon', sifre='1234', rol='resepsiyon', personel=personeller[1])
    Kullanici.objects.create(kullanici_adi='misafir1', sifre='1234', rol='misafir', misafir=misafirler[0])

    hizmetler = [
        EkHizmet.objects.create(hizmet_adi='Acik Bufe Kahvalti', birim_fiyat=350.00),
        EkHizmet.objects.create(hizmet_adi='Havaalani Transferi', birim_fiyat=900.00),
        EkHizmet.objects.create(hizmet_adi='Spa ve Masaj', birim_fiyat=1200.00),
        EkHizmet.objects.create(hizmet_adi='Minibar Kullanimi', birim_fiyat=450.00),
        EkHizmet.objects.create(hizmet_adi='Camasir Yikama', birim_fiyat=250.00),
    ]

    for oda in odalar:
        TemizlikKaydi.objects.create(oda=oda, personel=personeller[3], durum='Tamamlandi')

    bugun = date.today()
    toplam_rez = 0

    for idx, oda in enumerate(odalar):
        baslangic = date(2026, 1, 10) + timedelta(days=(idx % 4))
        for j in range(10):
            misafir = random.choice(misafirler)
            kisi = min(oda.oda_tipi.kapasite, random.randint(1, 3))

            if j < 8:
                gun = random.randint(2, 4)
                giris = baslangic
                cikis = giris + timedelta(days=gun)
                baslangic = cikis + timedelta(days=random.randint(18, 24))
                durum = 'tamamlandi'
            elif j == 8:
                giris = date(2026, 10, 2)
                cikis = date(2026, 10, 5)
                durum = 'tamamlandi'
            else:
                if idx < 5:
                    giris = bugun
                    cikis = bugun + timedelta(days=3)
                    durum = 'onaylandi'
                elif idx < 10:
                    giris = bugun - timedelta(days=3)
                    cikis = bugun
                    durum = 'onaylandi'
                else:
                    giris = bugun + timedelta(days=6)
                    cikis = bugun + timedelta(days=9)
                    durum = 'onaylandi'

            rez = Rezervasyon.objects.create(
                misafir=misafir,
                oda=oda,
                giris_tarihi=giris,
                cikis_tarihi=cikis,
                kisi_sayisi=kisi,
                durum=durum
            )
            toplam_rez += 1

            if durum == 'tamamlandi':
                giris_dt = datetime.combine(giris, datetime.min.time()) + timedelta(hours=14)
                cikis_dt = datetime.combine(cikis, datetime.min.time()) + timedelta(hours=11)
                konaklama = Konaklama.objects.create(
                    rezervasyon=rez,
                    personel=personeller[1],
                    gercek_giris_zamani=giris_dt,
                    gercek_cikis_zamani=cikis_dt
                )
                if random.random() > 0.4:
                    hizmet = random.choice(hizmetler)
                    KonaklamaHizmeti.objects.create(konaklama=konaklama, ek_hizmet=hizmet, adet=random.randint(1, 2))

                gun_sayisi = (cikis - giris).days
                tutar = float(oda.oda_tipi.temel_fiyat) * gun_sayisi
                Odeme.objects.create(
                    konaklama=konaklama,
                    tutar=tutar,
                    odeme_turu=random.choice(['Kredi Karti', 'Nakit', 'Havale'])
                )
            elif idx >= 5 and idx < 10 and j == 9:
                giris_dt = datetime.combine(giris, datetime.min.time()) + timedelta(hours=14)
                konaklama = Konaklama.objects.create(
                    rezervasyon=rez,
                    personel=personeller[2],
                    gercek_giris_zamani=giris_dt
                )
                Oda.objects.filter(id=oda.id).update(durum='dolu')

    print(f"Veri yukleme tamamlandi: {len(odalar)} oda, {len(misafirler)} misafir, {toplam_rez} rezervasyon eklendi.")

if __name__ == '__main__':
    calistir()
