# Rebuild Notes

This Django rebuild mirrors the general functionality and information architecture of the referenced site without copying protected branding, text, imagery, logos, decorative motifs, or proprietary code.

## Safe content approach

- All copy in the seed data is original placeholder text.
- Visual styling is original and implemented with Django templates, custom CSS, and small JavaScript helpers.
- Placeholder contact details, program names, leadership names, and page bodies are meant to be replaced through the Django admin.

## Conservative assumptions

- The reference site suggests pages for history, charter, leadership, membership, projects, contact, and program details.
- Public details for membership workflows and some legal sections are not fully clear from the live site, so those pages are modeled as generic editable content pages.
- Contact address, map, and access information live in `SiteSettings` so editors maintain them from global settings.
- Cookie handling is implemented as a lightweight local-preference flow. It does not enable third-party analytics by default.
- Program and global galleries are supported, but seeded content intentionally avoids copied images and therefore starts without uploaded media files.
