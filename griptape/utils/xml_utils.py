def schema_to_xml(action: dict) -> str:
    def json2xml(json_obj: dict, line_padding=""):
        result_list = list()

        if line_padding == "":
            result_list.append("<tool_description>")

        json_obj_type = type(json_obj)

        if json_obj_type is list:
            for sub_elem in json_obj:
                result_list.append(json2xml(sub_elem, line_padding))

        elif json_obj_type is dict:
            for tag_name in json_obj:
                sub_obj = json_obj[tag_name]
                result_list.append("%s<%s>" % (line_padding, tag_name))
                result_list.append(json2xml(sub_obj, "\t" + line_padding))
                result_list.append("%s</%s>" % (line_padding, tag_name))

        else:
            result_list.append("%s%s" % (line_padding, json_obj))
        if line_padding == "":
            result_list.append("</tool_description>")

        return "\n".join(result_list)

    del action["$schema"]
    del action["$id"]
    return json2xml(action)
