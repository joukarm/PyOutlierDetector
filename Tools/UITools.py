"""
Containing methods used in UI management
"""


def set_controls_enabled(controls, enabled=True):
    """
    Sets Enabled property of controls

    :param controls: controls whose enabled property should be set
    :param enabled: if enabled is true (default), the controls will be enabled; otherwise they will be disabled
    :return: enabled
    """
    for c in controls:
        c.setEnabled(enabled)

    return enabled
