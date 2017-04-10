from django.core.exceptions import ObjectDoesNotExist


def deactivate(user):
    try:
        user.token.delete()
    except ObjectDoesNotExist:
        pass
    user.is_active = False
    user.set_unusable_password()
    user.email = ''
    user.first_name = ''
    user.last_name = ''
    user.save()
