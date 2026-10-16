import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .services import AuthService, OtelService, jwt_required

@csrf_exempt
def login_view(request):
    if request.method != 'POST':
        return JsonResponse({'hata': 'Sadece POST desteklenir'}, status=405)
    data = json.loads(request.body)
    sonuc = AuthService.login(data.get('kullanici_adi'), data.get('sifre'))
    if not sonuc:
        return JsonResponse({'hata': 'Kullanici adi veya sifre hatali'}, status=401)
    return JsonResponse(sonuc)

def bos_odalar_view(request):
    giris = request.GET.get('giris')
    cikis = request.GET.get('cikis')
    oda_tipi = request.GET.get('oda_tipi_id')
    if not giris or not cikis:
        return JsonResponse({'hata': 'giris ve cikis tarihleri zorunludur'}, status=400)
    odalar = OtelService.bos_odalari_ara(giris, cikis, oda_tipi)
    return JsonResponse({'bos_odalar': odalar})

@csrf_exempt
@jwt_required(allowed_roles=['misafir', 'resepsiyon', 'yonetici'])
def rezervasyon_olustur_view(request):
    if request.method != 'POST':
        return JsonResponse({'hata': 'Sadece POST desteklenir'}, status=405)
    try:
        data = json.loads(request.body)
        rez_id = OtelService.rezervasyon_yap(data)
        return JsonResponse({'mesaj': 'Rezervasyon olusturuldu', 'rezervasyon_id': rez_id}, status=201)
    except Exception as e:
        return JsonResponse({'hata': str(e)}, status=400)

@csrf_exempt
@jwt_required(allowed_roles=['resepsiyon', 'yonetici'])
def checkin_view(request):
    if request.method != 'POST':
        return JsonResponse({'hata': 'Sadece POST desteklenir'}, status=405)
    try:
        data = json.loads(request.body)
        konaklama_id = OtelService.checkin_islemi(data['rezervasyon_id'], data.get('personel_id'))
        return JsonResponse({'mesaj': 'Check-in basarili', 'konaklama_id': konaklama_id})
    except Exception as e:
        return JsonResponse({'hata': str(e)}, status=400)

@csrf_exempt
@jwt_required(allowed_roles=['resepsiyon', 'yonetici'])
def checkout_view(request):
    if request.method != 'POST':
        return JsonResponse({'hata': 'Sadece POST desteklenir'}, status=405)
    try:
        data = json.loads(request.body)
        OtelService.checkout_islemi(data['konaklama_id'], data['tutar'], data.get('odeme_turu', 'Kredi Karti'))
        return JsonResponse({'mesaj': 'Check-out ve odeme islemi tamamlandi'})
    except Exception as e:
        return JsonResponse({'hata': str(e)}, status=400)

@jwt_required(allowed_roles=['resepsiyon', 'yonetici'])
def konaklama_tutar_view(request, konaklama_id):
    hesap = OtelService.konaklama_hesabi_getir(konaklama_id)
    return JsonResponse({'hesap_detayi': hesap})

@jwt_required(allowed_roles=['resepsiyon', 'yonetici'])
def gunluk_liste_view(request):
    liste = OtelService.gunluk_giris_cikislar()
    return JsonResponse({'bugun_giris_cikis': liste})

@jwt_required(allowed_roles=['resepsiyon', 'yonetici'])
def oda_durum_view(request):
    liste = OtelService.oda_ve_temizlik_durumlari()
    return JsonResponse({'oda_durumlari': liste})

@jwt_required(allowed_roles=['yonetici'])
def aylik_rapor_view(request):
    yil = int(request.GET.get('yil', 2026))
    ay = int(request.GET.get('ay', 10))
    rapor = OtelService.aylik_rapor(yil, ay)
    return JsonResponse({'rapor': rapor})
