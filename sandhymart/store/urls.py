from django.urls import path, include
from . import views

urlpatterns = [

    path('', views.store, name='store'),
    path('search/', views.searching, name='searching'),
    path('checkout/', views.checkout, name='checkout'),

    path('get_items/', views.getItems, name='getItemstotal'),

    path('add_item/', views.addItem, name='addItem'),
    path('update_item/', views.updateItem, name='update_item'),
    path('process_order', views.processOrder, name='processOrder'),

    path('product_list/', views.productList, name='productList'),
    path('add_product/', views.addProduct, name='addProduct'),
    path('update_product/<int:id_product>',
         views.updateProduct, name='updateProduct'),
    path('product_delete/', views.productDelete, name='productDelete'),

    path('register_page/', views.registerPage, name='registerPage'),
    path('login_page/', views.loginPage, name='loginPage'),
    path('logout_page/', views.logoutPage, name='logoutPage'),
    path('account_settings/', views.accountSettings, name='accountSettings'),

    path('order_list/', views.orderList, name='orderList'),
    path('detail_order/<str:order_id>', views.detailOrder, name='detailOrder'),

]
