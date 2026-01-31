import abc

import discord as d


class AuditLogEntryFormater:
    def __init__(self, entry: "d.AuditLogEntry"):
        self.entry = entry
        self.action = entry.action

    def format(self) -> "str | None":
        if cls := action_map.get(self.action):
            return cls().format(self.entry)
        return None

class AuditLogEntryActionFormater(abc.ABC):
    def format(self, entry: "d.AuditLogEntry"):
        ...

class MemberUpdateFormater(AuditLogEntryActionFormater):
    def format(self, entry: "d.AuditLogEntry"):
        changes = ", ".join([f"{k}=**{v}**" for k, v in entry.after])
        return f"✏️ <@{entry.user.id}> has updated <@{entry.target.id}>: {changes}"

class MemberRoleUpdateFormater(AuditLogEntryActionFormater):
    def format(self, entry: "d.AuditLogEntry"):
        before_roles: set[d.Role] = set(entry.before.roles)
        after_roles: set[d.Role] = set(entry.after.roles)
        added_roles = after_roles - before_roles
        removed_roles = before_roles - after_roles

        if not any((added_roles, removed_roles)):
            return None

        added_roles_str = ", ".join([f"+<@&{role.id}>" for role in added_roles])
        removed_roles_str = ", ".join([f"-<@&{role.id}>" for role in removed_roles])
        changed_roles = ", ".join(list(filter(bool, [added_roles_str, removed_roles_str])))
        return f"✏️ <@{entry.user.id}> has updated <@{entry.target.id}> roles: {changed_roles}"

class ChannelUpdateFormater(AuditLogEntryActionFormater):
    def format(self, entry: "d.AuditLogEntry"):
        changes = ", ".join([f"{k}=**{v}**" for k, v in entry.after])
        return f"✏️ <@{entry.user.id}> has updated <#{entry.target.id}>: {changes}"

class ChannelCreateFormater(AuditLogEntryActionFormater):
    def format(self, entry: "d.AuditLogEntry"):
        return f"✏️ <@{entry.user.id}> has created <#{entry.target.id}>"

class ChannelDeleteFormater(AuditLogEntryActionFormater):
    def format(self, entry: "d.AuditLogEntry"):
        return f"✏️ <@{entry.user.id}> has deleted <#{entry.target.id}>"

class ChannelPermissionsFormater(AuditLogEntryActionFormater):
    def format(self, entry: "d.AuditLogEntry"):
        allowed = [permission for permission, value in getattr(entry.after, "allow", []) if value]
        denied = [permission for permission, value in getattr(entry.after, "deny", []) if value]
        if not any((allowed, denied)):
            return None
        allowed_str = ", ".join([permission.replace("_", " ").title() + " <:checked:1459703224624877640>" for permission in allowed])
        denied_str = ", ".join([permission.replace("_", " ").title() + " <:unchecked:1459703221860831608>" for permission in denied])
        roles_str = ", ".join((allowed_str, denied_str))
        changes = ", ".join([f"{k}=**{v}**" for k, v in entry.after])
        return f"✏️ <@{entry.user.id}> has updated <#{entry.target.id}>'s permissions for <@&{entry.extra.id}>\n{roles_str}"

def format_none_bool(val: bool | None) -> str:
    if val is None:
        return ""
    else:
        return f"{val}"


action_map = {
    d.AuditLogAction.member_update: MemberUpdateFormater,
    d.AuditLogAction.member_role_update: MemberRoleUpdateFormater,
    d.AuditLogAction.channel_update: ChannelUpdateFormater,
    d.AuditLogAction.channel_create: ChannelCreateFormater,
    d.AuditLogAction.overwrite_update: ChannelPermissionsFormater,
    d.AuditLogAction.overwrite_create: ChannelPermissionsFormater,
    d.AuditLogAction.overwrite_delete: ChannelPermissionsFormater,
}