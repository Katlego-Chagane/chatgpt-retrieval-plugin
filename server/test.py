import openai

# ...

async def query_main(
    request: QueryRequest = Body(...),
    token: HTTPAuthorizationCredentials = Depends(validate_token),
):
    try:
        # Query Pinecone datastore
        results = await datastore.query(request.queries)
        
        # Extract and format the search results
        pinecone_results = results[0]["results"]
        formatted_results = [f"{i+1}. {result['text']}" for i, result in enumerate(pinecone_results)]
        
        # Generate a conversational response using OpenAI API and the search results
        openai_messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": request.queries[0]["query"]},
            {"role": "assistant", "content": "\n".join(formatted_results)}
        ]
        openai_response = openai.Completion.create(
            engine="text-davinci-002",
            messages=openai_messages,
            temperature=0.8,
            max_tokens=150,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
        )

        ai_message = openai_response.choices[0].message['content']

        # Return the conversational response
        return {"results": [{"query": request.queries[0]["query"], "results": [{"text": ai_message}]}]}

    except Exception as e:
        print("Error:", e)
        raise HTTPException(status_code=500, detail="Internal Service Error")
