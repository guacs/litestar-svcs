# Litestar Svcs

A plugin to integrate [litestar](https://github.com/litestar-org/litestar) with [svcs](https://github.com/hynek/svcs/).

# Basic Usage

```python
from litestar import Litestar
from litestar import get
from litestar_svcs import SvcsPlugin, SvcsPluginConfig

from svcs import Container, Registry

@get("/", sync_to_thread=False)
def get_user(svcs_container: Container) -> int:
  return svcs_container.get(int)


registry = Registry()
registry.register_factory(int, lambda: 10)

svcs_plugin_config = SvcsPluginConfig(registry=registry)
svcs_plugin = SvcsPlugin(svcs_plugin_config)

app = Litestar([get_user], plugins=[svcs_plugin])
```

# Configuring

- You can pass in the `registry` instance, as in the example, to the config or you can give it a callable (sync or async) and it will be used to create the registry when the app is starting.
- You can give a custom name to the name of the kwarg for injecting the containers by setting a different value for `container_dependency_key` (default is `svcs_container`).

  NOTE: You *cannot* configure the name of the kwarg which injects the registry (the kwarg name is `svcs_registry`).
