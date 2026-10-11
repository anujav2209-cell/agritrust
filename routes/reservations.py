from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from extensions import db
from models.reservation import FutureHarvest, Reservation
from models.user import User
from services.marketplace_service import MarketplaceService
from routes.auth import login_required, role_required

reservations_bp = Blueprint('reservations', __name__)

@reservations_bp.route('/reservations')
def reservations_view():
    # Future harvests available for reservation
    future_harvests = FutureHarvest.query.filter(
        FutureHarvest.status.in_(['Open for Reservation', 'Partially Reserved'])
    ).order_by(FutureHarvest.expected_harvest_date.asc()).all()

    my_reservations = []
    farmer_listings = []

    if 'user_id' in session:
        user_id = session['user_id']
        role = session.get('role')
        if role == 'BUYER':
            my_reservations = Reservation.query.filter_by(user_id=user_id).order_by(Reservation.created_at.desc()).all()
        elif role == 'FARMER':
            farmer_listings = FutureHarvest.query.filter_by(farmer_id=user_id).all()
            # Also get reservations made on this farmer's harvests
            my_reservations = Reservation.query.filter_by(farmer_id=user_id).order_by(Reservation.created_at.desc()).all()

    return render_template(
        'reservations.html',
        future_harvests=future_harvests,
        my_reservations=my_reservations,
        farmer_listings=farmer_listings
    )

@reservations_bp.route('/future-harvests/create', methods=['POST'])
@login_required
@role_required('FARMER', 'ADMIN')
def create_future_harvest():
    farmer_id = session['user_id']
    crop_name = request.form.get('crop_name', '').strip()
    harvest_date_str = request.form.get('expected_harvest_date')
    quantity_str = request.form.get('expected_quantity')
    target_price_str = request.form.get('target_price_per_kg')
    location = request.form.get('location', '').strip()
    notes = request.form.get('notes', '').strip()

    if not crop_name or not harvest_date_str or not quantity_str or not target_price_str or not location:
        flash('All fields are required to list an expected harvest.', 'danger')
        return redirect(url_for('reservations.reservations_view'))

    try:
        h_date = datetime.strptime(harvest_date_str, '%Y-%m-%d').date()
        qty = float(quantity_str)
        price = float(target_price_str)
        if qty <= 0 or price <= 0:
            flash('Expected quantity and target price must be greater than zero.', 'danger')
            return redirect(url_for('reservations.reservations_view'))
    except (ValueError, TypeError):
        flash('Invalid numeric or date values.', 'danger')
        return redirect(url_for('reservations.reservations_view'))

    new_fh = FutureHarvest(
        farmer_id=farmer_id,
        crop_name=crop_name,
        expected_harvest_date=h_date,
        expected_quantity=qty,
        reserved_quantity=0.0,
        target_price_per_kg=price,
        location=location,
        status='Open for Reservation',
        notes=notes
    )
    db.session.add(new_fh)
    db.session.commit()

    flash(f"Upcoming harvest for '{new_fh.crop_name}' is now open for buyer reservations!", 'success')
    return redirect(url_for('reservations.reservations_view'))

@reservations_bp.route('/reservations/book', methods=['POST'])
@login_required
@role_required('BUYER', 'ADMIN')
def book_reservation():
    buyer_id = session['user_id']
    fh_id = request.form.get('future_harvest_id')
    reserved_qty = request.form.get('reserved_quantity')
    contact_phone = request.form.get('contact_phone', '').strip()
    delivery_address = request.form.get('delivery_address', '').strip()
    notes = request.form.get('notes', '').strip()

    if not fh_id or not reserved_qty or not contact_phone:
        flash('Please fill in reservation quantity and contact information.', 'danger')
        return redirect(url_for('reservations.reservations_view'))

    success, msg, res = MarketplaceService.reserve_future_harvest(
        buyer_id=buyer_id,
        future_harvest_id=int(fh_id),
        reserved_qty=reserved_qty,
        phone=contact_phone,
        address=delivery_address,
        notes=notes
    )

    if success:
        flash(msg, 'success')
    else:
        flash(msg, 'danger')

    return redirect(url_for('reservations.reservations_view'))
