# D&D Book Roadmap

This document outlines the planned features and improvements for D&D Book. For detailed specifications and acceptance criteria, please refer to the [GitHub Issues](https://github.com/grimirg/dndbook/issues) section of the project.

---

## v1.2.0

### Tools Section with GM Tools and Player Tools

Create a "Tools" section with two separate repositories for uploading and organizing attachments and resources.

**Acceptance Criteria:**
- Two distinct categories: GM Tools and Player Tools
- Functional Upload/Download system for PDF and images
- Folder or Tag-based organization
- Granular access permissions (Players cannot access GM tools)
- Search bar for quick resource filtering

#### Sub-stories

- **#15**: Add campaign notes button and left slide-out panel - Creates CampaignResourcesAndTools component with toggleable slide-out panel
- **#16**: Implement notes tree with "Personal notes" and "Player notes" sections - Two tree sections with CRUD operations
- **#17**: Simple Markdown textarea editor with Save and Cancel - Markdown editor for creating/editing notes
- **#18**: Backend API and storage for notes - CRUD endpoints and persistent storage for notes
- **#19**: Per-player visibility menu for notes - Menu to control which players can see specific notes
- **#20**: Authorization rules for players notes - Server-side rules to ensure players only see allowed notes
- **#21**: Personal notes section visible only to DM - Restricts personal notes section to DM only

---

**Note:** This roadmap is a living document and may be updated as priorities shift. Check the GitHub Issues for the most up-to-date status on each item.
