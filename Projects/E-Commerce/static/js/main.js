// Wait for the DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Format price in Indian currency format
    function formatIndianCurrency(price) {
        if (!price) return "₹0.00";
        
        // Convert to number and fix to 2 decimal places
        price = parseFloat(price).toFixed(2);
        
        // Split into integer and decimal parts
        let [intPart, decimalPart] = price.split('.');
        
        // Format integer part with Indian thousands separators
        let lastThree = intPart.substring(intPart.length - 3);
        let otherNumbers = intPart.substring(0, intPart.length - 3);
        if (otherNumbers !== '') {
            lastThree = ',' + lastThree;
        }
        let formattedIntPart = otherNumbers.replace(/\B(?=(\d{2})+(?!\d))/g, ",") + lastThree;
        
        // Return formatted price with rupee symbol
        return `₹${formattedIntPart}.${decimalPart}`;
    }

    // Add to cart functionality
    const addToCartButtons = document.querySelectorAll('.add-to-cart-btn');
    addToCartButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const productId = this.getAttribute('data-product-id');
            const quantityInput = document.querySelector(`#quantity-${productId}`);
            const quantity = quantityInput ? parseInt(quantityInput.value) : 1;
            
            // Send AJAX request to add item to cart
            fetch(`/api/orders/cart/add/${productId}/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({ quantity: quantity })
            })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    showAlert('danger', data.error);
                } else {
                    showAlert('success', 'Product added to cart!');
                    // Update cart count if needed
                    updateCartCount();
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showAlert('danger', 'An error occurred. Please try again.');
            });
        });
    });

    // Remove from cart functionality
    const removeFromCartButtons = document.querySelectorAll('.remove-from-cart-btn');
    removeFromCartButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const productId = this.getAttribute('data-product-id');
            
            // Send AJAX request to remove item from cart
            fetch(`/api/orders/cart/remove/${productId}/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    showAlert('danger', data.error);
                } else {
                    // Remove the cart item from the DOM
                    const cartItem = document.querySelector(`#cart-item-${productId}`);
                    if (cartItem) {
                        cartItem.remove();
                    }
                    
                    // Update cart total
                    updateCartTotal();
                    
                    // Update cart count
                    updateCartCount();
                    
                    showAlert('success', 'Product removed from cart!');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showAlert('danger', 'An error occurred. Please try again.');
            });
        });
    });

    // Function to get CSRF token from cookies
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    // Function to show alert messages
    function showAlert(type, message) {
        const alertContainer = document.querySelector('.container');
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
        alertDiv.role = 'alert';
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
        
        // Insert alert at the top of the container
        alertContainer.insertBefore(alertDiv, alertContainer.firstChild);
        
        // Auto-dismiss after 3 seconds
        setTimeout(() => {
            alertDiv.classList.remove('show');
            setTimeout(() => {
                alertDiv.remove();
            }, 150);
        }, 3000);
    }

    // Function to update cart count
    function updateCartCount() {
        fetch('/api/orders/cart/')
            .then(response => response.json())
            .then(data => {
                const cartCount = data.items.length;
                const cartCountElement = document.querySelector('.cart-count');
                if (cartCountElement) {
                    cartCountElement.textContent = cartCount;
                    cartCountElement.style.display = cartCount > 0 ? 'inline-block' : 'none';
                }
            })
            .catch(error => console.error('Error:', error));
    }

    // Function to update cart total
    function updateCartTotal() {
        fetch('/api/orders/cart/')
            .then(response => response.json())
            .then(data => {
                const cartTotalElement = document.querySelector('.cart-total');
                if (cartTotalElement) {
                    cartTotalElement.textContent = formatIndianCurrency(data.total);
                }
                
                // Check if cart is empty
                if (data.items.length === 0) {
                    const cartItemsContainer = document.querySelector('.cart-items');
                    if (cartItemsContainer) {
                        cartItemsContainer.innerHTML = '<p class="text-center">Your cart is empty.</p>';
                    }
                    
                    const checkoutButton = document.querySelector('.checkout-btn');
                    if (checkoutButton) {
                        checkoutButton.disabled = true;
                    }
                }
            })
            .catch(error => console.error('Error:', error));
    }

    // Initialize cart count on page load
    updateCartCount();
}); 