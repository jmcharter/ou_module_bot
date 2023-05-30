from mako.lookup import TemplateLookup
from ou_bot.common.ou_module import OUModule
from ou_bot.reddit_bot.config import MakoConfig

config = MakoConfig(template_dir="src/ou_bot/reddit_bot/templates/")

templates = TemplateLookup(directories=[config.template_dir], output_encoding=config.output_encoding)


def serve_template(template_name: str, **kwargs):
    template = templates.get_template(template_name)
    return template.render(**kwargs)


def serve_modules_template(modules, user):
    return serve_template(
        template_name="module_general_table.mako",
        modules=modules,
        user=user,
    )
