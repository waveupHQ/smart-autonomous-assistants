import importlib.util
import os
from typing import Callable, Dict

import pluggy

hookspec = pluggy.HookspecMarker("saa_orchestrator")
hookimpl = pluggy.HookimplMarker("saa_orchestrator")


class PluginSpec:
    @hookspec
    def get_use_case_prompt(self, objective: str) -> str:
        """Generate a prompt for a specific use case."""


class PluginManager:
    def __init__(self):
        self.manager = pluggy.PluginManager("saa_orchestrator")
        self.manager.add_hookspecs(PluginSpec)

    def register_plugin(self, plugin):
        self.manager.register(plugin)

    def load_plugins(self, plugin_folder: str):
        if not os.path.exists(plugin_folder):
            return

        for filename in os.listdir(plugin_folder):
            if filename.endswith("_plugin.py"):
                module_name = filename[:-3]  # Remove '.py'
                module_path = os.path.join(plugin_folder, filename)
                try:
                    spec = importlib.util.spec_from_file_location(module_name, module_path)
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    for item_name in dir(module):
                        item = getattr(module, item_name)
                        if isinstance(item, type) and item_name.endswith("Plugin"):
                            plugin_instance = item()
                            self.register_plugin(plugin_instance)
                except Exception:
                    pass  # Silently ignore any loading errors

    def get_use_case_prompts(self) -> Dict[str, Callable]:
        prompts = {}
        for hook_impl in self.manager.hook.get_use_case_prompt.get_hookimpls():
            plugin_name = hook_impl.plugin.__class__.__name__
            prompts[plugin_name] = hook_impl.function
        return prompts


plugin_manager = PluginManager()
