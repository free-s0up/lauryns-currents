import json
import os
import re
import unicodedata
import zipfile

DIRECTORY = "files"
INDEX_PATH = os.path.join(DIRECTORY, "files.json")


def slugify(value):
    value = unicodedata.normalize("NFKD", value)
    value = value.encode("ascii", "ignore").decode("ascii")
    value = value.lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    value = value.strip("-")

    return value or "current"


def read_bundle(path):
    with zipfile.ZipFile(path, "r") as zip_file:
        with zip_file.open("repository.json") as repository_file:
            repository = json.load(repository_file)

    meta = repository.get("meta", {})

    bundle_id = meta.get("id")
    name = meta.get("name")
    description = meta.get("description", "")

    if not bundle_id:
        raise ValueError(f"{path} has no meta.id")

    if not name:
        raise ValueError(f"{path} has no meta.name")

    return bundle_id, name, description


existing = []

if os.path.exists(INDEX_PATH):
    with open(INDEX_PATH, "r", encoding="utf-8") as file:
        data = json.load(file)

        # old files.json format was just an array of filenames ignore those entries during the first migration
        if all(isinstance(item, dict) for item in data):
            existing = data


bundles_by_id = {
    bundle["id"]: bundle
    for bundle in existing
}

used_slugs = {
    bundle["slug"]
    for bundle in existing
}

published_files = {
    f'{bundle["slug"]}.zip'
    for bundle in existing
}

# anything that isn't already a published slug ZIP is treated as a newly uploaded bundle
uploads = [
    filename
    for filename in os.listdir(DIRECTORY)
    if filename.lower().endswith(".zip")
    and filename not in published_files
]

uploads.sort()

for filename in uploads:
    source_path = os.path.join(DIRECTORY, filename)

    bundle_id, name, description = read_bundle(source_path)

    if bundle_id in bundles_by_id:
        # existing current so preserve its permanent slug
        bundle = bundles_by_id[bundle_id]
        slug = bundle["slug"]

        bundle["name"] = name
        bundle["description"] = description

        print(f"Updating {slug} from {filename}")
    else:
        # new current so create its permanent slug from its first name
        base_slug = slugify(name)
        slug = base_slug
        suffix = 2

        while slug in used_slugs:
            slug = f"{base_slug}-{suffix}"
            suffix += 1

        used_slugs.add(slug)

        bundle = {
            "id": bundle_id,
            "slug": slug,
            "name": name,
            "description": description
        }

        bundles_by_id[bundle_id] = bundle

        print(f"Adding {slug} from {filename}")

    target_path = os.path.join(DIRECTORY, f"{slug}.zip")

    if os.path.abspath(source_path) != os.path.abspath(target_path):
        os.replace(source_path, target_path)


# remove currents whose published ZIP has been deleted
bundles_by_id = {
    bundle_id: bundle
    for bundle_id, bundle in bundles_by_id.items()
    if os.path.exists(os.path.join(DIRECTORY, f'{bundle["slug"]}.zip'))
}


bundles = sorted(
    bundles_by_id.values(),
    key=lambda bundle: bundle["name"].lower()
)

with open(INDEX_PATH, "w", encoding="utf-8") as file:
    json.dump(bundles, file, indent=2, ensure_ascii=False)
    file.write("\n")


print()
print("Generated files.json:")
print(json.dumps(bundles, indent=2, ensure_ascii=False))