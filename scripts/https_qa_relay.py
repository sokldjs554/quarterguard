"""QA fixed-origin relay preserving request content type; upstream TLS stays verified."""
import httpx
from fastapi import FastAPI, Request
from fastapi.responses import Response
app = FastAPI()
@app.api_route('/{path:path}', methods=['GET', 'POST'])
async def relay(path: str, request: Request):
    headers = {}
    if request.headers.get('content-type'):
        headers['content-type'] = request.headers['content-type']
    async with httpx.AsyncClient(timeout=60, follow_redirects=False) as client:
        response = await client.request(request.method, 'https://quarterguard.onrender.com/' + path,
                                        params=request.query_params, content=await request.body(), headers=headers)
    return Response(response.content, status_code=response.status_code,
                    headers={'content-type':response.headers.get('content-type','application/octet-stream'),
                             'x-qa-upstream':'https://quarterguard.onrender.com','x-qa-tls-verified':'true'})
