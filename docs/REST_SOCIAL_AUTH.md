# Django REST Social Auth
OAuth signin with django rest framework.
visit [rest-social-auth](https://github.com/st4lk/django-rest-social-auth)

This library will provide social auth logic for us! for more detail please see [rest-social-auth](https://github.com/st4lk/django-rest-social-auth)


## Extra Features
We provide some extra features that may useful

### Auto Create a User Profile
Usually, A user profile will create after register success. and thanks to `rest-social-auth` they've already provided 
get extra data from social provider (i.e. get a User Google's first name, profile picture)

#### How REST Social Auth Get Extra Data

1. authentication success 
2. create UserSocialAuth model 
3. get extra_data from social provider 
4. update UserSocialAuth.extra_data

So, we can create a user profile after step 4 with Django's `signals`

#### Enable Feature
We can simply enable this feature by set `SOCIAL_AUTH_AUTO_CREATE_PROFILE = True` in `settings.py`

#### What's the feature do
We'll create a user Profile model in receiver signal function.
At the moment we provided only Google OAuth2. Please add more logic for other social

```python
@receiver(post_save, sender=UserSocialAuth, dispatch_uid="create_profile_for_google_auth")
def create_profile_for_google_auth(sender, instance, created, **kwargs):
    # for google provider, if extra_data has "access_token" it does mean that request extra_data has been called.
    if (
        not instance.user.get_profile()
        and instance.provider == "google-oauth2"
        and getattr(settings, "SOCIAL_AUTH_AUTO_CREATE_PROFILE", False)
        and instance.extra_data.get("access_token")
    ):
        extra_data = instance.extra_data
        profile, _ = Profile.objects.create(
            user=instance.user,
            first_name=extra_data.get("given_name", "Unknown"),
            last_name=extra_data.get("family_name", "Unknown"),
        )
```
***see full code in user_manager/signals.py***

#### Save Social Profile Picture
If there has a profile picture in Profile model we can handle them here as well!
example for the Google OAuth2
```python
@receiver(post_save, sender=UserSocialAuth, dispatch_uid="create_profile_for_google_auth")
def create_profile_for_google_auth(sender, instance, created, **kwargs):
    ...
    avatar_url = instance.extra_data.get("picture")
    if avatar_url:
        response = requests.get(avatar_url)
        if response.status_code == 200:
            profile.avatar.save("image_name", ContentFile(response.content), save=True)
    
```

### Auto Verify a User
Usually, User will verify after social auth success.

#### Enable Feature
We can simply enable this feature by set `SOCIAL_AUTH_AUTO_VERIFY_USER = True` in `settings.py`

#### What's the feature do
We'll verify a user in receiver signal function same as create a user profile
but this time will verify immediately after UserSocialAuth has been created.
 
```python
@receiver(post_save, sender=UserSocialAuth, dispatch_uid="create_profile_for_google_auth")
def create_profile_for_google_auth(sender, instance, created, **kwargs):
    if (
        created
        and not instance.user.verified
        and getattr(settings, "SOCIAL_AUTH_AUTO_VERIFY_USER", False)
    ):
        instance.user.verified = True
        instance.user.save()
```
***see full code in user_manager/signals.py***


