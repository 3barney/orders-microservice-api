"""
  generic, contains definitions for the generic view classes that we 
  are going to use to create our own custom views.

  The status contains all the HTTP status code
"""
from rest_framework import generics, status
from rest_framework.response import Response
from django.http import HttpResponse

from .exceptions import InvalidArgumentError
from .exceptions import OrderAlreadyCancelledError
from .exceptions import OrderAlreadyCompletedError
from .serializers import OrderSerializer # serialization, deserialization, and the validation model.

# base class for all the views that will return a list of content to the client
# ListAPIView, Provide us with get and list methods  which we can override to add functionality

# The idea of this base class is that all the children classes need to implement the
# get_queryset method
class OrderListApiBaseView(generics.ListAPIView):
  serializer_class = OrderSerializer
  lookup_field = ''

  def get_queryset(self, lookup_field):
    pass

  def list(self, request, *args, **kwargs):
    try:
      result = self.get_queryset(kwargs.get(self.lookup_field, None))
    except Exception as err:
      return Response(err, status=status.HTTP_400_BAD_REQUEST)

    serializer = OrderSerializer(result, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

# will help us with the methods that will perform POST request.
# takes a function as an argument. Run the function; if one of the exceptions occurs
# return 404 or else return 204
def set_status_handler(set_status_delegate):
  try:
    set_status_delegate()
  except (InvalidArgumentError, OrderAlreadyCancelledError, OrderAlreadyCompletedError) as err:
    return HttpResponse(err, status=status.HTTP_400_BAD_REQUEST)

  return HttpResponse(status=status.HTTP_204_NO_CONTENT)