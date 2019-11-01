from allauth.account.models import EmailAddress

from custom_auth.models import User


def _set_password(user):
    user.set_password(user.password)
    user.save()


def confirm_emails():
    emails = [el.email for el in EmailAddress.objects.all()]
    [EmailAddress(user=el, email=el.email, verified=True, primary=True).save() for el in User.objects.all() if
     el.email not in emails]


def confirm_passwords():
    [_set_password(user) for user in User.objects.all() if user.password[:5] != 'pbkdf']
