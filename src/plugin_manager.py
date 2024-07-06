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
        self.manager.load_setuptools_entrypoints("saa_orchestrator_plugins")

    def get_use_case_prompts(self) -> Dict[str, Callable]:
        prompts = {}
        for hook_impl in self.manager.hook.get_use_case_prompt.get_hookimpls():
            prompts[hook_impl.plugin_name] = hook_impl.function
        return prompts


plugin_manager = PluginManager()
