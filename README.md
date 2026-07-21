Install Ollama:
curl -fsSL https://ollama.com/install.sh | sh

Pull Embedding Model
ollama pull mxbai-embed-large

Start Ollama
ollama serve

Install Redis
    Needed for:
        Celery
        queues
        orchestration

sudo apt update
sudo apt install redis-server  
sudo service redis-server start

Start Celery Worker
Terminal 1:
cd rag-server
celery -A orchestration.celery_tasks:celery_app worker --loglevel=info

Start FastAPI Server
Terminal 2
cd rag-server
uvicorn main:app --reload

Server starts at:
http://127.0.0.1:8000

Open Swagger UI
http://127.0.0.1:8000/docs

To Run the docker
docker compose up --build

To Stop the docker
docker compose down

Verify NGINX
http://localhost:8080/
You should receive:
{
    "message": "RAG Server Running"
}

Swagger UI
http://localhost:8080/docs


Test Upload API
/upload
curl -X POST "http://127.0.0.1:8000/upload" \
  -F "file=@sample.pdf"

/query  
curl -X POST "http://127.0.0.1:8000/query" \
-H "Content-Type: application/json" \
-d '{
  "question": "What is the project deadline?",
  "top_k": 5
}'