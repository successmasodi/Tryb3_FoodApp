from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from apps.restaurant.serializers import AddressSerializer, CuisineSerializer, FoodCategorySerializer , RestaurantSerializer, DishSerializer


address_list = swagger_auto_schema(
    operation_summary='Retrieve all addresses of the authenticated user.',
    operation_description='Endpoint to list all saved addresses for the current user.',
    responses={200: AddressSerializer(many=True)},
    tags=['Address']
)

address_create = swagger_auto_schema(
    operation_summary='Create a new address for the user.',
    operation_description='Endpoint to create and save a new address. The address is automatically linked to the logged-in user.',
    request_body=AddressSerializer,
    responses={201: AddressSerializer()},
    tags=['Address']
)

address_retrieve = swagger_auto_schema(
    manual_parameters=[
        openapi.Parameter(
            'id', openapi.IN_PATH, description='ID of the address', type=openapi.TYPE_INTEGER
        )
    ],
    operation_summary='Retrieve a specific address by ID.',
    operation_description='Endpoint to retrieve a specific address belonging to the current user.',
    responses={
        200: AddressSerializer(),
        404: '{"detail": "No address matches the given query."}'
    },
    tags=['Address']
)

address_update = swagger_auto_schema(
    manual_parameters=[
        openapi.Parameter(
            'id', openapi.IN_PATH, description='ID of the address', type=openapi.TYPE_INTEGER
        )
    ],
    operation_summary='Update an existing address.',
    operation_description='Endpoint to fully update an address. Only the owner can perform this action.',
    request_body=AddressSerializer,
    responses={
        200: AddressSerializer(),
        404: '{"detail": "No address matches the given query."}'
    },
    tags=['Address']
)

address_partial_update = swagger_auto_schema(
    manual_parameters=[
        openapi.Parameter(
            'id', openapi.IN_PATH, description='ID of the address', type=openapi.TYPE_INTEGER
        )
    ],
    operation_summary='Partially update an address.',
    operation_description='Endpoint to partially update address fields. Only the owner can perform this action.',
    request_body=AddressSerializer,
    responses={
        200: AddressSerializer(),
        404: '{"detail": "No address matches the given query."}'
    },
    tags=['Address']
)

address_destroy = swagger_auto_schema(
    manual_parameters=[
        openapi.Parameter(
            'id', openapi.IN_PATH, description='ID of the address', type=openapi.TYPE_INTEGER
        )
    ],
    operation_summary='Delete an address.',
    operation_description='Endpoint to delete an address. Only the owner can delete their address.',
    responses={
        204: '',
        404: '{"detail": "No address matches the given query."}'
    },
    tags=['Address']
)

address_docs = {
    'list': address_list,
    'create': address_create,
    'retrieve': address_retrieve,
    'update': address_update,
    'partial_update': address_partial_update,
    'destroy': address_destroy,
}


cuisine_list = swagger_auto_schema(
    operation_summary='Retrieve all cuisine.',
    operation_description='Endpoint to get the list of all cuisine. Search by name, ordered by name',
    responses={200: CuisineSerializer(many=True)},
    tags=['Cuisine']
)

cuisine_create = swagger_auto_schema(
    operation_summary='Create a new cuisine.',
    operation_description='Endpoint to create a new cuisine only by admin. The name should be capitalized.',
    request_body=CuisineSerializer,
    responses={201: CuisineSerializer()},
    tags=['Cuisine']
)

cuisine_retrieve = swagger_auto_schema(
    manual_parameters=[openapi.Parameter(
        'id', openapi.IN_PATH, description='id of the cuisine', type=openapi.TYPE_INTEGER)],
    operation_summary='Retrieve a specific cuisine by ID.',
    operation_description='Endpoint to get a cuisine by its unique ID.',
    responses={200: CuisineSerializer(),
               404: '{"detail": "No Cuisine matches the given query."}'
               },
    tags=['Cuisine']
)

cuisine_update = swagger_auto_schema(
    manual_parameters=[openapi.Parameter(
        'id', openapi.IN_PATH, description='id of the cuisine', type=openapi.TYPE_INTEGER)],
    operation_summary='Update an existing category only by admin.',
    operation_description='Endpoint to update a cuisine details by ID.',
    request_body=CuisineSerializer,
    responses={200: CuisineSerializer(),
            404: '{"detail": "No Cuisine matches the given query."}'
               },
    tags=['Cuisine']
)

cuisine_partial_update = swagger_auto_schema(
    manual_parameters=[openapi.Parameter(
        'id', openapi.IN_PATH, description='id of the cuisine', type=openapi.TYPE_INTEGER)],
    operation_summary='Partially update an existing category only by admin.',
    operation_description='Endpoint to partially update a cuisine details by ID.',
    request_body=CuisineSerializer,
    responses={200: CuisineSerializer(),
               404: '{"detail": "No Cuisine matches the given query."}'
               },
    tags=['Cuisine']
)

cuisine_destroy = swagger_auto_schema(
    manual_parameters=[openapi.Parameter('id', openapi.IN_PATH, description='id of the cuisine', type=openapi.TYPE_INTEGER)],
    operation_summary='Delete a category only by admin.',
    operation_description='Endpoint to delete a category by its ID.',
    request_body=CuisineSerializer,
    responses={204: '',
               404: '{"detail": "No Cuisine matches the given query."}'
               },
    tags=['Cuisine']
)

cuisine_docs = {
    'list': cuisine_list,
    'create': cuisine_create,
    'retrieve': cuisine_retrieve,
    'update': cuisine_update,
    'partial_update': cuisine_partial_update,
    'destroy': cuisine_destroy,
}



food_category_list = swagger_auto_schema(
    operation_summary='Retrieve all Food category.',
    operation_description='Endpoint to get the list of all Food category. Search by name',
    responses={200: FoodCategorySerializer(many=True)},
    tags=['Food_category']
)

food_category_create = swagger_auto_schema(
    operation_summary='Create a new Food category.',
    operation_description='Endpoint to create a new Food category only by admin. The name should be capitalized.',
    request_body=FoodCategorySerializer,
    responses={201: FoodCategorySerializer()},
    tags=['Food_category']
)

food_category_retrieve = swagger_auto_schema(
    manual_parameters=[openapi.Parameter(
        'id', openapi.IN_PATH, description='id of the Food category', type=openapi.TYPE_INTEGER)],
    operation_summary='Retrieve a specific Food category by ID.',
    operation_description='Endpoint to get a Food category by its unique ID.',
    responses={200: FoodCategorySerializer(),
               404: '{"detail": "No Food category matches the given query."}'
               },
    tags=['Food_category']
)

food_category_update = swagger_auto_schema(
    manual_parameters=[openapi.Parameter(
        'id', openapi.IN_PATH, description='id of the Food category', type=openapi.TYPE_INTEGER)],
    operation_summary='Update an existing category only by admin.',
    operation_description='Endpoint to update a Food category details by ID.',
    request_body=FoodCategorySerializer,
    responses={200: FoodCategorySerializer(),
            404: '{"detail": "No Food category matches the given query."}'
               },
    tags=['Food_category']
)

food_category_partial_update = swagger_auto_schema(
    manual_parameters=[openapi.Parameter(
        'id', openapi.IN_PATH, description='id of the Food category', type=openapi.TYPE_INTEGER)],
    operation_summary='Partially update an existing category only by admin.',
    operation_description='Endpoint to partially update a Food category details by ID.',
    request_body=FoodCategorySerializer,
    responses={200: FoodCategorySerializer(),
               404: '{"detail": "No Food category matches the given query."}'
               },
    tags=['Food_category']
)

food_category_destroy = swagger_auto_schema(
    manual_parameters=[openapi.Parameter('id', openapi.IN_PATH, description='id of the cuisine', type=openapi.TYPE_INTEGER)],
    operation_summary='Delete a category only by admin.',
    operation_description='Endpoint to delete a category by its ID.',
    request_body=FoodCategorySerializer,
    responses={204: '',
               404: '{"detail": "No Food category matches the given query."}'
               },
    tags=['Food_category']
)

food_category_docs = {
    'list': food_category_list,
    'create': food_category_create,
    'retrieve': food_category_retrieve,
    'update': food_category_update,
    'partial_update': food_category_partial_update,
    'destroy': food_category_destroy,
}




restaurant_list = swagger_auto_schema(
    operation_summary='Retrieve all restaurant.',
    operation_description='Endpoint to get the list of all restaurant. Search by name,address ,cuisine name, dish name',
    responses={200: RestaurantSerializer(many=True)},
    tags=['Restaurant']
)

restaurant_create = swagger_auto_schema(
    operation_summary='Create a new restaurant. Each user can create restaurant once.',
    operation_description='Endpoint to create a new restaurant. The name should be unique.',
    request_body=RestaurantSerializer,
    responses={201: RestaurantSerializer()},
    tags=['Restaurant']
)

restaurant_retrieve = swagger_auto_schema(
    manual_parameters=[openapi.Parameter(
        'id', openapi.IN_PATH, description= 'id of the restaurant', type=openapi.TYPE_INTEGER)],
    operation_summary='Retrieve a specific  restaurant by ID.',
    operation_description='Endpoint to get a  restaurant by its unique ID.',
    responses={200: RestaurantSerializer(),
               404: '{"detail": "No  restaurant matches the given query."}'
               },
    tags=['Restaurant']
)

restaurant_update = swagger_auto_schema(
    manual_parameters=[openapi.Parameter(
        'id', openapi.IN_PATH, description='id of the  restaurant', type=openapi.TYPE_INTEGER)],
    operation_summary='Update an existing restaurant only by the owner.',
    operation_description='Endpoint to update a restaurant details by ID.',
    request_body=RestaurantSerializer,
    responses={200: RestaurantSerializer(),
            404: '{"detail": "No  restaurant matches the given query."}'
               },
    tags=['Restaurant']
)

restaurant_partial_update = swagger_auto_schema(
    manual_parameters=[openapi.Parameter(
        'id', openapi.IN_PATH, description='id of the  restaurant', type=openapi.TYPE_INTEGER)],
    operation_summary='Partially update an existing  restaurant only by owner.',
    operation_description='Endpoint to partially update a  restaurant details by ID.',
    request_body=RestaurantSerializer,
    responses={200: RestaurantSerializer(),
               404: '{"detail": "No  restaurant matches the given query."}'
               },
    tags=['Restaurant']
)

restaurant_destroy = swagger_auto_schema(
    manual_parameters=[openapi.Parameter('id', openapi.IN_PATH, description='id of the  restaurant', type=openapi.TYPE_INTEGER)],
    operation_summary='Delete a  restaurant only by admin.',
    operation_description='Endpoint to delete a category by its ID.',
    request_body=RestaurantSerializer,
    responses={204: '',
               404: '{"detail": "No restaurant matches the given query."}'
               },
    tags=['Restaurant']
)

restaurant_docs = {
    'list': restaurant_list,
    'create': restaurant_create,
    'retrieve': restaurant_retrieve,
    'update': restaurant_update,
    'partial_update': restaurant_partial_update,
    'destroy': restaurant_destroy,
}



dish_list = swagger_auto_schema(
    operation_summary='Retrieve all dishes.',
    operation_description=(
        'Endpoint to get the list of all dishes. \n\n'
        '**Search by:** name, restaurant name, category name. \n'
        '**Order by:** is_featured, is_available, unit_price, name. \n'
        '**Filter by:** is_featured, restaurant, category, '
        'is_vegetarian, is_vegan, is_gluten_free, is_available.'
    ),
    responses={200: DishSerializer(many=True)},
    tags=['Dish']
)

dish_create = swagger_auto_schema(
    operation_summary='Create a new dish for your restaurant.',
    operation_description='Endpoint to create a new dish. Only restaurant owners can create dishes.',
    request_body=DishSerializer,
    responses={201: DishSerializer()},
    tags=['Dish']
)

dish_retrieve = swagger_auto_schema(
    manual_parameters=[
        openapi.Parameter(
            'id', openapi.IN_PATH, description='ID of the dish', type=openapi.TYPE_INTEGER
        )
    ],
    operation_summary='Retrieve a specific dish by ID.',
    operation_description='Endpoint to get a dish by its unique ID.',
    responses={
        200: DishSerializer(),
        404: '{"detail": "No dish matches the given query."}'
    },
    tags=['Dish']
)

dish_update = swagger_auto_schema(
    manual_parameters=[
        openapi.Parameter(
            'id', openapi.IN_PATH, description='ID of the dish', type=openapi.TYPE_INTEGER
        )
    ],
    operation_summary='Update an existing dish.',
    operation_description='Endpoint to update dish details. Only the dish creator can update it.',
    request_body=DishSerializer,
    responses={
        200: DishSerializer(),
        404: '{"detail": "No dish matches the given query."}'
    },
    tags=['Dish']
)

dish_partial_update = swagger_auto_schema(
    manual_parameters=[
        openapi.Parameter(
            'id', openapi.IN_PATH, description='ID of the dish', type=openapi.TYPE_INTEGER
        )
    ],
    operation_summary='Partially update a dish.',
    operation_description='Endpoint to partially update dish details. Only the dish creator can update it.',
    request_body=DishSerializer,
    responses={
        200: DishSerializer(),
        404: '{"detail": "No dish matches the given query."}'
    },
    tags=['Dish']
)

dish_destroy = swagger_auto_schema(
    manual_parameters=[
        openapi.Parameter(
            'id', openapi.IN_PATH, description='ID of the dish', type=openapi.TYPE_INTEGER
        )
    ],
    operation_summary='Delete a dish.',
    operation_description='Endpoint to delete a dish by its ID. Only the creator or admin can delete.',
    responses={
        204: '',
        404: '{"detail": "No dish matches the given query."}'
    },
    tags=['Dish']
)

dish_docs = {
    'list': dish_list,
    'create': dish_create,
    'retrieve': dish_retrieve,
    'update': dish_update,
    'partial_update': dish_partial_update,
    'destroy': dish_destroy,
}
