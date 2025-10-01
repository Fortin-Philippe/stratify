from flask import Blueprint, render_template
import bd

bp_coach = Blueprint('coach', __name__)

@bp_coach.route('/coachs')
def liste_coachs():
    """Affiche la liste de tous les coachs disponibles"""
    coachs = bd.obtenir_coachs()
    
    return render_template('coachs.jinja', coachs=coachs)