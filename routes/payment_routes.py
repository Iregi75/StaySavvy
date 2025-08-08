from flask import Blueprint, request, jsonify
from services.supabase_client import SupabaseClient

payment_bp = Blueprint('payments', __name__)
supabase = SupabaseClient().get_client()

@payment_bp.route('/process', methods=['POST'])
def process_payment():
    try:
        data = request.json
        booking_id = data['booking_id']
        payment_method = data['payment_method']
        amount = data['amount']
        
        # In a real app, you would integrate with a payment processor here
        # For demo, we'll just simulate a successful payment
        
        # Update booking status
        supabase.table('bookings').update({
            'status': 'confirmed',
            'payment_status': 'paid',
            'payment_date': 'now()'
        }).eq('id', booking_id).execute()
        
        # Create payment record
        payment = supabase.table('payments').insert({
            'booking_id': booking_id,
            'amount': amount,
            'method': payment_method,
            'status': 'completed'
        }).execute()
        
        return jsonify({
            'success': True,
            'payment_id': payment.data[0]['id'],
            'booking_status': 'confirmed'
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400