# from django.test import TestCase
# from django.contrib.auth import get_user_model
# from main.forms import CustomLoginForm

# User = get_user_model()
# class LoginFormTests(TestCase):
#     def setUp(self):
#         # Tạo người dùng để kiểm thử
#         self.user = User.objects.create_user(username="hoangnnse171944", password="123@", is_locked=False)
#         self.locked_user = User.objects.create_user(username="lockeduser", password="123@", is_locked=True)

#     def test_login_valid_user(self):
#         # Trường hợp đăng nhập với thông tin hợp lệ
#         form_data = {'username': 'hoangnnse171944', 'password': '123@'}
#         form = CustomLoginForm(data=form_data)
#         self.assertTrue(form.is_valid())

#     def test_login_invalid_username(self):
#         # Trường hợp tên đăng nhập không tồn tại
#         form_data = {'username': 'invaliduser', 'password': '123@'}
#         form = CustomLoginForm(data=form_data)
#         self.assertFalse(form.is_valid())
#         self.assertIn("Username does not exist.", form.errors['__all__'])

#     def test_login_incorrect_password(self):
#         # Trường hợp mật khẩu không chính xác
#         form_data = {'username': 'hoangnnse171944', 'password': 'wrongpassword'}
#         form = CustomLoginForm(data=form_data)
#         self.assertFalse(form.is_valid())
#         self.assertIn("Password is incorrect.", form.errors['__all__'])

#     def test_login_locked_user(self):
#         # Trường hợp tài khoản bị khóa
#         form_data = {'username': 'lockeduser', 'password': '123@'}
#         form = CustomLoginForm(data=form_data)
#         self.assertFalse(form.is_valid())
#         self.assertIn("Your account has been locked. Please contact the administrator..", form.errors['__all__'])

