from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import update_session_auth_hash
from .form import *
from .models import *
from .models import Comment
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import *


# Create your views here.

@login_required(login_url='loginpage')
 
def index(request):
    site_user = Profile.objects.all()
    posts = Post.objects.filter(user__profile__is_banned=False)  # Sadece banlı olmayan kullanıcıların postlarını çekin

    if not request.user.profile.is_approved and not request.user.is_staff:
        message = "Hesabınız admin tarafından onaylanmasını bekleyiniz."
        return render(request, 'index.html', {'message': message})

    context = {
        'site_user': site_user,
        'posts': posts,  # Postları context'e ekleyin
    }

    return render(request, 'index.html', context)

def giris(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        if username and password:
            user = authenticate(username=username, password=password)

            if user:
                if not user.profile.is_banned:  # Hesap banlı değilse giriş yap
                    login(request, user)
                    return redirect('homepage')
                else:
                    return render(request, 'banned.html')  # Hesap banlı ise banned.html sayfasını göster
            else:
                return redirect('loginpage')

    return render(request, 'login.html')

@login_required(login_url='loginpage')
def upload(request):

    if request.method == 'POST':

        user = request.user
        image = request.FILES.get('image_upload')
        caption = request.POST['caption']

    # You don't need to check if caption is valid, it's a string, not a form field
        new_post = Post.objects.create(user=user, image=image, caption=caption)

        if new_post:
            return redirect('homepage')
        else:
            # Handle the case where the post couldn't be created
            return HttpResponse('Error creating the post')
    else:
        return render(request, 'index.html')

def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    comments = Comment.objects.filter(post=post)
    
    # Moderatör kontrolü yapılıyor
    is_moderator = Profile.objects.filter(is_moderator=True, user=request.user).exists()

    return render(request, 'post-detail.html', {'post': post, 'comments': comments, 'is_moderator': is_moderator})

@login_required(login_url='loginpage')

def like(request):
    username = request.user.username
    post_id = request.GET.get('post_id')

    post = Post.objects.get(id=post_id)
    like_filter = LikePost.objects.filter(
        post_id=post_id, username=username).first()

    if like_filter is None:
        new_like = LikePost.objects.create(post_id=post_id, username=username)
        new_like.save()
        post.no_of_likes = post.no_of_likes + 1
        post.save()
        return redirect('homepage')
    else:
        like_filter.delete()
        post.no_of_likes = post.no_of_likes - 1
        post.save()
        return redirect('homepage')

@login_required(login_url='loginpage')
def profile(request, pk):
    user_object = get_object_or_404(User, username=pk)
    user_profile = get_object_or_404(Profile, user=user_object)
    user_posts = Post.objects.filter(user=user_object)
    user_post_length = len(user_posts)

    if request.method == 'POST':
        form = ApprovalForm(request.POST)
        if form.is_valid() and form.cleaned_data['approve']:
            # Kullanıcının hesabını onayla
            user_profile.is_approved = True
            user_profile.save()
            return redirect('profilepage')  # Profil sayfasına geri dön

    form = ApprovalForm()
    if request.user.is_staff:  # Admin kontrolü
        unapproved_users = User.objects.filter(profile__is_approved=False)
    else:
        unapproved_users = None

    context = {
        'user_object': user_object,
        'user_profile': user_profile,
        'user_posts': user_posts,
        'user_post_length': user_post_length,
        'form': form,
        'unapproved_users': unapproved_users,
    }

    return render(request, 'profile.html', context)

def cikis(request):

    logout(request)
    return redirect('homepage')

def register(request):

    context = {}

    if request.method == 'POST':

        form = registerForm(request.POST)

        if form.is_valid():

            first_name = form.cleaned_data["first_name"]
            last_name = form.cleaned_data["last_name"]
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            email = form.cleaned_data["email"]

            user = User.objects.create_user(
                first_name=first_name, last_name=last_name, username=username, password=password, email=email)
            siteUser = Profile(user=user)
            user = form.save(commit=False)
            siteUser.save()

            return redirect('loginpage')

        else:
            print("form hatası:", form.errors)
            return redirect('registerpage')
    else:
        context['form'] = registerForm()
        return render(request, 'register.html', context)

@login_required(login_url='loginpage')
def hesap(request):

    user_profile = Profile.objects.get(user=request.user)

    if request.method == 'POST':

        image = request.FILES.get('image')
        if image is None:
            image = user_profile.profileimg

        bio = request.POST.get('bio', '')
        location = request.POST.get('location', '')
        education = request.POST.get('education', '')

        birthdate = request.POST.get('birthdate')
        if birthdate == '':
            birthdate = None

        email = request.POST.get('email', '')

        user_profile.profileimg = image
        user_profile.bio = bio
        user_profile.location = location
        user_profile.education = education
        user_profile.birthdate = birthdate
        user_profile.email = email
        user_profile.save()

        return redirect('settingspage')

    return render(request, 'settings.html', {'user_profile': user_profile})


#post kısımları
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    profile = Profile.objects.filter(is_moderator=True, user=request.user).exists()

    if request.user == post.user or profile:
        if request.method == 'POST':
            post.delete()
            return redirect('homepage')

        return render(request, 'delete_post.html', {'post': post})
    else:
        # Kullanıcı postu silme yetkisine sahip değilse, bir hata mesajı gösterin veya başka bir işlem yapın.
        # Örneğin, 403 Forbidden hatası dönebilirsiniz.
        return HttpResponseForbidden("Bu işlemi yapmaya yetkiniz yok.")

def edit_post(request, post_id):

    post = get_object_or_404(Post, id=post_id)

    if request.method == 'POST':
        # Formdan gelen verileri burada işleyin (Post modelindeki alanları güncelleyin)
        image = request.FILES.get('image_upload')
        caption = request.POST['caption']

        post.image = image  # 'image' alanını güncelle
        post.caption = caption  # 'caption' alanını güncelle
        post.save()

        # Düzenleme tamamlandığında ana sayfaya yönlendirin
        return redirect('homepage')

    return render(request, 'index.html', {'post': post})

def add_comment_to_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            text = form.cleaned_data['text']
            author = request.user
            comment = Comment.objects.create(post=post, author=author, text=text)
            return redirect('post_detail', post_id=post_id)
    else:
        form = CommentForm()
    
    return render(request, 'add_comment_to_post.html', {'form': form})
        
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    post_id = comment.post.id
    profile = Profile.objects.filter(is_moderator=True, user=request.user).exists()

    if request.user == comment.author or profile :
        if request.method == 'POST':
            comment.delete()
            return redirect('post_detail',post_id=post_id)

        return render(request, 'delete_comment.html', {'comment': comment} )
    else:
        return HttpResponseForbidden("Bu işlemi yapmaya yetkiniz yok.")

def edit_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    post_id = comment.post.id
    profile = Profile.objects.filter(is_moderator=True, user=request.user).exists()

    if request.user == comment.author or  profile :
        if request.method == 'POST':
            new_text = request.POST.get('text')
            comment.text = new_text
            comment.save()
            return redirect('post_detail', post_id=comment.post.id)  # Yorum düzenleme tamamlandığında post detay sayfasına yönlendirin

        return render(request, 'edit_comment.html', {'comment': comment})

    return HttpResponseForbidden("Bu işlemi yapmaya yetkiniz yok.")



#yetkilendirme kısımları   

def approve_user(request, user_id):
    user_profile = get_object_or_404(Profile, user_id=user_id)
    user_profile.is_approved = True
    user_profile.save()
    return redirect('admin_dashboard')  # Profil sayfanıza yönlendirme yapın

def unapproved_users(request):
    # Onay bekleyen kullanıcıları sorgulayın
    unapproved_users = Profile.objects.filter(is_approved=False)

    context = {
        'unapproved_users': unapproved_users
    }

    return render(request, 'unapproved_users.html', context)

def grant_moderator(request, user_id):
    if request.user.is_superuser:  # Sadece admin yetkilisi bu işlemi yapabilir
        user_profile = get_object_or_404(Profile, user_id=user_id)
        user_profile.is_moderator = True
        user_profile.save()
        return redirect('admin_dashboard')  # Moderatör yetkisi verildikten sonra yönlendirilecek sayfa
    else:
        return HttpResponseForbidden("Bu işlemi yapmaya yetkiniz yok.")

def revoke_moderator(request, user_id):
    if request.user.is_superuser:  # Sadece admin yetkilisi bu işlemi yapabilir
        user_profile = get_object_or_404(Profile, user_id=user_id)
        user_profile.is_moderator = False  # Moderatör yetkisini kaldırın
        user_profile.save()
        return redirect('admin_dashboard')  # Moderatör yetkisi kaldırıldıktan sonra yönlendirilecek sayfa
    else:
        return HttpResponseForbidden("Bu işlemi yapmaya yetkiniz yok.")

def create_report(request, post_id):

    post = get_object_or_404(Post, id=post_id)
    
    if request.method == 'POST':
        user = request.user  # Kullanıcıyı alın
        title = request.POST.get('title')  # 'resolved' değerini alın
        description = request.POST.get('description')  # 'description' değerini alın
        
        # Report objesini oluşturun
        report = Report.objects.create(
            post=post,
            user=user,
            title=title,
            description=description
        )
        
        return redirect('homepage')
    
    
    return render(request, 'create_report', {'post': post})

def admin_dashboard(request):
    if request.user.is_superuser:  
        users = User.objects.all()
        reports = Report.objects.all()
        unapproved_users = Profile.objects.filter(is_approved=False)
        return render(request, 'admin_dashboard.html', {'users': users, 'reports': reports, 'unapproved_users': unapproved_users})
    else:
        return HttpResponseForbidden("Bu sayfaya erişim yetkiniz yok.")



def ban_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.profile.is_banned = True
    user.profile.save()

    # Eğer oturum açıksa, kullanıcıyı oturumdan at
    if request.user.is_authenticated and request.user == user:
        logout(request)

    return redirect('admin_dashboard')

def unban_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.profile.is_banned = False
    user.profile.save()

    if request.user.is_authenticated and request.user == user:
        logout(request)
    return redirect('admin_dashboard')

def update_email_password(request):
    if request.method == 'POST':
        user = request.user
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        # E-posta güncelleme
        user.email = email
        user.save()

        # Şifre güncelleme
        if password:
            user.set_password(password)
            user.save()
            update_session_auth_hash(request, user)  # Oturumu güncelle

        return redirect('settingspage')

    return HttpResponseBadRequest("Geçersiz istek")