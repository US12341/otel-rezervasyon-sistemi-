from django.db import connection

def dictfetchall(cursor):
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]

class OtelRepository:

    @staticmethod
    def bos_odalari_getir(giris_tarihi, cikis_tarihi, oda_tipi_id=None):
        with connection.cursor() as cursor:
            cursor.callproc('sp_bos_odalari_getir', [giris_tarihi, cikis_tarihi, oda_tipi_id])
            return dictfetchall(cursor)

    @staticmethod
    def konaklama_tutar_hesapla(konaklama_id):
        with connection.cursor() as cursor:
            cursor.callproc('sp_konaklama_toplam_tutar', [konaklama_id])
            sonuc = dictfetchall(cursor)
            return sonuc[0] if sonuc else None

    @staticmethod
    def aylik_rapor_getir(yil, ay):
        with connection.cursor() as cursor:
            cursor.callproc('sp_aylik_doluluk_ve_gelir', [yil, ay])
            sonuc = dictfetchall(cursor)
            return sonuc[0] if sonuc else None

    @staticmethod
    def bugun_giris_cikis_listesi():
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM vw_bugun_giris_cikis")
            return dictfetchall(cursor)

    @staticmethod
    def oda_durum_temizlik_listesi():
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM vw_oda_durum_temizlik")
            return dictfetchall(cursor)

    @staticmethod
    def rezervasyon_olustur(misafir_id, oda_id, giris_tarihi, cikis_tarihi, kisi_sayisi):
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO rezervasyon (misafir_id, oda_id, giris_tarihi, cikis_tarihi, kisi_sayisi, durum, olusturma_tarihi)
                VALUES (%s, %s, %s, %s, %s, 'onaylandi', NOW())
                """,
                [misafir_id, oda_id, giris_tarihi, cikis_tarihi, kisi_sayisi]
            )
            return cursor.lastrowid

    @staticmethod
    def checkin_yap(rezervasyon_id, personel_id):
        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO konaklama (rezervasyon_id, personel_id, gercek_giris_zamani) VALUES (%s, %s, NOW())",
                [rezervasyon_id, personel_id]
            )
            konaklama_id = cursor.lastrowid
            cursor.execute("UPDATE konaklama SET gercek_giris_zamani = NOW() WHERE id = %s", [konaklama_id])
            return konaklama_id

    @staticmethod
    def checkout_transaction(konaklama_id, odeme_tutari, odeme_turu):
        with connection.cursor() as cursor:
            try:
                cursor.execute("START TRANSACTION;")

                cursor.execute(
                    "UPDATE konaklama SET gercek_cikis_zamani = NOW() WHERE id = %s AND gercek_cikis_zamani IS NULL",
                    [konaklama_id]
                )
                if cursor.rowcount == 0:
                    raise Exception("Aktif konaklama bulunamadi veya zaten cikis yapilmis.")

                if float(odeme_tutari) <= 0:
                    raise Exception("Gecersiz odeme tutari! Islem geri alindi (ROLLBACK).")

                cursor.execute(
                    "INSERT INTO odeme (konaklama_id, tutar, odeme_turu, tarih) VALUES (%s, %s, %s, NOW())",
                    [konaklama_id, odeme_tutari, odeme_turu]
                )

                cursor.execute(
                    "UPDATE rezervasyon SET durum = 'tamamlandi' WHERE id = (SELECT rezervasyon_id FROM konaklama WHERE id = %s)",
                    [konaklama_id]
                )

                cursor.execute("COMMIT;")
                return True
            except Exception as e:
                cursor.execute("ROLLBACK;")
                raise e
