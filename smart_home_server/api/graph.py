import json
import io
from flask import request, Blueprint, current_app, Response
from flask_expects_json import expects_json

from smart_home_server.api import idSchema, colorSchema
from smart_home_server.helpers import addDefault

from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas

from smart_home_server.handlers.graphs import createGraph, deleteGraph, GraphAlreadyExists, GraphDoesNotExist, DatasourceDoesNotExist, generateFigure
import smart_home_server.constants as const

graphApi = Blueprint('graphApi', __name__)


postGraphSchema = \
{
        "type": "object",
        "properties": {
            "timeHours": { "type": "integer", "minimum": 1, "maximum": const.graphMaxHours}, #defaults to 1
            "datasource": idSchema,
            "color":  colorSchema
        },
        "required": ["datasource", "color"],
        'additionalProperties': False,
}
deleteGraphSchema = \
{
    "type": "object",
    "properties": {"id": idSchema},
    'required': ['id'],
    'additionalProperties': False,
}

@graphApi.route('/api/graph', methods=['POST'])
@expects_json(postGraphSchema, check_formats=True)
def postGraphRoute():
    data = json.loads(request.data)
    addDefault(data, 'timeHours', 1)

    datasource = data["datasource"]
    color = data["color"]
    try:
        createGraph(datasource, data["timeHours"], color)
        return current_app.response_class(status=200)
    except GraphAlreadyExists:
        return current_app.response_class("Graph With That ID Already Exists (should never occur)", status=400)
    except DatasourceDoesNotExist:
        return current_app.response_class(f"Unknown Datasource: {datasource}", status=400)
    except:
        return current_app.response_class(status=400)


@graphApi.route('/api/graph', methods=['DELETE'])
@expects_json(deleteGraphSchema, check_formats=True)
def deleteGraphRoute():
    data = json.loads(request.data)
    id = data['id']
    try:
        deleteGraph(id)
        return current_app.response_class(status=200)
    except GraphDoesNotExist:
        return current_app.response_class(f"Graph with ID:{id} Does Not Exist", status=400)
    except:
        return current_app.response_class(status=400)


@graphApi.route('/api/graph/figure/<id>.png', methods=['GET'])
def getFigureRoute(id):
    try:
        fig = generateFigure(id)
    except GraphDoesNotExist:
        return current_app.response_class(f"Graph with ID:{id} Does Not Exist", status=400)

    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')

