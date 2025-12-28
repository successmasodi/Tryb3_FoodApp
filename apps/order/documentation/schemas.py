from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from apps.order.serializers import PaymentMethodSerializer, AddCartItemSerializer, OrderSerializer


payment_method_list = swagger_auto_schema(
    operation_summary='Retrieve all payment methods',
    operation_description=(
        """Endpoint to list all available payment methods.
        **Search by:** payment_type, is_active \n'
        **Order by:** is_active"""
    ),
    responses={200: PaymentMethodSerializer(many=True)},
    tags=['PaymentMethod']
)

payment_method_create = swagger_auto_schema(
    operation_summary='Create a new payment method (admin only).',
    operation_description='Endpoint to create a new payment method option such as "Cash on Delivery" or "Bank Card" ( Only admin).',
    request_body=PaymentMethodSerializer,
    responses={201: PaymentMethodSerializer()},
    tags=['PaymentMethod']
)

payment_method_retrieve = swagger_auto_schema(
    manual_parameters=[
        openapi.Parameter(
            'id', openapi.IN_PATH, description='ID of the payment method', type=openapi.TYPE_INTEGER
        )
    ],
    operation_summary='Retrieve a specific payment method by ID.',
    operation_description='Endpoint to get a payment method by its ID.',
    responses={
        200: PaymentMethodSerializer(),
        404: '{"detail": "No payment method matches the given query."}'
    },
    tags=['PaymentMethod']
)

payment_method_update = swagger_auto_schema(
    manual_parameters=[
        openapi.Parameter(
            'id', openapi.IN_PATH, description='ID of the payment method', type=openapi.TYPE_INTEGER
        )
    ],
    operation_summary='Update a payment method (admin only).',
    operation_description='Endpoint to update an existing payment method.',
    request_body=PaymentMethodSerializer,
    responses={
        200: PaymentMethodSerializer(),
        404: '{"detail": "No payment method matches the given query."}'
    },
    tags=['PaymentMethod']
)

payment_method_partial_update = swagger_auto_schema(
    manual_parameters=[
        openapi.Parameter(
            'id', openapi.IN_PATH, description='ID of the payment method', type=openapi.TYPE_INTEGER
        )
    ],
    operation_summary='Partially update a payment method (admin only).',
    operation_description='Endpoint to partially update a payment method field.',
    request_body=PaymentMethodSerializer,
    responses={
        200: PaymentMethodSerializer(),
        404: '{"detail": "No payment method matches the given query."}'
    },
    tags=['PaymentMethod']
)

payment_method_destroy = swagger_auto_schema(
    manual_parameters=[
        openapi.Parameter(
            'id', openapi.IN_PATH, description='ID of the payment method', type=openapi.TYPE_INTEGER
        )
    ],
    operation_summary='Delete a payment method (admin only).',
    operation_description='Endpoint to delete a payment method by ID.',
    responses={
        204: '',
        404: '{"detail": "No payment method matches the given query."}'
    },
    tags=['PaymentMethod']
)

payment_method_docs = {
    'list': payment_method_list,
    'create': payment_method_create,
    'retrieve': payment_method_retrieve,
    'update': payment_method_update,
    'partial_update': payment_method_partial_update,
    'destroy': payment_method_destroy,
}


add_cart_item_list = swagger_auto_schema(
    operation_summary='Retrieve all cart items for the current user.',
    operation_description="Endpoint to list all items in the user\'s cart, grouped by restaurant.",
    responses={200: AddCartItemSerializer(many=True)},
    tags=['Cart']
)

add_cart_item_create = swagger_auto_schema(
    operation_summary="Add an item to the user's cart.",
    operation_description=(
        """Endpoint to add a dish to the user\'s cart. If the cart does not exist for the 
        specified restaurant, a new cart will be created. If the dish already exists in the cart,
        the quantity will be incremented."""
    ),
    request_body=AddCartItemSerializer,
    responses={201: AddCartItemSerializer()},
    tags=['Cart']
)

add_cart_docs = {
    'get': add_cart_item_list,
    'post': add_cart_item_create,
}


cart_item_destroy_docs = swagger_auto_schema(
    manual_parameters=[
        openapi.Parameter(
            'id', openapi.IN_PATH, description='ID of the cart item', type=openapi.TYPE_INTEGER
        )
    ],
    operation_summary='Delete an item (owner only).',
    operation_description='Endpoint to delete an cart item by ID.',
    responses={
        204: '',
        404: '{"detail": "No order matches the given query."}'
    },
    tags=['Cart']
)

cart_item_retrieve_docs = swagger_auto_schema(
    operation_summary='Retrieve  cart items for the current user by ID.',
    operation_description="Endpoint to retrieve a particular items in the user\'s cart by ID",
    responses={200: AddCartItemSerializer(many=True)},
    tags=['Cart']
)


order_list = swagger_auto_schema(
    operation_summary='Retrieve all orders (admin only).',
    operation_description=(
        'Endpoint to retrieve all orders. '
        'Supports search by status, payment status, restaurant name. '
        'Can be ordered by is_active or total.'
    ),
    responses={200: OrderSerializer(many=True)},
    tags=['Order']
)

order_create = swagger_auto_schema(
    operation_summary='Create a new order (after checkout).',
    operation_description=(
        'Endpoint to create a new order after a successful cart checkout. '
        'This also deletes the associated cart.'
    ),
    request_body=OrderSerializer,
    responses={201: OrderSerializer()},
    tags=['Order']
)

order_retrieve = swagger_auto_schema(
    manual_parameters=[
        openapi.Parameter(
            'id', openapi.IN_PATH, description='ID of the order', type=openapi.TYPE_INTEGER
        )
    ],
    operation_summary='Retrieve a specific order by ID.',
    operation_description='Endpoint to retrieve an order by its ID.',
    responses={
        200: OrderSerializer(),
        404: '{"detail": "No order matches the given query."}'
    },
    tags=['Order']
)

order_partial_update = swagger_auto_schema(
    manual_parameters=[
        openapi.Parameter(
            'id', openapi.IN_PATH, description='ID of the order', type=openapi.TYPE_INTEGER
        )
    ],
    operation_summary='Partially update an order (admin only).',
    operation_description='Endpoint to partially update fields (e.g status ) of an existing order by ID.',
    request_body=OrderSerializer,
    responses={
        200: OrderSerializer(),
        404: '{"detail": "No order matches the given query."}'
    },
    tags=['Order']
)

order_docs = {
    'list': order_list,
    'create': order_create,
    'retrieve': order_retrieve,
    'partial_update': order_partial_update
}
