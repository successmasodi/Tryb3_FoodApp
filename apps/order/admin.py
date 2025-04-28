from django.contrib import admin
from .models import PaymentMethod, DeliveryMethod, Cart, CartItem, PaymentRecord, Order, OrderItem


admin.site.register(PaymentMethod)
admin.site.register(DeliveryMethod)
admin.site.register(Cart)
admin.site.register(CartItem)


@admin.register(PaymentRecord)
class PaymentRecordAdmin(admin.ModelAdmin):
    list_display = ('truncated_tx_ref', 'cart', 'payment_method')
    list_filter = ('payment_method',)
    search_fields = ('tx_ref', 'cart__id')

    def truncated_tx_ref(self, obj):
        return f"{obj.tx_ref[:15]}..." if obj.tx_ref else None


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    fields = ('dish_name', 'unit_price', 'quantity')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'customer', 'status',
                    'payment_status', 'total', 'created_at')
    list_filter = ('status', 'payment_status', 'created_at')
    search_fields = ('order_number', 'customer__email')
    readonly_fields = ('order_number', 'subtotal',
                       'total', 'created_at', 'updated_at')
    fieldsets = (
        (None, {'fields': ('order_number', 'customer', 'status', 'payment_status')
                }),
        ('Financials', {
            'fields': ('subtotal', 'delivery_fee', 'tax', 'total')
        }),
        ('Delivery', {
            'fields': ('delivery_address', 'special_instructions', 'delivered_at')
        }),
    )
    inlines = [OrderItemInline]


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'dish_name', 'unit_price',
                    'quantity', 'sub_total')
    list_select_related = ('order',)
    readonly_fields = ('unit_price', 'quantity')
    search_fields = ('order__order_number', 'dish_name')

    @admin.display(ordering='unit_price')
    def sub_total(self, obj):
        return obj.sub_total
