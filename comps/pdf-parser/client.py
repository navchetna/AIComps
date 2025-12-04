import os
from marker.converters.pdf import PdfConverter
from marker.models import create_model_dict
from marker.config.parser import ConfigParser
from marker.output import text_from_rendered

from tree_parser.tree import Tree
from tree_parser.treeparser import TreeParser


user = "ali"
# pdf_path = "/home/intel/Ervin/Test/2305.15032v1-2-3.pdf"
pdf_path = "home/test/assets/budget_speech.pdf"

# config = {
#     "output_format": "json",
#     "ADDITIONAL_KEY": "VALUE"
# }

# Build config parser
# config_parser = ConfigParser(config)

# Create converter
# converter = PdfConverter(
#     config=config_parser.generate_config_dict(),
#     artifact_dict=create_model_dict(),
#     processor_list=config_parser.get_processors(),
#     renderer=config_parser.get_renderer(),
#     llm_service=config_parser.get_llm_service(),
# )

converter = PdfConverter(
    artifact_dict=create_model_dict(),
)

tree = Tree(pdf_path, user_param=user)
tree_parser = TreeParser(user)
tree_parser.populate_tree(tree, converter)

tree_parser.generate_output_text(tree)
tree_parser.generate_output_json(tree)
