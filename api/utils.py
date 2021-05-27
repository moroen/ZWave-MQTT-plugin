def merge_dicts(orig_dict, new_dict):
    from collections.abc import Mapping

    for key, val in new_dict.items():
        if isinstance(val, Mapping):
            tmp = merge_dicts(orig_dict.get(key, {}), val)
            orig_dict[key] = tmp
        elif isinstance(val, list):
            orig_dict[key] = orig_dict.get(key, []) + val
        else:
            orig_dict[key] = new_dict[key]
    return orig_dict
