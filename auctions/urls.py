from django.urls import path

from . import views

urlpatterns = [
    path("", views.active_listings, name="active_listings"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),

    path('create_listing', views.create_listing, name='create_listing'),

    path("active_listings", views.active_listings, name='active_listings'),

    path("listing_details/<int:listing_id>", views.listing_details, name="listing_details"),

    path('toggle_watchlist/<int:listing_id>/', views.toggle_watchlist, name='toggle_watchlist'),

    path('place_bid/<int:listing_id>/', views.place_bid, name='place_bid'),

    path('close_auction/<int:listing_id>/',views.close_auction, name='close_auction'),

    path("category_listings/<int:category_id>", views.category_listings, name="category_listings"),

    path('all_categories', views.all_categories, name='all_categories'),

    path('watchlist', views.watchlist, name='watchlist'),

    path("add_comment/<int:listing_id>", views.add_comment, name="add_comment"),
    
    path('unwatchlist/<int:listing_id>', views.unwatchlist, name='unwatchlist'),

     
]
