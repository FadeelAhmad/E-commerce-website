from django.shortcuts import render, get_object_or_404, redirect
from django.db import transaction
from django.contrib import messages
from .models import Product, Order, Category, Review


def product_list(request):
    products = Product.objects.filter(stock__gt=0).select_related('category')
    categories = Category.objects.all()

    # Category filter
    category_slug = request.GET.get('category')
    selected_category = None
    if category_slug:
        selected_category = get_object_or_404(Category, name__iexact=category_slug)
        products = products.filter(category=selected_category)

    # Search filter
    query = request.GET.get('q', '').strip()
    if query:
        products = products.filter(name__icontains=query) | products.filter(description__icontains=query)

    return render(request, 'customer_portal/product_list.html', {
        'products': products,
        'categories': categories,
        'selected_category': selected_category,
        'query': query,
    })


def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    reviews = product.reviews.order_by('-created_at')

    if request.method == 'POST':
        author_name = request.POST.get('author_name', 'Anonymous').strip() or 'Anonymous'
        rating = int(request.POST.get('rating', 5))
        comment = request.POST.get('comment', '').strip()
        Review.objects.create(product=product, author_name=author_name, rating=rating, comment=comment)
        messages.success(request, 'Your review has been submitted!')
        return redirect('product_detail', product_id=product.id)

    return render(request, 'customer_portal/product_detail.html', {
        'product': product,
        'reviews': reviews,
    })


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
        order.status = 'COMPLETED'
        order.save()
        messages.success(request, 'Payment successful! Your order has been placed.')
        return redirect('product_list')

    return render(request, 'customer_portal/payment.html', {
        'order': order,
        'total': order.product.price * order.quantity,
    })
