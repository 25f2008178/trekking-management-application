from flask_security import user_registered


def init_signals(app, user_datastore):
    @user_registered.connect_via(app)
    def user_registered_sighandler(app, user, confirm_token, form_data=None, **extra):
        default_role = user_datastore.find_or_create_role("user")
        user_datastore.add_role_to_user(user, default_role)
        user_datastore.commit()
