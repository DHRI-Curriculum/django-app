from django.db.models.signals import post_save
from django.contrib.auth.models import User, Group
from django.dispatch import receiver
from learner.models import Profile

@receiver(post_save, sender=User)
def post_save_user_signal_handler(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
        # instance.is_staff = True
        try:
            group = Group.objects.get(name='Learner')
            instance.groups.add(group)
        except Group.DoesNotExist:
            print("Could not add user!") # TODO: Debug so remove in production
        instance.save()