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

    # case1
    if content[0] == '[' and content[-1] != ']' and "]\n" not in content:
        print_error("!!! LLM makes a mistake, trying to fix it: no found ']'")

        # case: missing one '}' too.
        if content.endswith("\n}"):
            try:
                simplejson.loads(content + "}]")
                return content + "}]"
            except Exception:
                pass

        return content + "]"

    # case2
    if content[0] == '[' and "]\n" in content:
        print_error("!!! LLM makes a mistake, trying to fix it: found ']\\n'")
        i = content.find("\n]")
        if i > 0:
            return content[:i+2]

    # case3
    _new_content = convert_code_block_to_json_str(content)
    if _new_content:
        print_error("!!! LLM makes a mistake, fix it: found code block")
        content = _new_content
        return content

    # case4
    if content[0] == '[':
        # case, "\n}\n]"
        i = content.find("\n}\n]")
        fixed_i = content.find("\n}\n}\n]")
        if i > 0 and fixed_i < 0:
            content = content[:i] + "\n}" + content[i:]
            print_error("!!! LLM makes a mistake, fix it: found '\\n}\\n]'")
            return content

        # case, "\n]}]"
        i = content.find("\n]")
        if i > 0:
            content_tail = content[i+2:].strip()
            if content_tail and len(content_tail) < 11:
                print_error(f"!!! LLM makes a mistake, fix it: found error on tail '{content_tail}'")
                return content[:i+2]

    return content

def to_json_str(content, indent=2):
    """ convert list/dict to json string """
    if isinstance(content, str):
        content = fix_llm_mistakes_on_json(content)
        return content
    try:
        return simplejson.dumps(content, indent=indent, ensure_ascii=False, default=str)
    except Exception as e:
        print_error(f"format_content error: {e}, content: {content}")
        return str(content)

def json_dump(obj, indent=2):
    """ dump object to json str """
    if isinstance(obj, (set, tuple)):
        obj = list(obj)
    return to_json_str(obj, indent=indent)

def json_load(content):
    """ load json str to a object """
    if not isinstance(content, str):
        return content
    return simplejson.loads(content)
