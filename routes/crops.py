from flask import Blueprint, render_template, request, redirect, url_for, flash, session, abort
from extensions import db
from models.crop import Crop
from models.farm import Farm
from routes.auth import login_required, role_required
from datetime import datetime

crops_bp = Blueprint('crops', __name__)

@crops_bp.route('/crops')
@login_required
@role_required('FARMER')
def crops_view():
    user_id = session['user_id']
    crops = Crop.query.filter_by(user_id=user_id).order_by(Crop.created_at.desc()).all()
    farms = Farm.query.filter_by(user_id=user_id).all()
    return render_template('crops.html', crops=crops, farms=farms)

@crops_bp.route('/crops/add', methods=['POST'])
@login_required
@role_required('FARMER')
def add_crop():
    user_id = session['user_id']
    crop_name = request.form.get('crop_name', '').strip()
    farm_id = request.form.get('farm_id')
    planting_date_str = request.form.get('planting_date')
    growth_stage = request.form.get('growth_stage', 'Vegetative')
    growth_percentage = request.form.get('growth_percentage', 10)
    harvest_date_str = request.form.get('expected_harvest_date')
    expected_yield = request.form.get('expected_yield', 0)
    production_cost = request.form.get('production_cost', 0)
    expected_revenue = request.form.get('expected_revenue', 0)
    health_status = request.form.get('health_status', 'Healthy')

    if not crop_name or not planting_date_str or not harvest_date_str:
        flash('Crop name, planting date, and harvest date are required.', 'danger')
        return redirect(url_for('crops.crops_view'))

    try:
        p_date = datetime.strptime(planting_date_str, '%Y-%m-%d').date()
        h_date = datetime.strptime(harvest_date_str, '%Y-%m-%d').date()
        exp_yield = float(expected_yield)
        prod_cost = float(production_cost) if production_cost else 0.0
        exp_rev = float(expected_revenue) if expected_revenue else 0.0
        pct = int(growth_percentage)
    except (ValueError, TypeError):
        flash('Invalid date or numeric values provided.', 'danger')
        return redirect(url_for('crops.crops_view'))

    new_crop = Crop(
        user_id=user_id,
        farm_id=int(farm_id) if farm_id else None,
        crop_name=crop_name,
        planting_date=p_date,
        growth_stage=growth_stage,
        growth_percentage=max(0, min(100, pct)),
        expected_harvest_date=h_date,
        expected_yield=exp_yield,
        production_cost=prod_cost,
        expected_revenue=exp_rev,
        health_status=health_status
    )
    db.session.add(new_crop)
    db.session.commit()
    flash(f"Crop '{new_crop.crop_name}' added to monitoring schedule.", 'success')
    return redirect(url_for('crops.crops_view'))

@crops_bp.route('/crops/<int:id>/edit', methods=['POST'])
@login_required
@role_required('FARMER')
def edit_crop(id):
    crop = Crop.query.get_or_404(id)
    if crop.user_id != session['user_id']:
        abort(403)

    crop.crop_name = request.form.get('crop_name', crop.crop_name).strip()
    crop.growth_stage = request.form.get('growth_stage', crop.growth_stage)
    crop.health_status = request.form.get('health_status', crop.health_status)

    try:
        crop.growth_percentage = max(0, min(100, int(request.form.get('growth_percentage', crop.growth_percentage))))
        crop.expected_yield = float(request.form.get('expected_yield', crop.expected_yield))
        crop.production_cost = float(request.form.get('production_cost', crop.production_cost))
        crop.expected_revenue = float(request.form.get('expected_revenue', crop.expected_revenue))
        if request.form.get('expected_harvest_date'):
            crop.expected_harvest_date = datetime.strptime(request.form.get('expected_harvest_date'), '%Y-%m-%d').date()
    except (ValueError, TypeError):
        pass

    db.session.commit()
    flash(f"Crop '{crop.crop_name}' details updated.", 'success')
    return redirect(url_for('crops.crops_view'))

@crops_bp.route('/crops/<int:id>/delete', methods=['POST'])
@login_required
@role_required('FARMER')
def delete_crop(id):
    crop = Crop.query.get_or_404(id)
    if crop.user_id != session['user_id']:
        abort(403)

    name = crop.crop_name
    db.session.delete(crop)
    db.session.commit()
    flash(f"Crop record '{name}' deleted.", 'info')
    return redirect(url_for('crops.crops_view'))
