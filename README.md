# LinkedIn Profile Crawler

A Python-based web scraper that extracts professional information from LinkedIn profiles. This tool uses Selenium WebDriver to navigate LinkedIn and collect structured data from public profiles.

## Features

- Extracts comprehensive profile information:

  - Basic Information (Name, Title, Location)
  - Education Details (Schools, Degrees, Fields of Study)
  - Work Experience (Roles, Companies, Durations)
  - Skills

- Enhanced anti-detection measures:
  - Random delays between actions
  - User-agent rotation
  - Browser fingerprint randomization
  - Smooth scrolling simulation

## Prerequisites

- Python 3.x
- Google Chrome Browser
- LinkedIn Account

## Installation

1. Clone the repository:

```bash
git clone <repository-url>
cd linkedin-crawler
```

2. Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install required packages:

```bash
pip install selenium webdriver_manager python-dotenv fake-useragent random2
```

4. Create a `.env` file in the project root and add your LinkedIn credentials:

```
LINKEDIN_EMAIL=your_email@example.com
LINKEDIN_PASSWORD=your_password
```

## Usage

1. Make sure your LinkedIn credentials are set in the `.env` file

2. Run the script:

```bash
python linkedin_crawler.py
```

3. When prompted, enter the LinkedIn profile URL you want to scrape:

```
Enter LinkedIn profile URL (or 'quit' to exit): https://www.linkedin.com/in/username
```

4. The script will save the extracted data in a JSON file with a timestamp:

```json
{
    "name": "...",
    "title": "...",
    "education": [...],
    "experience": [...],
    "skills": [...]
}
```

## Output Structure

The crawler generates a JSON file with the following structure:

```json
{
  "name": "Example Name",
  "title": "Current Title",
  "education": [
    {
      "school": "University Name",
      "degree": "Degree Type",
      "field": "Field of Study",
      "duration": "2020 - 2024"
    }
  ],
  "experience": [
    {
      "role": "Job Title",
      "company": "Company Name",
      "duration": "Start Date - End Date",
      "location": "City, State, Country"
    }
  ],
  "skills": ["Skill 1", "Skill 2", "Skill 3"]
}
```

## Important Notes

- This tool is for educational purposes only
- Ensure compliance with LinkedIn's terms of service
- Use responsibly and avoid excessive requests
- Consider implementing delays between profile scrapes
- Some profiles might not be accessible based on your LinkedIn connection level

## Error Handling

The script includes error handling for common scenarios:

- Network timeouts
- Missing profile sections
- Different profile layouts
- Login verification
- Anti-bot detection

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Disclaimer

This tool is for educational purposes only. Users are responsible for ensuring their use of this tool complies with LinkedIn's terms of service and applicable laws.
