import simplejson
from utils.print_tool import print_error

def convert_code_block_to_json_str(content:str):
    """ return None for not match cases; string for json_str.
    example1:
    ```json
    {1:1}
    ```

    example2:
    ```json
    {1:1}
    ```
    ```json
    {2:2}
    ```
    """
    content = content.strip()
    if content.startswith("```json"):
        content = content.replace("```json", "")
        content = content.replace("```", ",")
        if content[-1] == ",":
            return f"[{content[:-1]}]"
    return None

def fix_llm_mistakes_on_json(content):
    """
    trying to fix mistakes of LLM.

    return str.
    """
    if not isinstance(content, str):
        return content

    content = content.strip()

    # LLM can make mistakes
    if content[0] == '[' and content[-1] != ']':
        print_error("!!! LLM makes a mistake, trying to fix it: no found ']'")
        return content + "]"
    elif content[0] == '[' and "]\n" in content:
        print_error("!!! LLM makes a mistake, trying to fix it: found ']\\n'")
        i = content.find("\n]")
        if i > 0:
            return content[:i+2]
    else:
        _new_content = convert_code_block_to_json_str(content)
        if _new_content:
            print_error("!!! LLM makes a mistake, fix it: found code block")
            content = _new_content

    return content

def to_json_str(content):
    """ convert list/dict to json string """
    if isinstance(content, str):
        content = fix_llm_mistakes_on_json(content)
        return content
    try:
        return simplejson.dumps(content, indent=2, ensure_ascii=False)
    except Exception as e:
        print_error(f"format_content error: {e}, content: {content}")
        return str(content)

def json_load(content):
    """ load json str to a object """
    if not isinstance(content, str):
        return content
    return simplejson.loads(content)
