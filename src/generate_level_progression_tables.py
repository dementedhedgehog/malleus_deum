from os.path import join
import webbrowser


LEVEL_PROGRESSION_TABLES_TEMPLATE_FNAME = join("docs", "level_progression_tables_template.html")
LEVEL_PROGRESSION_TABLES_HTML = join("build", "level_progression_tables.html")


def generate_level_progression_tables(jinja_env, db):    
    template = jinja_env.get_template(LEVEL_PROGRESSION_TABLES_TEMPLATE_FNAME)
    with open(LEVEL_PROGRESSION_TABLES_HTML, "w") as f:
        level_progression_table = template.render(
            db=db,
            archetypes=db.archetypes,
        )        
        f.write(level_progression_table)

    #webbrowser.open(LEVEL_PROGRESSION_TABLES_HTML)

