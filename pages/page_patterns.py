from settings import PRINT_POSE_IN_TERMINAL
from pages import helpers

import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

from widgets.dimensions_ui import SECTION_DIMENSION_CONTROL, DIMENSION_INPUTS
from widgets.leg_patterns_ui import SECTION_SLIDERS_TEST, SLIDERS_TEST_INPUTS
from hexapod.models import VirtualHexapod
from hexapod.plotter import HexapodPlot
from hexapod.const import (
  BASE_PLOTTER,
  NAMES_LEG,
  HEXAPOD_POSE,
  BASE_DIMENSIONS,
  base_figure
)

from copy import deepcopy
import json
from app import app
from pages.shared_callbacks import INPUT_DIMENSIONS_JSON, HIDDEN_BODY_DIMENSIONS
# *********************
# *  LAYOUT           *
# *********************
SECTION_CONTROLS = [SECTION_DIMENSION_CONTROL, SECTION_SLIDERS_TEST]

layout = html.Div([
  html.Div(SECTION_CONTROLS, style={'width': '35%'}),
  dcc.Graph(id='graph-hexapod-3', style={'width': '65%'}),
  HIDDEN_BODY_DIMENSIONS
  ],
  style={'display': 'flex'}
)

# *********************
# *  CALLBACKS        *
# *********************
OUTPUT = Output('graph-hexapod-3', 'figure')
INPUTS = [INPUT_DIMENSIONS_JSON] + SLIDERS_TEST_INPUTS
STATES = [State('graph-hexapod-3', 'relayoutData'), State('graph-hexapod-3', 'figure')]
@app.callback(OUTPUT, INPUTS, STATES)
def update_patterns_page(dimensions_json, alpha, beta, gamma, relayout_data, figure):

  if figure is None:
    return base_figure()

  try:
    dimensions = json.loads(dimensions_json)
  except:
    dimensions = BASE_DIMENSIONS

  virtual_hexapod = VirtualHexapod(dimensions)
  poses = helpers.make_pose(alpha, beta, gamma)
  virtual_hexapod.update(poses)
  BASE_PLOTTER.update(figure, virtual_hexapod)
  helpers.change_camera_view(figure, relayout_data)
  return figure
