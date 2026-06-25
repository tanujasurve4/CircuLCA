import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
import json
import base64
from io import BytesIO
import time
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import plotly.io as pio
st.set_page_config(
    page_title="CircuLCA - AI-Driven Life Cycle Assessment",
    page_icon="♻️",
    layout="wide",
    initial_sidebar_state="expanded"
)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 30px;
        border-radius: 20px;
        color: white;
        text-align: center;
        margin-bottom: 30px;
        position: relative;
        overflow: hidden;
        animation: shimmer 3s ease-in-out infinite;
    }
    @keyframes shimmer {
        0% { box-shadow: 0 0 20px rgba(102, 126, 234, 0.3); }
        50% { box-shadow: 0 0 40px rgba(102, 126, 234, 0.6); }
        100% { box-shadow: 0 0 20px rgba(102, 126, 234, 0.3); }
    }
    .metric-card {
        background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
        padding: 25px;
        border-radius: 20px;
        text-align: center;
        margin: 15px 0;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
        border: 2px solid transparent;
        color: white;
    }
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 48px rgba(0,0,0,0.15);
        border: 2px solid #667eea;
    }
    .metric-card h3, .metric-card h4 {
        color: white !important;
        margin: 0;
    }
    .metric-card p {
        color: #ecf0f1 !important;
        margin: 5px 0 0 0;
    }
    .circular-progress {
        width: 200px;
        height: 200px;
        border-radius: 50%;
        background: conic-gradient(from 0deg, #48bb78 0deg, #48bb78 calc(var(--progress) * 3.6deg), #e2e8f0 calc(var(--progress) * 3.6deg), #e2e8f0 360deg);
        display: flex;
        align-items: center;
        justify-content: center;
        position: relative;
        margin: 20px auto;
    }
    .circular-progress::before {
        content: '';
        width: 150px;
        height: 150px;
        border-radius: 50%;
        background: white;
        position: absolute;
    }
    .circular-progress-text {
        position: relative;
        z-index: 1;
        font-size: 24px;
        font-weight: bold;
        color: #2d3748;
    }
    .tab-content {
        padding: 20px;
        background: rgba(255,255,255,0.05);
        border-radius: 15px;
        margin-top: 10px;
    }
    .comparison-card {
        background: linear-gradient(135deg, #2c3e50, #34495e);
        padding: 20px;
        border-radius: 15px;
        margin: 10px 0;
        border-left: 4px solid #667eea;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        color: white;
    }
    .comparison-card h5 {
        color: #3498db;
        margin-bottom: 10px;
    }
    .optimization-card {
        background: linear-gradient(135deg, #48bb78, #38a169);
        color: white;
        padding: 25px;
        border-radius: 20px;
        text-align: center;
        margin: 25px 0;
        box-shadow: 0 8px 25px rgba(72, 187, 120, 0.3);
    }
    div[data-testid="metric-container"] {
        background: transparent;
        border: none;
        box-shadow: none;
    }
    div[data-testid="metric-container"] > div {
        background: transparent;
        color: white;
    }
    div[data-testid="metric-container"] label {
        color: #ecf0f1 !important;
    }
    div[data-testid="metric-container"] [data-testid="metric-value"] {
        color: #ffffff !important;
    }
    div[data-testid="metric-container"] [data-testid="metric-delta"] {
        color: #bdc3c7 !important;
    }
    .download-buttons {
        display: flex;
        gap: 10px;
        margin: 20px 0;
        justify-content: center;
    }
    .download-btn {
        background: #000000;
        color: white;
        padding: 12px 24px;
        border: 2px solid #333333;
        border-radius: 10px;
        text-decoration: none;
        display: inline-block;
        cursor: pointer;
        transition: all 0.3s ease;
        font-weight: 600;
    }
    .download-btn:hover {
        background: #333333;
        border-color: #555555;
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.4);
        color: white;
    }
    </style>
""", unsafe_allow_html=True)
METAL_DATA = {
    'Aluminum': {
        'primary_carbon': 11.5, 'secondary_carbon': 0.8, 'energy_intensity': 45.6,
        'water_usage': 12.3, 'recycling_rate': 0.85, 'density': 2.7, 'melting_point': 660,
        'market_price': 162375, 'abundance': 8.1, 'extraction_complexity': 3.2
    },
    'Copper': {
        'primary_carbon': 4.2, 'secondary_carbon': 0.5, 'energy_intensity': 28.4,
        'water_usage': 8.7, 'recycling_rate': 0.90, 'density': 8.96, 'melting_point': 1085,
        'market_price': 707500, 'abundance': 0.006, 'extraction_complexity': 4.1
    },
    'Steel': {
        'primary_carbon': 2.3, 'secondary_carbon': 0.4, 'energy_intensity': 20.1,
        'water_usage': 15.2, 'recycling_rate': 0.88, 'density': 7.85, 'melting_point': 1538,
        'market_price': 54125, 'abundance': 5.6, 'extraction_complexity': 2.8
    },
    'Lithium': {
        'primary_carbon': 15.8, 'secondary_carbon': 2.1, 'energy_intensity': 67.3,
        'water_usage': 2100, 'recycling_rate': 0.15, 'density': 0.534, 'melting_point': 180,
        'market_price': 2330000, 'abundance': 0.002, 'extraction_complexity': 5.8
    },
    'Rare_Earth': {
        'primary_carbon': 45.2, 'secondary_carbon': 5.3, 'energy_intensity': 120.4,
        'water_usage': 8.9, 'recycling_rate': 0.05, 'density': 6.8, 'melting_point': 1200,
        'market_price': 7072500, 'abundance': 0.00016, 'extraction_complexity': 7.2
    }
}
ENERGY_MULTIPLIERS = {
    'Renewable': {'carbon': 0.05, 'cost': 0.08, 'availability': 0.7},
    'Nuclear': {'carbon': 0.12, 'cost': 0.11, 'availability': 0.9},
    'Grid_Mix': {'carbon': 0.45, 'cost': 0.14, 'availability': 0.95},
    'Fossil': {'carbon': 0.82, 'cost': 0.12, 'availability': 0.98}
}
TRANSPORT_DATA = {
    'Truck': {'carbon_per_km': 0.12, 'cost_per_km': 100, 'capacity': 25},
    'Rail': {'carbon_per_km': 0.04, 'cost_per_km': 42, 'capacity': 1000},
    'Ship': {'carbon_per_km': 0.02, 'cost_per_km': 25, 'capacity': 50000},
    'Multimodal': {'carbon_per_km': 0.06, 'cost_per_km': 67, 'capacity': 500}
}
class CircularityPredictor:
    def __init__(self):
        self.carbon_model = RandomForestRegressor(n_estimators=50, random_state=42)
        self.energy_model = RandomForestRegressor(n_estimators=50, random_state=42)
        self.circularity_model = RandomForestRegressor(n_estimators=50, random_state=42)
        self.scaler = StandardScaler()
        self._train_models()
    def _train_models(self):
        n_samples = 500
        np.random.seed(42)
        X = np.random.rand(n_samples, 6)
        X[:, 0] = np.random.uniform(0.5, 10.0, n_samples)
        X[:, 1] = np.random.uniform(70, 99, n_samples)
        X[:, 2] = np.random.uniform(0.05, 0.82, n_samples)
        X[:, 3] = np.random.uniform(30, 95, n_samples)
        X[:, 4] = np.random.uniform(0.05, 0.95, n_samples)
        X[:, 5] = np.random.uniform(50, 95, n_samples)
        y_carbon = 15 - X[:, 0] * 0.5 + X[:, 2] * 20 - X[:, 4] * 10 + np.random.normal(0, 1, n_samples)
        y_energy = 50 - X[:, 0] * 2 + X[:, 2] * 30 - X[:, 3] * 0.2 + np.random.normal(0, 3, n_samples)
        y_circularity = 30 + X[:, 1] * 0.4 + X[:, 4] * 50 + X[:, 5] * 0.3 + np.random.normal(0, 5, n_samples)
        self.scaler.fit(X)
        X_scaled = self.scaler.transform(X)
        self.carbon_model.fit(X_scaled, y_carbon)
        self.energy_model.fit(X_scaled, y_energy)
        self.circularity_model.fit(X_scaled, y_circularity)
    def predict_parameters(self, inputs):
        features = [
            inputs.get('ore_grade', 2.5),
            inputs.get('recovery_rate', 85),
            ENERGY_MULTIPLIERS[inputs.get('energy_source', 'Grid_Mix')]['carbon'],
            inputs.get('automation_level', 60),
            METAL_DATA[inputs['metal_type']]['recycling_rate'],
            inputs.get('water_recycling', 70)
        ]
        X_input = np.array([features])
        X_scaled = self.scaler.transform(X_input)
        predicted_carbon = max(0.1, self.carbon_model.predict(X_scaled)[0] * (inputs.get('ore_grade', 2.5) / 2.5) * (inputs.get('automation_level', 60) / 100))
        predicted_energy = max(5, self.energy_model.predict(X_scaled)[0] * (inputs.get('recovery_rate', 85) / 85) * ENERGY_MULTIPLIERS[inputs.get('energy_source', 'Grid_Mix')]['carbon'])
        predicted_circularity = max(0, min(100, self.circularity_model.predict(X_scaled)[0] + inputs.get('water_recycling', 70) * 0.2 + inputs.get('automation_level', 60) * 0.15))
        return {
            'predicted_carbon': predicted_carbon,
            'predicted_energy': predicted_energy,
            'predicted_circularity': predicted_circularity,
            'recycled_content_potential': min(95, inputs.get('automation_level', 60) + METAL_DATA[inputs['metal_type']]['recycling_rate'] * 20),
            'reuse_potential': METAL_DATA[inputs['metal_type']]['recycling_rate'] * 80 + inputs.get('automation_level', 60) * 0.1,
            'extended_life_factor': 1.2 if inputs.get('automation_level', 60) > 70 else 1.0 + inputs.get('water_recycling', 70) * 0.002
        }
def create_pdf_report(data, filename):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        alignment=1
    )
    story.append(Paragraph("CircuLCA - Life Cycle Assessment Report", title_style))
    story.append(Spacer(1, 20))
    header_style = ParagraphStyle('CustomHeader', parent=styles['Heading2'], fontSize=16, spaceAfter=12)
    story.append(Paragraph(f"Analysis Date: {data['analysis_date']}", styles['Normal']))
    story.append(Spacer(1, 20))
    story.append(Paragraph("Input Parameters", header_style))
    input_data = []
    for key, value in data['inputs'].items():
        input_data.append([str(key).replace('_', ' ').title(), str(value)])
    input_table = Table(input_data)
    input_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(input_table)
    story.append(Spacer(1, 20))
    story.append(Paragraph("Environmental Results", header_style))
    env_data = []
    for key, value in data['environmental_results'].items():
        env_data.append([str(key).replace('_', ' ').title(), f"{value:.2f}"])
    env_table = Table(env_data)
    env_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.green),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.lightgreen),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(env_table)
    story.append(Spacer(1, 20))
    story.append(Paragraph("Economic Results", header_style))
    econ_data = []
    for key, value in data['economic_results'].items():
        if 'cost' in key.lower() or 'revenue' in key.lower() or ('profit' in key.lower() and 'margin' not in key.lower()):
            econ_data.append([str(key).replace('_', ' ').title(), f"₹{value:,.0f}"])
        else:
            econ_data.append([str(key).replace('_', ' ').title(), f"{value:.2f}%"])
    econ_table = Table(econ_data)
    econ_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.blue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.lightblue),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(econ_table)
    story.append(Spacer(1, 20))
    story.append(Paragraph("AI Predictions", header_style))
    pred_data = []
    for key, value in data['ai_predictions'].items():
        pred_data.append([str(key).replace('_', ' ').title(), f"{value:.2f}"])
    pred_table = Table(pred_data)
    pred_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.purple),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.lavender),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(pred_table)
    story.append(Spacer(1, 20))
    story.append(Paragraph("Recommendations", header_style))
    for i, rec in enumerate(data['recommendations'], 1):
        clean_rec = rec.replace('**', '').replace('₹', 'Rs.')
        story.append(Paragraph(f"{i}. {clean_rec}", styles['Normal']))
        story.append(Spacer(1, 8))
    story.append(Spacer(1, 20))
    story.append(Paragraph("Summary", header_style))
    summary_data = []
    for key, value in data['summary'].items():
        summary_data.append([str(key).replace('_', ' ').title(), str(value)])
    summary_table = Table(summary_data)
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkred),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.pink),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(summary_table)
    doc.build(story)
    pdf = buffer.getvalue()
    buffer.close()
    return pdf
def create_pdf_download_link(data, filename):
    pdf = create_pdf_report(data, filename)
    b64 = base64.b64encode(pdf).decode()
    href = f'<a href="data:application/pdf;base64,{b64}" download="{filename}" class="download-btn">Download PDF Report</a>'
    return href
def create_json_download_link(data, filename):
    json_string = json.dumps(data, indent=2)
    b64 = base64.b64encode(json_string.encode()).decode()
    href = f'<a href="data:file/json;base64,{b64}" download="{filename}" class="download-btn">Download JSON Data</a>'
    return href
def create_report_data(inputs, results, economic_results, predictions):
    report = {
        'analysis_date': time.strftime('%Y-%m-%d %H:%M:%S'),
        'inputs': inputs,
        'environmental_results': results,
        'economic_results': economic_results,
        'ai_predictions': predictions,
        'recommendations': generate_recommendations(results, predictions, economic_results),
        'summary': {
            'carbon_footprint_rating': 'Excellent' if results['carbon_footprint'] < 3 else 'Good' if results['carbon_footprint'] < 8 else 'Needs Improvement',
            'circularity_rating': 'Excellent' if results['circularity_score'] > 80 else 'Good' if results['circularity_score'] > 60 else 'Needs Improvement',
            'economic_rating': 'Excellent' if economic_results['profit_margin'] > 20 else 'Good' if economic_results['profit_margin'] > 10 else 'Needs Improvement'
        }
    }
    return report
def create_circular_economy_diagram(inputs, results):
    recycling_rate = METAL_DATA[inputs['metal_type']]['recycling_rate']
    automation_factor = inputs.get('automation_level', 60) / 100
    water_recycling_factor = inputs.get('water_recycling', 70) / 100
    ore_grade_factor = inputs.get('ore_grade', 2.5) / 2.5
    categories = ['Extraction', 'Production', 'Use', 'Collection', 'Processing', 'Recovery']
    base_values = [100, 85, 80, 70, recycling_rate * 100, recycling_rate * 95]
    current_values = [
        base_values[0] * ore_grade_factor,
        base_values[1] * (inputs.get('recovery_rate', 85) / 85),
        base_values[2] * automation_factor * 1.2,
        base_values[3] * automation_factor * 1.3,
        base_values[4] * water_recycling_factor * 1.1,
        base_values[5] * recycling_rate * 1.1
    ]
    optimized_values = [min(v * (1.25 + automation_factor * 0.15), 100) for v in current_values]
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=current_values,
        theta=categories,
        fill='toself',
        name='Current Flow',
        line=dict(color='#e74c3c', width=3),
        fillcolor='rgba(231, 76, 60, 0.3)'
    ))
    fig.add_trace(go.Scatterpolar(
        r=optimized_values,
        theta=categories,
        fill='toself',
        name='Optimized Flow',
        line=dict(color='#48bb78', width=3),
        fillcolor='rgba(72, 187, 120, 0.2)'
    ))
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 120],
                tickmode='linear',
                tick0=0,
                dtick=20,
                gridcolor='rgba(255,255,255,0.2)',
                tickcolor='white'
            ),
            angularaxis=dict(
                tickfont=dict(size=12, color='white')
            )
        ),
        showlegend=True,
        title={
            'text': f"🔄 Circular Economy Flow - {inputs['metal_type']}",
            'x': 0.5,
            'font': {'size': 18, 'color': 'white'}
        },
        height=500,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        legend=dict(font=dict(color='white'))
    )
    return fig
def create_enhanced_sankey_diagram(inputs, results):
    recycling_rate = METAL_DATA[inputs['metal_type']]['recycling_rate']
    total_flow = inputs.get('volume', 1000)
    ore_grade_factor = inputs.get('ore_grade', 2.5) / 2.5
    recovery_factor = inputs.get('recovery_rate', 85) / 85
    water_recycling_factor = inputs.get('water_recycling', 70) / 100
    automation_level = inputs.get('automation_level', 60) / 100
    extraction = total_flow * (1 / max(ore_grade_factor, 0.1)) * 0.8
    recycled_input = total_flow * recycling_rate * recovery_factor
    processing = (extraction + recycled_input * 0.9) * recovery_factor
    manufacturing = processing * 0.85 * (1 + automation_level * 0.1)
    use_phase = manufacturing * 0.95
    collection_rate = 0.7 + automation_level * 0.2
    collection = use_phase * collection_rate
    sorting_efficiency = 0.9 * (1 + automation_level * 0.05)
    sorting = collection * sorting_efficiency
    recycling_output = sorting * recycling_rate * (1 + water_recycling_factor * 0.1)
    remanufacturing = sorting * (0.15 + automation_level * 0.15)
    reuse = sorting * (0.1 + automation_level * 0.1)
    energy_recovery = sorting * 0.08
    disposal = use_phase - collection + sorting * (1 - recycling_rate - (0.15 + automation_level * 0.15) - (0.1 + automation_level * 0.1) - 0.08)
    environmental_loss = processing * 0.05 * (1 - water_recycling_factor)
    flow_values = [
        extraction, recycled_input*0.9, processing*0.85, manufacturing*0.95, 
        collection*sorting_efficiency, recycling_output, remanufacturing, 
        reuse, energy_recovery*0.6, recycling_output*0.85, remanufacturing*0.9, 
        reuse*0.95, disposal, environmental_loss
    ]
    fig = go.Figure(data=[go.Sankey(
        arrangement='snap',
        node=dict(
            pad=25,
            thickness=35,
            line=dict(color="rgba(255,255,255,0.6)", width=3),
            label=[
                "Raw Material Extraction", 
                "Recycling Input",
                "Primary Processing", 
                "Secondary Processing",
                "Manufacturing", 
                "Use Phase", 
                "Collection", 
                "Sorting",
                "Recycling", 
                "Remanufacturing", 
                "Reuse", 
                "Energy Recovery",
                "Disposal",
                "Environmental Loss"
            ],
            color=[
                "#e74c3c", "#2ecc71", "#f39c12", "#f1c40f", "#3498db", "#9b59b6", 
                "#1abc9c", "#34495e", "#27ae60", "#16a085", "#f39c12", "#e67e22", 
                "#95a5a6", "#7f8c8d"
            ]
        ),
        link=dict(
            source=[0, 1, 2, 3, 4, 5, 6, 7, 7, 7, 7, 8, 9, 10, 11, 5, 2],
            target=[2, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 1, 4, 5, 1, 12, 13],
            value=flow_values,
            color=[
                "rgba(231, 76, 60, 0.5)", "rgba(46, 204, 113, 0.6)", "rgba(243, 156, 18, 0.5)",
                "rgba(241, 196, 64, 0.5)", "rgba(52, 152, 219, 0.5)", "rgba(155, 89, 182, 0.5)",
                "rgba(26, 188, 156, 0.6)", "rgba(39, 174, 96, 0.7)", "rgba(22, 160, 133, 0.6)",
                "rgba(243, 156, 18, 0.6)", "rgba(230, 126, 34, 0.5)", "rgba(46, 204, 113, 0.4)",
                "rgba(22, 160, 133, 0.5)", "rgba(243, 156, 18, 0.4)",                 "rgba(230, 126, 34, 0.4)",
                "rgba(149, 165, 166, 0.6)", "rgba(127, 140, 141, 0.5)"
            ]
        )
    )])
    fig.update_layout(
        title={
            'text': f"🔄 Material Flow Analysis - {inputs['metal_type']} ({total_flow:,} tonnes/year)",
            'x': 0.5,
            'font': {'size': 16, 'color': 'white'}
        },
        height=600,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white')
    )
    return fig
def create_optimization_dashboard(inputs, results, predictions):
    automation_factor = inputs.get('automation_level', 60) / 100
    energy_multiplier = ENERGY_MULTIPLIERS[inputs.get('energy_source', 'Grid_Mix')]['carbon']
    water_recycling = inputs.get('water_recycling', 70) / 100
    ore_grade_factor = inputs.get('ore_grade', 2.5) / 2.5
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Carbon Optimization', 'Energy Efficiency', 'Water Usage', 'Circularity Score'),
        specs=[[{'type': 'bar'}, {'type': 'bar'}],
               [{'type': 'bar'}, {'type': 'bar'}]]
    )
    current_values = [
        results['carbon_footprint'],
        results['energy_intensity'],
        results['water_usage'],
        results['circularity_score']
    ]
    optimized_values = [
        predictions['predicted_carbon'],
        predictions['predicted_energy'],
        results['water_usage'] * (1 - water_recycling) * 0.4,
        predictions['predicted_circularity']
    ]
    categories = ['Carbon', 'Energy', 'Water', 'Circularity']
    for i, (current, optimized, category) in enumerate(zip(current_values, optimized_values, categories)):
        row = i // 2 + 1
        col = i % 2 + 1
        fig.add_trace(
            go.Bar(x=['Current', 'Optimized'], y=[current, optimized],
                  name=category, showlegend=False,
                  marker_color=['#e74c3c', '#27ae60']),
            row=row, col=col
        )
    fig.update_layout(
        title_text="🚀 AI-Driven Optimization Analysis",
        height=500,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white')
    )
    return fig
def create_economic_analysis(inputs, economic_results):
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=('Cost Breakdown', 'Profitability Analysis'),
        specs=[[{'type': 'pie'}, {'type': 'bar'}]]
    )
    volume_factor = inputs.get('volume', 1000) / 1000
    automation_factor = inputs.get('automation_level', 60) / 100
    energy_multiplier = ENERGY_MULTIPLIERS.get(inputs.get('energy_source', 'Grid_Mix'), ENERGY_MULTIPLIERS['Grid_Mix'])
    production_cost = economic_results['total_cost'] * 0.5 * (1 + volume_factor * 0.1)
    energy_cost = economic_results['total_cost'] * 0.3 * energy_multiplier['cost'] * (1 - automation_factor * 0.2)
    transport_cost = economic_results['total_cost'] * 0.15 * volume_factor * inputs.get('transport_distance', 500) / 1000
    other_cost = economic_results['total_cost'] * 0.05
    fig.add_trace(
        go.Pie(labels=['Production', 'Energy', 'Transport', 'Other'],
              values=[production_cost, energy_cost, transport_cost, other_cost],
              name="Cost Breakdown"),
        row=1, col=1
    )
    fig.add_trace(
        go.Bar(x=['Revenue', 'Cost', 'Profit'],
              y=[economic_results['total_revenue'], economic_results['total_cost'], economic_results['profit']],
              marker_color=['#3498db', '#e74c3c', '#27ae60'],
              name="Financial Metrics"),
        row=1, col=2
    )
    fig.update_layout(
        title_text="💰 Economic Performance Dashboard",
        height=400,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white')
    )
    return fig
def create_investment_analysis(inputs, economic_results, results):
    automation_level = inputs.get('automation_level', 60)
    energy_source = inputs.get('energy_source', 'Grid_Mix')
    recycling_rate = METAL_DATA[inputs['metal_type']]['recycling_rate']
    volume_factor = inputs.get('volume', 1000) / 1000
    ore_grade_factor = inputs.get('ore_grade', 2.5) / 2.5
    base_investment_costs = {
        'Basic Automation': 500000 * volume_factor * (2 - automation_level / 100),
        'Advanced Recycling': 1200000 * recycling_rate * volume_factor,
        'Energy Optimization': 800000 * (1.5 if energy_source == 'Renewable' else 1.0) * volume_factor,
        'Water Management': 600000 * (inputs.get('water_recycling', 70) / 100) * volume_factor,
        'Full Digitalization': 2500000 * volume_factor * ore_grade_factor
    }
    annual_savings = {
        'Basic Automation': economic_results['total_cost'] * 0.12 * (automation_level / 100) * ore_grade_factor,
        'Advanced Recycling': economic_results['total_cost'] * 0.18 * recycling_rate * volume_factor,
        'Energy Optimization': economic_results['total_cost'] * 0.25 * (0.8 if energy_source == 'Renewable' else 0.5),
        'Water Management': economic_results['total_cost'] * 0.08 * (inputs.get('water_recycling', 70) / 100),
        'Full Digitalization': economic_results['total_cost'] * 0.35 * (automation_level / 100) * ore_grade_factor
    }
    payback_periods = {}
    npv_5_years = {}
    for scenario in base_investment_costs:
        investment = base_investment_costs[scenario]
        savings = annual_savings[scenario]
        payback_periods[scenario] = investment / max(savings, 1)
        npv_5_years[scenario] = sum([savings / ((1 + 0.08) ** year) for year in range(1, 6)]) - investment
    investment_df = pd.DataFrame({
        'Scenario': list(base_investment_costs.keys()),
        'Investment': list(base_investment_costs.values()),
        'Annual_Savings': list(annual_savings.values()),
        'Payback_Period': list(payback_periods.values()),
        'NPV_5_Years': list(npv_5_years.values())
    })
    fig = px.scatter(investment_df, 
                    x='Investment', 
                    y='Annual_Savings',
                    size='NPV_5_Years',
                    color='Payback_Period',
                    hover_data=['Scenario'],
                    title="💡 Investment Scenario Analysis",
                    color_continuous_scale='RdYlGn_r')
    fig.update_layout(
        height=500,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        title_font=dict(color='white')
    )
    return fig
def create_economic_vs_environmental(inputs, results, economic_results):
    automation_level = inputs.get('automation_level', 60) / 100
    energy_multiplier = ENERGY_MULTIPLIERS.get(inputs.get('energy_source', 'Grid_Mix'), ENERGY_MULTIPLIERS['Grid_Mix'])
    recycling_rate = METAL_DATA[inputs['metal_type']]['recycling_rate']
    water_recycling = inputs.get('water_recycling', 70) / 100
    volume_factor = inputs.get('volume', 1000) / 1000
    ore_grade_factor = inputs.get('ore_grade', 2.5) / 2.5
    optimization_areas = {
        'Energy Efficiency': {
            'investment': 800000 * volume_factor,
            'annual_savings': economic_results['total_cost'] * 0.2 * energy_multiplier['carbon'] * ore_grade_factor,
            'co2_reduction': results['carbon_footprint'] * inputs.get('volume', 1000) * 0.35 * energy_multiplier['carbon']
        },
        'Material Recovery': {
            'investment': 1200000 * volume_factor,
            'annual_savings': economic_results['total_cost'] * 0.15 * recycling_rate * automation_level,
            'co2_reduction': results['carbon_footprint'] * inputs.get('volume', 1000) * 0.25 * recycling_rate
        },
        'Process Automation': {
            'investment': 2000000 * volume_factor * ore_grade_factor,
            'annual_savings': economic_results['total_cost'] * 0.18 * automation_level,
            'co2_reduction': results['carbon_footprint'] * inputs.get('volume', 1000) * 0.2 * automation_level
        },
        'Waste Reduction': {
            'investment': 600000 * volume_factor,
            'annual_savings': economic_results['total_cost'] * 0.1 * water_recycling,
            'co2_reduction': results['carbon_footprint'] * inputs.get('volume', 1000) * 0.15 * water_recycling
        },
        'Water Management': {
            'investment': 400000 * volume_factor,
            'annual_savings': economic_results['total_cost'] * 0.08 * water_recycling,
            'co2_reduction': results['carbon_footprint'] * inputs.get('volume', 1000) * 0.1 * water_recycling
        }
    }
    optimization_df = pd.DataFrame({
        'Area': list(optimization_areas.keys()),
        'Investment': [data['investment'] for data in optimization_areas.values()],
        'Annual_Savings': [data['annual_savings'] for data in optimization_areas.values()],
        'CO2_Reduction': [data['co2_reduction'] for data in optimization_areas.values()]
    })
    fig = px.scatter(optimization_df, 
                    x='Investment', 
                    y='Annual_Savings',
                    size='CO2_Reduction',
                    color='Area',
                    title="🎯 Economic vs Environmental Optimization",
                    hover_data=['Area'])
    fig.update_layout(
        height=500,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        title_font=dict(color='white')
    )
    return fig
def create_circularity_indicators(inputs, results, predictions):
    automation_level = inputs.get('automation_level', 60) / 100
    recycling_rate = METAL_DATA[inputs['metal_type']]['recycling_rate']
    water_recycling = inputs.get('water_recycling', 70) / 100
    ore_grade_efficiency = min(100, (inputs.get('ore_grade', 2.5) / 2.5) * 80)
    recovery_efficiency = inputs.get('recovery_rate', 85)
    material_efficiency = ore_grade_efficiency * (recovery_efficiency / 100) * (1 + automation_level * 0.5)
    resource_recovery = recycling_rate * 100 * (1 + automation_level * 0.3) * (inputs.get('recovery_rate', 85) / 85)
    waste_minimization = results['circularity_score'] * (1 + water_recycling * 0.2) * (1 + automation_level * 0.15)
    energy_recovery = 45 * (1 + automation_level * 0.4) * (1.2 if inputs.get('energy_source') == 'Renewable' else 0.8)
    product_life_extension = 60 * (1 + automation_level * 0.25) * predictions['extended_life_factor'] * (ore_grade_efficiency / 80)
    current_performance = [
        min(100, material_efficiency),
        min(100, resource_recovery),
        min(100, waste_minimization),
        min(100, energy_recovery),
        min(100, product_life_extension)
    ]
    target_performance = [90, 95, 85, 75, 80]
    indicators_data = pd.DataFrame({
        'Indicator': ['Material Efficiency', 'Resource Recovery', 'Waste Minimization', 'Energy Recovery', 'Product Life Extension'],
        'Current_Performance': current_performance,
        'Target_Performance': target_performance
    })
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=indicators_data['Current_Performance'],
        theta=indicators_data['Indicator'],
        fill='toself',
        name='Current',
        line=dict(color='#e74c3c', width=3),
        fillcolor='rgba(231, 76, 60, 0.3)'
    ))
    fig.add_trace(go.Scatterpolar(
        r=indicators_data['Target_Performance'],
        theta=indicators_data['Indicator'],
        fill='toself',
        name='Target',
        line=dict(color='#27ae60', width=3),
        fillcolor='rgba(39, 174, 96, 0.2)'
    ))
    fig.update_layout(
        title="🎯 Circular Economy Performance Radar",
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                gridcolor='rgba(255,255,255,0.2)',
                tickcolor='white'
            ),
            angularaxis=dict(
                tickfont=dict(size=12, color='white')
            )
        ),
        height=500, 
        paper_bgcolor='rgba(0,0,0,0)', 
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        title_font=dict(color='white'),
        legend=dict(font=dict(color='white'))
    )
    return fig
def calculate_results(inputs):
    metal_data = METAL_DATA[inputs['metal_type']]
    energy_multiplier = ENERGY_MULTIPLIERS.get(inputs.get('energy_source', 'Grid_Mix'), ENERGY_MULTIPLIERS['Grid_Mix'])
    primary_carbon = metal_data['primary_carbon'] * energy_multiplier['carbon']
    secondary_carbon = metal_data['secondary_carbon'] * energy_multiplier['carbon']
    if inputs.get('production_route', 'Primary') == 'Primary':
        carbon_footprint = primary_carbon
    elif inputs.get('production_route', 'Primary') == 'Secondary':
        carbon_footprint = secondary_carbon
    else:
        carbon_footprint = (primary_carbon + secondary_carbon) / 2
    ore_grade_factor = max(0.1, inputs.get('ore_grade', 2.5) / 2.5)
    recovery_factor = inputs.get('recovery_rate', 85) / 85
    automation_factor = inputs.get('automation_level', 60) / 100
    carbon_footprint *= (1 / ore_grade_factor) * (1 / recovery_factor) * (1 - automation_factor * 0.2)
    energy_base = metal_data['energy_intensity']
    if 'electricity_intensity' in inputs:
        energy_base = inputs['electricity_intensity'] * 3.6
    energy_intensity = energy_base * energy_multiplier['carbon'] * (1 / ore_grade_factor) * (1 - automation_factor * 0.15)
    water_base = metal_data['water_usage']
    water_recycling_factor = inputs.get('water_recycling', 70) / 100
    water_usage = water_base * (1 - water_recycling_factor * 0.8)
    transport_carbon = 0
    if 'transport_distance' in inputs and inputs.get('transport_mode'):
        transport_data = TRANSPORT_DATA.get(inputs['transport_mode'], TRANSPORT_DATA['Truck'])
        transport_carbon = (inputs['transport_distance'] * transport_data['carbon_per_km'] * inputs['volume']) / 1000
    elif 'transport_distance' in inputs:
        transport_carbon = (inputs.get('transport_distance', 500) * 0.12 * inputs['volume']) / 1000
    total_carbon = carbon_footprint + transport_carbon
    recycling_rate = metal_data['recycling_rate']
    reuse_potential = recycling_rate * 0.8 * (1 + automation_factor * 0.2)
    design_efficiency = automation_factor * (ore_grade_factor + recovery_factor) / 2
    byproduct_factor = inputs.get('byproduct_recovery', 40) / 100
    circularity_score = (recycling_rate * 40 + reuse_potential * 30 + design_efficiency * 20 + byproduct_factor * 10) * (1 + water_recycling_factor * 0.1)
    base_cost_per_tonne = {
        'Aluminum': 45000, 'Copper': 65000, 'Steel': 25000, 
        'Lithium': 180000, 'Rare_Earth': 350000
    }.get(inputs['metal_type'], 45000)
    ore_grade_cost_factor = max(1, 2 / ore_grade_factor)
    automation_cost_reduction = 1 - automation_factor * 0.25
    production_cost_per_tonne = base_cost_per_tonne * ore_grade_cost_factor * automation_cost_reduction
    energy_cost_per_mj = 4.2 * energy_multiplier['cost']
    water_cost_per_liter = 0.05
    transport_cost_multiplier = 1200
    if inputs.get('transport_mode'):
        transport_data = TRANSPORT_DATA.get(inputs['transport_mode'], TRANSPORT_DATA['Truck'])
        transport_cost_multiplier = transport_data['cost_per_km']
    total_production_cost = inputs['volume'] * production_cost_per_tonne
    total_energy_cost = inputs['volume'] * energy_intensity * energy_cost_per_mj
    total_water_cost = inputs['volume'] * water_usage * water_cost_per_liter
    transport_cost = inputs.get('transport_distance', 500) * transport_cost_multiplier * (inputs['volume'] / 1000)
    total_cost = total_production_cost + total_energy_cost + total_water_cost + transport_cost
    revenue_per_tonne = metal_data['market_price'] * (1 + automation_factor * 0.05)
    total_revenue = inputs['volume'] * revenue_per_tonne
    profit = total_revenue - total_cost
    profit_margin = (profit / total_revenue) * 100 if total_revenue > 0 else 0
    roi = (profit / total_cost) * 100 if total_cost > 0 else 0
    results = {
        'carbon_footprint': total_carbon,
        'energy_intensity': energy_intensity,
        'water_usage': water_usage,
        'circularity_score': min(100, circularity_score),
        'recycling_rate': recycling_rate * 100,
        'transport_emissions': transport_carbon
    }
    economic_results = {
        'total_cost': total_cost,
        'total_revenue': total_revenue,
        'profit': profit,
        'profit_margin': profit_margin,
        'roi': roi,
        'cost_per_tonne': total_cost / inputs['volume']
    }
    return results, economic_results
def generate_recommendations(results, predictions, economic_results):
    recommendations = []
    if results['carbon_footprint'] > 8:
        savings = min(250000, economic_results['total_cost'] * 0.15)
        recommendations.append(f"🌿 **Carbon Reduction**: Switch to renewable energy - 40% reduction potential (₹{savings:,.0f} savings)")
    if results['energy_intensity'] > 35:
        savings = min(480000, economic_results['total_cost'] * 0.18)
        recommendations.append(f"⚡ **Energy Optimization**: AI-driven process optimization - 25% reduction (₹{savings:,.0f} savings)")
    if results['water_usage'] > 10:
        savings = min(120000, economic_results['total_cost'] * 0.08)
        recommendations.append(f"💧 **Water Management**: Advanced recycling systems - 60% usage reduction (₹{savings:,.0f} savings)")
    if results['circularity_score'] < 70:
        revenue = min(890000, economic_results['total_revenue'] * 0.12)
        recommendations.append(f"♻️ **Material Recovery**: Establish recycling infrastructure - 25% circularity increase (₹{revenue:,.0f} revenue)")
    if economic_results['profit_margin'] < 15:
        profit = min(1560000, economic_results['total_cost'] * 0.20)
        recommendations.append(f"💰 **Profitability**: Optimize supply chain - 8-12% margin improvement (₹{profit:,.0f} profit)")
    if predictions['recycled_content_potential'] > 80:
        savings = min(1240000, economic_results['total_cost'] * 0.25)
        recommendations.append(f"🔄 **Secondary Materials**: Increase recycled content - 35% cost reduction (₹{savings:,.0f} savings)")
    return recommendations
predictor = CircularityPredictor()
st.markdown('<div class="main-header"><h1>♻️ CircuLCA</h1><p>AI-Driven Life Cycle Assessment Tool For Advancing Circularity And Sustainability In Metallurgy And Mining</p></div>', unsafe_allow_html=True)
with st.sidebar:
    st.header("Configuration")
    input_mode = st.radio("Input Complexity", ["Basic", "Intermediate", "Advanced"])
    if input_mode == "Basic":
        metal_type = st.selectbox("Metal Type", ["Aluminum", "Copper", "Steel", "Lithium"])
        production_route = st.selectbox("Production Route", ["Primary", "Secondary", "Hybrid"])
        volume = st.number_input("Volume (Tonnes/Year)", min_value=1, max_value=1000000, value=1000)
        energy_source = st.selectbox("Energy Source", ["Grid_Mix", "Renewable", "Fossil", "Nuclear"])
        inputs = {
            'metal_type': metal_type, 'production_route': production_route, 'volume': volume,
            'energy_source': energy_source, 'transport_distance': 500, 'ore_grade': 2.5,
            'recovery_rate': 85, 'water_recycling': 70, 'end_of_life': 'Recycle'
        }
    elif input_mode == "Intermediate":
        col1, col2 = st.columns(2)
        with col1:
            metal_type = st.selectbox("Metal Type", ["Aluminum", "Copper", "Steel", "Lithium"])
            volume = st.number_input("Volume (Tonnes)", min_value=1, value=1000)
            energy_source = st.selectbox("Energy Source", ["Grid_Mix", "Renewable", "Fossil"])
            ore_grade = st.number_input("Ore Grade (%)", min_value=0.1, value=2.5, step=0.1)
        with col2:
            transport_distance = st.number_input("Transport Distance (Km)", min_value=0, value=500)
            recovery_rate = st.number_input("Recovery Rate (%)", min_value=50, max_value=99, value=85)
            water_recycling = st.number_input("Water Recycling (%)", min_value=0, max_value=95, value=70)
            end_of_life = st.selectbox("End Of Life", ["Recycle", "Reuse", "Landfill"])
        inputs = {
            'metal_type': metal_type, 'volume': volume, 'energy_source': energy_source,
            'transport_distance': transport_distance, 'ore_grade': ore_grade,
            'recovery_rate': recovery_rate, 'water_recycling': water_recycling, 'end_of_life': end_of_life
        }
    else:
        col1, col2 = st.columns(2)
        with col1:
            metal_type = st.selectbox("Metal Type", ["Aluminum", "Copper", "Steel", "Lithium", "Rare_Earth"])
            volume = st.number_input("Volume (Tonnes/Year)", min_value=1, value=1000)
            ore_grade = st.number_input("Ore Grade (%)", min_value=0.1, max_value=50.0, value=2.5, step=0.1)
            recovery_rate = st.number_input("Recovery Rate (%)", min_value=50, max_value=99, value=85)
            smelting_temp = st.number_input("Smelting Temperature (°C)", min_value=500, max_value=2000, value=1200)
            electricity_intensity = st.number_input("Electricity (MWh/Tonne)", min_value=1.0, max_value=50.0, value=13.5, step=0.1)
        with col2:
            water_recycling = st.number_input("Water Recycling (%)", min_value=0, max_value=95, value=70)
            waste_treatment = st.selectbox("Waste Treatment", ["Conventional", "Advanced", "Zero_Waste"])
            transport_mode = st.selectbox("Transport Mode", ["Truck", "Rail", "Ship", "Multimodal"])
            facility_age = st.number_input("Facility Age (Years)", min_value=1, max_value=50, value=15)
            automation_level = st.number_input("Automation Level (%)", min_value=0, max_value=100, value=60)
            byproduct_recovery = st.number_input("Byproduct Recovery (%)", min_value=0, max_value=90, value=40)
        inputs = {
            'metal_type': metal_type, 'volume': volume, 'ore_grade': ore_grade,
            'recovery_rate': recovery_rate, 'smelting_temp': smelting_temp,
            'electricity_intensity': electricity_intensity, 'water_recycling': water_recycling,
            'waste_treatment': waste_treatment, 'transport_mode': transport_mode,
            'facility_age': facility_age, 'automation_level': automation_level,
            'byproduct_recovery': byproduct_recovery, 'transport_distance': 500
        }
    if st.button("🚀 Run Analysis", type="primary", use_container_width=True):
        st.session_state['run_analysis'] = True
        st.session_state['inputs'] = inputs
if st.session_state.get('run_analysis', False):
    inputs = st.session_state['inputs']
    progress_bar = st.progress(0)
    for i in range(100):
        progress_bar.progress(i + 1)
        time.sleep(0.01)
    results, economic_results = calculate_results(inputs)
    predictions = predictor.predict_parameters(inputs)
    report_data = create_report_data(inputs, results, economic_results, predictions)
    st.success("✅ Analysis Complete!")
    col1, col2 = st.columns(2)
    with col1:
        pdf_filename = f"CircuLCA_Report_{time.strftime('%Y%m%d_%H%M%S')}.pdf"
        pdf_link = create_pdf_download_link(report_data, pdf_filename)
        st.markdown(f'<div class="download-buttons">{pdf_link}</div>', unsafe_allow_html=True)
    with col2:
        json_filename = f"CircuLCA_Data_{time.strftime('%Y%m%d_%H%M%S')}.json"
        json_link = create_json_download_link(report_data, json_filename)
        st.markdown(f'<div class="download-buttons">{json_link}</div>', unsafe_allow_html=True)
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview Dashboard", "🔄 Circularity Analysis", "🚀 Optimization Insights", "💰 Economic Analysis"])
    with tab1:
        st.markdown('<div class="tab-content">', unsafe_allow_html=True)
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f'''
            <div class="metric-card">
                <h3>{results['carbon_footprint']:.2f}</h3>
                <p>kg CO₂-eq/kg</p>
                <small>Carbon Footprint</small>
            </div>
            ''', unsafe_allow_html=True)
        with col2:
            st.markdown(f'''
            <div class="metric-card">
                <h3>{results['energy_intensity']:.1f}</h3>
                <p>MJ/kg</p>
                <small>Energy Intensity</small>
            </div>
            ''', unsafe_allow_html=True)
        with col3:
            st.markdown(f'''
            <div class="metric-card">
                <h3>{results['water_usage']:.1f}</h3>
                <p>L/kg</p>
                <small>Water Usage</small>
            </div>
            ''', unsafe_allow_html=True)
        with col4:
            circularity_improvement = predictions['predicted_circularity'] - results['circularity_score']
            st.markdown(f'''
            <div class="metric-card">
                <h3>{results['circularity_score']:.1f}%</h3>
                <p>+{circularity_improvement:.1f}% potential</p>
                <small>Circularity Score</small>
            </div>
            ''', unsafe_allow_html=True)
        st.markdown("### 🎯 Key Performance Indicators")
        kpi_col1, kpi_col2, kpi_col3 = st.columns(3)
        with kpi_col1:
            circularity_progress = results['circularity_score']
            st.markdown(f"""
            <div class="circular-progress" style="--progress: {circularity_progress}">
                <div class="circular-progress-text">{circularity_progress:.1f}%</div>
            </div>
            <h5 style="text-align: center; color: white;">Circularity Score</h5>
            """, unsafe_allow_html=True)
        with kpi_col2:
            efficiency_score = max(0, 100 - (results['energy_intensity'] / 100 * 100))
            st.markdown(f"""
            <div class="circular-progress" style="--progress: {efficiency_score}">
                <div class="circular-progress-text">{efficiency_score:.1f}%</div>
            </div>
            <h5 style="text-align: center; color: white;">Energy Efficiency</h5>
            """, unsafe_allow_html=True)
        with kpi_col3:
            sustainability_score = max(0, 100 - (results['carbon_footprint'] / 20 * 100))
            st.markdown(f"""
            <div class="circular-progress" style="--progress: {sustainability_score}">
                <div class="circular-progress-text">{sustainability_score:.1f}%</div>
            </div>
            <h5 style="text-align: center; color: white;">Sustainability Score</h5>
            """, unsafe_allow_html=True)
        st.markdown("### 📈 Environmental Impact Trends")
        impact_data = pd.DataFrame({
            'Metric': ['Carbon Footprint', 'Energy Intensity', 'Water Usage', 'Waste Generation'],
            'Current': [results['carbon_footprint'], results['energy_intensity'], results['water_usage'], 100-results['circularity_score']],
            'Industry Average': [8.5, 35.2, 12.1, 45.0],
            'Best Practice': [3.2, 18.4, 4.8, 15.0]
        })
        fig_trends = px.bar(impact_data, x='Metric', y=['Current', 'Industry Average', 'Best Practice'], 
                           title="🌍 Environmental Performance Comparison", barmode='group',
                           color_discrete_map={'Current': '#e74c3c', 'Industry Average': '#f39c12', 'Best Practice': '#27ae60'})
        fig_trends.update_layout(
            height=400, 
            paper_bgcolor='rgba(0,0,0,0)', 
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            title_font=dict(color='white')
        )
        st.plotly_chart(fig_trends, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with tab2:
        st.markdown('<div class="tab-content">', unsafe_allow_html=True)
        col1, col2 = st.columns([1, 1])
        with col1:
            circular_fig = create_circular_economy_diagram(inputs, results)
            st.plotly_chart(circular_fig, use_container_width=True)
        with col2:
            st.markdown("### ♻️ Circularity Metrics")
            recycling_rate = METAL_DATA[inputs['metal_type']]['recycling_rate']
            st.markdown(f"""
            <div class="comparison-card">
                <h5>🔄 Material Recovery Rate</h5>
                <p><strong>{recycling_rate*100:.0f}%</strong> of material can be recovered</p>
            </div>
            """, unsafe_allow_html=True)
            st.markdown(f"""
            <div class="comparison-card">
                <h5>🎯 Reuse Potential</h5>
                <p><strong>{predictions['reuse_potential']:.1f}%</strong> components suitable for reuse</p>
            </div>
            """, unsafe_allow_html=True)
            st.markdown(f"""
            <div class="comparison-card">
                <h5>⚙️ Extended Life Factor</h5>
                <p><strong>{predictions['extended_life_factor']:.1f}x</strong> potential life extension</p>
            </div>
            """, unsafe_allow_html=True)
            st.markdown(f"""
            <div class="comparison-card">
                <h5>📊 Recycled Content Potential</h5>
                <p><strong>{predictions['recycled_content_potential']:.1f}%</strong> recycled content achievable</p>
            </div>
            """, unsafe_allow_html=True)
        st.markdown("### 🔄 Enhanced Material Flow Analysis")
        sankey_fig = create_enhanced_sankey_diagram(inputs, results)
        st.plotly_chart(sankey_fig, use_container_width=True)
        st.markdown("### 📊 Circular Economy Indicators")
        indicators_fig = create_circularity_indicators(inputs, results, predictions)
        st.plotly_chart(indicators_fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with tab3:
        st.markdown('<div class="tab-content">', unsafe_allow_html=True)
        st.markdown("### 🚀 AI-Powered Optimization Dashboard")
        optimization_fig = create_optimization_dashboard(inputs, results, predictions)
        st.plotly_chart(optimization_fig, use_container_width=True)
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### 🤖 Machine Learning Predictions")
            carbon_reduction = max(0, ((results['carbon_footprint'] - predictions['predicted_carbon']) / results['carbon_footprint'] * 100))
            energy_savings = max(0, ((results['energy_intensity'] - predictions['predicted_energy']) / results['energy_intensity'] * 100))
            confidence_score = 89.3 + inputs.get('automation_level', 60) * 0.1 + (inputs.get('ore_grade', 2.5) / 2.5) * 5
            st.markdown(f"""
            <div class="optimization-card">
                <h5>🎯 AI Model Confidence: {confidence_score:.1f}%</h5>
                <p><strong>Predicted Carbon Reduction:</strong> {carbon_reduction:.1f}%</p>
                <p><strong>Predicted Energy Savings:</strong> {energy_savings:.1f}%</p>
                <p><strong>Circularity Improvement:</strong> +{max(0, (predictions['predicted_circularity'] - results['circularity_score'])):.1f} points</p>
            </div>
            """, unsafe_allow_html=True)
            st.markdown("### 🎯 Smart Recommendations")
            recommendations = generate_recommendations(results, predictions, economic_results)
            for i, rec in enumerate(recommendations[:4], 1):
                st.markdown(f"""
                <div class="comparison-card">
                    <strong>{i}.</strong> {rec}
                </div>
                """, unsafe_allow_html=True)
        with col2:
            st.markdown("### 📊 Optimization Potential Analysis")
            automation_factor = inputs.get('automation_level', 60) / 100
            ore_grade_factor = inputs.get('ore_grade', 2.5) / 2.5
            potential_data = pd.DataFrame({
                'Process Stage': ['Raw Material', 'Processing', 'Manufacturing', 'Transport', 'End-of-Life'],
                'Current Efficiency': [65 * ore_grade_factor, 78 * (inputs.get('recovery_rate', 85)/85), 82 * automation_factor * 1.2, 70, results['circularity_score']],
                'Optimization Potential': [85, 92, 95, 88, predictions['predicted_circularity']]
            })
            fig_potential = px.line(potential_data, x='Process Stage', y=['Current Efficiency', 'Optimization Potential'],
                                  title="🎯 Process Optimization Roadmap",
                                  markers=True)
            fig_potential.update_layout(
                height=400, 
                paper_bgcolor='rgba(0,0,0,0)', 
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white'),
                title_font=dict(color='white')
            )
            st.plotly_chart(fig_potential, use_container_width=True)
            st.markdown("### 💡 Innovation Opportunities")
            energy_innovation = 75 if inputs.get('energy_source') == 'Renewable' else 45 + automation_factor * 20
            st.markdown(f"""
            <div class="comparison-card">
                <h5>⚡ Energy Innovation</h5>
                <p>Renewable integration potential: <strong>{energy_innovation:.0f}%</strong></p>
            </div>
            """, unsafe_allow_html=True)
            water_innovation = 85 if inputs.get('water_recycling', 70) > 80 else 60 + inputs.get('water_recycling', 70) * 0.3
            st.markdown(f"""
            <div class="comparison-card">
                <h5>💧 Water Innovation</h5>
                <p>Advanced recycling potential: <strong>{water_innovation:.0f}%</strong></p>
            </div>
            """, unsafe_allow_html=True)
            st.markdown(f"""
            <div class="comparison-card">
                <h5>🔬 Material Innovation</h5>
                <p>Secondary material usage: <strong>{predictions['recycled_content_potential']:.0f}%</strong></p>
            </div>
            """, unsafe_allow_html=True)
        st.markdown("### 📈 Optimization Timeline")
        timeline_data = pd.DataFrame({
            'Month': ['0-6', '6-12', '12-18', '18-24', '24-30', '30-36'],
            'Carbon Reduction': [0, 15 * automation_factor, 25 * automation_factor, 35 * automation_factor, 40 * automation_factor, min(45, carbon_reduction)],
            'Energy Savings': [0, 10 * ore_grade_factor, 20 * ore_grade_factor, 25 * ore_grade_factor, 28 * ore_grade_factor, min(30, energy_savings)],
            'Circularity Improvement': [results['circularity_score'], results['circularity_score']+5, 
                                      results['circularity_score']+10, results['circularity_score']+15, 
                                      results['circularity_score']+18, min(100, predictions['predicted_circularity'])]
        })
        fig_timeline = px.line(timeline_data, x='Month', y=['Carbon Reduction', 'Energy Savings', 'Circularity Improvement'],
                              title="📅 Optimization Implementation Timeline",
                              markers=True)
        fig_timeline.update_layout(
            height=400, 
            paper_bgcolor='rgba(0,0,0,0)', 
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            title_font=dict(color='white')
        )
        st.plotly_chart(fig_timeline, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with tab4:
        st.markdown('<div class="tab-content">', unsafe_allow_html=True)
        st.markdown("### 💰 Financial Performance Overview")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f'''
            <div class="metric-card">
                <h3>₹{economic_results['total_cost']:,.0f}</h3>
                <p>₹{economic_results['cost_per_tonne']:,.0f}/tonne</p>
                <small>Total Cost</small>
            </div>
            ''', unsafe_allow_html=True)
        with col2:
            st.markdown(f'''
            <div class="metric-card">
                <h3>₹{economic_results['total_revenue']:,.0f}</h3>
                <p>₹{economic_results['profit']:,.0f} profit</p>
                <small>Revenue</small>
            </div>
            ''', unsafe_allow_html=True)
        with col3:
            st.markdown(f'''
            <div class="metric-card">
                <h3>{economic_results['profit_margin']:.2f}%</h3>
                <p>Industry: 12.5%</p>
                <small>Profit Margin</small>
            </div>
            ''', unsafe_allow_html=True)
        with col4:
            st.markdown(f'''
            <div class="metric-card">
                <h3>{economic_results['roi']:.2f}%</h3>
                <p>Annual Return</p>
                <small>ROI</small>
            </div>
            ''', unsafe_allow_html=True)
        economic_fig = create_economic_analysis(inputs, economic_results)
        st.plotly_chart(economic_fig, use_container_width=True)
        st.markdown("### 💡 Investment Analysis")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### 📊 Cost-Benefit Analysis")
            investment_fig = create_investment_analysis(inputs, economic_results, results)
            st.plotly_chart(investment_fig, use_container_width=True)
        with col2:
            st.markdown("#### 📈 Financial Projections (5 Years)")
            years = list(range(1, 6))
            growth_rate = 0.05 + (inputs.get('automation_level', 60) / 1000) + (inputs.get('ore_grade', 2.5) / 2.5 * 0.02)
            cost_inflation = 0.03 - (inputs.get('automation_level', 60) / 2000) - ENERGY_MULTIPLIERS[inputs.get('energy_source', 'Grid_Mix')]['carbon'] * 0.01
            revenue_projection = [economic_results['total_revenue'] * (1 + growth_rate)**year for year in years]
            cost_projection = [economic_results['total_cost'] * (1 + cost_inflation)**year for year in years]
            projection_df = pd.DataFrame({
                'Year': years,
                'Projected Revenue': revenue_projection,
                'Projected Cost': cost_projection,
                'Projected Profit': [r - c for r, c in zip(revenue_projection, cost_projection)]
            })
            fig_projection = px.bar(projection_df, x='Year', y=['Projected Revenue', 'Projected Cost', 'Projected Profit'],
                                  title="📊 5-Year Financial Forecast",
                                  barmode='group')
            fig_projection.update_layout(
                height=400, 
                paper_bgcolor='rgba(0,0,0,0)', 
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white'),
                title_font=dict(color='white')
            )
            st.plotly_chart(fig_projection, use_container_width=True)
        st.markdown("### 🎯 Economic Optimization Opportunities")
        economic_environmental_fig = create_economic_vs_environmental(inputs, results, economic_results)
        st.plotly_chart(economic_environmental_fig, use_container_width=True)
        st.markdown("### 💼 Financial Recommendations")
        if economic_results['profit_margin'] < 15:
            automation_savings = economic_results['total_cost'] * 0.12 * (inputs.get('automation_level', 60) / 100)
            energy_savings = economic_results['total_cost'] * 0.15 * ENERGY_MULTIPLIERS[inputs.get('energy_source', 'Grid_Mix')]['carbon']
            material_savings = economic_results['total_cost'] * 0.08 * (inputs.get('ore_grade', 2.5) / 2.5)
            st.markdown(f"""
            <div class="comparison-card">
                <h5>📈 Profit Margin Improvement</h5>
                <p>Current margin is below industry average. Recommended actions:</p>
                <ul>
                    <li>Optimize energy procurement (₹{energy_savings:,.0f} savings)</li>
                    <li>Increase automation level (₹{automation_savings:,.0f} savings)</li>
                    <li>Negotiate better raw material contracts (₹{material_savings:,.0f} savings)</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        if economic_results['roi'] > 20:
            expansion_revenue = economic_results['total_revenue'] * 0.25
            recycling_investment = economic_results['total_cost'] * 0.15
            market_opportunity = economic_results['total_revenue'] * 0.18
            st.markdown(f"""
            <div class="comparison-card">
                <h5>💰 High ROI - Investment Opportunity</h5>
                <p>Excellent returns suggest potential for expansion:</p>
                <ul>
                    <li>Scale production capacity by 25% (₹{expansion_revenue:,.0f} revenue)</li>
                    <li>Invest in advanced recycling technology (₹{recycling_investment:,.0f} investment)</li>
                    <li>Explore new market opportunities (₹{market_opportunity:,.0f} potential)</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        circular_investment = economic_results['total_cost'] * 0.15 * (inputs.get('volume', 1000) / 1000)
        material_savings = economic_results['total_cost'] * 0.2 * METAL_DATA[inputs['metal_type']]['recycling_rate'] * (inputs.get('automation_level', 60) / 100)
        additional_revenue = economic_results['total_cost'] * 0.12 * (inputs.get('automation_level', 60) / 100) * (inputs.get('water_recycling', 70) / 100)
        payback_period = circular_investment / max(material_savings + additional_revenue, 1)
        st.markdown(f"""
        <div class="comparison-card">
            <h5>🎯 Circular Economy Investment</h5>
            <p>Investing ₹{circular_investment:,.0f} in circular economy initiatives could:</p>
            <ul>
                <li>Reduce material costs by {METAL_DATA[inputs['metal_type']]['recycling_rate']*20:.0f}% (₹{material_savings:,.0f})</li>
                <li>Improve sustainability score by 25 points</li>
                <li>Generate ₹{additional_revenue:,.0f} additional annual revenue</li>
                <li>Payback period: {payback_period:.1f} years</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)
