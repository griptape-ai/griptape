import os
from typing import Any

import markdown
from jinja2 import Environment, FileSystemLoader, select_autoescape
from markupsafe import Markup

config_scheme = {
    "spec_url": "https://griptape-cloud-assets.s3.amazonaws.com/Griptape.openapi.yaml",
    "template": "swagger.md.tmpl",
    "outfile": "griptape-cloud/api/api-reference.md",
}


def generate_page_contents(page: Any) -> str:
    spec_url = config_scheme["spec_url"]
    tmpl_url = config_scheme["template"]
    env = Environment(loader=FileSystemLoader("docs/plugins/tmpl"), autoescape=select_autoescape(["html", "xml"]))
    md = markdown.Markdown()
    env.filters["markdown"] = lambda text: Markup(md.convert(text))

    template = env.get_template(tmpl_url)
    tmpl_out = template.render(spec_url=spec_url)
    return tmpl_out


def on_config(config: Any) -> None:
    pass


def on_page_read_source(page: Any, config: Any) -> Any:
    index_path = os.path.join(config["docs_dir"], config_scheme["outfile"])
    page_path = os.path.join(config["docs_dir"], page.file.src_path)
    if index_path == page_path:
        contents = generate_page_contents(page)
        return contents
