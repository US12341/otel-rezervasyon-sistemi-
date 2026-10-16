from django.contrib import admin
from django.urls import path
from hotel import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/login/', views.login_view),
    path('api/odalar/bos/', views.bos_odalar_view),
    path('api/rezervasyon/olustur/', views.rezervasyon_olustur_view),
    path('api/konaklama/checkin/', views.checkin_view),
    path('api/konaklama/checkout/', views.checkout_view),
    path('api/konaklama/<int:konaklama_id>/tutar/', views.konaklama_tutar_view),
    path('api/rapor/gunluk-liste/', views.gunluk_liste_view),
    path('api/rapor/oda-durum/', views.oda_durum_view),
    path('api/rapor/aylik-gelir/', views.aylik_rapor_view),
]
