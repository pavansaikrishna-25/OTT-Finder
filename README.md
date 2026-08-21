# 🎬 OTT Finder

**OTT Finder** is a Flask-based movie and TV discovery web application that helps users search for movies and web series, view title information, discover similar content, and find streaming availability in India.

🔗 **Live Demo:** https://ott-finder-5s66.onrender.com/
🔗 **GitHub:** https://github.com/pavansaikrishna-25/OTT-Finder

---

## ✨ Features

* 🔎 **Movie & TV Search** — Search for movies and TV series using the TMDB API.
* 🎯 **Relevant Search Results** — Results are ranked using title similarity to improve search relevance.
* ✍️ **Typo Correction** — Suggests a likely title when the search query does not return an exact result.
* 📺 **OTT Availability in India** — Shows available streaming, free, rent and other provider options for India.
* 🎬 **Title Details** — View posters, ratings, release year, overview and available languages.
* 🔗 **Similar Titles** — Discover up to five similar movies or TV series.
* 🔥 **Trending Picks** — Displays popular movies and TV shows on the homepage.
* ⚡ **Concurrent API Requests** — Uses Python's `ThreadPoolExecutor` to retrieve additional title information efficiently.
* 📱 **Responsive Interface** — Designed to work across desktop and mobile screen sizes.
* 🔐 **Environment Variables** — API credentials are loaded securely using environment variables.

---

## 🖥️ How It Works

The application uses the **TMDB API** as its movie and TV data source.

### Search Flow

```text
User enters a movie / TV title
          ↓
      Flask Server
          ↓
       TMDB API
          ↓
 Search & rank results
          ↓
 Display results
```

If no suitable result is found:

```text
Search Query
     ↓
No exact results
     ↓
Fetch popular/trending titles
     ↓
Calculate title similarity
     ↓
Suggest the closest matching title
```

### OTT Availability Flow

```text
User selects a title
        ↓
Flask requests title details
        ↓
Flask requests watch providers
        ↓
TMDB provider data
        ↓
Filter India ("IN")
        ↓
Display available providers
```

---

## 🛠️ Technologies Used

### Backend

* Python
* Flask
* Requests
* python-dotenv

### Frontend

* HTML5
* CSS3
* Jinja2 Templates

### API

* TMDB API

### Python Concepts

* REST API integration
* Concurrent requests with `ThreadPoolExecutor`
* Fuzzy/similarity-based title matching using `SequenceMatcher`
* Environment variable configuration
* Error handling for API requests

### Deployment

* Gunicorn
* Render

---

## 📂 Project Structure

```text
OTT-Finder/
│
├── app.py
├── requirements.txt
├── .gitignore
│
├── templates/
│   ├── index.html
│   └── details.html
│
└── static/
    └── style.css
```

---

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/pavansaikrishna-25/OTT-Finder.git
cd OTT-Finder
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

Activate it on Windows:

```powershell
venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure the TMDB API key

Create a `.env` file in the project root:

```env
TMDB_API_KEY=your_tmdb_api_key
```

> Never commit your `.env` file or expose your API key publicly.

### 5. Run the application

```bash
python app.py
```

The application will be available locally at:

```text
http://127.0.0.1:5000
```

---

## 🔑 Environment Variables

The application requires the following environment variable:

| Variable       | Description                                   |
| -------------- | --------------------------------------------- |
| `TMDB_API_KEY` | API key used to access TMDB movie and TV data |

---

## 📡 TMDB API Integration

OTT Finder uses TMDB endpoints for:

* Multi-search
* Movie details
* TV details
* Trending titles
* Similar movies
* Similar TV shows
* Watch-provider information

The application retrieves streaming-provider information specifically for the **India (`IN`) region**.

---

## ⚡ Performance Considerations

For search results, OTT Finder retrieves additional language information for multiple titles.

Instead of processing every request sequentially, the application uses Python's:

```python
ThreadPoolExecutor
```

This allows multiple independent API requests to be processed concurrently.

The application also uses request timeouts and handles API request failures to prevent individual API failures from crashing the application.

---

## 🔍 Search Intelligence

OTT Finder uses `SequenceMatcher` to calculate similarity between the user's query and available titles.

This allows the application to:

* Rank search results by title similarity.
* Identify possible spelling mistakes.
* Suggest a likely title when an exact search produces no results.

For example:

```text
User input:
spidarman

        ↓

Similarity matching

        ↓

Suggested title:
Spider-Man
```

---

## 📱 Responsive Design

The frontend is built using HTML and CSS with a responsive layout so that the application can be used on:

* 💻 Desktop
* 💻 Laptop
* 📱 Mobile devices

---

## 🎯 Future Improvements

Potential improvements include:

* User accounts and watchlists
* Personalized recommendations
* Genre-based browsing
* Advanced filtering
* Language-based filtering
* Streaming-provider deep links
* Caching TMDB API responses
* Improved search ranking
* Automated testing
* Progressive Web App support

---

## 📸 Screenshots

Screenshots of the application will be added here.

### Homepage

<img width="1890" height="731" alt="image" src="https://github.com/user-attachments/assets/293f7840-0058-4400-9ced-5a76ee405f60" />


### Search Results

<img width="1896" height="879" alt="image" src="https://github.com/user-attachments/assets/11abb8be-3ef8-4336-9964-99b8569a1e0e" />


### Title Details & OTT Availability

<img width="1856" height="856" alt="image" src="https://github.com/user-attachments/assets/a0e36f5c-3b23-4f24-ac7b-c25c43760f00" />


---

## 👨‍💻 Author

**Pavan Sai Krishna**

Python Developer focused on building web applications, APIs and practical software solutions.

* GitHub: https://github.com/pavansaikrishna-25
* LinkedIn: *Add your LinkedIn profile here*

---

## 📄 License

This project is intended for educational and portfolio purposes.

Movie and TV metadata and images are provided through **TMDB**.

This project is **not affiliated with or endorsed by TMDB**.
