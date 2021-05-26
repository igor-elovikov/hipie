import jinja2

jenv = jinja2.Environment(loader=jinja2.FileSystemLoader(""))

jenv.lstrip_blocks = True
jenv.trim_blocks = True
jenv.line_statement_prefix = "::"

src_template = jenv.get_template("ie_noise.template")

with open("ie_noise.cl.h", "w") as noise_header:
    noise_header.write(src_template.render())