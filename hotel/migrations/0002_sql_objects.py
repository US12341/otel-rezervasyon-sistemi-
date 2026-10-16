from django.db import migrations

SQL_STATEMENTS = [
    "DROP TRIGGER IF EXISTS trg_rezervasyon_cakisma_engelle;",
    """
    CREATE TRIGGER trg_rezervasyon_cakisma_engelle
    BEFORE INSERT ON rezervasyon
    FOR EACH ROW
    BEGIN
        DECLARE cakisma_sayisi INT;
        SELECT COUNT(*) INTO cakisma_sayisi
        FROM rezervasyon
        WHERE oda_id = NEW.oda_id
          AND durum != 'iptal'
          AND (NEW.giris_tarihi < cikis_tarihi AND NEW.cikis_tarihi > giris_tarihi);

        IF cakisma_sayisi > 0 THEN
            SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Hata: Secilen tarihlerde bu oda zaten rezerve edilmis!';
        END IF;
    END;
    """,
    "DROP TRIGGER IF EXISTS trg_konaklama_durum_guncelle;",
    """
    CREATE TRIGGER trg_konaklama_durum_guncelle
    AFTER UPDATE ON konaklama
    FOR EACH ROW
    BEGIN
        DECLARE v_oda_id BIGINT;
        SELECT oda_id INTO v_oda_id FROM rezervasyon WHERE id = NEW.rezervasyon_id;

        IF OLD.gercek_giris_zamani IS NULL AND NEW.gercek_giris_zamani IS NOT NULL THEN
            UPDATE oda SET durum = 'dolu' WHERE id = v_oda_id;
        END IF;

        IF OLD.gercek_cikis_zamani IS NULL AND NEW.gercek_cikis_zamani IS NOT NULL THEN
            UPDATE oda SET durum = 'temizlikte' WHERE id = v_oda_id;
        END IF;
    END;
    """,
    "DROP TRIGGER IF EXISTS trg_rezervasyon_log;",
    """
    CREATE TRIGGER trg_rezervasyon_log
    AFTER INSERT ON rezervasyon
    FOR EACH ROW
    BEGIN
        INSERT INTO islem_log (tablo_adi, islem_turu, kayit_id, aciklama, tarih)
        VALUES ('rezervasyon', 'INSERT', NEW.id, CONCAT('Yeni rezervasyon. Oda ID: ', NEW.oda_id), NOW());
    END;
    """,
    "DROP TRIGGER IF EXISTS trg_odeme_log;",
    """
    CREATE TRIGGER trg_odeme_log
    AFTER INSERT ON odeme
    FOR EACH ROW
    BEGIN
        INSERT INTO islem_log (tablo_adi, islem_turu, kayit_id, aciklama, tarih)
        VALUES ('odeme', 'INSERT', NEW.id, CONCAT('Odeme alindi. Tutar: ', NEW.tutar), NOW());
    END;
    """,
    "DROP PROCEDURE IF EXISTS sp_bos_odalari_getir;",
    """
    CREATE PROCEDURE sp_bos_odalari_getir(
        IN p_giris_tarihi DATE,
        IN p_cikis_tarihi DATE,
        IN p_oda_tipi_id BIGINT
    )
    BEGIN
        SELECT o.id, o.oda_numarasi, o.kat, ot.tip_adi, ot.kapasite, ot.temel_fiyat
        FROM oda o
        INNER JOIN oda_tipi ot ON o.oda_tipi_id = ot.id
        WHERE (p_oda_tipi_id IS NULL OR o.oda_tipi_id = p_oda_tipi_id)
          AND o.id NOT IN (
              SELECT r.oda_id
              FROM rezervasyon r
              WHERE r.durum != 'iptal'
                AND (p_giris_tarihi < r.cikis_tarihi AND p_cikis_tarihi > r.giris_tarihi)
          );
    END;
    """,
    "DROP PROCEDURE IF EXISTS sp_konaklama_toplam_tutar;",
    """
    CREATE PROCEDURE sp_konaklama_toplam_tutar(IN p_konaklama_id BIGINT)
    BEGIN
        DECLARE v_oda_tutari DECIMAL(10,2) DEFAULT 0;
        DECLARE v_hizmet_tutari DECIMAL(10,2) DEFAULT 0;

        SELECT DATEDIFF(r.cikis_tarihi, r.giris_tarihi) * COALESCE(
            (SELECT sf.gecelik_fiyat FROM sezon_fiyati sf 
             WHERE sf.oda_tipi_id = o.oda_tipi_id 
               AND r.giris_tarihi BETWEEN sf.baslangic_tarihi AND sf.bitis_tarihi LIMIT 1),
            ot.temel_fiyat
        ) INTO v_oda_tutari
        FROM konaklama k
        INNER JOIN rezervasyon r ON k.rezervasyon_id = r.id
        INNER JOIN oda o ON r.oda_id = o.id
        INNER JOIN oda_tipi ot ON o.oda_tipi_id = ot.id
        WHERE k.id = p_konaklama_id;

        SELECT COALESCE(SUM(kh.adet * eh.birim_fiyat), 0) INTO v_hizmet_tutari
        FROM konaklama_hizmeti kh
        INNER JOIN ek_hizmet eh ON kh.ek_hizmet_id = eh.id
        WHERE kh.konaklama_id = p_konaklama_id;

        SELECT p_konaklama_id AS konaklama_id, v_oda_tutari AS oda_tutari,
               v_hizmet_tutari AS ek_hizmet_tutari, (v_oda_tutari + v_hizmet_tutari) AS toplam_tutar;
    END;
    """,
    "DROP PROCEDURE IF EXISTS sp_aylik_doluluk_ve_gelir;",
    """
    CREATE PROCEDURE sp_aylik_doluluk_ve_gelir(IN p_yil INT, IN p_ay INT)
    BEGIN
        DECLARE v_toplam_oda INT DEFAULT 1;
        SELECT COUNT(*) INTO v_toplam_oda FROM oda;
        IF v_toplam_oda = 0 THEN SET v_toplam_oda = 1; END IF;

        SELECT p_yil AS yil, p_ay AS ay,
               COUNT(DISTINCT r.id) AS toplam_rezervasyon,
               ROUND((COUNT(DISTINCT r.oda_id) / v_toplam_oda) * 100, 2) AS doluluk_orani_yuzde,
               COALESCE((SELECT SUM(od.tutar) FROM odeme od WHERE YEAR(od.tarih) = p_yil AND MONTH(od.tarih) = p_ay), 0) AS toplam_gelir
        FROM rezervasyon r
        WHERE YEAR(r.giris_tarihi) = p_yil AND MONTH(r.giris_tarihi) = p_ay AND r.durum != 'iptal';
    END;
    """,
    """
    CREATE OR REPLACE VIEW vw_bugun_giris_cikis AS
    SELECT r.id AS rezervasyon_id, m.ad, m.soyad, m.telefon, o.oda_numarasi,
           r.giris_tarihi, r.cikis_tarihi,
           CASE WHEN r.giris_tarihi = CURDATE() THEN 'Giris Yapacak'
                WHEN r.cikis_tarihi = CURDATE() THEN 'Cikis Yapacak' END AS islem_tipi
    FROM rezervasyon r
    INNER JOIN misafir m ON r.misafir_id = m.id
    INNER JOIN oda o ON r.oda_id = o.id
    WHERE (r.giris_tarihi = CURDATE() OR r.cikis_tarihi = CURDATE()) AND r.durum != 'iptal';
    """,
    """
    CREATE OR REPLACE VIEW vw_oda_durum_temizlik AS
    SELECT o.id AS oda_id, o.oda_numarasi, o.kat, ot.tip_adi,
           o.durum AS guncel_durum, MAX(tk.tarih) AS son_temizlik_tarihi
    FROM oda o
    INNER JOIN oda_tipi ot ON o.oda_tipi_id = ot.id
    LEFT JOIN temizlik_kaydi tk ON o.id = tk.oda_id
    GROUP BY o.id, o.oda_numarasi, o.kat, ot.tip_adi, o.durum;
    """
]

class Migration(migrations.Migration):
    dependencies = [
        ('hotel', '0001_initial'),
    ]
    operations = [
        migrations.RunSQL(SQL_STATEMENTS),
    ]
