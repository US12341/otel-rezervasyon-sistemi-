from django.db import models

class OdaTipi(models.Model):
    tip_adi = models.CharField(max_length=50)
    kapasite = models.IntegerField()
    aciklama = models.TextField(blank=True, null=True)
    temel_fiyat = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = 'oda_tipi'

class Oda(models.Model):
    oda_numarasi = models.CharField(max_length=10, unique=True, db_index=True)
    kat = models.IntegerField()
    oda_tipi = models.ForeignKey(OdaTipi, on_delete=models.CASCADE)
    durum = models.CharField(max_length=20, default='bos')

    class Meta:
        db_table = 'oda'

class SezonFiyati(models.Model):
    oda_tipi = models.ForeignKey(OdaTipi, on_delete=models.CASCADE)
    baslangic_tarihi = models.DateField()
    bitis_tarihi = models.DateField()
    gecelik_fiyat = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = 'sezon_fiyati'

class Misafir(models.Model):
    ad = models.CharField(max_length=50)
    soyad = models.CharField(max_length=50)
    tc_pasaport_no = models.CharField(max_length=20, unique=True)
    telefon = models.CharField(max_length=20)
    eposta = models.EmailField(unique=True, db_index=True)
    dogum_tarihi = models.DateField(null=True, blank=True)

    class Meta:
        db_table = 'misafir'

class Personel(models.Model):
    ad = models.CharField(max_length=50)
    soyad = models.CharField(max_length=50)
    gorev = models.CharField(max_length=30)
    ise_giris_tarihi = models.DateField()

    class Meta:
        db_table = 'personel'

class Kullanici(models.Model):
    kullanici_adi = models.CharField(max_length=50, unique=True)
    sifre = models.CharField(max_length=255)
    rol = models.CharField(max_length=20)
    misafir = models.ForeignKey(Misafir, on_delete=models.SET_NULL, null=True, blank=True)
    personel = models.ForeignKey(Personel, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        db_table = 'kullanici'

class Rezervasyon(models.Model):
    misafir = models.ForeignKey(Misafir, on_delete=models.CASCADE)
    oda = models.ForeignKey(Oda, on_delete=models.CASCADE)
    giris_tarihi = models.DateField(db_index=True)
    cikis_tarihi = models.DateField(db_index=True)
    kisi_sayisi = models.IntegerField()
    durum = models.CharField(max_length=20, default='beklemede')
    olusturma_tarihi = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'rezervasyon'

class Konaklama(models.Model):
    rezervasyon = models.OneToOneField(Rezervasyon, on_delete=models.CASCADE)
    gercek_giris_zamani = models.DateTimeField(null=True, blank=True)
    gercek_cikis_zamani = models.DateTimeField(null=True, blank=True)
    personel = models.ForeignKey(Personel, on_delete=models.SET_NULL, null=True)

    class Meta:
        db_table = 'konaklama'

class EkHizmet(models.Model):
    hizmet_adi = models.CharField(max_length=100)
    birim_fiyat = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = 'ek_hizmet'

class KonaklamaHizmeti(models.Model):
    konaklama = models.ForeignKey(Konaklama, on_delete=models.CASCADE)
    ek_hizmet = models.ForeignKey(EkHizmet, on_delete=models.CASCADE)
    adet = models.IntegerField(default=1)
    tarih = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'konaklama_hizmeti'

class Odeme(models.Model):
    konaklama = models.ForeignKey(Konaklama, on_delete=models.CASCADE)
    tutar = models.DecimalField(max_digits=10, decimal_places=2)
    odeme_turu = models.CharField(max_length=20)
    tarih = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'odeme'

class TemizlikKaydi(models.Model):
    oda = models.ForeignKey(Oda, on_delete=models.CASCADE)
    personel = models.ForeignKey(Personel, on_delete=models.SET_NULL, null=True)
    tarih = models.DateTimeField(auto_now_add=True)
    durum = models.CharField(max_length=30)

    class Meta:
        db_table = 'temizlik_kaydi'

class IslemLog(models.Model):
    tablo_adi = models.CharField(max_length=50)
    islem_turu = models.CharField(max_length=20)
    kayit_id = models.IntegerField()
    aciklama = models.TextField()
    tarih = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'islem_log'
