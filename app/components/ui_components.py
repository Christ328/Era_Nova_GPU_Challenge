import streamlit as st
import plotly.graph_objects as go

def render_score_gauge(score: int, risk_color: str, risk_label: str):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Score de crédit", 'font': {'size': 20}},
        gauge={
            'axis': {'range': [0, 100], 'tickwidth': 1},
            'bar': {'color': risk_color},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, 30], 'color': '#fef2f2'},
                {'range': [30, 45], 'color': '#fff7ed'},
                {'range': [45, 60], 'color': '#fefce8'},
                {'range': [60, 75], 'color': '#f0fdf4'},
                {'range': [75, 100], 'color': '#ecfdf5'}
            ],
            'threshold': {
                'line': {'color': "black", 'width': 4},
                'thickness': 0.75,
                'value': score
            }
        }
    ))
    fig.update_layout(height=300, margin=dict(l=20, r=20, t=40, b=20))
    st.plotly_chart(fig, use_container_width=True)

def render_confidence_bar(confidence: float, conf_color: str, conf_label: str):
    st.markdown(f"""
    <div style="margin: 1rem 0;">
        <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
            <span>Confiance</span>
            <span style="font-weight: 600; color: {conf_color};">{confidence:.0f}% - {conf_label}</span>
        </div>
        <div style="height: 12px; background: #e5e7eb; border-radius: 6px; overflow: hidden;">
            <div style="width: {confidence}%; height: 100%; background: {conf_color}; border-radius: 6px; transition: width 0.5s ease;"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_factor_card(factor: dict):
    direction = factor['direction']
    icon = "🟢" if direction == 'positive' else "🔴"
    color = "#059669" if direction == 'positive' else "#dc2626"
    
    st.markdown(f"""
    <div style="
        border: 1px solid {color}33;
        border-left: 4px solid {color};
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        background: {color}0a;
    ">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <strong>{icon} {factor['label']}</strong>
                <br>
                <small style="color: #6b7280;">Valeur: {factor['value']:.2f} {factor.get('unit', '')} | SHAP: {factor['contribution']:+.4f}</small>
            </div>
            <span style="
                background: {color};
                color: white;
                padding: 0.25rem 0.75rem;
                border-radius: 9999px;
                font-size: 0.75rem;
                font-weight: 600;
            ">{direction.title()}</span>
        </div>
        <p style="margin: 0.5rem 0 0; color: #374151;">{factor['explanation']}</p>
    </div>
    """, unsafe_allow_html=True)

def render_alert_badge(alert):
    severity_colors = {
        'error': {'bg': '#fef2f2', 'border': '#dc2626', 'icon': '🔴'},
        'warning': {'bg': '#fff7ed', 'border': '#ca8a04', 'icon': '🟡'},
        'info': {'bg': '#eff6ff', 'border': '#2563eb', 'icon': '🔵'}
    }
    c = severity_colors.get(alert.severity, severity_colors['info'])
    
    st.markdown(f"""
    <div style="
        background: {c['bg']};
        border: 1px solid {c['border']};
        border-radius: 8px;
        padding: 0.75rem 1rem;
        margin: 0.5rem 0;
        display: flex;
        align-items: center;
        gap: 0.75rem;
    ">
        <span style="font-size: 1.25rem;">{c['icon']}</span>
        <span style="flex: 1; color: {c['border']}; font-weight: 500;">{alert.message}</span>
        <span style="
            background: {c['border']};
            color: white;
            padding: 0.125rem 0.5rem;
            border-radius: 4px;
            font-size: 0.7rem;
            font-weight: 600;
        ">{alert.severity.upper()}</span>
    </div>
    """, unsafe_allow_html=True)