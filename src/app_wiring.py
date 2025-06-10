import importlib
import pkgutil

def import_submodules(package_name):
    """
    Dynamically imports all submodules within a given package.
    Useful for wiring dependency injection containers.
    """
    package = importlib.import_module(package_name)
    # Filter out __init__.py if it's treated as a module by pkgutil
    return [
        importlib.import_module(f"{package_name}.{name}")
        for _, name, _ in pkgutil.iter_modules(package.__path__)
        if name != "__init__" # Ensure __init__ is not re-imported as a separate module
    ]

def get_modules_to_wire():
    """
    Defines and returns the list of modules that need to be wired for
    dependency injection.
    """
    modules_to_wire = []

    # Identity feature
    modules_to_wire.extend(import_submodules("src.features.identity.api.v1.routes.auth"))
    modules_to_wire.extend(import_submodules("src.features.identity.api.v1.routes.profile"))

    # Bot feature
    modules_to_wire.extend(import_submodules("src.features.bot.api.v1.routes.bot_management"))
    modules_to_wire.extend(import_submodules("src.features.bot.api.v1.routes.bot_participants"))
    modules_to_wire.extend(import_submodules("src.features.bot.api.v1.routes.bot_services"))
    modules_to_wire.extend(import_submodules("src.features.bot.api.v1.routes.bot_documents"))
    modules_to_wire.extend(import_submodules("src.features.bot.api.v1.routes")) # Catch any direct routes in this folder

    # Conversation feature
    modules_to_wire.extend(import_submodules("src.features.conversation.api.v1.routes"))

    # Integrations feature
    modules_to_wire.extend(import_submodules("src.features.integrations.messengers.telegram.api.v1.routes"))

    # Announcement feature
    modules_to_wire.extend(import_submodules("src.features.announcement.api.v1.routes"))

    # Support feature
    modules_to_wire.extend(import_submodules("src.features.support.api.v1.routes"))

    # Prices feature
    modules_to_wire.extend(import_submodules("src.features.prices.api.v1.routes"))

    return modules_to_wire

