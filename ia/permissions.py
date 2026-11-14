ADMIN_GROUP_NAME = "Administrador"


def has_ia_admin_access(user):
    return bool(
        user.is_authenticated
        and user.groups.filter(name=ADMIN_GROUP_NAME).exists()
    )
