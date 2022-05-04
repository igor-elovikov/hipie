import jinja2

jenv = jinja2.Environment(loader=jinja2.FileSystemLoader(""))

jenv.lstrip_blocks = True
jenv.trim_blocks = True
jenv.line_statement_prefix = "::"

templates = ["hash_impl", "noise", "vnoise", "svnoise", "voronoise"]

for template in templates:
    src_template = jenv.get_template(f"{template}.template")
    with open(f"{template}.h", "w") as noise_header:
        noise_header.write(src_template.render())