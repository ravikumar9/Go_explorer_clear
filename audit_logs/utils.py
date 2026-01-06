import logging

logger = logging.getLogger('audit')


def mask_secret(value: str, keep=4):
    if not value:
        return ''
    s = str(value)
    if len(s) <= keep:
        return '*' * len(s)
    return '*' * (len(s) - keep) + s[-keep:]


def structured_log(module: str, action: str, actor=None, **kwargs):
    """Emit a structured log for auditing. Do not include secrets."""
    payload = {
        'module': module,
        'action': action,
        'actor': getattr(actor, 'username', None) if actor else None,
    }
    payload.update(kwargs)
    logger.info(payload)
