from django.contrib.auth.models import BaseUserManager
              
                
class UserAccountManager(BaseUserManager):
    def create_user(self, email, name, password=None):
        """Creates and saves a User with the given email, name and password."""
        if not email:
            raise ValueError('Users must have an email address')
                        
        email=self.normalize_email(email)
        email = email.lower()

        user = self.model(
            email=email,
            name=name
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_admin(self, email, name, password=None):
        """
        Creates and saves a superuser with the given email, name and password.
        """
        user = self.create_user(email, name, password)
        user.is_admin = True
        user.is_staff = True
        user.save(using=self._db)
        return user
  
    def create_superuser(self, email, name, password=None):
        """
        Creates and saves a superuser with the given email, name and password.
        """
        user = self.create_user(email, name, password)
        user.is_staff = True
        user.is_admin = True
        user.is_superuser = True
        user.save(using=self._db)
        return user
