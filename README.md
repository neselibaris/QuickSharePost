# QuickSharePost
### Tarafımdan Şunlar Eklendi;
- Hesap Ayarları sayfası düzenlendi.
- Bildirim eklendi.
- Ana sayfa görünümü değiştirildi.
- Dark mode eklendi.
Kullanıcıların kolaylıkla tweet paylaşıp düzenleme ve silme işlemlerini yapabilirler.

Yorum yapma düzenleme ve silme işlemi

Raporlama sistemi mevcuttur başlık ve açıklama şeklinde raporlama yapabilirler.

4 kısımdan oluşan yetkilendirme sistemi vardır
 
 -Kullanıcı ilk kayıt olduğunda hesabı onaylanmadığı için site de herhangi bir işlem yapamaz adminin onaylamasını beklemek zorundadır.
 
 -Hesabı onaylı kullanıcı site de tümüyle etkileşime geçebilir herhangi bir kısıtlaması yoktur.
 
 -Moderator normal kullanıcıdan farklı olarak tüm postları ve yorumları düzenleyip silme yetkisine sahiptir.
 
 -Admin, moderatorün yetkilerinin dışında yeni kayıt olmış hesapları onaylama yetlisine sahiptir.

Admin dashboard sayfası vardır. Bu sayfada tüm kullanıcılar listelenir ve admin sayfadan yetki verip banlama yapabilr aynı zamanda raporlamalarda sayfada gözükür.


Test etmek veya denemek için django ve python bilgisayarınız da yüklü olmalıdır, repoyu klonladıktan sorna terminale sırasıyla şu komutları yazınız:

py manage.py makemigrations

py manage.py migrate

py manage.py runserver

Örnekler:

Dashboard
![dashboard](https://github.com/neselibaris/QuickSharePost/assets/114444125/7b9033f3-a4bb-4ed2-aea8-e97206978037)

Post Paylaşım

![post-paylaşım](https://github.com/neselibaris/QuickSharePost/assets/114444125/57783c49-2831-4173-a998-83fc3cc375cd)


Profil sayfası
![profil-sayfası](https://github.com/neselibaris/QuickSharePost/assets/114444125/c43a60bf-1f51-4748-8ca9-ae57410cd40e)


Hesap ayarları
![hesap-ayarları](https://github.com/neselibaris/QuickSharePost/assets/114444125/6faf287d-174b-4b03-b15d-ec897db46d88)

Admin dashboard
![hesap-onaylama](https://github.com/neselibaris/QuickSharePost/assets/114444125/d76ed62d-cf09-4442-8f3e-92d90eeaf595)

Post-detail ve Yorumlar
![post_detail-ve-yorumlar](https://github.com/neselibaris/QuickSharePost/assets/114444125/409c5b4d-aa98-4668-9105-d924bce4877d)


