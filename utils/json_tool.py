import simplejson
from utils.print_tool import print_error

def to_json_str(content):
    """ convert list/dict to json string """
    if isinstance(content, str):
        return content
    try:
        return simplejson.dumps(content, indent=2, ensure_ascii=False)
    except Exception as e:
        print_error(f"format_content error: {e}, content: {content}")
        return str(content)
    