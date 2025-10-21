'''
  Author: DawsonLin
  Email: lin_dongsen@126.com
  Created: 2025-10-20
  Purpose:
'''

import chardet

# 自动检测编码
def safe_decode(data):
    """ safe to decode data to string """
    if isinstance(data, str):
        return data

    if not data:
        return ""

    # 检测编码
    detected = chardet.detect(data)
    encoding = detected.get('encoding', 'utf-8')

    if not encoding:
        try:
            return data.decode('utf-8', errors='replace')
        except Exception:
            return str(data)

    try:
        return data.decode(encoding)
    except UnicodeDecodeError:
        # 回退方案
        return data.decode('utf-8', errors='replace')
