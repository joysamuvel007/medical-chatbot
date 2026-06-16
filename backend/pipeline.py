
from utils.models import ChatRequest, ChatResponse
from utils.logger import logger
from memory.session_manager import session_manager
from agents.preprocessor import preprocessor
from agents.classifier import classifier
from agents.decision_engine import decision_engine
from agents.web_search import web_search_agent
from agents.context_builder import context_builder
from agents.responder import response_generator


async def run_pipeline(request: ChatRequest) -> ChatResponse:
    logger.info(f"PIPELINE START: '{request.user_message[:60]}'")

    if not request.session_id or not session_manager.session_exists(request.session_id):
        session_id = session_manager.create_session()
    else:
        session_id = request.session_id
    preprocessed = preprocessor.process(request.user_message)

    session_manager.add_message(session_id, "user", request.user_message)

    classification = await classifier.classify(preprocessed)
    logger.info(
        f"Classification: intent={classification.intent.value}, "
        f"emergency={classification.emergency_level.value}, "
        f"confidence={classification.confidence:.2f}"
    )

    history = session_manager.get_history(session_id)
    has_history = len(history) > 1
    metadata = session_manager.get_session_metadata(session_id)
    region = metadata.get("region")

    decision = decision_engine.decide(
        classification,
        session_has_history=has_history,
        region=region
    )
    logger.info(f"Decision: action={decision['action']}, skip_llm={decision['skip_llm']}")

    if decision["skip_llm"]:
        emergency_response = decision["emergency_message"]
        session_manager.add_message(session_id, "assistant", emergency_response)
        return ChatResponse(
            session_id=session_id,
            response=emergency_response,
            intent=classification.intent.value,
            emergency_level=decision["emergency_level"],
            emergency_message=emergency_response,
            sources=[],
            confidence=1.0,
            is_safe=True,
        )

    search_results = []
    if decision["needs_search"]:
        logger.info("Running web search...")
        search_results = web_search_agent.search(request.user_message)
        logger.info(f"Found {len(search_results)} search results")

    memory_summary = ""
    if decision["needs_memory"]:
        memory_summary = session_manager.get_session_summary(session_id)

    full_history = session_manager.get_history(session_id)
    context = context_builder.build(
        intent=classification.intent,
        emergency_level=classification.emergency_level,
        history=full_history,
        search_results=search_results if decision["needs_search"] else None,
        memory_summary=memory_summary,
    )

    response_text, is_safe = await response_generator.generate(context)

    session_manager.add_message(session_id, "assistant", response_text)

    logger.info(f"PIPELINE END: session={session_id}, safe={is_safe}")

    return ChatResponse(
        session_id=session_id,
        response=response_text,
        intent=classification.intent.value,
        emergency_level=decision["emergency_level"],
        emergency_message=decision.get("emergency_message"),
        sources=search_results,
        confidence=classification.confidence,
        is_safe=is_safe,
    )