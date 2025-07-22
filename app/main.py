from fastapi import FastAPI, Request, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import os
import uuid
from typing import List

from app.database import get_db, create_tables
from app.models import Video, Note, Prompt
from app.utils.file_validation import validate_video_file, check_file_size
from app.utils.video_processing import process_video

# Create FastAPI app
app = FastAPI(title="Public Speaking Coach", version="1.0.0")

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Templates
templates = Jinja2Templates(directory="app/templates")

# Create database tables on startup
@app.on_event("startup")
async def startup_event():
    create_tables()
    # Initialize default prompts if they don't exist
    db = next(get_db())
    if db.query(Prompt).count() == 0:
        init_prompts(db)

def init_prompts(db: Session):
    """Initialize default prompts for each view type"""
    default_prompts = [
        # Video view prompts
        {"view_type": "video", "question_text": "What do you notice about your body language and posture?", "order_index": 1},
        {"view_type": "video", "question_text": "How would you rate your eye contact and facial expressions?", "order_index": 2},
        {"view_type": "video", "question_text": "What gestures or movements stood out to you?", "order_index": 3},
        
        # Audio view prompts
        {"view_type": "audio", "question_text": "How was your speaking pace and rhythm?", "order_index": 1},
        {"view_type": "audio", "question_text": "Did you notice any filler words or vocal habits?", "order_index": 2},
        {"view_type": "audio", "question_text": "How clear and confident did your voice sound?", "order_index": 3},
        
        # Text view prompts
        {"view_type": "text", "question_text": "How well-structured was your content?", "order_index": 1},
        {"view_type": "text", "question_text": "What key points came across most clearly?", "order_index": 2},
        {"view_type": "text", "question_text": "What would you improve about your message?", "order_index": 3},
    ]
    
    for prompt_data in default_prompts:
        prompt = Prompt(**prompt_data)
        db.add(prompt)
    db.commit()

@app.get("/", response_class=HTMLResponse)
async def landing(request: Request):
    """Landing page for new visitors"""
    return templates.TemplateResponse("landing.html", {"request": request})

@app.get("/app", response_class=HTMLResponse)
async def homepage(request: Request):
    """Main application dashboard"""
    if not current_user.is_authenticated:
        return RedirectResponse(url="/login")
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/profile", response_class=HTMLResponse)
@login_required
async def profile(request: Request, db: Session = Depends(get_db)):
    """User profile page"""
    video_count = db.query(Video).filter(Video.user_id == current_user.id).count()
    note_count = db.query(Note).join(Video).filter(Video.user_id == current_user.id).count()
    
    return templates.TemplateResponse(
        "profile.html",
        {
            "request": request,
            "video_count": video_count,
            "note_count": note_count
        }
    )

@app.post("/upload")
async def upload_video(
    request: Request,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Handle video upload"""
    try:
        # Validate file
        validation_result = validate_video_file(file)
        if not validation_result["valid"]:
            raise HTTPException(status_code=400, detail=validation_result["error"])
        
        # Generate unique filename
        # Ensure upload directory exists
        upload_dir = "app/static/uploads"
        os.makedirs(upload_dir, exist_ok=True)
        
        file_extension = os.path.splitext(file.filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = os.path.join(upload_dir, unique_filename)
        
        print(f"Attempting to save file to: {os.path.abspath(file_path)}")  # Debug logging
        
        # Read and validate file size
        content = await file.read()
        size_validation = check_file_size(content)
        if not size_validation["valid"]:
            raise HTTPException(status_code=400, detail=size_validation["error"])
        
        # Save file
        try:
            print(f"Attempting to write to: {file_path}")
            print(f"Content size: {len(content)} bytes")
            
            with open(file_path, "wb") as buffer:
                bytes_written = buffer.write(content)
                print(f"Successfully wrote {bytes_written} bytes to {file_path}")
                
            # Verify file exists and has content
            if os.path.exists(file_path):
                file_size = os.path.getsize(file_path)
                print(f"File verification: {file_path} exists with size {file_size} bytes")
            else:
                print(f"ERROR: File {file_path} was not created")
                raise HTTPException(status_code=500, detail="File was not created on disk")
                
        except Exception as e:
            print(f"Error saving file: {type(e).__name__}: {e}")
            print(f"Full path attempted: {os.path.abspath(file_path)}")
            raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")
        
        # Create video record
        video = Video(
            filename=unique_filename,
            original_name=file.filename,
            file_size=len(content),
            status="uploaded"
        )
        db.add(video)
        db.commit()
        db.refresh(video)
        
        # Process video in background (for now, just get duration)
        try:
            duration = process_video(file_path)
            if duration is not None:
                video.duration = duration
            video.status = "completed"
            db.commit()
        except Exception as e:
            video.status = "error"
            db.commit()
            print(f"Video processing error: {e}")
        
        # Redirect to analysis page
        return RedirectResponse(url=f"/analysis/{video.id}", status_code=303)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@app.get("/analysis/{video_id}", response_class=HTMLResponse)
async def analysis_page(
    request: Request,
    video_id: int,
    db: Session = Depends(get_db)
):
    """Analysis page with three views"""
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    
    # Get prompts for each view
    video_prompts = db.query(Prompt).filter(Prompt.view_type == "video", Prompt.active == True).order_by(Prompt.order_index).all()
    audio_prompts = db.query(Prompt).filter(Prompt.view_type == "audio", Prompt.active == True).order_by(Prompt.order_index).all()
    text_prompts = db.query(Prompt).filter(Prompt.view_type == "text", Prompt.active == True).order_by(Prompt.order_index).all()
    
    # Get existing notes
    existing_notes = db.query(Note).filter(Note.video_id == video_id).all()
    notes_by_prompt = {note.prompt_id: note.content for note in existing_notes}
    
    return templates.TemplateResponse("analysis.html", {
        "request": request,
        "video": video,
        "video_prompts": video_prompts,
        "audio_prompts": audio_prompts,
        "text_prompts": text_prompts,
        "notes_by_prompt": notes_by_prompt
    })

@app.post("/save_note")
async def save_note(
    video_id: int = Form(...),
    prompt_id: int = Form(...),
    content: str = Form(...),
    db: Session = Depends(get_db)
):
    """Save or update a note"""
    # Check if note already exists
    existing_note = db.query(Note).filter(
        Note.video_id == video_id,
        Note.prompt_id == prompt_id
    ).first()
    
    if existing_note:
        existing_note.content = content
    else:
        # Get prompt to determine view_type
        prompt = db.query(Prompt).filter(Prompt.id == prompt_id).first()
        if not prompt:
            raise HTTPException(status_code=404, detail="Prompt not found")
        
        note = Note(
            video_id=video_id,
            prompt_id=prompt_id,
            view_type=prompt.view_type,
            content=content
        )
        db.add(note)
    
    db.commit()
    return {"status": "success"}

@app.get("/report/{video_id}", response_class=HTMLResponse)
async def report_page(
    request: Request,
    video_id: int,
    db: Session = Depends(get_db)
):
    """Generate simple report combining all notes"""
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    
    # Get all notes with prompts
    notes = db.query(Note).join(Prompt).filter(
        Note.video_id == video_id
    ).order_by(Prompt.view_type, Prompt.order_index).all()
    
    # Group notes by view type
    notes_by_view = {"video": [], "audio": [], "text": []}
    for note in notes:
        if note.content.strip():  # Only include non-empty notes
            notes_by_view[note.view_type].append(note)
    
    return templates.TemplateResponse("report.html", {
        "request": request,
        "video": video,
        "notes_by_view": notes_by_view
    })

from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer

security = HTTPBearer()

@app.get("/video/{video_id}")
async def serve_video(
    video_id: int,
    db: Session = Depends(get_db),
    credentials: HTTPBearer = Depends(security)
):
    """Serve video file with proper headers for HTML5 video playback"""
    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    
    # Verify video ownership
    if video.user_id != int(credentials.credentials):
        raise HTTPException(status_code=403, detail="Not authorized to access this video")
    
    file_path = f"app/static/uploads/{video.filename}"
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Video file not found")
    
    return FileResponse(
        file_path,
        media_type="video/mp4",
        headers={
            "Accept-Ranges": "bytes",
            "Content-Type": "video/mp4"
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)