from django.urls import path

import views

urlpatterns = [
    path("", views.health),
    path("predict", views.predict),
    path("api/turbines", views.get_all_turbines),
    path("api/turbines/<str:turbine_id>", views.get_turbine_by_id),
    path("api/forecast", views.forecast),
]
