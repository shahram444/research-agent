#!/usr/bin/env python3
"""
Research Agent GUI - Multi-API Version
=======================================

Supports both Claude (Anthropic) and ChatGPT (OpenAI) APIs.

Requirements:
    pip install anthropic openai pymupdf

Usage:
    python research_agent_gui.py

Set your API key (choose one):
    export ANTHROPIC_API_KEY="your-claude-key"
    export OPENAI_API_KEY="your-chatgpt-key"
"""

import os
import sys
import json
import re
import threading
from pathlib import Path
from typing import Optional, List, Dict, Any
import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext, messagebox

# Check dependencies
def check_deps():
    required = {'anthropic': 'anthropic', 'openai': 'openai', 'fitz': 'pymupdf'}
    missing = []
    for mod, pkg in required.items():
        try:
            __import__(mod)
        except ImportError:
            missing.append(pkg)
    if missing:
        print(f"Installing: {', '.join(missing)}")
        import subprocess
        subprocess.check_call([sys.executable, '-m', 'pip', 'install'] + missing)
        print("Packages installed. Please restart the script.")
        sys.exit(0)

check_deps()

import anthropic
import openai
import fitz


class AIClient:
    """Unified AI client that supports both Claude and ChatGPT."""
    
    def __init__(self, provider: str = "claude", api_key: str = ""):
        self.provider = provider.lower()
        self.api_key = api_key
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize the appropriate client based on provider."""
        if not self.api_key:
            return
        
        try:
            if self.provider == "claude":
                self.client = anthropic.Anthropic(api_key=self.api_key)
            elif self.provider == "chatgpt":
                self.client = openai.OpenAI(api_key=self.api_key)
        except Exception as e:
            print(f"Error initializing client: {e}")
            self.client = None
    
    def set_provider(self, provider: str, api_key: str):
        """Switch provider and API key."""
        self.provider = provider.lower()
        self.api_key = api_key
        self._initialize_client()
    
    def is_ready(self) -> bool:
        """Check if client is ready to make requests."""
        return self.client is not None
    
    def chat(self, messages: List[Dict], use_web_search: bool = False) -> str:
        """Send a chat request to the AI provider."""
        if not self.is_ready():
            return "Error: API client not initialized. Please check your API key."
        
        try:
            if self.provider == "claude":
                return self._claude_chat(messages, use_web_search)
            elif self.provider == "chatgpt":
                return self._chatgpt_chat(messages, use_web_search)
            else:
                return f"Error: Unknown provider {self.provider}"
        except Exception as e:
            return f"Error: {str(e)}"
    
    def _claude_chat(self, messages: List[Dict], use_web_search: bool = False) -> str:
        """Send chat to Claude API."""
        kwargs = {
            "model": "claude-sonnet-4-20250514",
            "max_tokens": 4096,
            "messages": messages
        }
        
        if use_web_search:
            kwargs["tools"] = [{"type": "web_search_20250305", "name": "web_search"}]
        
        response = self.client.messages.create(**kwargs)
        
        # Extract text from response
        result = ""
        for block in response.content:
            if hasattr(block, 'text'):
                result += block.text
        
        return result
    
    def _chatgpt_chat(self, messages: List[Dict], use_web_search: bool = False) -> str:
        """Send chat to ChatGPT API."""
        # Convert messages format if needed
        formatted_messages = []
        for msg in messages:
            formatted_messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })
        
        # Use appropriate model
        model = "gpt-4o" if use_web_search else "gpt-4o-mini"
        
        response = self.client.chat.completions.create(
            model=model,
            messages=formatted_messages,
            max_tokens=4096
        )
        
        return response.choices[0].message.content


class PDFProcessor:
    """PDF text extraction utilities."""
    
    @staticmethod
    def extract_text(pdf_path: str, max_pages: int = 30) -> str:
        try:
            doc = fitz.open(pdf_path)
            parts = []
            for i in range(min(len(doc), max_pages)):
                text = doc[i].get_text()
                if text.strip():
                    parts.append(f"--- Page {i+1} ---\n{text}")
            doc.close()
            return "\n\n".join(parts)
        except Exception as e:
            return f"Error: {e}"
    
    @staticmethod
    def get_metadata(pdf_path: str) -> Dict:
        try:
            doc = fitz.open(pdf_path)
            meta = doc.metadata
            pages = len(doc)
            doc.close()
            return {
                "title": meta.get("title", "Unknown"),
                "author": meta.get("author", "Unknown"),
                "pages": pages,
                "filename": os.path.basename(pdf_path),
                "path": pdf_path
            }
        except Exception as e:
            return {"error": str(e), "filename": os.path.basename(pdf_path), "path": pdf_path}


class ResearchAgentGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Research Agent - AI Paper Analysis (Claude & ChatGPT)")
        self.root.geometry("1200x850")
        
        # API setup
        self.provider = "claude"  # Default
        self.api_key = ""
        self.ai_client = None
        self.papers_folder = ""
        self.loaded_papers: Dict[str, Dict] = {}
        
        # Style
        style = ttk.Style()
        style.theme_use('clam')
        
        self.setup_ui()
        self.load_saved_settings()
    
    def setup_ui(self):
        """Build the user interface."""
        # Main notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Tab 1: Paper Finder
        self.finder_frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.finder_frame, text="🔍 Paper Finder")
        self.setup_finder_tab()
        
        # Tab 2: Local Paper Analyzer
        self.analyzer_frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.analyzer_frame, text="📁 Local Paper Analyzer")
        self.setup_analyzer_tab()
        
        # Tab 3: Citation Verifier
        self.verifier_frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.verifier_frame, text="✓ Citation Verifier")
        self.setup_verifier_tab()
        
        # Tab 4: Settings
        self.settings_frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.settings_frame, text="⚙ Settings")
        self.setup_settings_tab()
    
    def setup_finder_tab(self):
        """Setup the paper finder tab."""
        # Search frame
        search_frame = ttk.LabelFrame(self.finder_frame, text="Search for Papers Online", padding=10)
        search_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(search_frame, text="What papers are you looking for?").pack(anchor=tk.W)
        
        self.finder_query = scrolledtext.ScrolledText(search_frame, wrap=tk.WORD, height=4)
        self.finder_query.pack(fill=tk.X, pady=5)
        
        ttk.Label(search_frame, text="Example: pore-scale modeling anaerobic oxidation methane carbonate micro-CT", 
                  foreground="gray").pack(anchor=tk.W)
        
        self.finder_btn = ttk.Button(search_frame, text="🔍 Search Papers", command=self.find_papers)
        self.finder_btn.pack(pady=10)
        
        # Results
        results_frame = ttk.LabelFrame(self.finder_frame, text="Results", padding=10)
        results_frame.pack(fill=tk.BOTH, expand=True)
        
        self.finder_results = scrolledtext.ScrolledText(results_frame, wrap=tk.WORD, height=25)
        self.finder_results.pack(fill=tk.BOTH, expand=True)
    
    def setup_analyzer_tab(self):
        """Setup the local paper analyzer tab."""
        # Folder selection
        folder_frame = ttk.LabelFrame(self.analyzer_frame, text="Papers Folder", padding=10)
        folder_frame.pack(fill=tk.X, pady=(0, 10))
        
        folder_row = ttk.Frame(folder_frame)
        folder_row.pack(fill=tk.X)
        
        self.folder_var = tk.StringVar()
        self.folder_entry = ttk.Entry(folder_row, textvariable=self.folder_var, width=70)
        self.folder_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        ttk.Button(folder_row, text="Browse...", command=self.browse_folder).pack(side=tk.LEFT)
        ttk.Button(folder_row, text="Load", command=self.load_folder).pack(side=tk.LEFT, padx=5)
        
        # Papers list
        papers_frame = ttk.LabelFrame(self.analyzer_frame, text="Loaded Papers", padding=10)
        papers_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.papers_listbox = tk.Listbox(papers_frame, height=5, selectmode=tk.MULTIPLE)
        self.papers_listbox.pack(fill=tk.X)
        
        self.papers_count_label = ttk.Label(papers_frame, text="No papers loaded")
        self.papers_count_label.pack(anchor=tk.W, pady=5)
        
        # Query
        query_frame = ttk.LabelFrame(self.analyzer_frame, text="Ask About Your Papers", padding=10)
        query_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(query_frame, text="What would you like to know?").pack(anchor=tk.W)
        self.analyzer_query = scrolledtext.ScrolledText(query_frame, wrap=tk.WORD, height=3)
        self.analyzer_query.pack(fill=tk.X, pady=5)
        
        ttk.Label(query_frame, text="Examples: What methods are used? Find data about oxygen penetration. Compare approaches.", 
                  foreground="gray").pack(anchor=tk.W)
        
        self.analyzer_btn = ttk.Button(query_frame, text="🔬 Analyze Papers", command=self.analyze_papers)
        self.analyzer_btn.pack(pady=10)
        
        # Results
        results_frame = ttk.LabelFrame(self.analyzer_frame, text="Analysis Results", padding=10)
        results_frame.pack(fill=tk.BOTH, expand=True)
        
        self.analyzer_results = scrolledtext.ScrolledText(results_frame, wrap=tk.WORD, height=15)
        self.analyzer_results.pack(fill=tk.BOTH, expand=True)
    
    def setup_verifier_tab(self):
        """Setup the citation verifier tab."""
        # Paragraph input
        para_frame = ttk.LabelFrame(self.verifier_frame, text="Your Paragraph with Citations", padding=10)
        para_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.verifier_paragraph = scrolledtext.ScrolledText(para_frame, wrap=tk.WORD, height=8)
        self.verifier_paragraph.pack(fill=tk.X)
        self.verifier_paragraph.insert(tk.END, "Paste your paragraph here...")
        
        # Task
        task_frame = ttk.LabelFrame(self.verifier_frame, text="What to Verify", padding=10)
        task_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.verifier_task = ttk.Entry(task_frame, width=80)
        self.verifier_task.pack(fill=tk.X)
        self.verifier_task.insert(0, "Verify that the citations support the claims made")
        
        # Note about folder
        ttk.Label(task_frame, text="Note: Uses the papers folder from the Analyzer tab", 
                  foreground="gray").pack(anchor=tk.W, pady=5)
        
        self.verifier_btn = ttk.Button(task_frame, text="✓ Verify Citations", command=self.verify_citations)
        self.verifier_btn.pack(pady=10)
        
        # Results
        results_frame = ttk.LabelFrame(self.verifier_frame, text="Verification Results", padding=10)
        results_frame.pack(fill=tk.BOTH, expand=True)
        
        self.verifier_results = scrolledtext.ScrolledText(results_frame, wrap=tk.WORD, height=15)
        self.verifier_results.pack(fill=tk.BOTH, expand=True)
    
    def setup_settings_tab(self):
        """Setup the settings tab."""
        # Provider Selection
        provider_frame = ttk.LabelFrame(self.settings_frame, text="AI Provider", padding=10)
        provider_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.provider_var = tk.StringVar(value="claude")
        
        provider_row = ttk.Frame(provider_frame)
        provider_row.pack(fill=tk.X, pady=5)
        
        ttk.Radiobutton(provider_row, text="Claude (Anthropic)", variable=self.provider_var, 
                       value="claude", command=self.on_provider_change).pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(provider_row, text="ChatGPT (OpenAI)", variable=self.provider_var, 
                       value="chatgpt", command=self.on_provider_change).pack(side=tk.LEFT, padx=10)
        
        # API Key
        api_frame = ttk.LabelFrame(self.settings_frame, text="API Key", padding=10)
        api_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.api_key_label = ttk.Label(api_frame, text="Anthropic API Key:")
        self.api_key_label.pack(anchor=tk.W)
        
        key_row = ttk.Frame(api_frame)
        key_row.pack(fill=tk.X, pady=5)
        
        self.api_key_var = tk.StringVar()
        self.api_key_entry = ttk.Entry(key_row, textvariable=self.api_key_var, width=60, show="*")
        self.api_key_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        self.show_key_var = tk.BooleanVar()
        ttk.Checkbutton(key_row, text="Show", variable=self.show_key_var, 
                       command=self.toggle_key_visibility).pack(side=tk.LEFT)
        
        ttk.Button(api_frame, text="💾 Save & Connect", command=self.save_api_key).pack(pady=10)
        
        self.api_status = ttk.Label(api_frame, text="")
        self.api_status.pack(anchor=tk.W)
        
        # Quick links
        links_frame = ttk.LabelFrame(self.settings_frame, text="Get API Keys", padding=10)
        links_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(links_frame, text="Claude: https://console.anthropic.com", foreground="blue").pack(anchor=tk.W)
        ttk.Label(links_frame, text="ChatGPT: https://platform.openai.com/api-keys", foreground="blue").pack(anchor=tk.W)
        
        # Instructions
        instr_frame = ttk.LabelFrame(self.settings_frame, text="Instructions", padding=10)
        instr_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        instructions = """
HOW TO USE THIS TOOL:

1. CHOOSE YOUR AI PROVIDER:
   - Claude (Anthropic): Better for research, has web search
   - ChatGPT (OpenAI): Alternative option, widely used

2. PAPER FINDER TAB:
   - Enter a description of what papers you're looking for
   - Click Search to find relevant papers online
   - Results include title, authors, year, summary, and links

3. LOCAL PAPER ANALYZER TAB:
   - Click Browse to select your folder containing PDF papers
   - Click Load to scan and load all PDFs
   - Ask any question about your papers
   - The AI will read through them and answer your question

4. CITATION VERIFIER TAB:
   - First, load your cited papers in the Analyzer tab
   - Paste your paragraph with citations
   - Describe what you want verified
   - The AI will check if your citations support your claims

TIPS:
- Be specific in your queries for better results
- For large collections, analysis may take a minute
- Claude has web search built-in, ChatGPT uses training knowledge
        """
        
        instr_text = scrolledtext.ScrolledText(instr_frame, wrap=tk.WORD, height=15)
        instr_text.pack(fill=tk.BOTH, expand=True)
        instr_text.insert(tk.END, instructions)
        instr_text.config(state=tk.DISABLED)
    
    def on_provider_change(self):
        """Handle provider selection change."""
        provider = self.provider_var.get()
        if provider == "claude":
            self.api_key_label.config(text="Anthropic API Key:")
        else:
            self.api_key_label.config(text="OpenAI API Key:")
        
        # Clear current key display
        self.api_key_var.set("")
        self.api_status.config(text="Please enter your API key", foreground="orange")
    
    def toggle_key_visibility(self):
        self.api_key_entry.config(show="" if self.show_key_var.get() else "*")
    
    def save_api_key(self):
        """Save and validate API key."""
        self.api_key = self.api_key_var.get().strip()
        self.provider = self.provider_var.get()
        
        if not self.api_key:
            self.api_status.config(text="✗ No API Key provided", foreground="red")
            return
        
        # Initialize client
        self.ai_client = AIClient(provider=self.provider, api_key=self.api_key)
        
        if self.ai_client.is_ready():
            provider_name = "Claude" if self.provider == "claude" else "ChatGPT"
            self.api_status.config(text=f"✓ Connected to {provider_name}!", foreground="green")
            messagebox.showinfo("Success", f"Connected to {provider_name} successfully!")
        else:
            self.api_status.config(text="✗ Failed to connect. Check your API key.", foreground="red")
            messagebox.showerror("Error", "Failed to initialize API client. Please check your key.")
    
    def load_saved_settings(self):
        """Load settings from environment variables."""
        # Try Claude first
        claude_key = os.environ.get("ANTHROPIC_API_KEY", "")
        openai_key = os.environ.get("OPENAI_API_KEY", "")
        
        if claude_key:
            self.provider_var.set("claude")
            self.api_key_var.set(claude_key)
            self.api_key = claude_key
            self.provider = "claude"
            self.ai_client = AIClient(provider="claude", api_key=claude_key)
            if self.ai_client.is_ready():
                self.api_status.config(text="✓ Connected to Claude (from environment)", foreground="green")
        elif openai_key:
            self.provider_var.set("chatgpt")
            self.api_key_var.set(openai_key)
            self.api_key = openai_key
            self.provider = "chatgpt"
            self.ai_client = AIClient(provider="chatgpt", api_key=openai_key)
            if self.ai_client.is_ready():
                self.api_status.config(text="✓ Connected to ChatGPT (from environment)", foreground="green")
        else:
            self.api_status.config(text="Please select a provider and enter your API key", foreground="orange")
    
    def browse_folder(self):
        folder = filedialog.askdirectory(title="Select Papers Folder")
        if folder:
            self.folder_var.set(folder)
    
    def load_folder(self):
        folder = self.folder_var.get().strip()
        if not folder:
            messagebox.showwarning("No Folder", "Please select a folder first")
            return
        
        path = Path(folder)
        if not path.exists():
            messagebox.showerror("Error", f"Folder not found: {folder}")
            return
        
        self.papers_folder = folder
        self.loaded_papers = {}
        self.papers_listbox.delete(0, tk.END)
        
        pdf_files = list(path.glob("**/*.pdf"))
        
        for pdf_path in pdf_files:
            meta = PDFProcessor.get_metadata(str(pdf_path))
            self.loaded_papers[str(pdf_path)] = meta
            display_name = f"{meta['filename']} ({meta.get('pages', '?')} pages)"
            self.papers_listbox.insert(tk.END, display_name)
        
        self.papers_count_label.config(text=f"Loaded {len(self.loaded_papers)} papers")
        messagebox.showinfo("Success", f"Loaded {len(self.loaded_papers)} PDF files")
    
    def find_papers(self):
        query = self.finder_query.get("1.0", tk.END).strip()
        if not query:
            messagebox.showwarning("No Query", "Please enter a search query")
            return
        
        if not self.ai_client or not self.ai_client.is_ready():
            messagebox.showerror("Error", "Please set your API key in Settings tab")
            return
        
        self.finder_btn.config(state=tk.DISABLED)
        self.finder_results.delete(1.0, tk.END)
        self.finder_results.insert(tk.END, f"Searching for papers using {self.provider.upper()}...\n\n")
        
        def search():
            try:
                prompt = f"""You are a research assistant helping find academic papers. Search for papers related to:

"{query}"

Find relevant academic papers from Google Scholar, arXiv, PubMed, Semantic Scholar, or other academic databases.

Provide your findings in this JSON format (output ONLY the JSON array):

[
  {{
    "title": "Full paper title",
    "authors": ["Author 1", "Author 2"],
    "year": 2023,
    "link": "URL or DOI",
    "journal": "Journal name",
    "summary": "3-4 sentence summary",
    "relevance": "How it relates to the query"
  }}
]

Find 5-8 highly relevant papers. If you cannot find papers, return []."""

                messages = [{"role": "user", "content": prompt}]
                
                # Use web search only for Claude
                use_web = (self.provider == "claude")
                response = self.ai_client.chat(messages, use_web_search=use_web)
                
                # Try to parse JSON
                match = re.search(r'\[[\s\S]*\]', response)
                if match:
                    papers = json.loads(match.group())
                    result = self.format_papers(papers)
                else:
                    result = "Could not parse results. Raw response:\n\n" + response
                
            except Exception as e:
                result = f"Error: {e}"
            
            self.root.after(0, lambda: self.show_finder_results(result))
        
        threading.Thread(target=search, daemon=True).start()
    
    def format_papers(self, papers: List[Dict]) -> str:
        """Format papers for display."""
        if not papers:
            return "No papers found."
        
        result = f"Found {len(papers)} papers:\n\n"
        result += "=" * 70 + "\n\n"
        
        for i, p in enumerate(papers, 1):
            authors = p.get("authors", [])
            if isinstance(authors, list):
                authors_str = ", ".join(authors[:3])
                if len(authors) > 3:
                    authors_str += " et al."
            else:
                authors_str = str(authors)
            
            result += f"[{i}] {p.get('title', 'Unknown')}\n"
            result += f"    Authors: {authors_str}\n"
            result += f"    Year: {p.get('year', 'Unknown')}\n"
            if p.get('journal'):
                result += f"    Journal: {p.get('journal')}\n"
            result += f"\n    Summary: {p.get('summary', 'N/A')}\n"
            result += f"\n    Relevance: {p.get('relevance', 'N/A')}\n"
            if p.get('link'):
                result += f"\n    Link: {p.get('link')}\n"
            result += "\n" + "-" * 70 + "\n\n"
        
        return result
    
    def show_finder_results(self, result: str):
        self.finder_results.delete(1.0, tk.END)
        self.finder_results.insert(tk.END, result)
        self.finder_btn.config(state=tk.NORMAL)
    
    def analyze_papers(self):
        query = self.analyzer_query.get("1.0", tk.END).strip()
        if not query:
            messagebox.showwarning("No Query", "Please enter a question")
            return
        
        if not self.loaded_papers:
            messagebox.showwarning("No Papers", "Please load papers first")
            return
        
        if not self.ai_client or not self.ai_client.is_ready():
            messagebox.showerror("Error", "Please set your API key in Settings tab")
            return
        
        self.analyzer_btn.config(state=tk.DISABLED)
        self.analyzer_results.delete(1.0, tk.END)
        self.analyzer_results.insert(tk.END, "Reading and analyzing papers...\n\n")
        
        def analyze():
            try:
                # Read papers
                papers_text = []
                for path, meta in list(self.loaded_papers.items())[:10]:
                    text = PDFProcessor.extract_text(path, max_pages=30)
                    if len(text) > 50000:
                        text = text[:50000] + "\n... [truncated]"
                    papers_text.append(f"=== {meta['filename']} ===\n{text}\n=== END ===")
                
                all_text = "\n\n".join(papers_text)
                
                prompt = f"""Analyze these papers:

{all_text}

Question: {query}

Provide a detailed answer citing specific papers and quotes."""

                messages = [{"role": "user", "content": prompt}]
                result = self.ai_client.chat(messages, use_web_search=False)
                
            except Exception as e:
                result = f"Error: {e}"
            
            self.root.after(0, lambda: self.show_analyzer_results(result))
        
        threading.Thread(target=analyze, daemon=True).start()
    
    def show_analyzer_results(self, result: str):
        self.analyzer_results.delete(1.0, tk.END)
        self.analyzer_results.insert(tk.END, result)
        self.analyzer_btn.config(state=tk.NORMAL)
    
    def verify_citations(self):
        paragraph = self.verifier_paragraph.get(1.0, tk.END).strip()
        task = self.verifier_task.get().strip()
        
        if not paragraph or paragraph == "Paste your paragraph here...":
            messagebox.showwarning("No Paragraph", "Please paste your paragraph")
            return
        
        if not self.loaded_papers:
            messagebox.showwarning("No Papers", "Please load papers in the Analyzer tab first")
            return
        
        if not self.ai_client or not self.ai_client.is_ready():
            messagebox.showerror("Error", "Please set your API key in Settings tab")
            return
        
        self.verifier_btn.config(state=tk.DISABLED)
        self.verifier_results.delete(1.0, tk.END)
        self.verifier_results.insert(tk.END, "Reading papers and verifying citations...\n\n")
        
        def verify():
            try:
                # Read papers
                papers_text = []
                for path, meta in self.loaded_papers.items():
                    text = PDFProcessor.extract_text(path, max_pages=30)
                    if len(text) > 50000:
                        text = text[:50000] + "\n... [truncated]"
                    papers_text.append(f"=== {meta['filename']} ===\n{text}\n=== END ===")
                
                all_text = "\n\n".join(papers_text)
                
                prompt = f"""Verify citations in this paragraph:

PAPERS:
{all_text}

PARAGRAPH:
{paragraph}

TASK: {task}

Provide:
1. Overall verdict (SUPPORTED/PARTIALLY SUPPORTED/NOT SUPPORTED)
2. Claim-by-claim analysis with evidence
3. Recommendations"""

                messages = [{"role": "user", "content": prompt}]
                result = self.ai_client.chat(messages, use_web_search=False)
                
            except Exception as e:
                result = f"Error: {e}"
            
            self.root.after(0, lambda: self.show_verifier_results(result))
        
        threading.Thread(target=verify, daemon=True).start()
    
    def show_verifier_results(self, result: str):
        self.verifier_results.delete(1.0, tk.END)
        self.verifier_results.insert(tk.END, result)
        self.verifier_btn.config(state=tk.NORMAL)


def main():
    root = tk.Tk()
    app = ResearchAgentGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
