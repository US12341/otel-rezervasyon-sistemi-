import jwt
import datetime
from functools import wraps
from django.conf import settings
from django.http import JsonResponse
from .models import Kullanici
from .repositories import OtelRepository

class AuthService:

    @staticmethod
    def login(kullanici_adi, sifre):
        kullanici = Kullanici.objects.filter(kullanici_adi=kullanici_adi, sifre=sifre).first()
        if not kullanici:
            return None

        payload = {
            'user_id': kullanici.id,
            'kullanici_adi': kullanici.kullanici_adi,
            'rol': kullanici.rol,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=12)
        }
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
        return {'token': token, 'rol': kullanici.rol, 'kullanici_adi': kullanici.kullanici_adi}

def jwt_required(allowed_roles=None):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            auth_header = request.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                return JsonResponse({'hata': 'Yetkisiz erisim: Token eksik'}, status=401)

            token = auth_header.split(' ')[1]
            try:
                payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
                request.user_payload = payload
                if allowed_roles and payload.get('rol') not in allowed_roles:
                    return JsonResponse({'hata': 'Bu islem icin yetkiniz yok'}, status=403)
            except jwt.ExpiredSignatureError:
                return JsonResponse({'hata': 'Token suresi dolmus'}, status=401)
            except jwt.InvalidTokenError:
                return JsonResponse({'hata': 'Gecersiz token'}, status=401)

            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator

class OtelService:

    @staticmethod
    def bos_odalari_ara(giris, cikis, oda_tipi_id=None):
        return OtelRepository.bos_odalari_getir(giris, cikis, oda_tipi_id)

    @staticmethod
    def rezervasyon_yap(data):
        return OtelRepository.rezervasyon_olustur(
            data['misafir_id'], data['oda_id'], data['giris_tarihi'], data['cikis_tarihi'], data['kisi_sayisi']
        )

    @staticmethod
    def checkin_islemi(rezervasyon_id, personel_id):
        return OtelRepository.checkin_yap(rezervasyon_id, personel_id)

    @staticmethod
    def checkout_islemi(konaklama_id, odeme_tutari, odeme_turu):
        return OtelRepository.checkout_transaction(konaklama_id, odeme_tutari, odeme_turu)

    @staticmethod
    def konaklama_hesabi_getir(konaklama_id):
        return OtelRepository.konaklama_tutar_hesapla(konaklama_id)

    @staticmethod
    def aylik_rapor(yil, ay):
        return OtelRepository.aylik_rapor_getir(yil, ay)

    @staticmethod
    def gunluk_giris_cikislar():
        return OtelRepository.bugun_giris_cikis_listesi()

    @staticmethod
    def oda_ve_temizlik_durumlari():
        return OtelRepository.oda_durum_temizlik_listesi()
