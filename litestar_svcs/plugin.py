from __future__ import annotations

from contextlib import asynccontextmanager
from inspect import isawaitable
from typing import TYPE_CHECKING
from typing import AsyncGenerator
from typing import Final

from litestar.di import Provide
from litestar.exceptions import ImproperlyConfiguredException
from litestar.params import Dependency
from litestar.plugins import InitPluginProtocol
from svcs import Container
from svcs import Registry
from typing_extensions import override

if TYPE_CHECKING:
    from litestar.app import Litestar
    from litestar.config.app import AppConfig
    from litestar.datastructures.state import State

    from litestar_svcs.config import SvcsPluginConfig


class SvcsPlugin(InitPluginProtocol):
    """The plugin for integrating `svcs` to a `Litestar` application."""

    _registry: Registry
    _REGISTRY_DEPENDENCY_NAME: Final[str] = "svcs_registry"

    def __init__(self, config: SvcsPluginConfig) -> None:
        self._config = config

    @property
    def registry(self) -> Registry:
        """Get the registry instance.

        This will raise a `RuntimeError` if the application has not started yet
        and the registry has not been setup yet.
        """

        try:
            return self._registry
        except AttributeError as ex:
            msg = "the svcs registry has not been setup yet"
            raise RuntimeError(msg) from ex

    @asynccontextmanager
    async def get_container(self) -> AsyncGenerator[Container, None]:
        """Get a `svcs.Container` instance.

        This can be used in places where dependency injection is not possible
        within `litestar` such as in middlewares.
        """

        async with Container(self.registry) as container:
            yield container

    def provide_registry(self, state: State) -> Registry:
        """Provide the registry given the Litestar state.

        Args:
        ----
            state: The `Litestar` state instance.
        """

        registry = state.get(self._config.registry_state_key)

        assert registry is not None

        return registry

    async def provide_container(
        self,
        svcs_registry: Registry = Dependency(skip_validation=True),  # noqa: B008
    ) -> AsyncGenerator[Container, None]:
        """Provide the container from the given registry.

        Args:
        ----
            svcs_registry: A `svcs.Registry` instance.
        """

        async with Container(svcs_registry) as container:
            yield container

    async def on_app_startup(self, app: Litestar) -> None:
        """Create and add the registry to the app state."""

        registry: Registry
        if self._config.registry:
            registry = self._config.registry
        elif self._config.registry_factory:
            _registry = self._config.registry_factory()
            if isawaitable(_registry):
                self._registry = registry = await _registry
            else:
                self._registry = registry = _registry  # type: ignore[assignment]
        else:
            msg = "either `registry` or `registry_factory` must be provided"
            raise ImproperlyConfiguredException(
                msg,
            )
        app.state.update({self._config.registry_state_key: registry})

    async def on_app_shutdown(self, app: Litestar) -> None:
        """Close the registry."""

        registry: Registry | None = app.state.get(self._config.registry_state_key)

        assert registry is not None

        await registry.aclose()

    @override
    def on_app_init(self, app_config: AppConfig) -> AppConfig:
        app_config.dependencies.update(
            {
                self._config.container_dependency_key: Provide(self.provide_container),
                self._REGISTRY_DEPENDENCY_NAME: Provide(
                    self.provide_registry,
                    use_cache=True,
                    sync_to_thread=False,
                ),
            },
        )
        app_config.on_startup.insert(0, self.on_app_startup)
        app_config.on_shutdown.append(self.on_app_shutdown)
        app_config.signature_namespace.update(
            {
                "Container": Container,
                "Registry": Registry,
            },
        )

        return app_config
