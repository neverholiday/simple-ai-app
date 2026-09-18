---
status: accepted
---

# Server-rendered FastAPI, not Streamlit or Gradio

The app uses FastAPI with server-rendered Jinja2 templates and a small amount of vanilla JavaScript. The lessons depend on the audience seeing real HTTP behaviour: a form submit that saves a Recipe, a slow request, a timeout, and a Fallback page instead of an error page. Pydantic, already used for the Recipe schema in the original scripts, doubles as the model's output schema and as Draft validation.

## Considered Options

- Streamlit or Gradio: rejected. They hide requests and routes, rerun the whole script on each interaction, and blur the line between UI state and saved data, which erases the Draft and Review boundary the demo exists to show. Do not "simplify" the app to one of these.
- Flask: workable, but has no built-in Pydantic validation and makes per-attempt timeouts more awkward to demonstrate.
- JSON API with a React or Vue front end: needs a build step and doubles the code on screen without adding to any lesson.
