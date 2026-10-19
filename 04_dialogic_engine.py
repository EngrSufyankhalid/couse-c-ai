"""Conversational AI Mission 1: Socratic discovery and Galilean debate.

Requires: pip install google-genai python-dotenv
Set GEMINI_API_KEY in .env. Never commit .env.
"""
from __future__ import annotations

import argparse
import os
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types

MODEL_DEFAULT = "gemini-2.5-flash"

DISCOVERY_SYSTEM = """You are AURA, a patient Socratic examiner inspired by Plato's Euthyphro.
Your goal is conceptual clarification, not agreement or winning. Ask one precise,
non-leading question at a time, search for possible counterexamples, and distinguish
real logical contradictions from mere disagreement. Do not invent the user's views.
Be respectful and acknowledge uncertainty and unresolved questions (aporia)."""

JUDGE_SYSTEM = """You are a cautious logic auditor. Analyze the stated claim and
response. Only report a contradiction if the response explicitly commits to an
incompatible position under the same interpretation. Answer in exactly two lines:
CONTRADICTION: YES or NO
REASON: a concise, evidence-grounded explanation. Do not manufacture inconsistency."""

PERSONAS = {
    "Advocate (Salviati)": "Present the strongest carefully qualified argument FOR releasing model weights publicly. Respect risks and uncertainty; avoid strawmen.",
    "Traditionalist (Simplicio)": "Present the strongest carefully qualified argument AGAINST immediate public release of frontier model weights. Respect benefits and uncertainty; avoid strawmen.",
    "Mediator (Sagredo)": "Critically assess both arguments fairly, identify hidden assumptions and propose a workable conditional compromise. Do not automatically declare a winner.",
}

SCENARIO = ("A lab has developed an unusually capable general-purpose AI model. "
            "Publishing its weights could help small universities develop medical and accessibility tools, "
            "but evaluations reveal a meaningful potential for malicious misuse. "
            "Should the lab release the weights immediately, delay release for independent testing, "
            "or use a restricted-access model?")


def generate(client: genai.Client, model: str, system: str, prompt: str) -> str:
    response = client.models.generate_content(
        model=model,
        contents=prompt,
        config=types.GenerateContentConfig(system_instruction=system, temperature=0.5),
    )
    if not response.text:
        raise RuntimeError("The model returned no textual response. Review model access and safety settings.")
    return response.text.strip()


def socratic(client: genai.Client, model: str, premise: str, max_rounds: int, interactive: bool,
             answers: list[str] | None = None) -> str:
    """Finite state machine: CLAIM -> PROBE -> RESPONSE -> AUDIT -> REFINE/END.

    Automated responses are simulated *for testing*, not fabricated user statements.
    """
    log = ["MODE: Socratic discovery", f"Initial P0: {premise}"]
    current = premise
    history: list[str] = []
    for k in range(max_rounds):
        log.append(f"\nSTATE CLAIM P{k}: {current}")
        question = generate(client, model, DISCOVERY_SYSTEM,
                            f"Current definition: {current}\nPast dialogue:\n" + "\n".join(history[-8:]) +
                            "\nSTATE PROBE: Ask ONE targeted question that probes a boundary case or potential exception. "
                            "Do not decide whether a contradiction exists before the respondent replies.")
        log.append(f"STATE PROBE / AURA: {question}")
        if interactive:
            reply = input("Your answer (or type 'aporia' to stop): ").strip()
        elif answers and k < len(answers):
            reply = answers[k]
            log.append("RESPONSE SOURCE: supplied test response")
        else:
            # Explicitly labelled model-simulated user for repeatable demo runs.
            reply = generate(client, model,
                             "Simulate a thoughtful respondent to a philosophical question. "
                             "You may admit uncertainty. Do not force a contradiction.",
                             f"Belief: {current}\nQuestion: {question}\nReply as the respondent in 1–3 sentences.")
            log.append("RESPONSE SOURCE: model-simulated respondent (not a human)")
        log.append(f"STATE RESPONSE: {reply}")
        if reply.strip().lower() in {"aporia", "i don't know", "i do not know"}:
            log.append("STATE END: APORIA — respondent acknowledges uncertainty")
            break
        verdict = generate(client, model, JUDGE_SYSTEM,
                           f"Current claim: {current}\nProbe question: {question}\nRespondent answer: {reply}\n"
                           "Check only for a concrete logical conflict; explain with specific quotes or paraphrases.")
        log.append(f"STATE AUDIT: {verdict}")
        history.extend([f"Question: {question}", f"Response: {reply}", f"Audit: {verdict}"])
        contradiction = verdict.splitlines()[0].strip().upper() == "CONTRADICTION: YES"
        if contradiction:
            refined = generate(client, model, DISCOVERY_SYSTEM,
                               f"P{k}: {current}\nQuestion: {question}\nAnswer: {reply}\nAudit: {verdict}\n"
                               "Propose a single concise revised definition P(k+1) that accommodates the objection. "
                               "Clearly mark it as a TENTATIVE suggestion, not a claim made by the respondent.")
            current = refined
            log.append(f"STATE REFINE -> P{k+1} (tentative AI proposal): {current}")
        else:
            log.append("STATE CONTINUE: No demonstrated contradiction; retain premise and probe further")
    else:
        log.append(f"STATE END: ROUND LIMIT ({max_rounds}). Tentative current definition: {current}")
    return "\n".join(log)


def galilean(client: genai.Client, model: str, scenario: str) -> str:
    log = ["MODE: Galilean three-persona debate", f"SCENARIO: {scenario}"]
    transcript = ""
    for role, instruction in PERSONAS.items():
        message = generate(client, model,
                           f"You are {role}. {instruction} Keep your argument under 180 words. "
                           "Do not provide instructions for harm.",
                           f"Debate scenario:\n{scenario}\nEarlier statements:\n{transcript}\n"
                           "Give your argument and one question for another speaker.")
        log.append(f"\n{role}: {message}")
        transcript += f"\n{role}: {message}\n"
    return "\n".join(log)


def main() -> None:
    load_dotenv()
    parser = argparse.ArgumentParser(description="AURA Dialogic Engine")
    parser.add_argument("--mode", choices=["socratic", "galilean", "both"], default="both")
    parser.add_argument("--model", default=os.getenv("GEMINI_MODEL", MODEL_DEFAULT))
    parser.add_argument("--premise", default="An AI agent is benevolent if it obeys human commands.")
    parser.add_argument("--rounds", type=int, default=3)
    parser.add_argument("--interactive", action="store_true", help="Enter responses yourself during Socratic dialogue")
    parser.add_argument("--output", default="05_Execution_Transcript.txt")
    args = parser.parse_args()
    if args.rounds < 1 or args.rounds > 12:
        parser.error("--rounds must be from 1 to 12")
    
    key = os.getenv("GEMINI_API_KEY")
    if not key:
        parser.error("GEMINI_API_KEY missing. Copy .env.example to .env and add your private key.")
    client = genai.Client(api_key=key)
    sections = [f"AURA DIALOGIC ENGINE — ACTUAL API RUN\nUTC timestamp: {datetime.now(timezone.utc).isoformat()}\nModel: {args.model}\n"]
    try:
        if args.mode in ("socratic", "both"):
            sections.append(socratic(client, args.model, args.premise, args.rounds, args.interactive))
        if args.mode in ("galilean", "both"):
            sections.append(galilean(client, args.model, SCENARIO))
    except Exception as exc:
        # Never write a partially successful run as the required complete transcript.
        raise SystemExit(f"API/engine error: {exc}") from exc
    result = "\n\n" + ("\n" + "=" * 70 + "\n").join(sections) + "\n"
    Path(args.output).write_text(result, encoding="utf-8")
    print(result)
    print(f"\nSaved genuine API output to: {Path(args.output).resolve()}")


if __name__ == "__main__":
    main()
