import asyncio
from app.services.ai_service import AIService


async def test_pdf_rag():
    ai = AIService()

    result = await ai.generate_with_rag_from_pdf(
        query="what is the name of the college this course is done and How was the experience?",
        pdf_path="sample.pdf",  # put a small PDF in project root
        top_k=3,
    )

    print("\n=== ANSWER ===")
    print(result["answer"])

    print("\n=== SOURCES ===")
    for doc, score, metadata in result["sources"]:
        print(
            "-",
            doc[:120],
            "→",
            score,
            "|",
            metadata
        )


if __name__ == "__main__":
    asyncio.run(test_pdf_rag())
