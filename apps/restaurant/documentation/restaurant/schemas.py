from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from apps.restaurant.serializers import CuisineSerializer


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
    responses={200: CuisineSerializer(many=True)},
    tags=['Food_category']
)

food_category_create = swagger_auto_schema(
    operation_summary='Create a new Food category.',
    operation_description='Endpoint to create a new Food category only by admin. The name should be capitalized.',
    request_body=CuisineSerializer,
    responses={201: CuisineSerializer()},
    tags=['Food_category']
)

food_category_retrieve = swagger_auto_schema(
    manual_parameters=[openapi.Parameter(
        'id', openapi.IN_PATH, description='id of the Food category', type=openapi.TYPE_INTEGER)],
    operation_summary='Retrieve a specific Food category by ID.',
    operation_description='Endpoint to get a Food category by its unique ID.',
    responses={200: CuisineSerializer(),
               404: '{"detail": "No Food category matches the given query."}'
               },
    tags=['Food_category']
)

food_category_update = swagger_auto_schema(
    manual_parameters=[openapi.Parameter(
        'id', openapi.IN_PATH, description='id of the Food category', type=openapi.TYPE_INTEGER)],
    operation_summary='Update an existing category only by admin.',
    operation_description='Endpoint to update a Food category details by ID.',
    request_body=CuisineSerializer,
    responses={200: CuisineSerializer(),
            404: '{"detail": "No Food category matches the given query."}'
               },
    tags=['Food_category']
)

food_category_partial_update = swagger_auto_schema(
    manual_parameters=[openapi.Parameter(
        'id', openapi.IN_PATH, description='id of the Food category', type=openapi.TYPE_INTEGER)],
    operation_summary='Partially update an existing category only by admin.',
    operation_description='Endpoint to partially update a Food category details by ID.',
    request_body=CuisineSerializer,
    responses={200: CuisineSerializer(),
               404: '{"detail": "No Food category matches the given query."}'
               },
    tags=['Food_category']
)

food_category_destroy = swagger_auto_schema(
    manual_parameters=[openapi.Parameter('id', openapi.IN_PATH, description='id of the cuisine', type=openapi.TYPE_INTEGER)],
    operation_summary='Delete a category only by admin.',
    operation_description='Endpoint to delete a category by its ID.',
    request_body=CuisineSerializer,
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
