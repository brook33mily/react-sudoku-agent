"""Public tool request parser cases from specs/tool_schemas.md.

V2 interface decision: parse_request(mapping) returns a typed request object
with .tool and rejects malformed mappings with ValueError.
"""
import pytest
from src.tools import parse_request

@pytest.mark.parametrize('request', [
    {'tool':'inspect','scope':'board'},
    {'tool':'inspect','scope':'cell','row':0,'column':1},
    {'tool':'place','row':0,'column':2,'digit':4},
    {'tool':'undo'},
    {'tool':'add_fact','atom':'A'},
    {'tool':'add_rule','premises':['A'],'conclusion':'B'},
    {'tool':'query','atom':'A'},
    {'tool':'submit'},
])
def test_valid_requests_parse(request):
    assert parse_request(request).tool == request['tool']

@pytest.mark.parametrize('request', [
    {'tool':'unknown'},
    {'tool':'place','row':True,'column':2,'digit':4},
    {'tool':'place','row':'0','column':2,'digit':4},
    {'tool':'place','row':9,'column':2,'digit':4},
    {'tool':'undo','extra':1},
    {'tool':'inspect','scope':'cell','row':0},
    {'tool':'query','atom':'!A'},
    {'tool':'add_rule','premises':'A','conclusion':'B'},
])
def test_malformed_requests_rejected(request):
    with pytest.raises(ValueError):
        parse_request(request)
