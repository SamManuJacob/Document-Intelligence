# Quick Run Instructions for Persona-Driven Document Intelligence

## Building the Image
From the project directory (with `Dockerfile` and `main.py`):

""docker build --platform linux/amd64 -t mysolutionname:somerandomidentifier .""
- This builds the image with all deps pre-loaded (no internet later).

## Running the System
Pass arguments directly: PDF paths (space-separated, relative to mount), then `--persona="..."` and `--job="..."`.

General command:
docker run --platform linux/amd64
-v /path/to/your/pdfs:/app/pdfs
mysolutionname:somerandomidentifier
pdfs/your-doc1.pdf pdfs/your-doc2.pdf ...
--persona="Your Persona"
--job="Your Job Description"


- `-v /path/to/your/pdfs:/app/pdfs`: Mounts your local folder (absolute path on your machine, e.g., `/c/Users/sammj/AdobeProj/Persona_Driven/pdfs` on Windows) to `/app/pdfs` in the container.
- PDF paths: List as arguments (e.g., `pdfs/"File with Spaces.pdf"`—use quotes for spaces; these are relative to `/app/pdfs`).
- `--persona` and `--job`: String values in quotes if spaces are present.
- Output: `output.json` in the container. Add `-v /path/to/your/output:/app/output` to save locally (update `main.py` to write there).

### Example (Travel Planner Test Case)
Assuming PDFs in `C:/Users/sammj/AdobeProj/Persona_Driven/pdfs`:
docker run --platform linux/amd64
-v /c/Users/sammj/AdobeProj/Persona_Driven/pdfs:/app/pdfs
mysolutionname:somerandomidentifier
pdfs/"South of France - Cities.pdf"
pdfs/"South of France - Cuisine.pdf"
pdfs/"South of France - History.pdf"
pdfs/"South of France - Restaurants and Hotels.pdf"
pdfs/"South of France - Things to Do.pdf"
pdfs/"South of France - Tips and Tricks.pdf"
pdfs/"South of France - Traditions and Culture.pdf"
--persona="Travel Planner"
--job="Plan a trip of 4 days for a group of 10 college friends."

text
- Processes PDFs, generates JSON with ranked sections.
- For other cases, swap paths/persona/job.