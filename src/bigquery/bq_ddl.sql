CREATE TABLE IF NOT EXISTS book_agent_v1.searches_v1
(
    search_id      STRING    NOT NULL,
    search_text    STRING    NOT NULL,
    result_count   INT64     NOT NULL,
    execution_time FLOAT64   NOT NULL,
    error_message  STRING,
    results_json   STRING,
    inserted_at    TIMESTAMP NOT NULL
);

CREATE OR REPLACE TABLE FUNCTION book_agent_v1.search_paragraphs(search_text STRING)
AS SELECT 
    embeddings.book_id,
    embeddings.paragraph_id,
    embeddings.page_number,
    embeddings.start_char,
    embeddings.end_char,
    embeddings.content,
    ML.DISTANCE(embeddings.embedding, search_embedding.ml_generate_embedding_result, 'COSINE') as similarity_score,
    embeddings.inserted_at
FROM paragraph_to_embedding_v1.embeddings_v1 embeddings
CROSS JOIN (
    SELECT ml_generate_embedding_result
    FROM ML.GENERATE_EMBEDDING(
        MODEL paragraph_to_embedding_v1.gemini_embedding_model,
        (SELECT search_text AS content),
        STRUCT('RETRIEVAL_DOCUMENT' AS task_type, 768 AS output_dimensionality)
    )
) search_embedding
WHERE embeddings.embedding IS NOT NULL
ORDER BY similarity_score ASC;
