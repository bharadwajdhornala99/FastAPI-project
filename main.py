from fastapi import FastAPI, File, UploadFile, HTTPException, Depends # type: ignore
from fastapi.security.api_key import APIKeyHeader # type: ignore
import fitz  # PyMuPDF # type: ignore
import docx2txt # type: ignore
import io

API_KEY = "api-143" 
api_key_header = APIKeyHeader(name="Authorization", auto_error=False)

app = FastAPI()

def get_api_key(api_key_header: str = Depends(api_key_header)):
    if not api_key_header or api_key_header != f"API-Key {API_KEY}":
        raise HTTPException(status_code=401, detail="Invalid API key")
    return api_key_header

@app.post("/upload-resume", dependencies=[Depends(get_api_key)])
async def upload_resume(file: UploadFile = File(...)):
    if not file:
        raise HTTPException(status_code=400, detail="No file uploaded.")
    try:
        if file.content_type == "application/pdf":
            pdf_bytes = await file.read()
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            text = "\n".join([page.get_text() for page in doc])
        elif file.content_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            contents = await file.read()
            text = docx2txt.process(io.BytesIO(contents))
        else:
            raise HTTPException(status_code=400, detail="Invalid file format")
        return {"filename": file.filename, "content": text}
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=422, detail="Error processing file")