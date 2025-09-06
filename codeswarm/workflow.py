from google.adk.agents import SequentialAgent, ParallelAgent
from .adk_agents import create_admin_llm_agent, create_dev_llm_agent, create_revisor_llm_agent

def create_codeswarm_workflow(pairs=1, model_override=None):
    """
    Creates the main CodeSwarm workflow using a SequentialAgent.
    """
    admin_agent = create_admin_llm_agent(model_override=model_override)

    dev_revisor_pairs = []
    for i in range(pairs):
        dev_agent = create_dev_llm_agent(i + 1, model_override=model_override)
        revisor_agent = create_revisor_llm_agent(i + 1, model_override=model_override)

        # Create a SequentialAgent for each Dev-Revisor pair
        pair_workflow = SequentialAgent(
            name=f"DevRevisorPair_{i+1}",
            sub_agents=[dev_agent, revisor_agent]
        )
        dev_revisor_pairs.append(pair_workflow)

    # The Dev-Revisor pairs can run in parallel
    parallel_dev_revisor_workflow = ParallelAgent(
        name="ParallelDevRevisor",
        sub_agents=dev_revisor_pairs
    )

    codeswarm_workflow = SequentialAgent(
        name="CodeSwarmWorkflow",
        sub_agents=[
            admin_agent,
            parallel_dev_revisor_workflow,
        ],
    )
    return codeswarm_workflow
