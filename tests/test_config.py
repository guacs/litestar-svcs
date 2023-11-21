from __future__ import annotations

import pytest
from litestar.exceptions import ImproperlyConfiguredException
from svcs import Registry

from litestar_svcs.config import SvcsPluginConfig


def test_no_registry_given() -> None:
    """Instantiation should raise an error if neither `registry` nor `registry_factory` is provided."""

    with pytest.raises(
        ImproperlyConfiguredException,
        match="either `registry` or `registry_factory` must be provided",
    ):
        _ = SvcsPluginConfig()


def test_both_registry_and_factory_given() -> None:
    """Instantiation should raise an error if both `registry and `registry_facotry` is provided."""

    registry = Registry()

    def registry_factory() -> Registry:
        return registry

    with pytest.raises(
        ImproperlyConfiguredException,
        match="only one of `registry` and `registry_factory` must be provided",
    ):
        _ = SvcsPluginConfig(registry=registry, registry_factory=registry_factory)
