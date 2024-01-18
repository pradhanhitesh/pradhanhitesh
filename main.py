from jinja2 import Environment, FileSystemLoader
from scripts import custom

def main():
    search_terms = ["dementia","dementia+alzheimers","alzheimers","alzheimers+disease","dementia+MRI","alzheimers+MRI",
                    "dementia+alzheimers+MRI"]

    data_df,data_dict = custom.arrange_metadata(search_terms)
    custom.update_pubmed_json(data_dict=data_dict)
    custom.generate_plot(data_df,time=custom.get_timestamp())
    template_vars = custom.generate_html_for_plot()

    env = Environment(loader=FileSystemLoader("template"))
    template = env.get_template("template.html")
    output_from_parsed_template = template.render(template_vars)

    with open("README.md", "w+") as fh:
        fh.write(output_from_parsed_template)

    return

if __name__ == "__main__":
    main()