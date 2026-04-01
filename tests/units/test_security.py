from security.security import encrypt, decrypt

class TestSecurity:
    def test_encrypt_and_decrypt(self):
        """Проверяем корректность шифрования и дешифрования последующего"""
        original_password = "45368102abBA/"
        encrypted_password = encrypt(original_password)
        decrypted_password = decrypt(encrypted_password)

        assert original_password == decrypted_password

    def test_different_shifr_after_encryption(self):
        """Проверка разных шифротекстов после повторного шифрования одно и того же пароля"""
        original_password = "74298384mavaMilaRamy"

        encrypted_password_first_time = encrypt(original_password)
        encrypted_password_second_time = encrypt(original_password)

        assert encrypted_password_first_time != encrypted_password_second_time