
import pkgutil

# this is the package we are inspecting -- for example 'email' from stdlib
from BIDSit import go

package = go

for importer, modname, ispkg in pkgutil.iter_modules(package.__path__):
    print("Found submodule %s (is a package: %s)" % (modname, ispkg))

