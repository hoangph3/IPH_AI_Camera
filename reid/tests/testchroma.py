import chromadb
chroma_client = chromadb.HttpClient(host='mct-chroma', port=8000)
print(chroma_client.heartbeat())