
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from socialm.views import *
import uuid

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index, name='homepage'),
    path('register', register, name= 'registerpage'),
    path('login', giris, name='loginpage'),
    path('logout',cikis, name='logoutpage'),
    path('settings', hesap, name='settingspage'),
    path('upload', upload, name='uploadpage'),
    path('profile/<str:pk>', profile, name='profilepage'),
    path('like-post', like, name='like-post'),
    path('post/<uuid:post_id>/', post_detail, name='post_detail'),
    path('post/<uuid:post_id>/add_comment/',add_comment_to_post, name='add_comment_to_post'),
    path('edit-post/<uuid:post_id>/',edit_post, name='edit_post'),
    path('edit-comment/<uuid:comment_id>/', edit_comment, name='edit_comment'),
    path('delete-post/<uuid:post_id>/',delete_post, name='delete_post'),
    path('delete-comment/<uuid:comment_id>/', delete_comment, name='delete_comment'),
    path('approve_user/<int:user_id>/', approve_user, name='approve_user'),
    path('unapproved-users/',unapproved_users, name='unapproved_users'),
    path('grant_moderator/<str:user_id>/',grant_moderator, name='grant_moderator'),
    path('revoke_moderator/<int:user_id>/', revoke_moderator, name='revoke_moderator'),
    path('admin_dashboard/', admin_dashboard, name='admin_dashboard'),
    path('create_report/<uuid:post_id>/', create_report, name='create_report'),
    path('ban-user/<int:user_id>/', ban_user, name='ban_user'),
    path('unban-user/<int:user_id>/', unban_user, name='unban_user'),
    path('update_email_password/', update_email_password, name='update_email_password'),
   


]
urlpatterns = urlpatterns+static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
