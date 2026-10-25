# Coffice ☕💻

A web application for finding work-friendly cafés (Wi-Fi, power outlets, noise levels, etc.).

Users can suggest new cafés through a multi-step form.

> 🚧 **Status:** Work in progress, developed as part of my portfolio.

## Features implemented so far

- Search for cafés using Geoapify autocomplete, with automatic form filling
- Manually add a café with address autocomplete
- Automatically load opening hours from OpenStreetMap data
- Multi-step form with client-side and server-side validation
- Photo uploads with file type, size, and content validation
- Detection of cafés that are already in the database or are waiting for approval

## Technologies

Python, Flask, SQLAlchemy (SQLite), JavaScript, Bootstrap 5, Geoapify API

## How to run it

1. Clone the repository: git clone ...
2. Create a virtual environment: python -m venv venv and activate it.
3. Install the dependencies: pip install -r requirements.txt
4. Sign up for a Geoapify account and get your own free API key.
5. Create a .env file and add your API key: GEOAPIFY_API_KEY=your_api_key
6. Run the application: python main.py

## Planned Features
- [ ] Admin login and Café suggestions approval
- [ ] User registration and login
- [ ] Café listing and filtering
- [ ] User possibility to suggest changes on Café / write a review
