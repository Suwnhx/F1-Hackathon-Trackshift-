import dash
from dash import dcc, html, Input, Output, State, callback_context
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
import pandas as pd
import numpy as np
from datetime import datetime
import json

# Initialize the Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "ApexMind - F1 Race Engineer"

# F1-inspired color scheme
colors = {
		'bg_primary': '#0a0a0a',
		'bg_secondary': '#1a1a1a',
		'bg_tertiary': '#252525',
		'accent_red': '#e10600',
		'accent_silver': '#c0c0c0',
		'accent_gold': '#d4af37',
		'text_primary': '#ffffff',
		'text_secondary': '#b0b0b0',
		'chart_line': '#00d4ff',
		'chart_warn': '#ff9500',
		'chart_danger': '#dc0000'
}

# Race Simulator Class
class RaceSimulator:
		def __init__(self):
				self.lap = 0
				self.total_laps = 50
				self.speed = 280
				self.battery = 100
				self.tyre_wear = 0
				self.tyre_temp = 85
				self.fuel = 100
				self.position = 3
				self.tyre_compound = "Medium"
				self.weather = "Dry"
				self.safety_car = False
				self.lap_times = []
				self.tyre_age = 0
				self.pit_stops = 0
				self.historical_degradation = []
			
		def to_dict(self):
				return {
						'lap': self.lap,
						'total_laps': self.total_laps,
						'speed': self.speed,
						'battery': self.battery,
						'tyre_wear': self.tyre_wear,
						'tyre_temp': self.tyre_temp,
						'fuel': self.fuel,
						'position': self.position,
						'tyre_compound': self.tyre_compound,
						'weather': self.weather,
						'safety_car': self.safety_car,
						'lap_times': self.lap_times,
						'tyre_age': self.tyre_age,
						'pit_stops': self.pit_stops,
						'historical_degradation': self.historical_degradation
				}
	
		@staticmethod
		def from_dict(data):
				sim = RaceSimulator()
				for key, value in data.items():
						setattr(sim, key, value)
				return sim
	
		def simulate_lap(self):
				self.lap += 1
				self.tyre_age += 1
			
				base_degradation = 1.2
				degradation_factor = 1 + (self.tyre_age / 15) ** 1.5
				self.tyre_wear = min(100, self.tyre_wear + base_degradation * degradation_factor)
			
				if self.weather == "Wet":
						self.tyre_wear += 0.3
						self.speed = max(200, self.speed - 15)
				else:
						self.speed = 280 - (self.tyre_wear * 0.4) + np.random.uniform(-5, 5)
					
				self.tyre_temp = 85 + (self.tyre_age * 1.5) - (self.tyre_wear * 0.2) + np.random.uniform(-3, 3)
				self.tyre_temp = max(60, min(110, self.tyre_temp))
			
				self.battery = max(0, self.battery - np.random.uniform(1.5, 2.5))
				self.fuel = max(0, self.fuel - np.random.uniform(1.6, 2.0))
			
				base_lap_time = 82.5
				wear_penalty = (self.tyre_wear / 100) * 5
				weather_penalty = 8 if self.weather == "Wet" else 0
				lap_time = base_lap_time + wear_penalty + weather_penalty + np.random.uniform(-0.5, 0.5)
				self.lap_times.append(lap_time)
			
				self.historical_degradation.append({
						'lap': self.lap,
						'tyre_age': self.tyre_age,
						'wear': self.tyre_wear,
						'lap_time': lap_time,
						'compound': self.tyre_compound
				})
			
				return lap_time
	
		def predict_future_performance(self, laps_ahead=10):
				predictions = []
			
				if len(self.historical_degradation) < 3:
						return predictions
			
				recent_data = self.historical_degradation[-5:]
				wear_rates = [recent_data[i]['wear'] - recent_data[i-1]['wear'] 
											for i in range(1, len(recent_data))]
				avg_wear_rate = np.mean(wear_rates) if wear_rates else 1.2
			
				current_wear = self.tyre_wear
				current_age = self.tyre_age
			
				for i in range(1, laps_ahead + 1):
						future_age = current_age + i
						future_wear = min(100, current_wear + (avg_wear_rate * i))
						base_time = 82.5
						predicted_time = base_time + (future_wear / 100) * 5 + np.random.uniform(-0.3, 0.3)
					
						predictions.append({
								'lap': self.lap + i,
								'predicted_wear': future_wear,
								'predicted_time': predicted_time,
								'tyre_age': future_age
						})
					
				return predictions
	
		def ai_strategy_recommendation(self):
				predictions = self.predict_future_performance(laps_ahead=10)
				laps_remaining = self.total_laps - self.lap
			
				if self.tyre_wear < 30:
						recommendation = "STAY OUT"
						confidence = 95
						reasoning = "Tyres in excellent condition. No performance loss detected."
				elif self.tyre_wear < 55:
						if laps_remaining > 15:
								recommendation = "STAY OUT 3-5 LAPS"
								confidence = 78
								reasoning = "Tyres degrading but still competitive. Monitor closely."
						else:
								recommendation = "STAY OUT"
								confidence = 85
								reasoning = "Too few laps remaining. Push current tyres to the end."
				elif self.tyre_wear < 75:
						if laps_remaining > 10:
								recommendation = "PIT WITHIN 2 LAPS"
								confidence = 88
								reasoning = "Significant tyre wear detected. Fresh tyres will gain 1-1.5s/lap."
						else:
								recommendation = "PIT NOW (OPTIONAL)"
								confidence = 65
								reasoning = "High wear but few laps left. Marginal call."
				else:
						recommendation = "PIT NOW!"
						confidence = 98
						reasoning = "Critical tyre wear! Losing 2+ seconds per lap. Immediate pit required."
					
				if self.weather == "Wet" and self.tyre_compound != "Wet":
						recommendation = "PIT NOW - WRONG TYRES!"
						confidence = 99
						reasoning = "Wet conditions require wet tyres immediately for safety."
					
				if self.safety_car:
						recommendation = "PIT NOW (SAFETY CAR)"
						confidence = 95
						reasoning = "Safety car deployed! Free pit stop opportunity."
					
				return {
						'recommendation': recommendation,
						'confidence': confidence,
						'reasoning': reasoning,
						'predictions': predictions
				}
	
		def pit_stop(self, new_compound="Medium"):
				self.tyre_wear = 0
				self.tyre_age = 0
				self.tyre_compound = new_compound
				self.pit_stops += 1
				self.position = min(20, self.position + 2)
				return 22.5
	
# Dashboard Layout
app.layout = dbc.Container([
		# Store for simulator state
		dcc.Store(id='simulator-state', data=RaceSimulator().to_dict()),
		dcc.Store(id='chat-history', data=[{"role": "ai", "message": "AI ENGINEER: Ready to assist! Ask me anything about race strategy."}]),
	
		# Auto-run interval
		dcc.Interval(id='auto-interval', interval=1500, disabled=True, n_intervals=0),
	
		# Header
		dbc.Row([
				dbc.Col([
						html.Div([
								html.H1("APEXMIND", 
												style={
														'fontFamily': 'Consolas, monospace',
														'fontWeight': 'bold',
														'fontSize': '48px',
														'color': colors['accent_red'],
														'textAlign': 'center',
														'marginBottom': '5px',
														'letterSpacing': '3px'
												}),
								html.P("AI RACE ENGINEER | HAAS F1 × MPHASIS TRACKSHIFT",
											style={
													'fontFamily': 'Consolas, monospace',
													'fontSize': '12px',
													'color': colors['text_secondary'],
													'textAlign': 'center',
													'marginBottom': '0'
											})
						], style={
								'backgroundColor': colors['bg_secondary'],
								'padding': '20px',
								'borderRadius': '5px',
								'marginBottom': '20px'
						})
				], width=12)
		]),
	
		# Main Content
		dbc.Row([
				# Left Panel - Controls & Telemetry
				dbc.Col([
						# Race Control
						dbc.Card([
								dbc.CardHeader(" RACE CONTROL", style={
										'fontFamily': 'Consolas, monospace',
										'fontWeight': 'bold',
										'backgroundColor': colors['bg_tertiary'],
										'color': colors['text_primary'],
										'border': 'none'
								}),
								dbc.CardBody([
										dbc.Row([
												dbc.Col([
														dbc.Button("▶ NEXT LAP", id="next-lap-btn", color="dark", 
																			className="w-100 mb-2",
																			style={'fontFamily': 'Consolas, monospace', 'fontWeight': 'bold'})
												], width=6),
												dbc.Col([
														dbc.Button(" AUTO RUN", id="auto-run-btn", color="dark",
																			className="w-100 mb-2",
																			style={'fontFamily': 'Consolas, monospace', 'fontWeight': 'bold',
																							'color': colors['accent_silver']})
												], width=6),
										]),
										dbc.Row([
												dbc.Col([
														dbc.Button("🔄 RESET", id="reset-btn", color="dark",
																			className="w-100 mb-2",
																			style={'fontFamily': 'Consolas, monospace', 'fontWeight': 'bold',
																							'color': colors['accent_gold']})
												], width=6),
												dbc.Col([
														dbc.Button("🔧 PIT STOP", id="pit-btn", 
																			className="w-100 mb-2",
																			style={'fontFamily': 'Consolas, monospace', 'fontWeight': 'bold',
																							'backgroundColor': colors['accent_red'],
																							'color': colors['text_primary'],
																							'border': 'none'})
												], width=6),
										]),
										html.Hr(style={'borderColor': colors['text_secondary']}),
										html.Label("WEATHER:", style={
												'fontFamily': 'Consolas, monospace',
												'fontSize': '11px',
												'color': colors['text_secondary'],
												'fontWeight': 'bold'
										}),
										dcc.Dropdown(
												id='weather-dropdown',
												options=[
														{'label': 'Dry', 'value': 'Dry'},
														{'label': 'Wet', 'value': 'Wet'}
												],
												value='Dry',
												clearable=False,
												style={'marginBottom': '10px', 'fontFamily': 'Consolas, monospace'}
										),
										html.Label("SAFETY CAR:", style={
												'fontFamily': 'Consolas, monospace',
												'fontSize': '11px',
												'color': colors['text_secondary'],
												'fontWeight': 'bold'
										}),
										dbc.Checklist(
												id='safety-car-switch',
												options=[{'label': ' Active', 'value': 1}],
												value=[],
												switch=True,
												style={'fontFamily': 'Consolas, monospace'}
										)
								], style={'backgroundColor': colors['bg_tertiary']})
						], style={'backgroundColor': colors['bg_tertiary'], 'border': 'none', 'marginBottom': '20px'}),
					
						# Telemetry
						dbc.Card([
								dbc.CardHeader("TELEMETRY", style={
										'fontFamily': 'Consolas, monospace',
										'fontWeight': 'bold',
										'backgroundColor': colors['bg_tertiary'],
										'color': colors['text_primary'],
										'border': 'none'
								}),
								dbc.CardBody([
										html.Div(id='telemetry-display')
								], style={'backgroundColor': colors['bg_tertiary']})
						], style={'backgroundColor': colors['bg_tertiary'], 'border': 'none'})
				], width=12, lg=4),
			
				# Right Panel - Strategy & Charts
				dbc.Col([
						# AI Strategy
						dbc.Card([
								dbc.CardHeader(" AI STRATEGY", style={
										'fontFamily': 'Consolas, monospace',
										'fontWeight': 'bold',
										'backgroundColor': colors['bg_secondary'],
										'color': colors['accent_red'],
										'border': 'none'
								}),
								dbc.CardBody([
										html.Div(id='strategy-display')
								], style={'backgroundColor': colors['bg_secondary'], 'minHeight': '120px'})
						], style={'backgroundColor': colors['bg_secondary'], 'border': 'none', 'marginBottom': '20px'}),
					
						# Charts
						dbc.Card([
								dbc.CardBody([
										dcc.Graph(id='lap-times-chart', config={'displayModeBar': False},
															style={'height': '300px', 'marginBottom': '10px'}),
										dcc.Graph(id='tyre-wear-chart', config={'displayModeBar': False},
															style={'height': '300px'})
								], style={'backgroundColor': colors['bg_tertiary'], 'padding': '10px'})
						], style={'backgroundColor': colors['bg_tertiary'], 'border': 'none', 'marginBottom': '20px'}),
					
						# Chatbot
						dbc.Card([
								dbc.CardHeader(" PIT CREW ASSISTANT", style={
										'fontFamily': 'Consolas, monospace',
										'fontWeight': 'bold',
										'backgroundColor': colors['bg_tertiary'],
										'color': colors['text_primary'],
										'border': 'none'
								}),
								dbc.CardBody([
										html.Div(id='chat-display', style={
												'height': '150px',
												'overflowY': 'auto',
												'backgroundColor': colors['bg_primary'],
												'padding': '10px',
												'borderRadius': '5px',
												'marginBottom': '10px',
												'fontFamily': 'Consolas, monospace',
												'fontSize': '12px',
												'color': colors['text_primary']
										}),
										dbc.InputGroup([
												dbc.Input(id='chat-input', placeholder="Ask about strategy...",
																	style={'fontFamily': 'Consolas, monospace',
																				'backgroundColor': colors['bg_primary'],
																				'color': colors['text_primary'],
																				'border': 'none'}),
												dbc.Button("SEND", id='send-btn', 
																	style={'fontFamily': 'Consolas, monospace',
																				'fontWeight': 'bold',
																				'backgroundColor': colors['bg_secondary'],
																				'border': 'none'})
										])
								], style={'backgroundColor': colors['bg_tertiary']})
						], style={'backgroundColor': colors['bg_tertiary'], 'border': 'none'})
				], width=12, lg=8)
		])
], fluid=True, style={'backgroundColor': colors['bg_primary'], 'minHeight': '100vh', 'padding': '20px'})

# Callbacks
@app.callback(
		[Output('simulator-state', 'data'),
			Output('auto-interval', 'disabled')],
		[Input('next-lap-btn', 'n_clicks'),
			Input('auto-run-btn', 'n_clicks'),
			Input('auto-interval', 'n_intervals'),
			Input('reset-btn', 'n_clicks'),
			Input('pit-btn', 'n_clicks'),
			Input('weather-dropdown', 'value'),
			Input('safety-car-switch', 'value')],
		[State('simulator-state', 'data'),
			State('auto-interval', 'disabled')],
		prevent_initial_call=True
)
def update_simulator(next_clicks, auto_clicks, n_intervals, reset_clicks, pit_clicks,
										weather, safety_car, sim_data, interval_disabled):
		ctx = callback_context
	
		if not ctx.triggered:
				return sim_data, interval_disabled
	
		trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
	
		simulator = RaceSimulator.from_dict(sim_data)
	
		if trigger_id == 'reset-btn':
				simulator = RaceSimulator()
				interval_disabled = True
		elif trigger_id == 'pit-btn':
				simulator.pit_stop()
		elif trigger_id == 'auto-run-btn':
				interval_disabled = not interval_disabled
		elif trigger_id in ['next-lap-btn', 'auto-interval']:
				if simulator.lap < simulator.total_laps:
						simulator.simulate_lap()
					
		simulator.weather = weather
		simulator.safety_car = len(safety_car) > 0
	
		return simulator.to_dict(), interval_disabled

@app.callback(
		[Output('telemetry-display', 'children'),
			Output('strategy-display', 'children'),
			Output('lap-times-chart', 'figure'),
			Output('tyre-wear-chart', 'figure'),
			Output('auto-run-btn', 'children')],
		[Input('simulator-state', 'data'),
			Input('auto-interval', 'disabled')]
)
def update_displays(sim_data, interval_disabled):
		simulator = RaceSimulator.from_dict(sim_data)
		strategy = simulator.ai_strategy_recommendation()
	
		# Telemetry Display
		telemetry = html.Div([
				html.H3(f"LAP: {simulator.lap}/{simulator.total_laps}",
								style={'fontFamily': 'Consolas, monospace', 'color': colors['chart_line'],
											'textAlign': 'center', 'marginBottom': '10px'}),
				html.H3(f"POSITION: P{simulator.position}",
								style={'fontFamily': 'Consolas, monospace', 'color': colors['accent_gold'],
											'textAlign': 'center', 'marginBottom': '10px'}),
				html.H5(f"SPEED: {simulator.speed:.0f} KM/H",
								style={'fontFamily': 'Consolas, monospace', 'color': colors['text_primary'],
											'textAlign': 'center', 'marginBottom': '10px'}),
				html.H5(f"TYRE: {simulator.tyre_compound[0]} ({simulator.tyre_age} LAPS)",
								style={'fontFamily': 'Consolas, monospace', 'color': colors['accent_silver'],
											'textAlign': 'center', 'marginBottom': '20px'}),
			
				html.Label("BATTERY:", style={'fontFamily': 'Consolas, monospace', 'fontSize': '11px',
																			'color': colors['text_secondary'], 'fontWeight': 'bold'}),
				dbc.Progress(value=simulator.battery, 
										color='info' if simulator.battery > 50 else 'warning' if simulator.battery > 20 else 'danger',
										style={'height': '20px', 'marginBottom': '5px'}),
				html.P(f"{simulator.battery:.1f}%", 
							style={'fontFamily': 'Consolas, monospace', 'textAlign': 'center',
										'color': colors['chart_line'] if simulator.battery > 50 else colors['chart_warn'] if simulator.battery > 20 else colors['chart_danger'],
										'fontWeight': 'bold', 'marginBottom': '15px'}),
			
				html.Label("TYRE WEAR:", style={'fontFamily': 'Consolas, monospace', 'fontSize': '11px',
																				'color': colors['text_secondary'], 'fontWeight': 'bold'}),
				dbc.Progress(value=simulator.tyre_wear,
										color='info' if simulator.tyre_wear < 40 else 'warning' if simulator.tyre_wear < 70 else 'danger',
										style={'height': '20px', 'marginBottom': '5px'}),
				html.P(f"{simulator.tyre_wear:.1f}%",
							style={'fontFamily': 'Consolas, monospace', 'textAlign': 'center',
										'color': colors['chart_line'] if simulator.tyre_wear < 40 else colors['chart_warn'] if simulator.tyre_wear < 70 else colors['chart_danger'],
										'fontWeight': 'bold'})
		])
	
		# Strategy Display
		strategy_display = html.Div([
				html.H4(strategy['recommendation'],
								style={'fontFamily': 'Consolas, monospace', 'fontWeight': 'bold',
											'color': colors['text_primary'], 'marginBottom': '10px'}),
				html.P(f"CONFIDENCE: {strategy['confidence']}%",
							style={'fontFamily': 'Consolas, monospace', 'fontSize': '14px',
										'color': colors['text_primary'], 'marginBottom': '10px'}),
				html.P(strategy['reasoning'],
							style={'fontFamily': 'Consolas, monospace', 'fontSize': '13px',
										'color': colors['text_secondary']})
		])
	
		# Lap Times Chart
		lap_times_fig = go.Figure()
		lap_times_fig.update_layout(
				template='plotly_dark',
				paper_bgcolor=colors['bg_tertiary'],
				plot_bgcolor=colors['bg_primary'],
				font=dict(family='Consolas, monospace', color=colors['text_secondary']),
				title={'text': 'LAP TIMES & PREDICTIONS', 'font': {'size': 14, 'color': colors['text_primary']}},
				xaxis_title="Lap",
				yaxis_title="Time (s)",
				margin=dict(l=50, r=20, t=40, b=40),
				showlegend=True,
				legend=dict(orientation='h', yanchor='top', y=1.1, xanchor='left', x=0)
		)
	
		if simulator.lap_times:
				laps = list(range(1, len(simulator.lap_times) + 1))
				lap_times_fig.add_trace(go.Scatter(
						x=laps, y=simulator.lap_times,
						mode='lines+markers',
						name='ACTUAL',
						line=dict(color=colors['chart_line'], width=3),
						marker=dict(size=6)
				))
			
				if strategy['predictions']:
						pred_laps = [p['lap'] for p in strategy['predictions']]
						pred_times = [p['predicted_time'] for p in strategy['predictions']]
						lap_times_fig.add_trace(go.Scatter(
								x=pred_laps, y=pred_times,
								mode='lines+markers',
								name='PREDICTION',
								line=dict(color=colors['chart_warn'], width=2, dash='dash'),
								marker=dict(size=5, symbol='square')
						))
					
		# Tyre Wear Chart
		tyre_wear_fig = go.Figure()
		tyre_wear_fig.update_layout(
				template='plotly_dark',
				paper_bgcolor=colors['bg_tertiary'],
				plot_bgcolor=colors['bg_primary'],
				font=dict(family='Consolas, monospace', color=colors['text_secondary']),
				title={'text': 'TYRE DEGRADATION ANALYSIS', 'font': {'size': 14, 'color': colors['text_primary']}},
				xaxis_title="Lap",
				yaxis_title="Wear (%)",
				yaxis=dict(range=[0, 105]),
				margin=dict(l=50, r=20, t=40, b=40),
				showlegend=True,
				legend=dict(orientation='h', yanchor='top', y=1.1, xanchor='left', x=0)
		)
	
		if simulator.historical_degradation:
				laps = [d['lap'] for d in simulator.historical_degradation]
				wear = [d['wear'] for d in simulator.historical_degradation]
				tyre_wear_fig.add_trace(go.Scatter(
						x=laps, y=wear,
						mode='lines+markers',
						name='ACTUAL WEAR',
						fill='tozeroy',
						line=dict(color=colors['chart_danger'], width=3),
						marker=dict(size=6),
						fillcolor=f"rgba({int(colors['chart_danger'][1:3], 16)}, {int(colors['chart_danger'][3:5], 16)}, {int(colors['chart_danger'][5:7], 16)}, 0.2)"
				))
			
				if strategy['predictions']:
						pred_laps = [p['lap'] for p in strategy['predictions']]
						pred_wear = [p['predicted_wear'] for p in strategy['predictions']]
						tyre_wear_fig.add_trace(go.Scatter(
								x=pred_laps, y=pred_wear,
								mode='lines+markers',
								name='PREDICTED',
								line=dict(color=colors['chart_warn'], width=2, dash='dash'),
								marker=dict(size=5, symbol='square')
						))
					
				# Critical zone
				tyre_wear_fig.add_hrect(y0=70, y1=100, fillcolor=colors['chart_danger'], opacity=0.15,
																line_width=0, annotation_text="CRITICAL ZONE",
																annotation_position="top right")
			
		auto_btn_text = "⏸ PAUSE" if not interval_disabled else "⚡ AUTO RUN"
	
		return telemetry, strategy_display, lap_times_fig, tyre_wear_fig, auto_btn_text

@app.callback(
		[Output('chat-display', 'children'),
			Output('chat-history', 'data'),
			Output('chat-input', 'value')],
		[Input('send-btn', 'n_clicks')],
		[State('chat-input', 'value'),
			State('chat-history', 'data'),
			State('simulator-state', 'data')],
		prevent_initial_call=True
)
def update_chat(n_clicks, user_msg, chat_history, sim_data):
		if not user_msg or not user_msg.strip():
				return [html.P(msg['message'], style={'marginBottom': '5px'}) for msg in chat_history], chat_history, ""
	
		simulator = RaceSimulator.from_dict(sim_data)
		user_msg_lower = user_msg.lower()
	
		# Add user message
		chat_history.append({"role": "user", "message": f"YOU: {user_msg}"})
	
		# Generate AI response
		if 'pit' in user_msg_lower or 'stop' in user_msg_lower:
				strategy = simulator.ai_strategy_recommendation()
				response = f"AI ENGINEER: {strategy['recommendation']} - {strategy['reasoning']}"
		elif 'tyre' in user_msg_lower or 'tire' in user_msg_lower:
				response = f"AI ENGINEER: Current tyre wear is {simulator.tyre_wear:.1f}%. {simulator.tyre_compound} compound with {simulator.tyre_age} laps of age."
		elif 'lap time' in user_msg_lower or 'pace' in user_msg_lower:
				if simulator.lap_times:
						avg = np.mean(simulator.lap_times[-3:])
						response = f"AI ENGINEER: Current pace is {avg:.2f}s. Optimal is 82.5s. Degradation: {(avg-82.5):.2f}s."
				else:
						response = "AI ENGINEER: No lap data yet. Complete some laps first!"
		elif 'strategy' in user_msg_lower:
				response = f"AI ENGINEER: We're on a {simulator.pit_stops + 1}-stop strategy. {simulator.total_laps - simulator.lap} laps remaining."
		elif 'position' in user_msg_lower:
				response = f"AI ENGINEER: Currently P{simulator.position}. Push to gain positions or manage tyres strategically."
		else:
				response = "AI ENGINEER: I can help with pit strategy, tyre analysis, lap times, and race positions. What would you like to know?"
			
		chat_history.append({"role": "ai", "message": response})
	
		# Keep only last 10 messages
		if len(chat_history) > 10:
				chat_history = chat_history[-10:]
			
		chat_display = [html.P(msg['message'], style={'marginBottom': '8px', 'wordWrap': 'break-word'}) 
										for msg in chat_history]
	
		return chat_display, chat_history, ""

if __name__ == '__main__':
		app.run (debug=True, port=8050)

	