import React, { useState, useEffect, useRef } from "react";
import axios from "axios";
import NewsCard from "../components/NewsCard";

function Home() {
  const [news, setNews] = useState([]);
  const [query, setQuery] = useState(" ");
  const [loading, setLoading] = useState(false);
  const [listening, setListening] = useState(false);
  const recognitionRef = useRef(null);

  const fetchNews = async () => {
    setLoading(true);
    try {
      const response = await axios.get(
        `http://127.0.0.1:8000/news?query=${query}`
      );
      setNews(response.data.articles || []);
    } catch (error) {
      console.error("Error fetching news:", error);
      setNews([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchNews();
    // eslint-disable-next-line
  }, []);

  // --- SPEECH TO TEXT LOGIC ---
  const startListening = () => {
    if (!("webkitSpeechRecognition" in window) && !("SpeechRecognition" in window)) {
      alert("Speech recognition is not supported in this browser.");
      return;
    }
    const SpeechRecognition =
      window.SpeechRecognition || window.webkitSpeechRecognition;
    recognitionRef.current = new SpeechRecognition();
    recognitionRef.current.lang = "en-US";
    recognitionRef.current.interimResults = false;
    recognitionRef.current.maxAlternatives = 1;

    recognitionRef.current.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      setQuery(transcript);
      setListening(false);
    };
    recognitionRef.current.onstart = () => setListening(true);
    recognitionRef.current.onend = () => setListening(false);
    recognitionRef.current.onerror = (event) => {
      setListening(false);
      alert("Speech recognition error: " + event.error);
    };

    recognitionRef.current.start();
  };

  return (
    <div className="p-6 bg-gray-50 min-h-screen">
      <div className="max-w-xl mx-auto mb-6 flex items-center space-x-2">
        <input
          type="text"
          placeholder="Search topics (e.g., AI, climate, sports)..."
          className="flex-grow border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-blue-500 outline-none"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
        <button
          onClick={fetchNews}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition"
        >
          Search
        </button>
        <button
          onClick={startListening}
          disabled={listening}
          title="Search by Voice"
          className={`ml-2 px-3 py-2 rounded-lg border hover:bg-blue-50 transition ${
            listening ? "bg-blue-200 text-blue-900" : "bg-white text-blue-600"
          }`}
        >
          {listening ? (
            <span className="animate-pulse">🎤 Listening...</span>
          ) : (
            <span>🎤</span>
          )}
        </button>
      </div>

      {loading ? (
        <p className="text-center text-gray-600">Fetching latest headlines...</p>
      ) : news.length > 0 ? (
        <div className="grid sm:grid-cols-2 md:grid-cols-3 gap-6">
          {news.map((article, index) => (
            <NewsCard key={index} article={article} />
          ))}
        </div>
      ) : (
        <p className="text-center text-gray-500 mt-10">
          No results found for your search.
        </p>
      )}
    </div>
  );
}

export default Home;
