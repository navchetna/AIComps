import json
import re
from base64 import b64decode
import os

def extract_markdown_and_images(json_file_path):
    with open(json_file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    if "content" not in data or len(data["content"]) == 0:
        return False

    base_name = os.path.splitext(os.path.basename(json_file_path))[0]
    output_dir = os.path.join('outputs', base_name)
    os.makedirs(output_dir, exist_ok=True)
    md_file_path = os.path.join(output_dir, 'output.md')

    content = data["content"][0]
    markdown = content.get("markdown", "")
    images_dict = content.get("images", {})

    image_refs = re.findall(r"!\[\]\((_page_[^\)]+)\)", markdown)

    for img_key in image_refs:
        if img_key in images_dict:
            img_data = b64decode(images_dict[img_key])
            img_filename = img_key
            img_path = os.path.join(output_dir, img_filename)
            with open(img_path, 'wb') as img_file:
                img_file.write(img_data)
            markdown = markdown.replace(f"![]({img_key})", f"![]({img_filename})")

    with open(md_file_path, 'w', encoding='utf-8') as md_file:
        md_file.write(markdown)

    return True

if __name__ == "__main__":
    file_name = '/home/intel/Ervin/Test/output.json'
    output_dir = os.path.splitext(os.path.basename(file_name))[0]
    success = extract_markdown_and_images(file_name)
    if success:
        print(f"Markdown extracted, images decoded/saved, and outputs stored in outputs/{output_dir}/")
    else:
        print("No markdown content found or extraction failed.")