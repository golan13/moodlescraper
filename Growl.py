import gntp.notifier


image = open('moodlescraper/static/img/grade_icon.png', 'rb').read()
growl = gntp.notifier.GrowlNotifier(
    applicationName="Moodle",
    notifications=["New Updates", "New Messages"],
    defaultNotifications=["New Messages"],
)
growl.register()


def send_notification(subject, assignment, grade):
    growl.notify(
        noteType="New Messages",
        title="New Grade in " + subject,
        description=assignment + " : " + str(grade),
        icon=image,
        sticky=False,
        priority=1,
    )
