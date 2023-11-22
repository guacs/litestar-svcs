from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING
from typing import Awaitable
from typing import Callable

from litestar.exceptions import ImproperlyConfiguredException

if TYPE_CHECKING:
    from svcs import Registry


@dataclass(frozen=True)
class SvcsPluginConfig:
    """The config for the `SvcsPlugin`."""

    registry: Registry | None = None
    """The `svcs.Registry` instance.

    If provided, this is used and if not a Registry is created with `registry_factory`.
    """

    registry_factory: (
        Callable[[], Registry] | Callable[[], Awaitable[Registry]] | None
    ) = None
    """A factory function to get registry.

    This is called on app startup if the registry instance has not been
    provided. This can be async or sync.
    """

    container_dependency_key: str = "svcs_container"
    """The dependency key to use for injecting `svcs.Container`."""

    registry_state_key: str = "svcs_registry"
    """The key used to store the Registry within the Litestar `State` instance."""

    def __post_init__(self) -> None:
        if self.registry is None and self.registry_factory is None:
            msg = "either `registry` or `registry_factory` must be provided"
            raise ImproperlyConfiguredException(
                msg,
            )

        if self.registry is not None and self.registry_factory is not None:
            msg = "only one of `registry` and `registry_factory` must be provided"
            raise ImproperlyConfiguredException(
                msg,
            )
