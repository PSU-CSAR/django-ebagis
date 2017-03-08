import binascii
import os

from datetime import timedelta

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _


# Note that this code was pulled directly from the DRF authentication
# module as I needed to create a custom subclass of Token, but needed to
# have the primary key be on the user field, and not on the key field.


# get the expire hours setting, default of 1 week
EXPIRE_HOURS = getattr(settings, 'REST_FRAMEWORK_TOKEN_EXPIRE_HOURS',  168)

# Prior to Django 1.5, the AUTH_USER_MODEL setting does not exist.
# Note that we don't perform this code in the compat module due to
# bug report #1297
# See: https://github.com/tomchristie/django-rest-framework/issues/1297
AUTH_USER_MODEL = getattr(settings, 'AUTH_USER_MODEL', 'auth.User')


@python_2_unicode_compatible
class ExpiringToken(models.Model):
    """
    Based on the default authorization token model. However, cannot
    inherit as primary key is changed.
    """
    key = models.CharField(_("Key"), max_length=40, unique=True)
    user = models.OneToOneField(
        AUTH_USER_MODEL,
        related_name='token',
        on_delete=models.CASCADE, verbose_name=_("User"),
        primary_key=True
    )
    created = models.DateTimeField(_("Created"), auto_now_add=True)

    class Meta:
        verbose_name = _("Token")
        verbose_name_plural = _("Tokens")

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_key()
        return super(ExpiringToken, self).save(*args, **kwargs)

    def update(self):
        self.created = timezone.now()
        while True:
            self.key = self.generate_key()
            try:
                self.save()
            except:
                pass
            else:
                break

    def generate_key(self):
        return binascii.hexlify(os.urandom(20)).decode()

    def __str__(self):
        return self.key

    @property
    def is_valid(self):
        if self.created >= timezone.now() - timedelta(hours=EXPIRE_HOURS):
            return True
        return False
