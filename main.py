import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

load_dotenv()

app = FastAPI(
    title="Claude Code API Wrapper",
    description="Claude Code CLI를 API로 래핑한 서버",
    version="1.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class PromptRequest(BaseModel):
    prompt: str
    working_directory: str | None = None  # 작업 디렉토리 (선택)


class PromptResponse(BaseModel):
    success: bool
    response: str
    error: str | None = None


@app.post("/ask", response_model=PromptResponse)
async def ask_claude(request: PromptRequest):
    """
    Claude Code CLI에 프롬프트를 전달하고 응답을 반환합니다.
    """
    try:
        # claude --print 옵션으로 non-interactive 실행
        # Windows에서는 shell=True로 실행해야 .cmd 파일을 찾을 수 있음
        cmd = f'claude --print "{request.prompt}"'

        process = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=request.working_directory
        )

        stdout, stderr = await process.communicate()

        if process.returncode != 0:
            return PromptResponse(
                success=False,
                response="",
                error=stderr.decode("utf-8", errors="replace")
            )

        return PromptResponse(
            success=True,
            response=stdout.decode("utf-8", errors="replace"),
            error=None
        )

    except FileNotFoundError:
        raise HTTPException(
            status_code=500,
            detail="Claude CLI를 찾을 수 없습니다. Claude Code가 설치되어 있는지 확인하세요."
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"오류 발생: {str(e)}"
        )


@app.get("/health")
async def health_check():
    """서버 상태 확인"""
    return {"status": "ok"}


@app.get("/")
async def root():
    """웹 UI 페이지 제공"""
    html_path = Path(__file__).parent / "examples" / "index.html"
    return FileResponse(html_path)


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8000"))
    host = os.getenv("HOST", "0.0.0.0")
    uvicorn.run(app, host=host, port=port)
