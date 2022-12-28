from django.contrib.auth.base_user import BaseUserManager


class UserManager(BaseUserManager):
    SUPERUSER = "superuser"
    STAFF = "staff"

    def _is_valid_role(self, role):
        roles = [self.SUPERUSER, self.STAFF]
        return role is None or role.lower() in roles

    def _create_user(self, email, password=None, **extra_fields):
        """
        Creates and saves a User with the given email and password.
        """
        if not email:
            raise ValueError("Users may have an email set.")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, role=None, **extra_fields):
        if role is not None:
            role = role.lower()
            if not self._is_valid_role(role):
                raise ValueError(f'Role "{role}" is not valid.')
            extra_fields.setdefault(f"is_{role}", True)
            if extra_fields.get(f"is_{role}") is not True:
                raise ValueError(f"{role.capitalize()} must have is_{role}=True.")
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        return self.create_user(email, password, role=self.SUPERUSER, **extra_fields)
