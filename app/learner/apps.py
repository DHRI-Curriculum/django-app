from django.apps import AppConfig


class LearnerConfig(AppConfig):
    name = 'learner'

    def ready(self):
        import learner.signals