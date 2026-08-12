"""Minimal programmatic runner for the GTM agent (an alternative to `adk web`).

Run a single turn from the command line:

    python run_cli.py "How qualified is the Acme Retail deal, and what's the gap?"

This shows the ADK Runner + SessionService pattern. For interactive use or a nice
UI, prefer `adk web` from the project root, or the chat frontend in web/ (see README).

Note: ADK's session API is async in current releases; this script uses the async
runner accordingly.
"""

from __future__ import annotations

import asyncio
import sys

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from gtm_agent import root_agent

APP_NAME = "gtm_agent"
USER_ID = "local-user"
SESSION_ID = "cli-session"


async def _run(prompt: str) -> None:
    session_service = InMemorySessionService()
    await session_service.create_session(
        app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID
    )
    runner = Runner(
        agent=root_agent, app_name=APP_NAME, session_service=session_service
    )
    message = types.Content(role="user", parts=[types.Part(text=prompt)])

    async for event in runner.run_async(
        user_id=USER_ID, session_id=SESSION_ID, new_message=message
    ):
        if event.is_final_response() and event.content and event.content.parts:
            print(event.content.parts[0].text)


def main() -> None:
    prompt = " ".join(sys.argv[1:]).strip() or (
        "Give me a deal-team plan to advance the Acme Retail opportunity to close."
    )
    asyncio.run(_run(prompt))


if __name__ == "__main__":
    main()
