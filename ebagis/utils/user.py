def deactivate(user):
    user.is_active = False
    user.set_unusable_password()
    user.email = ''
    user.first_name = ''
    user.last_name = ''
    user.save()
    user.token.delete()
