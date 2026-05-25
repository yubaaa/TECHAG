"""
CPIRS - Sample Data
===================
Seed helpers to populate containers with realistic documents.
"""

from ..core.models import Document
from ..containers.container import Container


SAMPLE_DOCS = [
    Document(title="Introduction to Machine Learning",
             content="Supervised learning, classification, regression, neural networks.",
             keywords=["machine learning", "AI", "neural network", "classification"],
             category="AI"),

    Document(title="Deep Learning with Python",
             content="TensorFlow, Keras, CNN, RNN, transformers, backpropagation.",
             keywords=["deep learning", "python", "tensorflow", "keras"],
             category="AI"),

    Document(title="Database Systems: Concepts",
             content="Relational databases, SQL, transactions, indexing, normalisation.",
             keywords=["database", "SQL", "relational", "ACID"],
             category="databases"),

    Document(title="NoSQL and Distributed Data",
             content="MongoDB, Cassandra, CAP theorem, eventual consistency.",
             keywords=["NoSQL", "MongoDB", "distributed", "Cassandra"],
             category="databases"),

    Document(title="Mobile Agent Technology",
             content="JADE framework, agent migration, inter-platform, FIPA standards.",
             keywords=["mobile agent", "JADE", "migration", "FIPA"],
             category="agents"),

    Document(title="Information Retrieval Fundamentals",
             content="TF-IDF, BM25, inverted index, personalised ranking, query expansion.",
             keywords=["information retrieval", "TF-IDF", "ranking", "search"],
             category="IR"),

    Document(title="Natural Language Processing",
             content="Tokenisation, POS tagging, NER, transformers, BERT, GPT.",
             keywords=["NLP", "BERT", "transformers", "text"],
             category="AI"),

    Document(title="Cloud Computing Architecture",
             content="IaaS, PaaS, SaaS, microservices, containers, Kubernetes.",
             keywords=["cloud", "kubernetes", "microservices", "docker"],
             category="cloud"),

    Document(title="Cybersecurity Essentials",
             content="Encryption, PKI, firewall, intrusion detection, zero-trust.",
             keywords=["security", "encryption", "firewall", "PKI"],
             category="security"),

    Document(title="Personalised Recommendation Systems",
             content="Collaborative filtering, content-based, hybrid, user profile.",
             keywords=["recommendation", "collaborative filtering", "user profile"],
             category="IR"),
]


def seed_containers(*containers: Container) -> None:
    """Distribute sample documents across the given containers."""
    n = len(SAMPLE_DOCS)
    k = len(containers)
    for i, doc in enumerate(SAMPLE_DOCS):
        containers[i % k].add_document(doc)
