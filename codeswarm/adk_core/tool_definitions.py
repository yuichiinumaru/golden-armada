from google.adk.tools import FunctionTool
from . import tool_logic

@FunctionTool
def read_file(file_path: str) -> dict:
  """Reads and returns the entire content of the specified file.

  Args:
    file_path: The absolute or relative path to the file to be read.

  Returns:
    dict: {'status': 'success', 'content': str} on success, or {'status': 'error', 'message': str} on failure.
  """
  return tool_logic.read_file(file_path=file_path)

@FunctionTool
def write_file(file_path: str, content: str) -> dict:
  """Writes the given content to the specified file, overwriting if it exists.

  Args:
    file_path: The absolute or relative path to the file to be written.
    content: The content to write to the file.

  Returns:
    dict: {'status': 'success', 'result': str} on success, or {'status': 'error', 'message': str} on failure.
  """
  return tool_logic.write_file(file_path=file_path, content=content)

@FunctionTool
def list_folder_contents(folder_path: str) -> dict:
  """Lists the files and folders in the specified directory.

  Args:
    folder_path: The path to the directory to list.

  Returns:
    dict: {'status': 'success', 'content': list} on success, or {'status': 'error', 'message': str} on failure.
  """
  return tool_logic.list_folder_contents(folder_path=folder_path)

@FunctionTool
def search_files_content(folder_path: str, search_query: str) -> dict:
  """Searches for a string in all files under the given folder (recursively).

  Args:
    folder_path: The root folder to search.
    search_query: The string to search for.

  Returns:
    dict: {'status': 'success', 'content': list} (list of file paths containing the query), or {'status': 'error', 'message': str}.
  """
  return tool_logic.search_files_content(folder_path=folder_path, search_query=search_query)

@FunctionTool
def fetch_web_page_text_content(url: str) -> dict:
  """Fetches and returns the visible text content of a web page.

  Args:
    url: The URL to fetch.

  Returns:
    dict: {'status': 'success', 'content': str} on success, or {'status': 'error', 'message': str} on failure.
  """
  return tool_logic.fetch_web_page_text_content(url=url)

@FunctionTool
def chunk_file(file_path: str, max_chunk_size: int) -> dict:
  """Reads a file and splits its content into chunks of up to max_chunk_size characters.

  Args:
    file_path: Path to the file.
    max_chunk_size: Maximum size of each chunk (in characters).

  Returns:
    dict: {'status': 'success', 'content': list} on success, or {'status': 'error', 'message': str}.
  """
  return tool_logic.chunk_file(file_path=file_path, max_chunk_size=max_chunk_size)

@FunctionTool
def summarize_chunks(chunks: list[str], summarizer_fn_placeholder: str) -> dict:
  """
  Provides chunks of text that an agent can then use to make summarization calls to an LLM.
  This tool itself does not perform LLM summarization due to ADK tool constraints.
  It prepares the data for an agent to orchestrate summarization.

  Args:
    chunks: List of text chunks to be prepared for summarization.
    summarizer_fn_placeholder: Indicates the intended summarization method (e.g., 'gemini_llm'). Not directly used by this tool's logic.

  Returns:
    A dictionary containing the provided chunks, ready for an agent to process with an LLM.
    Example: {'status': 'success', 'prepared_chunks': list[str]}
  """
  # This tool's role is to pass through the chunks.
  # The agent that calls this tool will then take these 'prepared_chunks'
  # and iterate through them, making individual calls to its LLM for summarization,
  # and then potentially another call to combine summaries.
  if not isinstance(chunks, list):
      return {"status": "error", "message": "Input 'chunks' must be a list."}
  return {"status": "success", "prepared_chunks": chunks}


# Tool lists for agent roles - now using the decorated functions directly
admin_tools_adk = [
    read_file,
    write_file,
    list_folder_contents,
    search_files_content,
    fetch_web_page_text_content,
    chunk_file,
    summarize_chunks, # Agent receives chunks, then uses its LLM to summarize them.
]
dev_tools_adk = [
    read_file,
    write_file,
    list_folder_contents,
    search_files_content,
    chunk_file,
]
revisor_tools_adk = [
    read_file,
    list_folder_contents,
    fetch_web_page_text_content,
    chunk_file,
    summarize_chunks, # Agent receives chunks, then uses its LLM to summarize them.
]