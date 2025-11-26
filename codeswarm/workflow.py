from google.adk.agents import SequentialAgent, ParallelAgent, LoopAgent
from .adk_agents import create_admin_llm_agent, create_dev_llm_agent, create_revisor_llm_agent

def create_codeswarm_workflow(pairs=1, rounds=1, model_override=None):
    """
    Creates the main CodeSwarm workflow using a SequentialAgent and LoopAgent.
    """
    admin_agent = create_admin_llm_agent(model_override=model_override)

    dev_revisor_pairs = []
    for i in range(pairs):
        dev_agent = create_dev_llm_agent(i + 1, model_override=model_override)
        revisor_agent = create_revisor_llm_agent(i + 1, model_override=model_override)

        pair_workflow = SequentialAgent(
            name=f"DevRevisorPair_{i+1}",
            sub_agents=[dev_agent, revisor_agent]
        )
        dev_revisor_pairs.append(pair_workflow)

    parallel_dev_revisor_workflow = ParallelAgent(
        name="ParallelDevRevisor",
        sub_agents=dev_revisor_pairs
    )

    looped_workflow = LoopAgent(
        name="CodeSwarmLoop",
        sub_agents=[
            admin_agent,
            parallel_dev_revisor_workflow,
        ],
        max_iterations=rounds,
    )

    codeswarm_workflow = SequentialAgent(
        name="CodeSwarmWorkflow",
        sub_agents=[
            looped_workflow,
        ],
    )
    return codeswarm_workflow
