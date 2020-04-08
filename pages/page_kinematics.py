from settings import WHICH_POSE_CONTROL_UI, PRINT_POSE_IN_TERMINAL
from pages import helpers

if WHICH_POSE_CONTROL_UI == 1:
  from widgets.pose_control.generic_slider_ui import SECTION_POSE_CONTROL
elif WHICH_POSE_CONTROL_UI == 2:
  from widgets.pose_control.generic_input_ui import SECTION_POSE_CONTROL
else:
  from widgets.pose_control.generic_daq_slider_ui import SECTION_POSE_CONTROL

import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from hexapod.models import VirtualHexapod
from hexapod.const import (
  NAMES_LEG,
  NAMES_JOINT,
  BASE_PLOTTER,
  HEXAPOD_FIGURE,
  HEXAPOD_POSE
)

from widgets.dimensions_ui import SECTION_DIMENSION_CONTROL, DIMENSION_INPUTS
from copy import deepcopy
import json
from app import app

# *********************
# *  LAYOUT           *
# *********************
HIDDEN_LEG_POSES = [html.Div(id='pose-{}'.format(leg_name), style={'display': 'none'}) for leg_name in NAMES_LEG]
HIDDEN_BODY_DIMENSIONS = [html.Div(id='hexapod-dimensions-values', style={'display': 'none'})]
HIDDEN_LEG_POSES_ALL = [html.Div(id='hexapod-poses-values', style={'display': 'none'})]
HIDDEN_DIVS = HIDDEN_LEG_POSES + HIDDEN_BODY_DIMENSIONS +  HIDDEN_LEG_POSES_ALL

SECTION_CONTROLS = [SECTION_DIMENSION_CONTROL, SECTION_POSE_CONTROL]
layout = html.Div([
  html.Div(SECTION_CONTROLS, style={'width': '45%'}),
  dcc.Graph(id='graph-hexapod', style={'width': '55%'}),
  html.Div(HIDDEN_DIVS)],
  style={'display': 'flex'}
)

# *********************
# *  CALLBACKS        *
# *********************
# -------------------
# Listen if we need to update the hexapod graph
# -------------------
INPUT_ALL = [Input(name, 'children') for name in ['hexapod-poses-values', 'hexapod-dimensions-values']]
@app.callback(
  Output('graph-hexapod', 'figure'),
  INPUT_ALL,
  [State('graph-hexapod', 'relayoutData'), State('graph-hexapod', 'figure')]
)
def update_kinematics_page(poses_json, dimensions_json, relayout_data, figure):

  if figure is None:
    return HEXAPOD_FIGURE

  if dimensions_json is None:
    raise PreventUpdate

  try:
    poses = json.loads(poses_json)
  except:
    print("can't parse:", poses_json)
    raise PreventUpdate

  dimensions = json.loads(dimensions_json)
  virtual_hexapod = VirtualHexapod(dimensions)
  virtual_hexapod.update(poses)

  BASE_PLOTTER.update(figure, virtual_hexapod)
  helpers.change_camera_view(figure, relayout_data)
  return figure

# -------------------
# Listen if the robot dimensions are updated
# -------------------
@app.callback(
  Output('hexapod-dimensions-values', 'children'),
  DIMENSION_INPUTS
)
def update_hexapod_dimensions(fro, sid, mid, cox, fem, tib):
  dimensions = {
    'front': fro or 0,
    'side': sid or 0,
    'middle': mid or 0,

    'coxia': cox or 0,
    'femur': fem or 0,
    'tibia': tib or 0,
  }
  return json.dumps(dimensions)

# -------------------
# Listen if we need to update pose (IE one of the leg's pose is updated)
# -------------------
INPUT_LEGS = [Input(f'pose-{leg_name}', 'children') for leg_name in NAMES_LEG]
@app.callback(
  Output('hexapod-poses-values', 'children'),
  INPUT_LEGS
)
def update_hexapod_pose_values(rm, rf, lf, lm, lb, rb):
  poses = [rm, rf, lf, lm, lb, rb]
  poses_json = {}

  for i, name, pose in zip(range(6), NAMES_LEG, poses):
    try:
      pose = json.loads(pose)
      pose['name'] = name
      pose['id'] = i
      poses_json[i] = pose
    except:
      print(" can't parse:", pose)

  return json.dumps(poses_json)

# -------------------
# Listen if a leg pose is updated
# -------------------
def leg_inputs(leg_name):
  return [Input(f'input-{leg_name}-{joint_name}', 'value') for joint_name in NAMES_JOINT]

def leg_output(leg_name):
  return Output(f'pose-{leg_name}', 'children')

def leg_json(coxia, femur, tibia):
  return json.dumps({'coxia': coxia, 'femur': femur, 'tibia': tibia})

@app.callback(leg_output('right-middle'), leg_inputs('right-middle'))
def update_right_middle(coxia, femur, tibia):
  return leg_json(coxia, femur, tibia)

@app.callback(leg_output('right-front'), leg_inputs('right-front'))
def update_right_front(coxia, femur, tibia):
  return leg_json(coxia, femur, tibia)

@app.callback(leg_output('left-front'), leg_inputs('left-front'))
def update_left_front(coxia, femur, tibia):
  return leg_json(coxia, femur, tibia)

@app.callback(leg_output('left-middle'), leg_inputs('left-middle'))
def update_left_middle(coxia, femur, tibia):
  return leg_json(coxia, femur, tibia)

@app.callback(leg_output('left-back'), leg_inputs('left-back'))
def update_left_back(coxia, femur, tibia):
  return leg_json(coxia, femur, tibia)

@app.callback(leg_output('right-back'), leg_inputs('right-back'))
def update_right_back(coxia, femur, tibia):
  return leg_json(coxia, femur, tibia)
