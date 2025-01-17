from django.urls import path, include
from django.contrib import admin
from .views import user, vendor, material, receipt, invoice, purchaserequisition, quotation, purchaseorder, document
from .views.ajax import material_api, data_api, stock_api, vendor_api, user_api, receipt_api, invoice_api
from django.shortcuts import redirect

app_name = 'MM'
urlpatterns = [
    # user
    path('login/', user.login, name='login'),
    path('register/', user.register, name='register'),
    path('home/', user.home, name='home'),
    path('logout/', user.logout, name='logout'),
    # vendor
    path('vendor/create/', vendor.create, name='create_vendor'),
    path('vendor/display/<int:pk>/', vendor.display, name='display_vendor'),
    path('vendor/search/', vendor.search, name='search_vendor'),
    path('vendor/history/', vendor.history, name='search_vendor_history'),
    # material
    path('material/search/', material.search_material, name='search_material'),
    path('material/item/create/', material.create_item, name='create_item'),
    path('material/item/stock/', material.search_item_stock, name='search_item_stock'),
    # receipt
    path('receipt/display/', receipt.display_receipt, name='display_receipt'),
    path('receipt/search/', receipt.search_receipt, name='search_receipt'),
    path('receipt/create/', receipt.load_order_item, name='load_order_item_receipt'),
    path('receipt/order/display/<int:pk>/', receipt.display_purchase_order, name='display_order_receipt'),
    path('receipt/orders/search/', receipt.search_orders, name='search_orders_receipt'),
    # invoice
    path('invoice/create/', invoice.load_order_item, name='load_order_item_invoice'),
    path('invoice/search/', invoice.search_invoice, name='search_invoice'),
    path('invoice/display/', invoice.display_invoice, name='display_invoice'),
    path('invoice/payment/', invoice.payment, name='pay_invoice'),
    path('invoice/order/display/<int:pk>/', invoice.display_purchase_order, name='display_order_invoice'),
    path('invoice/orders/search/', invoice.search_orders, name='search_orders_invoice'),
    # document flow
    path('document/search/', document.search_document_flow, name='search_document_flow'),
    path('document/display/<int:pk>/', document.display_document_flow, name='display_document_flow'),

    # ajax
    ## user
    path('api/user/loadAll/', user_api.load_user, name='ajax_load_user'),
    path('get_user_info/', user_api.get_user_info, name='get_user_info'),
    ## vendor
    path('api/vendor/update/', vendor_api.update_vendor, name='ajax_update_vendor'),
    path('api/vendor/search/', vendor_api.search_vendor, name='ajax_search_vendor'),
    path('api/vendor/create/', vendor_api.create_vendor, name='ajax_create_vendor'),
    path('api/vendor/score/', vendor_api.search_vendor_history, name='ajax_search_vendor_history'),
    path('api/vendor/search_info/', vendor_api.get_countries_and_companies, name='get_countries_and_companies'),
    ## material
    path('api/material/item/search/', material_api.search_item, name='ajax_search_item'),
    path('api/material/item/update/', material_api.update_item, name='ajax_update_item'),
    path('api/material/item/create/', material_api.create_item, name='ajax_create_item'),
    path('api/material/item/stockHistory/', material_api.update_item, name='ajax_update_item'),
    path('api/material/stock/search/', material_api.search_stock_history, name='ajax_search_stock_history'),
    path('api/material/stock/getByName/', stock_api.getByName, name='ajax_getStockByName'),
    ## receipt
    path('api/receipt/create/', receipt_api.create_receipt, name='ajax_create_receipt'),
    path('api/receipt/search/', receipt_api.search_receipt, name='ajax_search_receipt'),
    ## invoice
    path('api/invoice/search/', invoice_api.search_invoice, name='ajax_search_invoice'),
    path('api/invoice/create/', invoice_api.create_invoice, name='ajax_create_invoice'),
    path('api/invoice/searchUnpaid/', invoice_api.search_unpaied_invoice, name='ajax_search_unpaied_invoice'),
    path('api/invoice/pay/', invoice_api.pay, name='ajax_pay_invoice'),
    # pre-determined data
    path('api/data/country/', data_api.load_country, name='ajax_load_country'),
    path('api/data/company/', data_api.load_company, name='ajax_load_company'),
    path('api/data/currency/', data_api.load_currency, name='ajax_load_currency'),
    path('api/data/language/', data_api.load_language, name='ajax_load_language'),
    path('api/data/meaunit/', data_api.load_meaunit, name='ajax_load_meaunit'),
    path('api/data/pgrp/', data_api.load_pgrp, name='ajax_load_pgrp'),
    path('api/data/plant/', data_api.load_plant, name='ajax_load_plant'),
    path('api/data/porg/', data_api.load_porg, name='ajax_load_porg'),
    path('api/data/sorg/', data_api.load_sorg, name='ajax_load_sorg'),
    path('api/data/tptype/', data_api.load_tptype, name='ajax_load_tptype'),
    ##
    path('purchaserequisition/insert/', purchaserequisition.insert, name='insert_pur'),
    path('purchaserequisition/insertreque/', purchaserequisition.requeinsert, name='insert_pur'),
    path('purchaserequisition/delete/', purchaserequisition.deletereque, name='display_item'),
    path('purchaserequisition/getpq/', purchaserequisition.getpq, name='insert_pur'),
    path('purchaserequisition/getpqinfo/<int:pk>/', purchaserequisition.getpqinfo, name='insert_pur'),
    path('purchaserequisition/newinsertreque/', purchaserequisition.newrequeinsert, name='insert_pur'),

    path('quotation/getall', quotation.getall, name='search_pur'),
    path('quotation/searchqinggou', quotation.searchqinggou, name='search_pur'),
    path('quotation/searchquo', quotation.searchquo, name='search_pur'),
    path('quotation/vqcreate/<int:pk>/', purchaseorder.vqcreate, name='search_pur'),
    path('quotation/vqcreatejiekou/', purchaseorder.vqcreatejiekou, name='search_pur'),
    path('quotation/vreview/', purchaseorder.vreview, name='search_pur'),

    path('purchaseorder/pcs/', quotation.pcs, name='search_pur'),
    path('purchaseorder/info/<int:pk>/', purchaseorder.poinfo, name='search_pur'),
    path('purchaseorder/modifyinfo/<int:pk>/', purchaseorder.pomodifyinfo, name='search_pur'),
    path('purchaseorder/modifyinfo2/', purchaseorder.pomodifyinfo2, name='search_pur'),
    path('purchaseorder/modifyinfo3/', purchaseorder.pomodifyinfo3, name='search_pur'),
    path('purchaseorder/cresys/<int:pk>/', purchaserequisition.createsys, name='search_pur'),
    path('purchaseorder/cremanujiekou/', purchaserequisition.creamanujiekou, name='search_pur'),
    path('purchaseorder/quomodify/<int:pk>/', purchaserequisition.quomodify, name='search_pur'),
    path('purchaseorder/quomodifyjiekou/', purchaserequisition.quomodifyjiekou, name='search_pur'),

    path('quotation/makebyrq/<int:pk>/<int:itemId>', quotation.makebyrq, name='search_pur'),
    path('quotation/rfqinfo', quotation.rfqinfojiekou, name='search_pur'),
    path('purchaseorder/searchpo', purchaseorder.searchpo, name='search_pur'),
    path('purchaseorder/choose', purchaseorder.choose, name='search_pur'),
    path('quotation/searchqo', purchaseorder.searchqo, name='search_pur'),
    path('purchaserequisition/getmodifyinfo/<int:pk>/', purchaserequisition.getmodifyinfo, name='insert_pur'),
    path('purchaserequisition/getmodifyinfo2/', purchaserequisition.getmodifyinfo2, name='insert_pur'),
    path('quotation/rfqcreateinfo/<int:pk>/', quotation.rfqinfo, name='insert_pur'),
    path('quotation/rfqinfo/<int:pk>/', quotation.rfqinfo2, name='insert_pur'),
    path('purchaseorder/searchjiekou', purchaseorder.searchjiekou, name='search_pur'),
    path('purchaseorder/searchjiekouzhuanhua', purchaseorder.searchjiekouzhuanhua, name='search_pur'),
    path('purchaserequisition/pomanage', purchaserequisition.pomanage, name='search_pur'),
    path('purchaserequisition/prmanage', purchaserequisition.prmanage, name='search_pur'),
    path('purchaserequisition/quoma', purchaserequisition.quoma, name='search_pur'),
]
