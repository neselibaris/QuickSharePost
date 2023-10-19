from django.db import models
from django.contrib.auth.models import User
import uuid
from datetime import datetime


# Create your models here.


# Create your models here.
def custom_upload_to(instance, filename):
    # instance.user.username ile yeni yükleme yolunu oluşturun
    return f"profile_image/{instance.user.username}/{filename}"


def custom_upload_post_to(instance, filename):
    # instance.user.username ile yeni yükleme yolunu oluşturun
    return f"post_images/{instance.user.username}/{filename}"


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    id_user = models.IntegerField(default=True)
    bio = models.TextField(blank=True, null=True)
    profileimg = models.ImageField(
        upload_to=custom_upload_to, default="blank-profile-picture.jpg"
    )
    location = models.CharField(max_length=100, blank=True)
    is_banned = models.BooleanField(("Hesap yasaklanmış mı?"), default=False)
    is_approved = models.BooleanField(("Hesap onaylanmış mı?"), default=True)
    is_moderator = models.BooleanField(("Moderatör yetkisi verildi mi?"), default=False)
    education = models.CharField(max_length=100, blank=True, null=True)  # Eğitim süreci
    birthdate = models.DateField(null=True, blank=True)  # Doğum tarihi
    email = models.EmailField(max_length=100, blank=True, null=True)  # E-posta

    def __str__(self):
        return self.user.username


class Post(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to="post_images")
    caption = models.TextField()
    created_at = models.DateTimeField(default=datetime.now)
    no_of_likes = models.IntegerField(default=0)
    liked_by = models.ManyToManyField(User, related_name="liked_posts", blank=True)

    def get_like_count(self):
        return LikePost.objects.filter(post_id=str(self.id)).count()

    def __str__(self):
        return self.user.username


class Comment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    text = models.TextField()
    created_on = models.DateTimeField(default=datetime.now)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.author.username} - {self.text} - {self.post}"


class Notification(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE
    )  # Bildirimi alacak kullanıcı
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE
    )  # Bildirim hangi gönderi ile ilgili
    comment = models.ForeignKey(
        Comment, on_delete=models.CASCADE, null=True, blank=True
    )  # Eğer yorumla ilgiliyse yorumu belirtin
    is_read = models.BooleanField(
        default=False
    )  # Bildirimin okunup okunmadığını belirtin
    created_at = models.DateTimeField(auto_now_add=True)  # Bildirim oluşturulma tarihi

    def __str__(self):
        return f"Bildirim {self.id}"

    def get_notification_text(self):
        if self.is_comment:
            return f'{self.user.username} yorum yaptı: "{self.comment.text}"'
        else:
            return f'Birisi "{self.post.caption}" adlı postunu beğendi'


class LikePost(models.Model):
    post = models.ForeignKey("Post", on_delete=models.CASCADE)
    username = models.CharField(max_length=100)

    def __str__(self):
        return self.username


class Report(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name="Raporlamayı Yapan"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        default=1,
        verbose_name="Raporlanan Postun Sahibi",
    )

    def __str__(self):
        return f"{self.user.username} : {self.title}"
