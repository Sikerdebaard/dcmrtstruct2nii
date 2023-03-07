from cleo.commands.command import Command


class PatchedCommand(Command):
    def __init__(self):
        super(PatchedCommand, self).__init__()

    def _castToBool(self, val):
        if isinstance(val, bool):
            return val

        return val.lower() in ['true', '1', 't', 'y', 'yes', 'yeah', 'yup', 'certainly', 'uh-huh', 'yarr']
