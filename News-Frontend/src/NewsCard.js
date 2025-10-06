import React from "react";

function NewsCard({ article }) {
  return (
    <div className="bg-white rounded-lg shadow hover:shadow-lg transition overflow-hidden">
      {article.image && (
        <img
          src={article.image}
          alt={article.title}
          className="w-full h-48 object-cover"
        />
      )}
      <div className="p-4">
        <h3 className="font-semibold text-lg mb-2 text-gray-800">
          {article.title || "No title available"}
        </h3>
        <p className="text-sm text-gray-600 mb-3">
          {article.description || "No description available."}
        </p>
        <p className="text-xs text-gray-500 mb-2">
          📅 {article.publishedAt ? new Date(article.publishedAt).toLocaleString() : "Unknown date"}
        </p>
        <a
          href={article.url}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-block text-blue-600 hover:text-blue-800 font-medium"
        >
          Read More →
        </a>
      </div>
    </div>
  );
}

export default NewsCard;
