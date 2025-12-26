from django.urls import path
from users.views import signup,signin,signout

urlpatterns = [
    path('signup/', signup, name='signup'),
    path('signin/', signin, name='signin'),
    path('logout/', signout, name='logout'),
]
