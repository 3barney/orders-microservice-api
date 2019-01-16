class InvalidArgumentError(Exception):

  # With {argument_name} we can specify what caused exception to be raised
  def __init__(self, argument_name):
    message = f'The argument {argument_name} is invalid'
    super().__init__(message) #Call constructor on superclass


class OrderAlreadyCompletedError(Exception):

  def __init__(self, order):
    message = f'The order with ID {order} is already completed'
    super().__init__(message)


class OrderAlreadyCancelledError(Exception):

  def __init__(self, order):
    message = f'The order with ID {order} is already cancelled'
    super().__init__(message)

class OrderCancellationError(Exception):
  pass

class OrderNotFoundError(Exception):
  pass