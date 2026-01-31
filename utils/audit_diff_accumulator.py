import discord as d
import copy


def accumulate_changes(logs: list[d.AuditLogEntry]) -> d.AuditLogEntry:
    base = copy.copy(logs[0])
    for log in logs[1:]:
        for key, value in log.before:
            if isinstance(value, list):
                base.before.__dict__[key].extend(value)
            else:
                base.before.__dict__[key] = value
        for key, value in log.after:
            if isinstance(value, list):
                base.after.__dict__[key].extend(value)
            else:
                base.after.__dict__[key] = value

    return base