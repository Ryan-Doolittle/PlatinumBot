from nextcord import Interaction


def check_if_role(bot, interaction:Interaction, role_id):
    has_role = interaction.user.get_role(role_id)
    if has_role:
        return True
    return False


def check_if_privileged(bot, interaction:Interaction):
    valid_roles = [
        bot.server_settings["admin_role_id"],
        bot.server_settings["developer_role_id"]
    ]

    for role in valid_roles:
        found = check_if_role(bot, interaction, role)
        if found:
            return True
    return False
    