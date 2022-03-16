# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from octoprint.util import ResettableTimer
import octoprint.plugin


class AutoShutdownPlugin(octoprint.plugin.TemplatePlugin,
                       octoprint.plugin.SettingsPlugin,
                         octoprint.plugin.ShutdownPlugin):

    def __init__(self):
        self.enabled = False
        self.timeout = 0


    def _shutdown_system(self):
        shutdown_command = self._settings.global_get(["server", "commands", "systemShutdownCommand"])
        self._logger.info("Shutting down system with command: {command}".format(command=shutdown_command))
        try:
            import sarge
            p = sarge.run(shutdown_command, async_=True)
        except Exception as e:
            self._logger.exception("Error when shutting down: {error}".format(error=e))
            return

    def _shutdown_init(self):
        if self.enabled:
            t = ResettableTimer(self.timeout, self._shutdown_system)
            t.start()
            self._logger.info("Timer started")
        else:
            self._logger.info("Timer is not enabled")

    def on_shutdown(self):
        self._logger.info("Shutting down via AutoShutdown")

    def get_settings_defaults(self):
        return dict(timeout=3600, enabled=False)

    def on_settings_save(self, data):
        octoprint.plugin.SettingsPlugin.on_settings_save(self, data)
        self.enabled = self._settings.get_boolean(["enabled"])
        self.timeout = self._settings.get_int(["timeout"])
        self._logger.info("enabled: {en}, timeout: {t}".format(en = self.enabled, t = self.timeout))
        self._shutdown_init()


    def get_template_vars(self):
        return dict(timeout=self._settings.get(["Timeout"]))

    def get_template_configs(self):
        return [dict(
            type="sidebar",
            name="AutoShutdown",
            custom_bindings=False,
            icon="power-off"
        ), dict(
            type="settings",
            custom_bindings=False
        )]



__plugin_name__ = "AutoShutdown"
__plugin_pythoncompat__ = ">=2.7,<4"
__plugin_implementation__ = AutoShutdownPlugin()

