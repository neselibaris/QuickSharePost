from django.db import models
from django.contrib.auth.models import User
import uuid
from datetime import datetime


# Create your models here.

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    id_user = models.IntegerField(default=True)
    bio = models.TextField(blank=True, null=True)
    profileimg = models.ImageField(
        upload_to='profile_image', default='blank-profile-picture.jpg')
    location = models.CharField(max_length=100, blank=True)
    is_banned = models.BooleanField(("Hesap yasaklanmış mı?"), default=False)
    is_approved = models.BooleanField(("Hesap onaylanmış mı?"), default=False)
    is_moderator = models.BooleanField(("Moderatör yetkisi verildi mi?"), default=False)
    education = models.CharField(max_length=100, blank=True, null=True)  # Eğitim süreci
    birthdate = models.DateField(null=True, blank=True)  # Doğum tarihi
    email = models.EmailField(max_length=100, blank=True, null=True)  # E-posta

    def __str__(self):
        return self.user.username
    


class Post(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='post_images')
    caption = models.TextField()
    created_at = models.DateTimeField(default=datetime.now)
    no_of_likes = models.IntegerField(default=0)


    def get_like_count(self):
        return LikePost.objects.filter(post_id=str(self.id)).count()
    

    def __str__(self):
        return self.user.username


class LikePost(models.Model):
    post_id = models.CharField(max_length=500)
    username = models.CharField(max_length=100)

    def __str__(self):
        return self.username


class Comment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    text = models.TextField()
    created_on = models.DateTimeField(default=datetime.now)

    def __str__(self):
        return f"{self.author.username} - {self.text} - {self.post}"


class Report(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE ,verbose_name="Raporlamayı Yapan")
    created_at = models.DateTimeField(auto_now_add=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, default=1, verbose_name="Raporlanan Postun Sahibi")

    def __str__(self):
        return f"{self.user.username} : {self.title}" 

