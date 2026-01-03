import asyncio
import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

load_dotenv()

app = FastAPI(
    title="Claude Code API Wrapper",
    description="Claude Code CLI를 API로 래핑한 서버",
    version="1.0.0"
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
        cmd = ["claude", "--print", request.prompt]

        # asyncio subprocess로 실행
        process = await asyncio.create_subprocess_exec(
            *cmd,
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


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8000"))
    host = os.getenv("HOST", "0.0.0.0")
    uvicorn.run(app, host=host, port=port)
