from behave import *
from pycmbs.benchmarking import config2
import tempfile

@given(u'config file is empty')
def step_impl(context):
    tfile = tempfile.TemporaryFile()
    tfile.write('')
    tfile.seek(0)
    assert tfile.read() == ""
    tfile.seek(0)
    context.config_contents = tfile.read()   

@given(u'config file is not empty')
def step_impl(context):
    tfile = tempfile.TemporaryFile()
    tfile.write('moo: foo')
    tfile.seek(0)
    assert tfile.read() == "moo: foo"
    tfile.seek(0)
    context.config_contents = tfile.read()   

@then(u'read yaml config file')
def step_impl(context):
    config_contents = context.config_contents
    yaml_config_contents = config2.parse_config(config_contents, fmt='yaml')
    context.config_contents = yaml_config_contents

@then(u'read json config file')
def step_impl(context):
    config_contents = context.config_contents
    json_config_contents = config2.parse_config(config_contents, fmt='json')
    context.config_contents = json_config_contents

@then(u'check the config contents are empty')
def step_impl(context):
     assert context.config_contents is None 

@then(u'check the config contents are not empty')
def step_impl(context):
     assert context.config_contents is not None
