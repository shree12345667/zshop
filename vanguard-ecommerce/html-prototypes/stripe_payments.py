from flask import Blueprint, request, jsonify
import stripe

# Create a Blueprint for stripe routes
stripe_payments_bp = Blueprint('stripe_payments_bp', __name__)

# YOUR SECRET KEY (Never put this in HTML)
stripe.api_key = "sk_test_51TdUJ6812isbxieOWr0a1BkVDViRb3uf8uIGFOyDYJAeO3YozOrRixVAj4Cvqflcx3b1c7zqVCcVshXxJ8QOlzcv00jc51EuNv"

@stripe_payments_bp.route('/api/create-payment-intent', methods=['POST'])
def create_payment():
    try:
        data = request.json
        
        # The frontend sends the total as a string like "$120.50". 
        # We must convert it to cents (12050) for Stripe.
        amount_str = str(data.get('amount', '0')).replace('$', '').replace(',', '')
        amount_cents = int(float(amount_str) * 100)
        
        # STRIPE BUG FIX: Minimum charge is 50 cents ($0.50).
        # If you are testing with a $0.01 item, this automatically bumps it to 50 cents 
        # so the Stripe API doesn't crash and reject your payment.
        if amount_cents < 50:
            print(f"Cart amount is only {amount_cents} cents. Bumping to minimum 50 cents for Stripe.")
            amount_cents = 50

        # Create the PaymentIntent. This tells Stripe "Get ready to charge this amount"
        intent = stripe.PaymentIntent.create(
            amount=amount_cents,
            currency='usd',
            payment_method_types=['card'], # Accept credit/debit cards
        )
        
        # Return the secure "client_secret" back to the HTML file to complete the charge
        return jsonify({
            'clientSecret': intent['client_secret']
        })
        
    except Exception as e:
        print(f"Stripe Payment Error: {str(e)}")
        return jsonify(error=str(e)), 403
