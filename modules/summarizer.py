from pathlib import Path

from ollama import Client

from config import (
    OLLAMA_HOST,
    OLLAMA_MODEL,
    SUMMARY_DIR,
)

# Create Ollama client
client = Client(host=OLLAMA_HOST)


def summarize_text(
    transcript: str,
    file_name: str,
    output_language: str,
) -> tuple[str, Path]:
    """
    Generate structured study notes using Ollama
    and save them as a Markdown file.
    """

    # Language instruction
    if output_language == "Auto (Same as Lecture)":
        language_instruction = (
            "Generate the notes in the same language as the lecture transcript."
        )
    else:
        language_instruction = (
            f"Generate ALL headings, explanations, bullet points, questions, and answers in {output_language}."
        )

    prompt = f"""
You are an expert educational note-taking assistant.

{language_instruction}

Your task is to convert the following lecture transcript into professional, well-organized study notes.

Return ONLY a valid Markdown document.

Do NOT include:
- Any introduction before the Markdown
- Any conclusion outside the Markdown
- Triple backticks (```)
- Explanations about your process
- Statements like "Here are the notes"

## Objective

Create notes that resemble those written by an experienced teacher or student.

The notes should be:

- Easy to study
- Well structured
- Accurate
- Concise
- Suitable for revision
- Logically organized

---

## Instructions

### 1. Title

Generate a clear, descriptive title based on the lecture topic.

Do not use generic titles.

---

### 2. Overview

Write a brief overview (2–4 sentences) summarizing the lecture.

---

### 3. Analyze the Lecture

Carefully analyze the transcript and identify all major concepts discussed.

Organize the notes into logical sections using meaningful Markdown headings (##).

Generate section headings dynamically based on the lecture content.

Examples:

For a Python lecture:
- Functions
- Parameters
- Return Values
- Lambda Functions
- Decorators
- Exception Handling

For Networking:
- OSI Model
- TCP/IP
- Routing
- DNS
- HTTP
- HTTPS

For Artificial Intelligence:
- LLMs
- RAG
- Agents
- Embeddings
- Vector Databases
- Prompt Engineering

Never use generic headings like:

- Topic 1
- Topic 2
- Main Topics
- Section 1

---

### 4. Explain Each Section

For every section:

- Explain the concept clearly.
- Preserve important technical terminology.
- Use bullet points whenever appropriate.
- Remove repeated information.
- Merge duplicate ideas.
- Correct obvious transcription mistakes only when the intended meaning is clear.
- Do NOT invent missing information.
- Preserve important examples mentioned in the lecture.
- Keep explanations concise but complete.

---

### 5. Optional Sections

If the lecture contains any of the following, create separate sections for them.

Only include these sections if they actually exist in the lecture.

- Important Definitions
- Formulas
- Algorithms
- Code Snippets (preserve formatting using Markdown code blocks)
- Examples
- Best Practices
- Advantages and Disadvantages
- Comparisons
- Tips and Notes
- Warnings
- Common Mistakes
- Interview Questions
- Frequently Asked Questions

For comparison topics, prefer Markdown tables whenever they improve readability.

Do not invent any information.

---

### 6. Key Takeaways

Summarize the lecture into 5–10 important bullet points.

Focus only on the most important concepts.

---

### 7. Quick Revision

Create 5–10 revision questions.

Cover different sections of the lecture.

Format exactly like this:

**Q:** Question

**A:** Answer

Questions should test the important concepts explained in the lecture.

---

## Language Rules

- Preserve multilingual content whenever appropriate.
- Do not translate technical terms unless required by the selected output language.
- If the output language differs from the lecture language, translate explanations naturally while keeping technical keywords (such as Python, HTTP, API, SQL, TensorFlow, RAG, etc.) unchanged unless there is a well-established translation.

---

## Transcript Quality Rules

If parts of the transcript are:

- incomplete,
- unclear,
- corrupted,
- repeated,
- or caused by speech recognition errors,

then:

- infer only obvious corrections.
- never guess missing facts.
- clearly indicate uncertainty when necessary.
- remove filler words such as:
  - um
  - uh
  - you know
  - okay
  - right
  - basically
  - actually

whenever doing so improves readability.

---

## Formatting Rules

Use proper Markdown.

Use:

- # for the title
- ## for major sections
- ### for subsections when needed

Use:

- Bullet lists
- Numbered lists
- Tables (when useful)
- Markdown code blocks for code
- Bold text for important concepts
- Italics only where appropriate

Keep paragraphs short.

Avoid walls of text.

---

## Strict Rules

- Return ONLY the Markdown document.
- Do not hallucinate or invent facts.
- Do not add information not supported by the transcript.
- If something is unclear, explicitly mention that it is unclear.
- Avoid repeating the same information across multiple sections.
- Preserve technical names exactly.
- Preserve formulas exactly.
- Preserve code syntax exactly.
- Preserve mathematical expressions.
- Preserve units, numbers, versions, commands, and filenames exactly.
- Make the notes suitable for exam preparation and future revision.

---

Lecture Transcript:

{transcript}
"""

    response = client.chat(
        model=OLLAMA_MODEL,
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
    )

    summary = response["message"]["content"].strip()

    summary_path = SUMMARY_DIR / f"{file_name}.md"

    with open(summary_path, "w", encoding="utf-8") as file:
        file.write(summary)

    return summary, summary_path