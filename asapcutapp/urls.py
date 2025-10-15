from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from .views.invoice import invoice_pdf

from .views.arrears import arrears_list, download_excel, download_pdf
from .views.base_view import base
from .views.authentication import login_view, user_logout
from .views.dashboard import dashboard
from .views.universities import university_list, add_university, update_university, delete_university
from .views.association import association_list, add_association, update_association, delete_association
from .views.contribution import contribution_list, add_contribution_for_year, contributions_pdf, contributions_excel
from .users_list import users_list


urlpatterns = [
    path('', base, name='base'),
    path('login/', login_view, name='login'),
    path('dashboard/', dashboard, name='dashboard'),
    path('login/', user_logout, name='user_logout'),

    path('universities/', university_list, name='university_list'),
    path('universities/add/', add_university, name='add_university'),
    path('universities/update/<int:id>/', update_university, name='update_university'),
    path('universities/delete/<int:id>/', delete_university, name='delete_university'),

    path('associations/', association_list, name='association_list'),
    path('associations/add/', add_association, name='add_association'),
    path('associations/<int:id>/update/', update_association, name='update_association'),
    path('associations/<int:id>/delete/', delete_association, name='delete_association'),

    path('contributions/', contribution_list, name='contribution_list'),
    path('add/<str:year>/', add_contribution_for_year, name='add_contribution_for_year'),

    path('contributions/export/pdf/<str:year>/', contributions_pdf, name='contributions_pdf'),
    path('contributions/export/excel/<str:year>/', contributions_excel, name='contributions_excel'),


    path('arrears/', arrears_list, name='arrears_list'),

    path('arrears/download/pdf/', download_pdf, name='download_pdf'),
    path('arrears/download/excel/', download_excel, name='download_excel'),
    path('invoice/<str:year>/', invoice_pdf, name='invoice_pdf'),
    path('users/', views.users_list, name='users_list'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

