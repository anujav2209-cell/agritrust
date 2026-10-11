from flask import Blueprint, render_template, request
from services.recommendation_service import RecommendationService
from routes.auth import login_required, role_required

recommendations_bp = Blueprint('recommendations', __name__)

@recommendations_bp.route('/recommendations', methods=['GET', 'POST'])
@login_required
@role_required('FARMER')
def recommendations_view():
    recommendations = []
    form_data = {
        'location': 'Nashik, Maharashtra',
        'land_size': '2.5',
        'soil_type': 'Black',
        'season': 'Kharif',
        'water_availability': 'Irrigated'
    }

    if request.method == 'POST':
        form_data['location'] = request.form.get('location', '').strip() or 'Local Region'
        form_data['land_size'] = request.form.get('land_size', '1.0').strip()
        form_data['soil_type'] = request.form.get('soil_type', 'Loamy').strip()
        form_data['season'] = request.form.get('season', 'Kharif').strip()
        form_data['water_availability'] = request.form.get('water_availability', 'Moderate').strip()

        recommendations = RecommendationService.get_crop_recommendations(
            location=form_data['location'],
            land_size_acres=form_data['land_size'],
            soil_type=form_data['soil_type'],
            season=form_data['season'],
            water_availability=form_data['water_availability']
        )
    else:
        # Default initial recommendations
        recommendations = RecommendationService.get_crop_recommendations(
            location=form_data['location'],
            land_size_acres=form_data['land_size'],
            soil_type=form_data['soil_type'],
            season=form_data['season'],
            water_availability=form_data['water_availability']
        )

    return render_template('recommendations.html', recommendations=recommendations, form_data=form_data)
