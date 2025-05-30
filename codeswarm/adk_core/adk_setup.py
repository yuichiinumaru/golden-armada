from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner

# Global instance of the session service
_SESSION_SERVICE_INSTANCE = None

def get_session_service():
    """Returns a singleton instance of the in-memory session service."""
    global _SESSION_SERVICE_INSTANCE
    if _SESSION_SERVICE_INSTANCE is None:
        _SESSION_SERVICE_INSTANCE = InMemorySessionService()
    return _SESSION_SERVICE_INSTANCE

def get_runner(agent_instance, session_service_instance, app_name="codeswarm"):
    """
    Returns an instance of the Runner configured with the agent, session service, and app name.

    Args:
        agent_instance: The agent instance to be run.
        session_service_instance: The session service instance.
        app_name: The name of the application.
    """
    return Runner(
        agent=agent_instance, # Pass the specific agent instance
        session_service=session_service_instance,
        app_name=app_name
    )

async def create_new_session(session_service, app_name="codeswarm", user_id="user"):
    """Creates a new session using the provided session service."""
    return await session_service.create_session(app_name=app_name, user_id=user_id)