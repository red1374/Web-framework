from jsonpickle import dumps, loads


# -- Behavioral pattern Observer
class Observer:
    def update(self, subject, message):
        pass


class Subject:
    def __init__(self):
        self.observers = []

    def notify(self, message):
        for item in self.observers:
            item.update(self, message)

    def notify_course_users(self, message):
        for student in self.students:
            for item in self.observers:
                item.update(self, f'To student "{student.name}. {message}".')


class SmsNotifier(Observer):
    def update(self, subject, message):
        print('SMS->', message)


class EmailNotifier(Observer):
    def update(self, subject, message):
        print('EMAIL->', message)


class Notifier:
    def __init__(self):
        self.sms_notifier = SmsNotifier()
        self.email_notifier = EmailNotifier()

    def update(self, subject, message: str):
        self.sms_notifier.update(subject, message)
        self.email_notifier.update(subject, message)


class BaseSerializer:
    def __init__(self, obj):
        self.obj = obj

    def save(self):
        return dumps(self.obj)

    @staticmethod
    def load(data):
        return loads(data)
