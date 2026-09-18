from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Product, Order
from django.db import transaction
from django.contrib import messages

def product_list(request):
    products = Product.objects.filter(stock__gt=0)
    return render(request, 'customer_portal/product_list.html', {'products': products})

def place_order(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        
        with transaction.atomic():
            product.refresh_from_db()
            if product.stock >= quantity:
                product.stock -= quantity
                product.save()
                
                customer = request.user if request.user.is_authenticated else None
                order = Order.objects.create(
                    product=product,
                    customer=customer,
                    quantity=quantity
                )
                return redirect('process_payment', order_id=order.id)
            else:
                messages.error(request, 'Not enough stock available.')
                
    return render(request, 'customer_portal/place_order.html', {'product': product})

def process_payment(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    
    if request.method == 'POST':
        # Simulate payment processing
        order.status = 'COMPLETED'
        order.save()
        messages.success(request, 'Payment successful! Your order has been placed.')
        return redirect('product_list')
        
    return render(request, 'customer_portal/payment.html', {'order': order, 'total': order.product.price * order.quantity})


