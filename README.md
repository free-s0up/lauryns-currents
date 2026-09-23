# Soggy Beans Hosting Template

A GitHub Pages template for hosting and sharing Soggy Beans Currents

## How to use

1. Create a repository from this template
2. Enable GitHub Pages for the repository
3. Customize your site in `config.js`
4. Export a Current from Soggy Beans
5. Upload the exported `.zip` file into the `files` folder
6. Commit your changes

That’s it.

The GitHub Action will automatically:

- Read the Current's name and description from the zip
- Give each Current a permanent URL
- Update existing Currents when a new export with the same ID is uploaded
- Keep the original URL even if the Current's name or description changes
- Update `files.json` automatically