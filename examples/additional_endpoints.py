"""
Examples for additional Zaguan SDK endpoints.

This example demonstrates:
- Embeddings
- Audio transcription and translation
- Text-to-speech
- Image generation, editing, and variations
- Content moderation
"""

from zaguan_sdk import (
    ZaguanClient,
    EmbeddingRequest,
    AudioSpeechRequest,
    ImageGenerationRequest,
    ModerationRequest
)


def embeddings_example():
    """Example using embeddings for semantic search."""
    client = ZaguanClient(
        base_url="https://api.zaguanai.com",
        api_key="your-api-key"
    )
    
    # Create embeddings for text
    request = EmbeddingRequest(
        model="openai/text-embedding-3-small",
        input="The quick brown fox jumps over the lazy dog"
    )
    
    response = client.create_embeddings(request)
    print(f"Embedding dimensions: {len(response.data[0].embedding)}")
    print(f"First 5 values: {response.data[0].embedding[:5]}")
    
    # Batch embeddings
    batch_request = EmbeddingRequest(
        model="openai/text-embedding-3-small",
        input=[
            "First document",
            "Second document",
            "Third document"
        ]
    )
    
    batch_response = client.create_embeddings(batch_request)
    print(f"Created {len(batch_response.data)} embeddings")


def audio_transcription_example():
    """Example using Whisper for audio transcription."""
    client = ZaguanClient(
        base_url="https://api.zaguanai.com",
        api_key="your-api-key"
    )
    
    # Transcribe audio file
    response = client.create_transcription(
        file_path="audio.mp3",
        model="whisper-1",
        language="en",
        response_format="verbose_json"
    )
    
    print(f"Transcription: {response.text}")
    if response.language:
        print(f"Detected language: {response.language}")
    if response.duration:
        print(f"Duration: {response.duration}s")


def audio_translation_example():
    """Example translating audio to English."""
    client = ZaguanClient(
        base_url="https://api.zaguanai.com",
        api_key="your-api-key"
    )
    
    # Translate non-English audio to English
    response = client.create_translation(
        file_path="spanish_audio.mp3",
        model="whisper-1"
    )
    
    print(f"Translation: {response.text}")


def text_to_speech_example():
    """Example using text-to-speech."""
    client = ZaguanClient(
        base_url="https://api.zaguanai.com",
        api_key="your-api-key"
    )
    
    # Generate speech from text
    request = AudioSpeechRequest(
        model="tts-1",
        input="Hello! This is a test of the text to speech system.",
        voice="alloy",
        response_format="mp3",
        speed=1.0
    )
    
    client.create_speech(request, "output.mp3")
    print("Speech saved to output.mp3")
    
    # HD quality speech
    hd_request = AudioSpeechRequest(
        model="tts-1-hd",
        input="This is high definition audio.",
        voice="nova",
        response_format="mp3"
    )
    
    client.create_speech(hd_request, "output_hd.mp3")
    print("HD speech saved to output_hd.mp3")


def image_generation_example():
    """Example generating images with DALL-E."""
    client = ZaguanClient(
        base_url="https://api.zaguanai.com",
        api_key="your-api-key"
    )
    
    # Generate image with DALL-E 3
    request = ImageGenerationRequest(
        prompt="A serene landscape with mountains and a lake at sunset",
        model="dall-e-3",
        size="1024x1024",
        quality="hd",
        style="vivid",
        n=1
    )
    
    response = client.create_image(request)
    print(f"Image URL: {response.data[0].url}")
    if response.data[0].revised_prompt:
        print(f"Revised prompt: {response.data[0].revised_prompt}")
    
    # Generate multiple images with DALL-E 2
    request_multi = ImageGenerationRequest(
        prompt="A cute robot",
        model="dall-e-2",
        size="512x512",
        n=4
    )
    
    response_multi = client.create_image(request_multi)
    print(f"Generated {len(response_multi.data)} images")


def image_editing_example():
    """Example editing images with DALL-E."""
    client = ZaguanClient(
        base_url="https://api.zaguanai.com",
        api_key="your-api-key"
    )
    
    # Edit image with mask
    response = client.edit_image(
        image_path="original.png",
        prompt="Add a red hat to the person",
        mask_path="mask.png",
        model="dall-e-2",
        size="1024x1024",
        n=1
    )
    
    print(f"Edited image URL: {response.data[0].url}")


def image_variation_example():
    """Example creating image variations."""
    client = ZaguanClient(
        base_url="https://api.zaguanai.com",
        api_key="your-api-key"
    )
    
    # Create variations of an image
    response = client.create_image_variation(
        image_path="original.png",
        model="dall-e-2",
        n=3,
        size="1024x1024"
    )
    
    print(f"Created {len(response.data)} variations")
    for i, img in enumerate(response.data):
        print(f"Variation {i+1}: {img.url}")


def moderation_example():
    """Example using content moderation."""
    client = ZaguanClient(
        base_url="https://api.zaguanai.com",
        api_key="your-api-key"
    )
    
    # Check single text
    request = ModerationRequest(
        input="I want to hurt someone",
        model="text-moderation-latest"
    )
    
    response = client.create_moderation(request)
    result = response.results[0]
    
    if result.flagged:
        print("Content flagged!")
        print(f"Categories: {result.categories}")
        print(f"Scores: {result.category_scores}")
    else:
        print("Content is safe")
    
    # Check multiple texts
    batch_request = ModerationRequest(
        input=[
            "Hello, how are you?",
            "This is inappropriate content",
            "Have a great day!"
        ]
    )
    
    batch_response = client.create_moderation(batch_request)
    for i, result in enumerate(batch_response.results):
        print(f"Text {i+1}: {'Flagged' if result.flagged else 'Safe'}")


def semantic_search_example():
    """Example using embeddings for semantic search."""
    client = ZaguanClient(
        base_url="https://api.zaguanai.com",
        api_key="your-api-key"
    )
    
    # Documents to search
    documents = [
        "Python is a programming language",
        "The cat sat on the mat",
        "Machine learning is a subset of AI",
        "Dogs are loyal animals"
    ]
    
    # Create embeddings for documents
    doc_request = EmbeddingRequest(
        model="openai/text-embedding-3-small",
        input=documents
    )
    doc_response = client.create_embeddings(doc_request)
    doc_embeddings = [d.embedding for d in doc_response.data]
    
    # Create embedding for query
    query = "What is Python?"
    query_request = EmbeddingRequest(
        model="openai/text-embedding-3-small",
        input=query
    )
    query_response = client.create_embeddings(query_request)
    query_embedding = query_response.data[0].embedding
    
    # Calculate cosine similarity (simplified)
    import math
    
    def cosine_similarity(a, b):
        dot_product = sum(x * y for x, y in zip(a, b))
        magnitude_a = math.sqrt(sum(x * x for x in a))
        magnitude_b = math.sqrt(sum(y * y for y in b))
        return dot_product / (magnitude_a * magnitude_b)
    
    # Find most similar document
    similarities = [
        (doc, cosine_similarity(query_embedding, emb))
        for doc, emb in zip(documents, doc_embeddings)
    ]
    similarities.sort(key=lambda x: x[1], reverse=True)
    
    print(f"Query: {query}")
    print(f"Most similar: {similarities[0][0]} (score: {similarities[0][1]:.4f})")


if __name__ == "__main__":
    print("=== Embeddings Example ===")
    # embeddings_example()
    
    print("\n=== Audio Transcription Example ===")
    # audio_transcription_example()
    
    print("\n=== Text-to-Speech Example ===")
    # text_to_speech_example()
    
    print("\n=== Image Generation Example ===")
    # image_generation_example()
    
    print("\n=== Content Moderation Example ===")
    # moderation_example()
    
    print("\n=== Semantic Search Example ===")
    # semantic_search_example()
    
    print("\nExamples are commented out. Uncomment and add your API credentials to run.")
