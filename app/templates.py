from fastapi.templating import Jinja2Templates

html_templates = Jinja2Templates(directory="ui/templates/html")
js_templates = Jinja2Templates(directory="ui/templates/js")
misc_templates = Jinja2Templates(directory="ui/templates/misc")
