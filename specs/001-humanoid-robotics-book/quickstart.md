# Quickstart: Humanoid Robotics AI Book

This guide provides instructions to set up the development environment, build the Docusaurus site, and run it locally.

## Prerequisites

-   Node.js (v18.x or later)
-   npm (v9.x or later)
-   Git

## 1. Initialize Docusaurus Project

This project is designed to be a Docusaurus website. If this is the first time setting up the project, initialize Docusaurus in the current directory.

```bash
# This will scaffold a new Docusaurus site in the current directory
npx create-docusaurus@latest . classic
```
*Note: This command will add a number of files and directories. Commit them to the repository.*

## 2. Install Dependencies

Once the project is initialized, install the dependencies.

```bash
npm install
```

## 3. Run the Development Server

Start the local development server. This will open a browser window with a live-reloading preview of the book.

```bash
npm run start
```

The site will be available at `http://localhost:3000`. The content for the book will be added to the `/docs` directory.

## 4. Build the Static Site

To create a production-ready static build of the site, run the following command.

```bash
npm run build
```

The output will be placed in the `/build` directory. This is the content that gets deployed to GitHub Pages.

## 5. Deployment

Deployment to GitHub Pages is handled automatically by a GitHub Action whenever changes are pushed to the `main` branch. Manual deployment can be done using the following command (requires appropriate permissions).

```bash
npm run deploy
```
