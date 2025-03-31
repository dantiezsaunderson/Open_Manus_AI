"""
News API Integration Module

This module provides integration with news data APIs for the Open Manus AI system.
"""

import os
import logging
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Configure logging
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class NewsAPI:
    """
    News API integration for accessing news articles and headlines.
    """
    
    def __init__(self):
        """Initialize the News API integration."""
        self.newsapi_key = os.getenv("NEWSAPI_KEY")
        
        if not self.newsapi_key:
            logger.warning("News API key not found in environment variables")
        else:
            logger.info("News API integration initialized successfully")
    
    def get_top_headlines(self, country="us", category=None, query=None, page_size=10, page=1):
        """
        Get top headlines from News API.
        
        Args:
            country (str, optional): 2-letter ISO 3166-1 country code
            category (str, optional): Category of news (business, entertainment, general, health, science, sports, technology)
            query (str, optional): Keywords or phrases to search for
            page_size (int, optional): Number of results to return per page (max 100)
            page (int, optional): Page number
            
        Returns:
            dict: Top headlines data
        """
        try:
            if not self.newsapi_key:
                return {"success": False, "error": "News API key not configured"}
            
            # Set up parameters
            params = {
                "country": country,
                "pageSize": min(page_size, 100),  # Ensure page_size doesn't exceed 100
                "page": page,
                "apiKey": self.newsapi_key
            }
            
            # Add optional parameters if provided
            if category:
                params["category"] = category
            if query:
                params["q"] = query
            
            # Make API request
            url = "https://newsapi.org/v2/top-headlines"
            response = requests.get(url, params=params)
            data = response.json()
            
            # Check for error
            if data.get("status") != "ok":
                return {"success": False, "error": data.get("message", "Unknown error")}
            
            # Process and format the data
            articles = data.get("articles", [])
            formatted_articles = []
            
            for article in articles:
                formatted_article = {
                    "title": article.get("title", ""),
                    "description": article.get("description", ""),
                    "content": article.get("content", ""),
                    "url": article.get("url", ""),
                    "image_url": article.get("urlToImage", ""),
                    "source": {
                        "name": article.get("source", {}).get("name", ""),
                        "id": article.get("source", {}).get("id", "")
                    },
                    "author": article.get("author", ""),
                    "published_at": article.get("publishedAt", "")
                }
                formatted_articles.append(formatted_article)
            
            return {
                "headlines": formatted_articles,
                "total_results": data.get("totalResults", 0),
                "page": page,
                "page_size": page_size,
                "country": country,
                "category": category,
                "query": query,
                "timestamp": datetime.now().isoformat(),
                "success": True
            }
            
        except Exception as e:
            logger.error(f"Error retrieving top headlines: {e}")
            return {"success": False, "error": str(e)}
    
    def search_news(self, query, from_date=None, to_date=None, language="en", sort_by="publishedAt", page_size=10, page=1):
        """
        Search for news articles from News API.
        
        Args:
            query (str): Keywords or phrases to search for
            from_date (str, optional): Start date in YYYY-MM-DD format
            to_date (str, optional): End date in YYYY-MM-DD format
            language (str, optional): 2-letter ISO 639-1 language code
            sort_by (str, optional): Sort order (relevancy, popularity, publishedAt)
            page_size (int, optional): Number of results to return per page (max 100)
            page (int, optional): Page number
            
        Returns:
            dict: News search results
        """
        try:
            if not self.newsapi_key:
                return {"success": False, "error": "News API key not configured"}
            
            # Set default dates if not provided
            if not from_date:
                from_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
            if not to_date:
                to_date = datetime.now().strftime("%Y-%m-%d")
            
            # Set up parameters
            params = {
                "q": query,
                "from": from_date,
                "to": to_date,
                "language": language,
                "sortBy": sort_by,
                "pageSize": min(page_size, 100),  # Ensure page_size doesn't exceed 100
                "page": page,
                "apiKey": self.newsapi_key
            }
            
            # Make API request
            url = "https://newsapi.org/v2/everything"
            response = requests.get(url, params=params)
            data = response.json()
            
            # Check for error
            if data.get("status") != "ok":
                return {"success": False, "error": data.get("message", "Unknown error")}
            
            # Process and format the data
            articles = data.get("articles", [])
            formatted_articles = []
            
            for article in articles:
                formatted_article = {
                    "title": article.get("title", ""),
                    "description": article.get("description", ""),
                    "content": article.get("content", ""),
                    "url": article.get("url", ""),
                    "image_url": article.get("urlToImage", ""),
                    "source": {
                        "name": article.get("source", {}).get("name", ""),
                        "id": article.get("source", {}).get("id", "")
                    },
                    "author": article.get("author", ""),
                    "published_at": article.get("publishedAt", "")
                }
                formatted_articles.append(formatted_article)
            
            return {
                "articles": formatted_articles,
                "total_results": data.get("totalResults", 0),
                "page": page,
                "page_size": page_size,
                "query": query,
                "from_date": from_date,
                "to_date": to_date,
                "language": language,
                "sort_by": sort_by,
                "timestamp": datetime.now().isoformat(),
                "success": True
            }
            
        except Exception as e:
            logger.error(f"Error searching news: {e}")
            return {"success": False, "error": str(e)}
    
    def get_news_sources(self, category=None, language="en", country=None):
        """
        Get available news sources from News API.
        
        Args:
            category (str, optional): Category of news (business, entertainment, general, health, science, sports, technology)
            language (str, optional): 2-letter ISO 639-1 language code
            country (str, optional): 2-letter ISO 3166-1 country code
            
        Returns:
            dict: News sources data
        """
        try:
            if not self.newsapi_key:
                return {"success": False, "error": "News API key not configured"}
            
            # Set up parameters
            params = {
                "language": language,
                "apiKey": self.newsapi_key
            }
            
            # Add optional parameters if provided
            if category:
                params["category"] = category
            if country:
                params["country"] = country
            
            # Make API request
            url = "https://newsapi.org/v2/sources"
            response = requests.get(url, params=params)
            data = response.json()
            
            # Check for error
            if data.get("status") != "ok":
                return {"success": False, "error": data.get("message", "Unknown error")}
            
            # Process and format the data
            sources = data.get("sources", [])
            formatted_sources = []
            
            for source in sources:
                formatted_source = {
                    "id": source.get("id", ""),
                    "name": source.get("name", ""),
                    "description": source.get("description", ""),
                    "url": source.get("url", ""),
                    "category": source.get("category", ""),
                    "language": source.get("language", ""),
                    "country": source.get("country", "")
                }
                formatted_sources.append(formatted_source)
            
            return {
                "sources": formatted_sources,
                "category": category,
                "language": language,
                "country": country,
                "timestamp": datetime.now().isoformat(),
                "success": True
            }
            
        except Exception as e:
            logger.error(f"Error retrieving news sources: {e}")
            return {"success": False, "error": str(e)}
    
    def summarize_news(self, articles, ai_engine=None):
        """
        Summarize a list of news articles using AI.
        
        Args:
            articles (list): List of news articles
            ai_engine (AIEngine, optional): AI engine instance for summarization
            
        Returns:
            dict: Summarized news data
        """
        try:
            if not articles:
                return {"success": False, "error": "No articles provided for summarization"}
            
            # If AI engine is provided, use it for summarization
            if ai_engine:
                # Prepare the input for the AI
                article_texts = []
                for i, article in enumerate(articles[:5]):  # Limit to 5 articles for summarization
                    article_text = f"Article {i+1}: {article.get('title', '')}\n"
                    article_text += f"Source: {article.get('source', {}).get('name', '')}\n"
                    article_text += f"Description: {article.get('description', '')}\n"
                    article_text += f"Content: {article.get('content', '')}\n\n"
                    article_texts.append(article_text)
                
                prompt = "Summarize the following news articles into a concise overview:\n\n"
                prompt += "\n".join(article_texts)
                prompt += "\nProvide a brief summary of the key points from these articles."
                
                system_message = "You are a news summarization assistant. Provide concise, factual summaries of news articles."
                
                # Generate summary using AI
                response = ai_engine.generate_response(prompt, system_message=system_message)
                
                return {
                    "summary": response,
                    "articles_summarized": len(articles[:5]),
                    "timestamp": datetime.now().isoformat(),
                    "success": True
                }
            else:
                # Without AI engine, return basic metadata
                return {
                    "articles_count": len(articles),
                    "topics": self._extract_topics(articles),
                    "sources": list(set(article.get("source", {}).get("name", "") for article in articles if article.get("source"))),
                    "timestamp": datetime.now().isoformat(),
                    "success": True,
                    "message": "AI engine not provided for detailed summarization"
                }
            
        except Exception as e:
            logger.error(f"Error summarizing news: {e}")
            return {"success": False, "error": str(e)}
    
    def _extract_topics(self, articles):
        """
        Extract common topics from a list of articles.
        
        Args:
            articles (list): List of news articles
            
        Returns:
            list: Common topics
        """
        # Simple keyword extraction from titles
        all_words = []
        for article in articles:
            title = article.get("title", "").lower()
            # Remove punctuation and split into words
            words = ''.join(c if c.isalnum() or c.isspace() else ' ' for c in title).split()
            all_words.extend(words)
        
        # Count word frequencies
        word_counts = {}
        for word in all_words:
            if len(word) > 3:  # Ignore short words
                word_counts[word] = word_counts.get(word, 0) + 1
        
        # Get top words
        top_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        return [word for word, count in top_words]
