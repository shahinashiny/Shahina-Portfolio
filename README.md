# Shahina Shaik | Data Engineering Portfolio

My personal portfolio website for showcasing my data engineering background, technical skills, experience, and selected project work.

**Live website:** [benevolent-wisp-556282.netlify.app](https://benevolent-wisp-556282.netlify.app/)  
**LinkedIn:** [linkedin.com/in/shahina-shaik-8ba21a24a](https://www.linkedin.com/in/shahina-shaik-8ba21a24a)  
**GitHub profile:** [github.com/shahinashiny](https://github.com/shahinashiny)

## About the site

The portfolio is a responsive, single-page static website built with HTML, CSS, and vanilla JavaScript. The styles and scripts are embedded in `index.html`, so no package installation or build step is needed.

### Features

- Responsive layout with mobile navigation.
- Animated SVG illustration of a data engineering workflow.
- Technical-skills section with category filters.
- Professional experience and an approximately 30% workflow-automation impact highlight.
- Featured attendance-intelligence platform overview.
- Education and contact sections.
- Contact form that opens the visitor's email application with a prefilled message.

The featured attendance platform is presented as a project overview, not as a public hosted demo or live application.

## Technology

- HTML5
- CSS3, responsive layouts, and reduced-motion styling
- Vanilla JavaScript
- SVG illustration
- Google Fonts (Inter and JetBrains Mono)
- Netlify for hosting

## Repository structure

```text
Shahina-Portfolio/
├── index.html   # Complete static website: markup, CSS, and JavaScript
└── README.md    # Project overview and maintenance notes
```

## Run locally

1. Clone the repository:

   ```bash
   git clone https://github.com/shahinashiny/Shahina-Portfolio.git
   cd Shahina-Portfolio
   ```

2. Open `index.html` in a browser.

   Alternatively, start a local static web server:

   ```bash
   python -m http.server 8000
   ```

   Then visit [http://localhost:8000](http://localhost:8000).

No Node.js dependencies or build command are required.

## Resume and contact behavior

The resume button uses a configurable `CONFIG.resume` value in the JavaScript section of `index.html`.

- When `CONFIG.resume` is set to a real, publicly accessible resume file URL, the button becomes a download link.
- When `CONFIG.resume` is empty, the button links to an email request instead. The button label should reflect that behavior.
- The contact form has no backend. It validates the required fields in the browser and opens the visitor's default email application; the message is not sent automatically.
- The email address, LinkedIn URL, and GitHub URL are configured in the same `CONFIG` object.

Only use a public resume URL if you are comfortable making that document publicly accessible.

## Deployment

The live site is hosted on Netlify. To deploy a new version, push the updated `index.html` to the connected GitHub repository and confirm that the Netlify deployment succeeds. If the site is not connected to automatic deployments, publish the repository's root directory as a static site.

## Before publishing changes

- Check all social and contact links.
- Confirm experience, education, project descriptions, and skills are accurate and up to date.
- Test navigation and the skills filters on desktop and mobile.
- Test the resume button's configured behavior.
- Confirm the contact form opens an email draft and does not imply that a message is submitted to a backend.
- Never commit passwords, API keys, or cloud credentials.

## Maintainer

**Shahina Shaik**  
[LinkedIn](https://www.linkedin.com/in/shahina-shaik-8ba21a24a) · [GitHub](https://github.com/shahinashiny) · [Live Portfolio](https://benevolent-wisp-556282.netlify.app/)
