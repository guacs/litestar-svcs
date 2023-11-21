from __future__ import annotations

from http import HTTPStatus
from typing import Callable

import pytest
from litestar import get
from litestar.params import Dependency
from litestar.testing import create_test_client
from svcs import Container
from svcs import Registry

from litestar_svcs.config import SvcsPluginConfig
from litestar_svcs.plugin import SvcsPlugin

NUMBER = 10
STRING = "foo"


def _registry_factory() -> Registry:
    registry = Registry()

    registry.register_factory(int, lambda: NUMBER)
    registry.register_factory(str, lambda: STRING)

    return registry


async def _async_registry_factory() -> Registry:
    return _registry_factory()


@pytest.mark.parametrize(
    "registry",
    (_registry_factory(), _registry_factory, _async_registry_factory),
)
def test_container_injected(registry: Registry | Callable[[], Registry]) -> None:
    """Ensure the container is injected as a dependency."""

    @get("/", sync_to_thread=False)
    def get_handler(
        svcs_container: Container = Dependency(skip_validation=True),
    ) -> None:
        assert svcs_container.get(int) == NUMBER
        assert svcs_container.get(str) == STRING

    config = (
        SvcsPluginConfig(registry)
        if isinstance(registry, Registry)
        else SvcsPluginConfig(registry_factory=registry)
    )
    plugin = SvcsPlugin(config)

    with create_test_client([get_handler], plugins=[plugin]) as client:
        response = client.get("/")

        assert response.status_code == HTTPStatus.OK


def test_container_injected_custom_key() -> None:
    """Test container is injected when using a custom dependency key."""

    @get("/", sync_to_thread=False)
    def get_handler(
        container: Container = Dependency(skip_validation=True),
    ) -> None:
        assert container.get(int) == NUMBER
        assert container.get(str) == STRING

    registry = _registry_factory()
    config = SvcsPluginConfig(registry, container_dependency_key="container")
    plugin = SvcsPlugin(config)

    with create_test_client([get_handler], plugins=[plugin]) as client:
        response = client.get("/")

        assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    "registry",
    (_registry_factory(), _registry_factory, _async_registry_factory),
)
def test_registry_injected(registry: Registry | Callable[[], Registry]) -> None:
    """Ensure the registry is injected as a dependency."""

    @get("/", sync_to_thread=False)
    def get_handler(svcs_registry: Registry = Dependency(skip_validation=True)) -> None:
        container = Container(svcs_registry)

        assert container.get(int) == NUMBER
        assert container.get(str) == STRING

    config = (
        SvcsPluginConfig(registry)
        if isinstance(registry, Registry)
        else SvcsPluginConfig(registry_factory=registry)
    )
    plugin = SvcsPlugin(config)

    with create_test_client([get_handler], plugins=[plugin]) as client:
        response = client.get("/")

        assert response.status_code == HTTPStatus.OK


def test_registry_closed() -> None:
    """The registry must be closed after the app is shutdown."""

    @get("/", sync_to_thread=False)
    def get_handler() -> None:
        ...

    registry = _registry_factory()
    config = SvcsPluginConfig(registry)
    plugin = SvcsPlugin(config)

    with create_test_client([get_handler], plugins=[plugin]) as client:
        response = client.get("/")

        assert response.status_code == HTTPStatus.OK

    # The registry clears all services when it's closed.
    assert int not in registry
    assert str not in registry
