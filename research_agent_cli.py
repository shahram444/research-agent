#!/usr/bin/env python3
"""
Research Agent CLI - Multi-API Command Line Version
====================================================

Supports both Claude (Anthropic) and ChatGPT (OpenAI) APIs.

Requirements:
    pip install anthropic openai pymupdf rich

Usage:
    python research_agent_cli.py
"""

import os
import sys
import json
import re
from pathlib import Path
from typing import List, Dict

# Install missing packages
def check_deps():
    pkgs = {'anthropic': 'anthropic', 'openai': 'openai', 'fitz': 'pymupdf', 'rich': 'rich'}
    missing = [p for m, p in pkgs.items() if not __import__(m, globals(), locals(), [], 0) is None or True]
    missing = []
    for mod, pkg in pkgs.items():
        try:
            __import__(mod)
        except ImportError:
            missing.append(pkg)
    if missing:
        print(f"Installing: {', '.join(missing)}")
        import subprocess
        subprocess.check_call([sys.executable, '-m', 'pip', 'install'] + missing)
        print("Restart the script.")
        sys.exit(0)

check_deps()

import anthropic
import openai
import fitz
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.table import Table
from rich.prompt import Prompt

console = Console()


class AIClient:
    def __init__(self, provider: str, api_key: str):
        self.provider = provider
        self.api_key = api_key
        self.client = None
        if provider == "claude":
            self.client = anthropic.Anthropic(api_key=api_key)
        else:
            self.client = openai.OpenAI(api_key=api_key)
    
    def chat(self, prompt: str, use_web: bool = False) -> str:
        messages = [{"role": "user", "content": prompt}]
        try:
            if self.provider == "claude":
                kwargs = {"model": "claude-sonnet-4-20250514", "max_tokens": 4096, "messages": messages}
                if use_web:
                    kwargs["tools"] = [{"type": "web_search_20250305", "name": "web_search"}]
                resp = self.client.messages.create(**kwargs)
                return "".join(b.text for b in resp.content if hasattr(b, 'text'))
            else:
                resp = self.client.chat.completions.create(
                    model="gpt-4o", messages=messages, max_tokens=4096
                )
                return resp.choices[0].message.content
        except Exception as e:
            return f"Error: {e}"


def extract_pdf_text(path: str, max_pages: int = 30) -> str:
    try:
        doc = fitz.open(path)
        text = "\n\n".join(doc[i].get_text() for i in range(min(len(doc), max_pages)))
        doc.close()
        return text
    except Exception as e:
        return f"Error reading PDF: {e}"


def main():
    console.print(Panel.fit(
        "[bold cyan]Research Agent CLI[/bold cyan]\n"
        "[dim]Supports Claude & ChatGPT[/dim]",
        border_style="cyan"
    ))
    
    # Check for API keys
    claude_key = os.environ.get("ANTHROPIC_API_KEY", "")
    openai_key = os.environ.get("OPENAI_API_KEY", "")
    
    if claude_key:
        provider = "claude"
        api_key = claude_key
        console.print("[green]✓ Using Claude (Anthropic)[/green]")
    elif openai_key:
        provider = "chatgpt"
        api_key = openai_key
        console.print("[green]✓ Using ChatGPT (OpenAI)[/green]")
    else:
        console.print("[yellow]No API key found in environment.[/yellow]")
        provider = Prompt.ask("Choose provider", choices=["claude", "chatgpt"], default="claude")
        api_key = Prompt.ask("Enter API key")
    
    client = AIClient(provider, api_key)
    papers_folder = ""
    loaded_papers = {}
    
    console.print("\n[green]Ready! Commands:[/green]")
    console.print("  [cyan]folder <path>[/cyan] - Set papers folder")
    console.print("  [cyan]list[/cyan] - List loaded papers")
    console.print("  [cyan]find <query>[/cyan] - Search papers online")
    console.print("  [cyan]analyze <question>[/cyan] - Analyze local papers")
    console.print("  [cyan]verify[/cyan] - Verify citations")
    console.print("  [cyan]quit[/cyan] - Exit\n")
    
    while True:
        try:
            user_input = Prompt.ask("[bold]research>[/bold]")
            
            if not user_input.strip():
                continue
            
            parts = user_input.split(maxsplit=1)
            cmd = parts[0].lower()
            args = parts[1] if len(parts) > 1 else ""
            
            # QUIT
            if cmd in ['quit', 'exit', 'q']:
                console.print("[yellow]Goodbye![/yellow]")
                break
            
            # SET FOLDER
            elif cmd == 'folder':
                if not args:
                    console.print(f"Current folder: {papers_folder or 'Not set'}")
                else:
                    path = Path(args).expanduser().resolve()
                    if path.exists() and path.is_dir():
                        papers_folder = str(path)
                        loaded_papers = {}
                        for pdf in path.glob("**/*.pdf"):
                            loaded_papers[str(pdf)] = {"filename": pdf.name, "path": str(pdf)}
                        console.print(f"[green]Loaded {len(loaded_papers)} PDFs from {papers_folder}[/green]")
                    else:
                        console.print(f"[red]Folder not found: {args}[/red]")
            
            # LIST PAPERS
            elif cmd == 'list':
                if not loaded_papers:
                    console.print("[yellow]No papers loaded. Use 'folder <path>' first.[/yellow]")
                else:
                    table = Table(title="Loaded Papers")
                    table.add_column("#", style="dim")
                    table.add_column("Filename", style="cyan")
                    for i, (_, meta) in enumerate(loaded_papers.items(), 1):
                        table.add_row(str(i), meta["filename"])
                    console.print(table)
            
            # FIND PAPERS ONLINE
            elif cmd in ['find', 'search']:
                if not args:
                    console.print("[yellow]Usage: find <query>[/yellow]")
                else:
                    console.print(f"[cyan]Searching for papers...[/cyan]")
                    prompt = f"""Search for academic papers about: "{args}"

Find 5-8 relevant papers and return ONLY a JSON array:
[{{"title": "...", "authors": ["..."], "year": 2023, "link": "...", "summary": "...", "relevance": "..."}}]"""
                    
                    result = client.chat(prompt, use_web=(provider == "claude"))
                    
                    # Try to parse JSON
                    match = re.search(r'\[[\s\S]*\]', result)
                    if match:
                        try:
                            papers = json.loads(match.group())
                            console.print(f"\n[green]Found {len(papers)} papers:[/green]\n")
                            for i, p in enumerate(papers, 1):
                                authors = p.get("authors", [])
                                if isinstance(authors, list):
                                    authors = ", ".join(authors[:3])
                                console.print(Panel(
                                    f"[bold]{p.get('title', 'Unknown')}[/bold]\n"
                                    f"[yellow]{authors}[/yellow] ({p.get('year', '?')})\n\n"
                                    f"{p.get('summary', '')}\n\n"
                                    f"[dim]Relevance: {p.get('relevance', '')}[/dim]\n"
                                    f"[link]{p.get('link', '')}[/link]",
                                    title=f"Paper #{i}"
                                ))
                        except json.JSONDecodeError:
                            console.print(result)
                    else:
                        console.print(result)
            
            # ANALYZE LOCAL PAPERS
            elif cmd == 'analyze':
                if not args:
                    console.print("[yellow]Usage: analyze <question>[/yellow]")
                elif not loaded_papers:
                    console.print("[yellow]No papers loaded. Use 'folder <path>' first.[/yellow]")
                else:
                    console.print("[cyan]Reading and analyzing papers...[/cyan]")
                    
                    # Read papers
                    papers_text = []
                    for path, meta in list(loaded_papers.items())[:10]:
                        text = extract_pdf_text(path)
                        if len(text) > 40000:
                            text = text[:40000] + "\n...[truncated]"
                        papers_text.append(f"=== {meta['filename']} ===\n{text}\n=== END ===")
                    
                    prompt = f"""Analyze these papers:

{chr(10).join(papers_text)}

Question: {args}

Provide a detailed answer citing specific papers."""

                    result = client.chat(prompt)
                    console.print(Panel(Markdown(result), title="Analysis Results", border_style="green"))
            
            # VERIFY CITATIONS
            elif cmd == 'verify':
                if not loaded_papers:
                    console.print("[yellow]No papers loaded. Use 'folder <path>' first.[/yellow]")
                else:
                    console.print("Paste your paragraph (Enter twice to finish):")
                    lines = []
                    while True:
                        line = input()
                        if line == "" and lines and lines[-1] == "":
                            break
                        lines.append(line)
                    paragraph = "\n".join(lines).strip()
                    
                    if paragraph:
                        console.print("[cyan]Verifying citations...[/cyan]")
                        
                        papers_text = []
                        for path, meta in loaded_papers.items():
                            text = extract_pdf_text(path)
                            if len(text) > 40000:
                                text = text[:40000]
                            papers_text.append(f"=== {meta['filename']} ===\n{text}\n=== END ===")
                        
                        prompt = f"""Verify if these papers support the claims in this paragraph:

PAPERS:
{chr(10).join(papers_text)}

PARAGRAPH:
{paragraph}

Provide:
1. Overall verdict (SUPPORTED/PARTIALLY SUPPORTED/NOT SUPPORTED)
2. Claim-by-claim analysis
3. Recommendations"""

                        result = client.chat(prompt)
                        console.print(Panel(Markdown(result), title="Verification Results", border_style="green"))
            
            # HELP
            elif cmd == 'help':
                console.print("""
[bold]Commands:[/bold]
  folder <path>     Set the folder containing your PDFs
  list              List all loaded papers
  find <query>      Search for papers online
  analyze <question> Analyze your local papers
  verify            Verify citations in a paragraph
  quit              Exit
                """)
            
            else:
                console.print(f"[yellow]Unknown command: {cmd}. Type 'help' for commands.[/yellow]")
                
        except KeyboardInterrupt:
            console.print("\n[yellow]Use 'quit' to exit.[/yellow]")
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")


if __name__ == "__main__":
    main()
