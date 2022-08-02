import re
import json
import pprint
import markdown
import xmltodict
from typing import List
from lxml import html, etree

import wandb
import wandb.apis.reports as wb_report

wandb.require("report-editing")


def get_about_me_section(content: str) -> List:
    blocks = []
    _, _, rest = content.partition("<!-- about-me -->")
    result, _, _ = rest.partition("<!-- about-me-end -->")
    result = result.split("\n")
    unordered_list, in_list = [], False

    for line in result:

        if line.startswith("###"):
            blocks.append(wb_report.H2(line.split("###")[-1].strip()))
        elif line.startswith("-"):
            blocks.append(wb_report.H3(line[2:]))
            in_list = True

        if line.startswith("   -"):
            unordered_list.append(line.strip()[2:])
        elif line.strip() == "" and in_list:
            blocks.append(wb_report.UnorderedList(unordered_list))
            unordered_list, in_list = [], False

    return blocks


def get_content_section(content: str) -> List:
    blocks = []
    _, _, rest = content.partition("<!-- content -->")
    result, _, _ = rest.partition("<!-- content-end -->")
    result = result.split("\n")
    unordered_list, in_list = [], False
    for r in result:
        print(r)
    return result


if __name__ == "__main__":
    readme_content = str(open("README.md").read())
    htmldoc = html.fromstring(markdown.markdown(readme_content))
    xml_doc = etree.tostring(htmldoc)
    readme_content_dict = xmltodict.parse(xml_doc)["div"]
    blocks = [
        wb_report.H1(readme_content_dict["h1"]["#text"]),
        wb_report.H2(readme_content_dict["h3"][0]["#text"]),
        wb_report.HorizontalRule(),
        wb_report.MarkdownBlock(
            f"[![]({readme_content_dict['p'][1]['a'][0]['img']['@src']})]({readme_content_dict['p'][1]['a'][0]['@href']}) [![]({readme_content_dict['p'][1]['a'][1]['img']['@src']})]({readme_content_dict['p'][1]['a'][1]['@href']})"
        ),
    ]
    blocks += get_about_me_section(readme_content)
    # get_content_section(readme_content)
    
    for block in blocks:
        print(block)

    report = wb_report.Report(
        project="resume",
        entity="geekyrakshit",
        title="Resume of Soumik Rakshit",
        description="Interactive Resume of Soumik Rakshit",
        blocks=blocks,
    )
    report.save()
