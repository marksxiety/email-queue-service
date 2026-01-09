from app.config import jinja_env


def render_email_template(template_name, data):
    template = jinja_env.get_template(f"{template_name}.html")
    return template.render(**data)
