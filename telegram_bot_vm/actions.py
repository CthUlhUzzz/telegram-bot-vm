import re

from .helpers import format_message

__all__ = ('BaseAction', 'SendMessageAction', 'GetInputAction', 'ForwardToPositionAction')


class BaseAction:
    def exec(self, vm_context):
        raise NotImplementedError


class SendMessageAction(BaseAction):
    def __init__(self, text):
        self.text = text

    def exec(self, vm_context):
        vm_context.position += 1
        return format_message(self.text, vm_context.variables)


class GetInputAction(BaseAction):
    def __init__(self, variable_name):
        self.variable_name = variable_name

    def exec(self, vm_context):
        input_ = vm_context.input
        if input_ is not None:
            vm_context.variables[self.variable_name] = input_
            vm_context.input = None
            vm_context.position += 1


class ForwardToPositionAction(BaseAction):
    def __init__(self, position, variable_name=None, condition_regex=None):
        self.variable_name = variable_name
        self.position = position
        self.condition_regex = condition_regex

    def exec(self, vm_context):
        if self.variable_name is not None and self.condition_regex is not None:
            variable = vm_context.variables.get(self.variable_name)
            if variable is not None and re.fullmatch(self.condition_regex, variable) is not None:
                vm_context.position = self.position
            else:
                vm_context.position += 1
        else:
            vm_context.position = self.position
