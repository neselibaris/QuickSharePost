from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import update_session_auth_hash
from .form import *
from .models import *
from .models import Comment
from .models import Notification
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import *
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from .models import Message
from django.core.serializers import serialize
from django.views.decorators.http import require_POST
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse, Http404
from django.shortcuts import get_object_or_404
from .models import Profile

import json

# Create your views here.


@login_required(login_url="loginpage")
def index(request):
    site_user = Profile.objects.all()
    posts = Post.objects.filter(
        user__profile__is_banned=False
    )  # Sadece banlı olmayan kullanıcıların postlarını çekin

    if not request.user.profile.is_approved and not request.user.is_staff:
        message = "Hesabınız admin tarafından onaylanmasını bekleyiniz."
        return render(request, "index.html", {"message": message})

    context = {
        "site_user": site_user,
        "posts": posts,  # Postları context'e ekleyin
    }

    return render(request, "index.html", context)


def create_notification(user, post, is_comment=False):
    # Bildirim oluştur
    Notification.objects.create(user=user, post=post, is_comment=is_comment)


def message_view(request):
    if request.user.is_authenticated:
        messages_received = Message.objects.filter(receiver=request.user)
        messages_sent = Message.objects.filter(sender=request.user)
        all_messages = messages_received | messages_sent
        all_messages = all_messages.order_by("timestamp")
        return render(request, "messages.html", {"all_messages": all_messages})
    else:
        return render(
            request, "login.html"
        )  # Ya da uygun bir yönlendirme yapabilirsiniz


def get_notification_count(request):
    if request.user.is_authenticated:
        unread_notification_count = Notification.objects.filter(
            user=request.user, is_read=False
        ).count()
        return JsonResponse({"count": unread_notification_count})
    else:
        return JsonResponse({"count": 0})


def search_users(request):
    query = request.GET.get("query", "")
    users = User.objects.filter(username__icontains=query)
    user_list = []

    for u in users:
        profile = Profile.objects.get(user=u)
        user_list.append({
            'username': u.username,
            'profileimg': profile.profileimg.url if profile.profileimg else ''
        })

    return JsonResponse(user_list, safe=False)


def get_past_conversations(request):
    user = request.user
    conversations = Message.objects.filter(Q(sender=user) | Q(receiver=user)).values_list('sender', 'receiver').distinct()
    unique_users = set()

    for sender, receiver in conversations:
        if sender != user.id:
            unique_users.add(sender)
        if receiver != user.id:
            unique_users.add(receiver)

    past_users = User.objects.filter(id__in=unique_users)
    user_list = []

    for u in past_users:
        profile = Profile.objects.get(user=u)
        # Okunmamış mesaj sayısını hesapla
        unread_count = Message.objects.filter(sender=u, receiver=user, is_read=False).count()
        
        user_list.append({
            'username': u.username,
            'profileimg': profile.profileimg.url if profile.profileimg else '',
            'unread_count': unread_count  # Okunmamış mesaj sayısını ekle
        })

    return JsonResponse(user_list, safe=False)


def send_message(request):
    if request.method != 'POST':
        return JsonResponse({"status": "error", "message": "Method not allowed"}, status=405)

    sender = request.user
    receiver_username = request.POST.get("receiver")

    if not receiver_username:
        return JsonResponse({"status": "error", "message": "Receiver username not provided"}, status=400)

    try:
        receiver = User.objects.get(username=receiver_username)
    except ObjectDoesNotExist:
        return JsonResponse({"status": "error", "message": "Receiver does not exist"}, status=404)

    message = request.POST.get("message")

    if not message:
        return JsonResponse({"status": "error", "message": "Message content not provided"}, status=400)

    Message.objects.create(sender=sender, receiver=receiver, message=message)
    return JsonResponse({"status": "ok"})

@login_required
def get_messages(request, username=None):
    user = User.objects.get(username=username)
    messages = (
        Message.objects.filter(
            Q(sender=request.user, receiver=user) |
            Q(sender=user, receiver=request.user),
            is_deleted=False
        )
        .values("message", "timestamp", "sender__username")
        .order_by("timestamp")
    )
    return JsonResponse(list(messages), safe=False)

@login_required
def get_unread_messages_count(request):
    count = Message.objects.filter(receiver=request.user, is_read=False).count()
    return JsonResponse({'count': count})

@login_required
def mark_as_read(request, username):
    Message.objects.filter(receiver=request.user, sender__username=username).update(is_read=True)
    return JsonResponse({"status": "ok"})

def delete_messages(request, username=None):
    user = User.objects.get(username=username)
    Message.objects.filter(
        Q(sender=request.user, receiver=user) |
        Q(sender=user, receiver=request.user)
    ).update(is_deleted=True)
    return JsonResponse({"status": "ok"})





def giris(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]

        if username and password:
            user = authenticate(username=username, password=password)

            if user:
                if not user.profile.is_banned:  # Hesap banlı değilse giriş yap
                    login(request, user)
                    return redirect("homepage")
                else:
                    return render(
                        request, "banned.html"
                    )  # Hesap banlı ise banned.html sayfasını göster
            else:
                return redirect("loginpage")

    return render(request, "login.html")


@login_required(login_url="loginpage")
def upload(request):
    if request.method == "POST":
        user = request.user
        image = request.FILES.get("image_upload")
        caption = request.POST["caption"]
        # You don't need to check if caption is valid, it's a string, not a form field
        new_post = Post.objects.create(user=user, image=image, caption=caption)
      
        if new_post:
            return redirect("homepage")
        else:
            # Handle the case where the post couldn't be created
            return HttpResponse("Error creating the post")
    else:
        return render(request, "index.html")


def go_latest_notification(request):
    if request.user.is_authenticated:
        latest_notification = Notification.objects.filter(user=request.user).latest(
            "created_at"
        )
        latest_notification.is_read = True
        latest_notification.save()

        # Bildirim içeriğini oluşturun
        if latest_notification.comment:
            # Eğer bildirim bir yorumla ilgiliyse
            comment_author = latest_notification.comment.author.username
            notification_content = f'{comment_author} kullanıcısı sizin gönderinize "{latest_notification.comment.text}" yorumunu yazdı.'
        elif latest_notification.is_comment:
            # Eğer bildirim bir beğeniyle ilgiliyse
            liker = latest_notification.user.username
            notification_content = f'{liker} kullanıcısı "{latest_notification.post.caption}" adlı kişi gönderinizi beğendi.'
        else:
            # Bildirim gönderi ile ilgiliyse
            notification_content = f'"{latest_notification.post.caption}" adlı gönderiniz hakkında bir bildirim.'

        return JsonResponse(
            {"content": notification_content, "id": latest_notification.id}
        )
    else:
        return JsonResponse({"content": "Unauthorized"}, status=401)


def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    comments = Comment.objects.filter(post=post)

    # Moderatör kontrolü yapılıyor
    is_moderator = Profile.objects.filter(is_moderator=True, user=request.user).exists()

    return render(
        request,
        "post-detail.html",
        {"post": post, "comments": comments, "is_moderator": is_moderator},
    )


@login_required(login_url="loginpage")
@transaction.atomic  # Atomik işlem garantisi için
def like(request, post_id):
    try:
        post = get_object_or_404(Post, id=post_id)
        username = request.user.username

        # Veritabanında bir filtre uygulayarak like'ı buluyoruz
        like_filter = LikePost.objects.filter(
            post_id=post_id, username=username
        ).first()

        # Eğer bu kullanıcı bu post'u daha önce beğenmemişse
        if like_filter is None:
            # Yeni bir LikePost oluşturuyoruz ve beğeni sayısını artırıyoruz
            LikePost.objects.create(post_id=post_id, username=username)
            post.no_of_likes += 1
        else:
            # Mevcut beğeniyi kaldırıyoruz ve beğeni sayısını azaltıyoruz
            like_filter.delete()
            post.no_of_likes -= 1

        # Beğeni sayısını negatif olmamak üzere güncelliyoruz
        if post.no_of_likes < 0:
            post.no_of_likes = 0

        # Post nesnesini güncelliyoruz
        post.save()

        # Başarılı bir şekilde JsonResponse döndürüyoruz
        return JsonResponse({"success": True, "likes": post.no_of_likes})

    except Exception as e:
        # Hata durumunda uygun bir hata yanıtı döndürüyoruz
        return JsonResponse({"success": False, "error_message": str(e)}, status=400)


def mark_notification_as_read(request, notification_id):
    notification = Notification.objects.get(pk=notification_id)

    if not notification.is_read:  # Check if it's not already marked as read
        notification.is_read = True
        notification.save()

    # Calculate and fetch the updated notification count
    updated_notification_count = Notification.objects.filter(
        user=request.user, is_read=False
    ).count()

    return JsonResponse(
        {"status": "Notification marked as read", "count": updated_notification_count}
    )


@login_required(login_url="loginpage")
def profile(request, pk):
    user_object = get_object_or_404(User, username=pk)
    user_profile = get_object_or_404(Profile, user=user_object)
    user_posts = Post.objects.filter(user=user_object)
    user_post_length = len(user_posts)
    form = ApprovalForm()
    if request.user.is_staff:  # Admin kontrolü
        unapproved_users = User.objects.filter(profile__is_approved=False)
    else:
        unapproved_users = None


    context = {
        'user_profile': user_profile,
        'user_posts': user_posts,
        'user_post_length': user_post_length,
        "user_object": user_object,
        "user_profile": user_profile,
        "user_posts": user_posts,
        "user_post_length": user_post_length,
        "form": form,
        "unapproved_users": unapproved_users,
    }

    if request.method == "POST":
        form = ApprovalForm(request.POST)
        if form.is_valid() and form.cleaned_data["approve"]:
            # Kullanıcının hesabını onayla
            user_profile.is_approved = True
            user_profile.save()
            return redirect("profilepage")  # Profil sayfasına geri dön

    return render(request, 'profile.html', context)


@login_required(login_url="loginpage")
def upload_banner(request):
    if request.method == 'POST':
        banner_file = request.FILES.get('banner', None)
        if banner_file:
            try:
                # Kullanıcının kimliğini alabilirsiniz veya başka bir yol kullanabilirsiniz
                # Örneğin, request.user kullanarak
                user_id = request.user.id
                profile = Profile.objects.get(user__id=user_id)
                profile.banner = banner_file
                profile.save()
                banner_url = profile.banner.url
                return JsonResponse({'status': 'success', 'banner_url': banner_url})
            except Profile.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': 'Kullanıcı bulunamadı.'})
    
    return JsonResponse({'status': 'error', 'message': 'Geçersiz istek.'})


def cikis(request):
    logout(request)
    return redirect("homepage")


def register(request):
    context = {}

    if request.method == "POST":
        form = registerForm(request.POST)

        if form.is_valid():
            first_name = form.cleaned_data["first_name"]
            last_name = form.cleaned_data["last_name"]
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            email = form.cleaned_data["email"]

            user = User.objects.create_user(
                first_name=first_name,
                last_name=last_name,
                username=username,
                password=password,
                email=email,
            )
            siteUser = Profile(user=user)
            user = form.save(commit=False)
            siteUser.save()

            return redirect("loginpage")

        else:
            print("form hatası:", form.errors)
            return redirect("registerpage")
    else:
        context["form"] = registerForm()
        return render(request, "register.html", context)


@login_required(login_url="loginpage")
def hesap(request):
    user_profile = Profile.objects.get(user=request.user)

    if request.method == "POST":
        image = request.FILES.get("image")
        if image is None:
            image = user_profile.profileimg

        bio = request.POST.get("bio", "")
        location = request.POST.get("location", "")
        education = request.POST.get("education", "")

        birthdate = request.POST.get("birthdate")
        if birthdate == "":
            birthdate = None

        email = request.POST.get("email", "")

        user_profile.profileimg = image
        user_profile.bio = bio
        user_profile.location = location
        user_profile.education = education
        user_profile.birthdate = birthdate
        user_profile.email = email
        user_profile.save()

        return redirect("settingspage")

    return render(request, "settings.html", {"user_profile": user_profile})


# post kısımları
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    profile = Profile.objects.filter(is_moderator=True, user=request.user).exists()

    if request.user == post.user or profile:
        if request.method == "POST":
            post.delete()
            return redirect("homepage")

        return render(request, "delete_post.html", {"post": post})
    else:
        # Kullanıcı postu silme yetkisine sahip değilse, bir hata mesajı gösterin veya başka bir işlem yapın.
        # Örneğin, 403 Forbidden hatası dönebilirsiniz.
        return HttpResponseForbidden("Bu işlemi yapmaya yetkiniz yok.")


def edit_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if request.method == "POST":
        # Formdan gelen verileri burada işleyin (Post modelindeki alanları güncelleyin)
        image = request.FILES.get("image_upload")
        caption = request.POST["caption"]

        post.image = image  # 'image' alanını güncelle
        post.caption = caption  # 'caption' alanını güncelle
        post.save()

        # Düzenleme tamamlandığında ana sayfaya yönlendirin
        return redirect("homepage")

    return render(request, "index.html", {"post": post})


from .models import Notification


def add_comment_to_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            text = form.cleaned_data["text"]
            author = request.user
            comment = Comment.objects.create(post=post, author=author, text=text)

            # Yorum sahibini belirleyin
            post_owner = post.user

            # Yeni bildirim oluşturun
            notification = Notification.objects.create(
                user=post_owner,
                post=post,
                comment=comment,
            )

            return redirect("post_detail", post_id=post_id)
    else:
        form = CommentForm()

    return render(request, "add_comment_to_post.html", {"form": form})


def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    post_id = comment.post.id
    profile = Profile.objects.filter(is_moderator=True, user=request.user).exists()

    if request.user == comment.author or profile:
        if request.method == "POST":
            comment.delete()
            return redirect("post_detail", post_id=post_id)

        return render(request, "delete_comment.html", {"comment": comment})
    else:
        return HttpResponseForbidden("Bu işlemi yapmaya yetkiniz yok.")


def edit_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    post_id = comment.post.id
    profile = Profile.objects.filter(is_moderator=True, user=request.user).exists()

    if request.user == comment.author or profile:
        if request.method == "POST":
            new_text = request.POST.get("text")
            comment.text = new_text
            comment.save()
            return redirect(
                "post_detail", post_id=comment.post.id
            )  # Yorum düzenleme tamamlandığında post detay sayfasına yönlendirin

        return render(request, "edit_comment.html", {"comment": comment})

    return HttpResponseForbidden("Bu işlemi yapmaya yetkiniz yok.")


# yetkilendirme kısımları


def approve_user(request, user_id):
    user_profile = get_object_or_404(Profile, user_id=user_id)
    user_profile.is_approved = True
    user_profile.save()
    return redirect("admin_dashboard")  # Profil sayfanıza yönlendirme yapın


def unapproved_users(request):
    # Onay bekleyen kullanıcıları sorgulayın
    unapproved_users = Profile.objects.filter(is_approved=False)

    context = {"unapproved_users": unapproved_users}

    return render(request, "unapproved_users.html", context)

def verified_user(request, user_id):
    user_profile = get_object_or_404(Profile, user_id=user_id)
    user_profile.verified = True
    user_profile.save()
    return redirect("admin_dashboard")  # Profil sayfanıza yönlendirme yapın
def unverified(request):
    # Onay bekleyen kullanıcıları sorgulayın
    unverified = Profile.objects.filter(verified=False)

    context = {"unverified": unverified}

    return render(request, "unverified.html", context)

def grant_moderator(request, user_id):
    if request.user.is_superuser:  # Sadece admin yetkilisi bu işlemi yapabilir
        user_profile = get_object_or_404(Profile, user_id=user_id)
        user_profile.is_moderator = True
        user_profile.save()
        return redirect(
            "admin_dashboard"
        )  # Moderatör yetkisi verildikten sonra yönlendirilecek sayfa
    else:
        return HttpResponseForbidden("Bu işlemi yapmaya yetkiniz yok.")


def revoke_moderator(request, user_id):
    if request.user.is_superuser:  # Sadece admin yetkilisi bu işlemi yapabilir
        user_profile = get_object_or_404(Profile, user_id=user_id)
        user_profile.is_moderator = False  # Moderatör yetkisini kaldırın
        user_profile.save()
        return redirect(
            "admin_dashboard"
        )  # Moderatör yetkisi kaldırıldıktan sonra yönlendirilecek sayfa
    else:
        return HttpResponseForbidden("Bu işlemi yapmaya yetkiniz yok.")


@csrf_exempt
def update_profile_image(request):
    if request.method == "POST" and request.FILES.get("image"):
        user_profile = request.user.profile
        user_profile.profileimg = request.FILES["image"]
        user_profile.save()
        return JsonResponse({"message": "Profil resmi güncellendi"}, status=200)
    return JsonResponse({"error": "Geçersiz istek"}, status=400)


def create_report(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if request.method == "POST":
        user = request.user  # Kullanıcıyı alın
        title = request.POST.get("title")  # 'resolved' değerini alın
        description = request.POST.get("description")  # 'description' değerini alın

        # Report objesini oluşturun
        report = Report.objects.create(
            post=post, user=user, title=title, description=description
        )

        return redirect("homepage")

    return render(request, "create_report", {"post": post})


def admin_dashboard(request):
    if request.user.is_superuser:
        users = User.objects.all()
        reports = Report.objects.all()
        unapproved_users = Profile.objects.filter(is_approved=False)
        unverified = Profile.objects.filter(verified=False)
        return render(
            request,
            "admin_dashboard.html",
            {"users": users, "reports": reports, "unapproved_users": unapproved_users, "unverified": unverified},
        )
    else:
        return HttpResponseForbidden("Bu sayfaya erişim yetkiniz yok.")


def ban_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.profile.is_banned = True
    user.profile.save()

    # Eğer oturum açıksa, kullanıcıyı oturumdan at
    if request.user.is_authenticated and request.user == user:
        logout(request)

    return redirect("admin_dashboard")


def unban_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.profile.is_banned = False
    user.profile.save()

    if request.user.is_authenticated and request.user == user:
        logout(request)
    return redirect("admin_dashboard")


def messages_view(request):
    current_user = request.user
    previous_chats = User.objects.filter(
        Q(sent_messages__receiver=current_user)
        | Q(received_messages__sender=current_user)
    ).distinct()

    # Arama kutusu için
    search_query = request.GET.get("q")
    if search_query:
        users = User.objects.filter(username__icontains=search_query).exclude(
            username=current_user.username
        )
    else:
        users = None

    # İlk önce konuşulan kişi veya aranan kişi için
    receiver_id = request.GET.get("chat_with")
    if receiver_id:
        receiver = User.objects.get(id=receiver_id)
        messages = Message.objects.filter(
            (Q(sender=current_user) & Q(receiver=receiver))
            | (Q(sender=receiver) & Q(receiver=current_user))
        ).order_by("timestamp")
    else:
        receiver = None
        messages = None

    context = {
        "previous_chats": previous_chats,
        "search_results": users,
        "messages": messages,
        "receiver": receiver,
    }

    return render(request, "messages.html", context)


def update_email_password(request):
    if request.method == "POST":
        user = request.user
        email = request.POST.get("email")
        password = request.POST.get("password")

        # E-posta güncelleme
        user.email = email
        user.save()

        # Şifre güncelleme
        if password:
            user.set_password(password)
            user.save()
            update_session_auth_hash(request, user)  # Oturumu güncelle

        return redirect("settingspage")

    return HttpResponseBadRequest("Geçersiz istek")
