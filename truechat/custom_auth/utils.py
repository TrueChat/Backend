from custom_auth.models import User
from allauth.account.models import EmailAddress


def confirm_emails():
    emails = [el.email for el in EmailAddress.objects.all()]
    [EmailAddress(user=el, email=el.email, verified=True, primary=True) for el in User.objects.all() if el.email not in emails]
