import os
from flask import Flask, jsonify
from flask_cors import CORS
from config import Config
from models import db, User, AssessmentResult, RoadmapProgress
from routes.auth_routes import auth_bp
from routes.career_routes import career_bp
from routes.roadmap_routes import roadmap_bp
from routes.resume_routes import resume_bp
from routes.analytics_routes import analytics_bp

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Enable CORS
    CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)

    # Initialize Database
    db.init_app(app)

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(career_bp)
    app.register_blueprint(roadmap_bp)
    app.register_blueprint(resume_bp)
    app.register_blueprint(analytics_bp)

    @app.route('/api/health', methods=['GET'])
    def health_check():
        return jsonify({
            'status': 'healthy',
            'platform': 'Career Nova AI',
            'version': '1.0.0',
            'database': 'connected'
        }), 200

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({'error': 'Resource not found'}), 404

    @app.errorhandler(500)
    def internal_error(e):
        return jsonify({'error': 'Internal server error'}), 500

    # Ensure tables exist and seed demo user on start
    with app.app_context():
        db.create_all()
        _seed_demo_user()

    return app

def _seed_demo_user():
    demo_email = 'demo@careernova.ai'
    if not User.query.filter_by(email=demo_email).first():
        demo_user = User(
            name='Alex Rivera',
            email=demo_email,
            education_level='Undergraduate',
            degree_specialization='B.Tech in Computer Science',
            current_year='3rd Year',
            technical_skills='Python, SQL, Pandas, NumPy, Git & Version Control, REST APIs, HTML5 & CSS3',
            programming_languages='Python, JavaScript, SQL',
            interests='Artificial Intelligence, Data Science, Web Applications',
            certifications='Python for Data Science, AWS Cloud Foundations',
            projects='E-Commerce Customer Analytics Dashboard; Smart Task Planner API',
            preferred_role='Machine Learning Engineer',
            career_goals='Master modern ML engineering pipelines and crack an AI internship',
            experience_level='Intermediate'
        )
        demo_user.set_password('Password123!')
        db.session.add(demo_user)
        db.session.commit()
        print("Demo user seeded: demo@careernova.ai / Password123!")

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app = create_app()
    print(f"Career Nova AI Backend running on http://127.0.0.1:{port}")
    app.run(host='0.0.0.0', port=port, debug=True)
