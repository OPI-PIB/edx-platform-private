"""
Utility functions for validating forms
"""
import re
from importlib import import_module

from django import forms
from django.conf import settings
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.hashers import UNUSABLE_PASSWORD_PREFIX
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import ValidationError
from django.forms import widgets
from django.template import loader
from django.utils.http import int_to_base36
from django.utils.translation import ugettext_lazy as _
from django.core.validators import RegexValidator, slug_re

from openedx.core.djangoapps.site_configuration import helpers as configuration_helpers
from openedx.core.djangoapps.user_api import accounts as accounts_settings
from student.models import CourseEnrollmentAllowed
from util.password_policy_validators import password_max_length, password_min_length, validate_password


class PasswordResetFormNoActive(PasswordResetForm):
    error_messages = {
        'unknown': _("That e-mail address doesn't have an associated "
                     "user account. Are you sure you've registered?"),
        'unusable': _("The user account associated with this e-mail "
                      "address cannot reset the password."),
    }

    def clean_email(self):
        """
        This is a literal copy from Django 1.4.5's django.contrib.auth.forms.PasswordResetForm
        Except removing the requirement of active users
        Validates that a user exists with the given email address.
        """
        email = self.cleaned_data["email"]
        #The line below contains the only change, removing is_active=True
        self.users_cache = User.objects.filter(email__iexact=email)
        if not len(self.users_cache):
            raise forms.ValidationError(self.error_messages['unknown'])
        if any((user.password.startswith(UNUSABLE_PASSWORD_PREFIX))
               for user in self.users_cache):
            raise forms.ValidationError(self.error_messages['unusable'])
        return email

    def save(
            self,
            subject_template_name='emails/password_reset_subject.txt',
            email_template_name='registration/password_reset_email.html',
            use_https=False,
            token_generator=default_token_generator,
            from_email=configuration_helpers.get_value('email_from_address', settings.DEFAULT_FROM_EMAIL),
            request=None
    ):
        """
        Generates a one-use only link for resetting password and sends to the
        user.
        """
        # This import is here because we are copying and modifying the .save from Django 1.4.5's
        # django.contrib.auth.forms.PasswordResetForm directly, which has this import in this place.
        from django.core.mail import send_mail
        for user in self.users_cache:
            site_name = configuration_helpers.get_value(
                'SITE_NAME',
                settings.SITE_NAME
            )
            context = {
                'email': user.email,
                'site_name': site_name,
                'uid': int_to_base36(user.id),
                'user': user,
                'token': token_generator.make_token(user),
                'protocol': 'https' if use_https else 'http',
                'platform_name': configuration_helpers.get_value('platform_name', settings.PLATFORM_NAME),
                'domain': configuration_helpers.get_value('LMS_BASE', settings.LMS_BASE)
            }
            subject = loader.render_to_string(subject_template_name, context)
            # Email subject *must not* contain newlines
            subject = subject.replace('\n', '')
            email = loader.render_to_string(email_template_name, context)
            send_mail(subject, email, from_email, [user.email], html_message=email)


class TrueCheckbox(widgets.CheckboxInput):
    """
    A checkbox widget that only accepts "true" (case-insensitive) as true.
    """
    def value_from_datadict(self, data, files, name):
        value = data.get(name, '')
        return value.lower() == 'true'


class TrueField(forms.BooleanField):
    """
    A boolean field that only accepts "true" (case-insensitive) as true
    """
    widget = TrueCheckbox


def validate_username(username):
    """
    Verifies a username is valid, raises a ValidationError otherwise.
    Args:
        username (unicode): The username to validate.

    This function is configurable with `ENABLE_UNICODE_USERNAME` feature.
    """

    username_re = slug_re
    flags = None
    message = accounts_settings.USERNAME_INVALID_CHARS_ASCII

    if settings.FEATURES.get("ENABLE_UNICODE_USERNAME"):
        username_re = r"^{regex}$".format(regex=settings.USERNAME_REGEX_PARTIAL)
        flags = re.UNICODE
        message = accounts_settings.USERNAME_INVALID_CHARS_UNICODE

    validator = RegexValidator(
        regex=username_re,
        flags=flags,
        message=message,
        code='invalid',
    )

    validator(username)


def contains_html(value):
    """
    Validator method to check whether name contains html tags
    """
    regex = re.compile('(<|>)', re.UNICODE)
    return bool(regex.search(value))


def validate_name(name):
    """
    Verifies a Full_Name is valid, raises a ValidationError otherwise.
    Args:
        name (unicode): The name to validate.
    """
    if contains_html(name):
        raise forms.ValidationError(_('Full Name cannot contain the following characters: < >'))

def name_editable(existing_user_profile):
    """
    Check if a Full_Name is editable, raises a ValidationError otherwise.
    Args:
        existing_user_profile: UserProfile model
    """
    if existing_user_profile.name_change_count > 0:
        raise forms.ValidationError(_('You can no longer change full name by yourself. If you think such a change is necessary, please contact us by sending an e-mail to {email_help}').format(
            email_help=settings.TECH_SUPPORT_EMAIL
        ))

class UsernameField(forms.CharField):
    """
    A CharField that validates usernames based on the `ENABLE_UNICODE_USERNAME` feature.
    """

    default_validators = [validate_username]

    def __init__(self, *args, **kwargs):
        super(UsernameField, self).__init__(
            min_length=accounts_settings.USERNAME_MIN_LENGTH,
            max_length=accounts_settings.USERNAME_MAX_LENGTH,
            error_messages={
                "required": accounts_settings.USERNAME_BAD_LENGTH_MSG,
                "min_length": accounts_settings.USERNAME_BAD_LENGTH_MSG,
                "max_length": accounts_settings.USERNAME_BAD_LENGTH_MSG,
            }
        )

    def clean(self, value):
        """
        Strips the spaces from the username.

        Similar to what `django.forms.SlugField` does.
        """

        value = self.to_python(value).strip()
        return super(UsernameField, self).clean(value)


class AccountCreationForm(forms.Form):
    """
    A form to for account creation data. It is currently only used for
    validation, not rendering.
    """

    _EMAIL_INVALID_MSG = _("A properly formatted e-mail is required")
    _PASSWORD_INVALID_MSG = _("A valid password is required")
    _NAME_TOO_SHORT_MSG = _("Your legal name must be a minimum of two characters long")

    # TODO: Resolve repetition

    username = UsernameField()

    email = forms.EmailField(
        max_length=accounts_settings.EMAIL_MAX_LENGTH,
        min_length=accounts_settings.EMAIL_MIN_LENGTH,
        error_messages={
            "required": _EMAIL_INVALID_MSG,
            "invalid": _EMAIL_INVALID_MSG,
            "max_length": _("Email cannot be more than %(limit_value)s characters long"),
        }
    )
    password = forms.CharField(
        min_length=password_min_length(),
        max_length=password_max_length(),
        error_messages={
            "required": _PASSWORD_INVALID_MSG,
            "min_length": _PASSWORD_INVALID_MSG,
            "max_length": _PASSWORD_INVALID_MSG,
        }
    )
    confirm_password = forms.CharField(
        min_length=password_min_length(),
        max_length=password_max_length(),
        error_messages={
            "required": _PASSWORD_INVALID_MSG,
            "min_length": _PASSWORD_INVALID_MSG,
            "max_length": _PASSWORD_INVALID_MSG,
        }
    )
    name = forms.CharField(
        min_length=accounts_settings.NAME_MIN_LENGTH,
        error_messages={
            "required": _NAME_TOO_SHORT_MSG,
            "min_length": _NAME_TOO_SHORT_MSG,
        },
        validators=[validate_name]
    )

    def __init__(
            self,
            data=None,
            extra_fields=None,
            extended_profile_fields=None,
            enforce_password_policy=False,
            tos_required=True
    ):
        super(AccountCreationForm, self).__init__(data)

        extra_fields = extra_fields or {}
        self.extended_profile_fields = extended_profile_fields or {}
        self.enforce_password_policy = enforce_password_policy
        if tos_required:
            self.fields["terms_of_service"] = TrueField(
                error_messages={"required": _("You must accept the terms of service.")}
            )

        # TODO: These messages don't say anything about minimum length
        error_message_dict = {
            "level_of_education": _("A level of education is required"),
            "gender": _("Your gender is required"),
            "year_of_birth": _("Your year of birth is required"),
            "mailing_address": _("Your mailing address is required"),
            "goals": _("A description of your goals is required"),
            "city": _("A city is required"),
            "country": _("A country is required")
        }
        for field_name, field_value in extra_fields.items():
            if field_name not in self.fields:
                if field_name == "honor_code":
                    if field_value == "required":
                        self.fields[field_name] = TrueField(
                            error_messages={
                                "required": _("To enroll, you must follow the honor code.")
                            }
                        )
                else:
                    required = field_value == "required"
                    min_length = 1 if field_name in ("gender", "level_of_education") else 2
                    error_message = error_message_dict.get(
                        field_name,
                        _("You are missing one or more required fields")
                    )
                    self.fields[field_name] = forms.CharField(
                        required=required,
                        min_length=min_length,
                        error_messages={
                            "required": error_message,
                            "min_length": error_message,
                        }
                    )

        for field in self.extended_profile_fields:
            if field not in self.fields:
                self.fields[field] = forms.CharField(required=False)

    def clean_password(self):
        """Enforce password policies (if applicable)"""
        password = self.cleaned_data["password"]
        if self.enforce_password_policy:
            validate_password(password, username=self.cleaned_data.get('username'))
        return password

    def clean_confirm_password(self):
        """Enforce password policies (if applicable)"""
        confirm_password = self.cleaned_data["confirm_password"]

        if (
                "password" in self.cleaned_data and
                self.cleaned_data["password"] != confirm_password
        ):
            raise ValidationError(_("Passwords Don't Match"))

        return confirm_password

    def clean_email(self):
        """ Enforce email restrictions (if applicable) """
        email = self.cleaned_data["email"]
        if settings.REGISTRATION_EMAIL_PATTERNS_ALLOWED is not None:
            # This Open edX instance has restrictions on what email addresses are allowed.
            allowed_patterns = settings.REGISTRATION_EMAIL_PATTERNS_ALLOWED
            # We append a '$' to the regexs to prevent the common mistake of using a
            # pattern like '.*@edx\\.org' which would match 'bob@edx.org.badguy.com'
            if not any(re.match(pattern + "$", email) for pattern in allowed_patterns):
                # This email is not on the whitelist of allowed emails. Check if
                # they may have been manually invited by an instructor and if not,
                # reject the registration.
                if not CourseEnrollmentAllowed.objects.filter(email=email).exists():
                    raise ValidationError(_("Unauthorized email address."))
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError(
                _(
                    "It looks like {email} belongs to an existing account. Try again with a different email address."
                ).format(email=email)
            )
        return email

    def clean_year_of_birth(self):
        """
        Parse year_of_birth to an integer, but just use None instead of raising
        an error if it is malformed
        """
        try:
            year_str = self.cleaned_data["year_of_birth"]
            return int(year_str) if year_str is not None else None
        except ValueError:
            return None

    @property
    def cleaned_extended_profile(self):
        """
        Return a dictionary containing the extended_profile_fields and values
        """
        return {
            key: value
            for key, value in self.cleaned_data.items()
            if key in self.extended_profile_fields and value is not None
        }


def get_registration_extension_form(*args, **kwargs):
    """
    Convenience function for getting the custom form set in settings.REGISTRATION_EXTENSION_FORM.

    An example form app for this can be found at http://github.com/open-craft/custom-form-app
    """
    if not settings.FEATURES.get("ENABLE_COMBINED_LOGIN_REGISTRATION"):
        return None
    if not getattr(settings, 'REGISTRATION_EXTENSION_FORM', None):
        return None
    module, klass = settings.REGISTRATION_EXTENSION_FORM.rsplit('.', 1)
    module = import_module(module)
    return getattr(module, klass)(*args, **kwargs)
