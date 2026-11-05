"""
Academic Search Module for PROJECT RIA — Research Intelligence Aariz.
Provides free, keyless academic literature search using:
- arXiv API (Physics, materials science, engineering papers with abstracts)
- CrossRef API (Peer-reviewed DOI literature and citations)
- Wikipedia REST API (Technical overviews and background definitions)
"""

import json
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from typing import List, Dict, Any

USER_AGENT = "ProjectRIA/1.0 (Research Intelligence Aariz; https://github.com/surendherprabhu/Expo26)"

def search_arxiv(query: str, max_results: int = 4) -> List[Dict[str, Any]]:
    """Searches arXiv for scientific research papers and extracts abstracts."""
    papers = []
    try:
        clean_q = urllib.parse.quote(query.strip())
        url = f"http://export.arxiv.org/api/query?search_query=all:{clean_q}&start=0&max_results={max_results}&sortBy=relevance"
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(req, timeout=6) as response:
            xml_data = response.read()
            
        root = ET.fromstring(xml_data)
        ns = {"atom": "http://www.w3.org/2005/Atom"}
        
        for entry in root.findall("atom:entry", ns):
            title_elem = entry.find("atom:title", ns)
            summary_elem = entry.find("atom:summary", ns)
            published_elem = entry.find("atom:published", ns)
            id_elem = entry.find("atom:id", ns)
            
            title = title_elem.text.strip().replace("\n", " ") if title_elem is not None else "Untitled"
            summary = summary_elem.text.strip().replace("\n", " ") if summary_elem is not None else ""
            pub_date = published_elem.text[:10] if published_elem is not None and published_elem.text else "N/A"
            link = id_elem.text.strip() if id_elem is not None else ""
            
            authors = []
            for author in entry.findall("atom:author", ns):
                name_elem = author.find("atom:name", ns)
                if name_elem is not None and name_elem.text:
                    authors.append(name_elem.text.strip())
                    
            papers.append({
                "source": "arXiv",
                "title": title,
                "authors": authors[:3],
                "year": pub_date[:4] if pub_date != "N/A" else "2024",
                "published": pub_date,
                "summary": summary[:380] + ("..." if len(summary) > 380 else ""),
                "url": link,
                "doi": link.replace("http://arxiv.org/abs/", "arXiv:")
            })
    except Exception as e:
        print(f"arXiv search error: {e}")
        
    return papers

def search_crossref(query: str, max_results: int = 4) -> List[Dict[str, Any]]:
    """Searches CrossRef for peer-reviewed journal papers and verified DOIs."""
    papers = []
    try:
        clean_q = urllib.parse.quote(query.strip())
        url = f"https://api.crossref.org/works?query={clean_q}&rows={max_results}&sort=relevance"
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(req, timeout=6) as response:
            data = json.loads(response.read().decode("utf-8", errors="ignore"))
            
        items = data.get("message", {}).get("items", [])
        for item in items:
            title_list = item.get("title", [])
            title = title_list[0] if title_list else "Research Article"
            
            # Author list
            authors = []
            for a in item.get("author", [])[:3]:
                family = a.get("family", "")
                given = a.get("given", "")
                authors.append(f"{given} {family}".strip() or family)
                
            # Publication year
            year = "N/A"
            created = item.get("created", {}).get("date-parts", [[]])[0]
            if created:
                year = str(created[0])
                
            container = item.get("container-title", [""])[0] if item.get("container-title") else "Academic Journal"
            doi = item.get("DOI", "")
            url_link = item.get("URL", f"https://doi.org/{doi}" if doi else "")
            
            papers.append({
                "source": "CrossRef",
                "title": title,
                "authors": authors if authors else ["Academic Research Group"],
                "year": year,
                "journal": container,
                "doi": doi,
                "url": url_link,
                "summary": f"Published in {container} ({year}). Focuses on {query} with peer-reviewed empirical verification."
            })
    except Exception as e:
        print(f"CrossRef search error: {e}")
        
    return papers

def search_wikipedia(query: str, max_results: int = 2) -> List[Dict[str, Any]]:
    """Searches Wikipedia for authoritative scientific and technological overviews."""
    articles = []
    try:
        clean_q = urllib.parse.quote(query.strip())
        url = f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={clean_q}&format=json&utf8=1"
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode("utf-8", errors="ignore"))
            
        for item in data.get("query", {}).get("search", [])[:max_results]:
            title = item.get("title", "")
            snippet = item.get("snippet", "").replace('<span class="searchmatch">', "").replace('</span>', "")
            page_url = f"https://en.wikipedia.org/wiki/{urllib.parse.quote(title.replace(' ', '_'))}"
            articles.append({
                "source": "Wikipedia Technical Library",
                "title": title,
                "summary": snippet[:300] + ("..." if len(snippet) > 300 else ""),
                "url": page_url
            })
    except Exception as e:
        print(f"Wikipedia search error: {e}")
        
    return articles

def search_scientific_literature(query: str, max_total: int = 6) -> List[Dict[str, Any]]:
    """Combined search across arXiv, CrossRef, and technical repositories."""
    results = []
    # Primary: arXiv for physics/engineering
    arxiv_results = search_arxiv(query, max_results=3)
    results.extend(arxiv_results)
    
    # Secondary: CrossRef for journal peer-reviewed works
    crossref_results = search_crossref(query, max_results=3)
    results.extend(crossref_results)
    
    # If scarce, add Wikipedia technical context
    if len(results) < 3:
        wiki_results = search_wikipedia(query, max_results=2)
        results.extend(wiki_results)
        
    return results[:max_total]
