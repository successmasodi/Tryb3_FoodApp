from .models import PaymentRecord
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAdminUser


class PaymentRecordView(GenericAPIView):
  queryset = PaymentRecord.objects.select_related('cart')
  permission_classes = [IsAdminUser]

  def get(self, *args, **kwargs):
    payment_records = self.filter_queryset(self.get_queryset())

    data = [{
      'id':value.id,
     'tx_ref': value.tx_ref,
     'cart': {
       'id': str(value.cart),
       'customer': value.cart.customer.email
       },
     'payment_method': value.payment_method,
     'created_at': value.created_at
    } for value in payment_records]

    return Response(data, status=status.HTTP_200_OK)
