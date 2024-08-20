from griptape.structures import Agent
from griptape.tasks import TextSummaryTask

# Create a new agent
agent = Agent()

# Add the TextSummaryTask to the agent
agent.add_task(TextSummaryTask())


# Run the agent
agent.run(
    "Artificial Intelligence (AI) is a branch of computer science that deals with "
    "creating machines capable of thinking and learning. It encompasses various fields "
    "such as machine learning, neural networks, and deep learning. AI has the potential "
    "to revolutionize many sectors, including healthcare, finance, and transportation. "
    "Our life in this modern age depends largely on computers. It is almost impossible "
    "to think about life without computers. We need computers in everything that we use "
    "in our daily lives. So it becomes very important to make computers intelligent so "
    "that our lives become easy. Artificial Intelligence is the theory and development "
    "of computers, which imitates the human intelligence and senses, such as visual "
    "perception, speech recognition, decision-making, and translation between languages."
    " Artificial Intelligence has brought a revolution in the world of technology. "
)
