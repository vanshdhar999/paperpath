"""
Seed script: inserts 3 tracks + 25 ML/AI papers + prerequisite edges + track assignments.
Run from backend/ directory: python -m scripts.seed
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import uuid
from dotenv import load_dotenv
load_dotenv()

from app.db.session import SessionLocal
from app.db.models import Paper, Track, TrackPaper, Prerequisite


# ── Stable UUIDs keyed by arxiv_id ──────────────────────────────────────────
def uid(arxiv_id: str) -> str:
    return str(uuid.uuid5(uuid.NAMESPACE_URL, f"paperpath:paper:{arxiv_id}"))


PAPERS = [
    # ── BEGINNER ────────────────────────────────────────────────────────────
    {
        "id": uid("1301.3781"),
        "arxiv_id": "1301.3781",
        "title": "Efficient Estimation of Word Representations in Vector Space",
        "authors": ["Tomas Mikolov", "Kai Chen", "Greg Corrado", "Jeffrey Dean"],
        "abstract": (
            "Introduces Word2Vec — shallow neural networks that learn dense word "
            "embeddings from raw text. Foundational for all subsequent representation learning."
        ),
        "pdf_url": "https://arxiv.org/pdf/1301.3781",
        "difficulty_tier": "beginner",
        "venue": "ICLR 2013",
    },
    {
        "id": uid("1412.6980"),
        "arxiv_id": "1412.6980",
        "title": "Adam: A Method for Stochastic Optimization",
        "authors": ["Diederik P. Kingma", "Jimmy Ba"],
        "abstract": (
            "Introduces Adam optimizer combining momentum and adaptive learning rates. "
            "The default optimizer for training deep neural networks."
        ),
        "pdf_url": "https://arxiv.org/pdf/1412.6980",
        "difficulty_tier": "beginner",
        "venue": "ICLR 2015",
    },
    {
        "id": uid("1502.03167"),
        "arxiv_id": "1502.03167",
        "title": "Batch Normalization: Accelerating Deep Network Training by Reducing Internal Covariate Shift",
        "authors": ["Sergey Ioffe", "Christian Szegedy"],
        "abstract": (
            "Batch normalization normalizes layer inputs to stabilize and accelerate training. "
            "Became a standard component in deep networks."
        ),
        "pdf_url": "https://arxiv.org/pdf/1502.03167",
        "difficulty_tier": "beginner",
        "venue": "ICML 2015",
    },
    {
        "id": uid("1512.03385"),
        "arxiv_id": "1512.03385",
        "title": "Deep Residual Learning for Image Recognition",
        "authors": ["Kaiming He", "Xiangyu Zhang", "Shaoqing Ren", "Jian Sun"],
        "abstract": (
            "ResNet introduces skip connections to train very deep networks (100+ layers). "
            "Won ImageNet 2015 and remains a backbone architecture."
        ),
        "pdf_url": "https://arxiv.org/pdf/1512.03385",
        "difficulty_tier": "beginner",
        "venue": "CVPR 2016",
    },
    {
        "id": uid("1406.2661"),
        "arxiv_id": "1406.2661",
        "title": "Generative Adversarial Nets",
        "authors": ["Ian J. Goodfellow", "Jean Pouget-Abadie", "Mehdi Mirza",
                    "Bing Xu", "David Warde-Farley", "Sherjil Ozair",
                    "Aaron Courville", "Yoshua Bengio"],
        "abstract": (
            "Introduces GANs — a generator and discriminator trained adversarially. "
            "Foundational paper for generative modelling."
        ),
        "pdf_url": "https://arxiv.org/pdf/1406.2661",
        "difficulty_tier": "beginner",
        "venue": "NeurIPS 2014",
    },
    {
        "id": uid("1706.03762"),
        "arxiv_id": "1706.03762",
        "title": "Attention Is All You Need",
        "authors": ["Ashish Vaswani", "Noam Shazeer", "Niki Parmar",
                    "Jakob Uszkoreit", "Llion Jones", "Aidan N. Gomez",
                    "Lukasz Kaiser", "Illia Polosukhin"],
        "abstract": (
            "Introduces the Transformer architecture based entirely on self-attention. "
            "The foundation of BERT, GPT, and all modern LLMs."
        ),
        "pdf_url": "https://arxiv.org/pdf/1706.03762",
        "difficulty_tier": "beginner",
        "venue": "NeurIPS 2017",
    },
    {
        "id": uid("2006.11239"),
        "arxiv_id": "2006.11239",
        "title": "Denoising Diffusion Probabilistic Models",
        "authors": ["Jonathan Ho", "Ajay Jain", "Pieter Abbeel"],
        "abstract": (
            "DDPM formalises diffusion as a Markov chain of noising/denoising steps. "
            "The probabilistic backbone of Stable Diffusion and DALL-E 2."
        ),
        "pdf_url": "https://arxiv.org/pdf/2006.11239",
        "difficulty_tier": "beginner",
        "venue": "NeurIPS 2020",
    },
    # ── INTERMEDIATE ────────────────────────────────────────────────────────
    {
        "id": uid("1810.04805"),
        "arxiv_id": "1810.04805",
        "title": "BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding",
        "authors": ["Jacob Devlin", "Ming-Wei Chang", "Kenton Lee", "Kristina Toutanova"],
        "abstract": (
            "BERT pre-trains a bidirectional Transformer on masked language modelling. "
            "Fine-tuning BERT achieves SOTA on 11 NLP tasks."
        ),
        "pdf_url": "https://arxiv.org/pdf/1810.04805",
        "difficulty_tier": "intermediate",
        "venue": "NAACL 2019",
    },
    {
        "id": uid("1907.11692"),
        "arxiv_id": "1907.11692",
        "title": "RoBERTa: A Robustly Optimized BERT Pretraining Approach",
        "authors": ["Yinhan Liu", "Myle Ott", "Naman Goyal", "Jingfei Du",
                    "Mandar Joshi", "Danqi Chen", "Omer Levy", "Mike Lewis",
                    "Luke Zettlemoyer", "Veselin Stoyanov"],
        "abstract": (
            "Shows BERT was significantly undertrained. RoBERTa trains longer, on more data, "
            "with larger batches, outperforming BERT on all benchmarks."
        ),
        "pdf_url": "https://arxiv.org/pdf/1907.11692",
        "difficulty_tier": "intermediate",
        "venue": "arXiv 2019",
    },
    {
        "id": uid("1910.10683"),
        "arxiv_id": "1910.10683",
        "title": "Exploring the Limits of Transfer Learning with a Unified Text-to-Text Transformer",
        "authors": ["Colin Raffel", "Noam Shazeer", "Adam Roberts", "Katherine Lee",
                    "Sharan Narang", "Michael Matena", "Yanqi Zhou", "Wei Li", "Peter J. Liu"],
        "abstract": (
            "T5 frames every NLP task as text-to-text. Comprehensive study of transfer learning "
            "at scale using the C4 dataset."
        ),
        "pdf_url": "https://arxiv.org/pdf/1910.10683",
        "difficulty_tier": "intermediate",
        "venue": "JMLR 2020",
    },
    {
        "id": uid("2010.11929"),
        "arxiv_id": "2010.11929",
        "title": "An Image is Worth 16x16 Words: Transformers for Image Recognition at Scale",
        "authors": ["Alexey Dosovitskiy", "Lucas Beyer", "Alexander Kolesnikov",
                    "Dirk Weissenborn", "Xiaohua Zhai", "Thomas Unterthiner",
                    "Mostafa Dehghani", "Matthias Minderer", "Georg Heigold",
                    "Sylvain Gelly", "Jakob Uszkoreit", "Neil Houlsby"],
        "abstract": (
            "ViT applies a pure Transformer to image patches, showing that CNNs are not "
            "necessary when training on large datasets."
        ),
        "pdf_url": "https://arxiv.org/pdf/2010.11929",
        "difficulty_tier": "intermediate",
        "venue": "ICLR 2021",
    },
    {
        "id": uid("2005.14165"),
        "arxiv_id": "2005.14165",
        "title": "Language Models are Few-Shot Learners",
        "authors": ["Tom B. Brown", "Benjamin Mann", "Nick Ryder"],
        "abstract": (
            "GPT-3: a 175B parameter autoregressive language model demonstrating in-context "
            "learning — new tasks from a few examples in the prompt alone."
        ),
        "pdf_url": "https://arxiv.org/pdf/2005.14165",
        "difficulty_tier": "intermediate",
        "venue": "NeurIPS 2020",
    },
    {
        "id": uid("2001.08361"),
        "arxiv_id": "2001.08361",
        "title": "Scaling Laws for Neural Language Models",
        "authors": ["Jared Kaplan", "Sam McCandlish", "Tom Henighan",
                    "Tom B. Brown", "Benjamin Chess", "Rewon Child",
                    "Scott Gray", "Alec Radford", "Jeffrey Wu", "Dario Amodei"],
        "abstract": (
            "Empirical study showing loss scales as a power law with model size, "
            "dataset size, and compute. Guides how to allocate budgets for LLM training."
        ),
        "pdf_url": "https://arxiv.org/pdf/2001.08361",
        "difficulty_tier": "intermediate",
        "venue": "arXiv 2020",
    },
    {
        "id": uid("2103.00020"),
        "arxiv_id": "2103.00020",
        "title": "Learning Transferable Visual Models From Natural Language Supervision",
        "authors": ["Alec Radford", "Jong Wook Kim", "Chris Hallacy",
                    "Aditya Ramesh", "Gabriel Goh", "Sandhini Agarwal",
                    "Girish Sastry", "Amanda Askell", "Pamela Mishkin",
                    "Jack Clark", "Gretchen Krueger", "Ilya Sutskever"],
        "abstract": (
            "CLIP trains a vision encoder and text encoder jointly via contrastive learning on "
            "400M image-text pairs. Enables zero-shot image classification."
        ),
        "pdf_url": "https://arxiv.org/pdf/2103.00020",
        "difficulty_tier": "intermediate",
        "venue": "ICML 2021",
    },
    {
        "id": uid("2106.09685"),
        "arxiv_id": "2106.09685",
        "title": "LoRA: Low-Rank Adaptation of Large Language Models",
        "authors": ["Edward J. Hu", "Yelong Shen", "Phillip Wallis", "Zeyuan Allen-Zhu",
                    "Yuanzhi Li", "Shean Wang", "Lu Wang", "Weizhu Chen"],
        "abstract": (
            "LoRA freezes pre-trained weights and injects trainable low-rank matrices. "
            "Reduces fine-tuning parameters by 10,000x with no quality loss."
        ),
        "pdf_url": "https://arxiv.org/pdf/2106.09685",
        "difficulty_tier": "intermediate",
        "venue": "ICLR 2022",
    },
    {
        "id": uid("2112.10752"),
        "arxiv_id": "2112.10752",
        "title": "High-Resolution Image Synthesis with Latent Diffusion Models",
        "authors": ["Robin Rombach", "Andreas Blattmann", "Dominik Lorenz",
                    "Patrick Esser", "Björn Ommer"],
        "abstract": (
            "Latent Diffusion Models (Stable Diffusion) run the diffusion process in a "
            "compressed latent space, enabling high-res image synthesis at low compute."
        ),
        "pdf_url": "https://arxiv.org/pdf/2112.10752",
        "difficulty_tier": "intermediate",
        "venue": "CVPR 2022",
    },
    {
        "id": uid("2204.06125"),
        "arxiv_id": "2204.06125",
        "title": "Hierarchical Text-Conditional Image Generation with CLIP Latents",
        "authors": ["Aditya Ramesh", "Prafulla Dhariwal", "Alex Nichol",
                    "Casey Chu", "Mark Chen"],
        "abstract": (
            "DALL-E 2 uses a CLIP prior to map text embeddings to image embeddings, "
            "then a diffusion decoder. Achieves photorealistic text-to-image synthesis."
        ),
        "pdf_url": "https://arxiv.org/pdf/2204.06125",
        "difficulty_tier": "intermediate",
        "venue": "arXiv 2022",
    },
    # ── PRO ─────────────────────────────────────────────────────────────────
    {
        "id": uid("2203.02155"),
        "arxiv_id": "2203.02155",
        "title": "Training language models to follow instructions with human feedback",
        "authors": ["Long Ouyang", "Jeffrey Wu", "Xu Jiang"],
        "abstract": (
            "InstructGPT: fine-tunes GPT-3 with RLHF to follow instructions, "
            "showing aligned models preferred over larger unaligned ones."
        ),
        "pdf_url": "https://arxiv.org/pdf/2203.02155",
        "difficulty_tier": "pro",
        "venue": "NeurIPS 2022",
    },
    {
        "id": uid("2201.11903"),
        "arxiv_id": "2201.11903",
        "title": "Chain-of-Thought Prompting Elicits Reasoning in Large Language Models",
        "authors": ["Jason Wei", "Xuezhi Wang", "Dale Schuurmans",
                    "Maarten Bosma", "Brian Ichter", "Fei Xia",
                    "Ed Chi", "Quoc Le", "Denny Zhou"],
        "abstract": (
            "Shows that prompting LLMs with step-by-step reasoning examples (chain-of-thought) "
            "dramatically improves performance on arithmetic, commonsense, and symbolic tasks."
        ),
        "pdf_url": "https://arxiv.org/pdf/2201.11903",
        "difficulty_tier": "pro",
        "venue": "NeurIPS 2022",
    },
    {
        "id": uid("2203.15556"),
        "arxiv_id": "2203.15556",
        "title": "Training Compute-Optimal Large Language Models",
        "authors": ["Jordan Hoffmann", "Sebastian Borgeaud", "Arthur Mensch"],
        "abstract": (
            "Chinchilla: shows GPT-3-class models are undertrained. Optimal scaling "
            "allocates equal budget to model size and token count."
        ),
        "pdf_url": "https://arxiv.org/pdf/2203.15556",
        "difficulty_tier": "pro",
        "venue": "NeurIPS 2022",
    },
    {
        "id": uid("2205.14135"),
        "arxiv_id": "2205.14135",
        "title": "FlashAttention: Fast and Memory-Efficient Exact Attention with IO-Awareness",
        "authors": ["Tri Dao", "Daniel Y. Fu", "Stefano Ermon", "Atri Rudra", "Christopher Ré"],
        "abstract": (
            "FlashAttention rewrites attention computation to be IO-aware, reducing memory "
            "from O(N²) to O(N) and speeding up Transformer training 2-4x."
        ),
        "pdf_url": "https://arxiv.org/pdf/2205.14135",
        "difficulty_tier": "pro",
        "venue": "NeurIPS 2022",
    },
    {
        "id": uid("2302.13971"),
        "arxiv_id": "2302.13971",
        "title": "LLaMA: Open and Efficient Foundation Language Models",
        "authors": ["Hugo Touvron", "Thibaut Lavril", "Gautier Izacard",
                    "Xavier Martinet", "Marie-Anne Lachaux", "Timothée Lacroix",
                    "Baptiste Rozière", "Naman Goyal", "Eric Hambro",
                    "Faisal Azhar", "Aurelien Rodriguez", "Armand Joulin",
                    "Edouard Grave", "Guillaume Lample"],
        "abstract": (
            "LLaMA releases open foundation models (7B–65B) trained on public data only. "
            "Outperforms GPT-3 on most benchmarks at 13B parameters."
        ),
        "pdf_url": "https://arxiv.org/pdf/2302.13971",
        "difficulty_tier": "pro",
        "venue": "arXiv 2023",
    },
    {
        "id": uid("2212.08073"),
        "arxiv_id": "2212.08073",
        "title": "Constitutional AI: Harmlessness from AI Feedback",
        "authors": ["Yuntao Bai", "Saurav Kadavath", "Sandipan Kundu"],
        "abstract": (
            "Constitutional AI trains a model to critique and revise its own outputs "
            "using a set of principles, reducing reliance on human labellers for harmlessness."
        ),
        "pdf_url": "https://arxiv.org/pdf/2212.08073",
        "difficulty_tier": "pro",
        "venue": "arXiv 2022",
    },
    {
        "id": uid("2305.18290"),
        "arxiv_id": "2305.18290",
        "title": "Direct Preference Optimization: Your Language Model is Secretly a Reward Model",
        "authors": ["Rafael Rafailov", "Archit Sharma", "Eric Mitchell",
                    "Stefano Ermon", "Christopher D. Manning", "Chelsea Finn"],
        "abstract": (
            "DPO eliminates the separate reward model in RLHF, training the policy directly "
            "on preference pairs. Simpler, more stable, and competitive with PPO-based RLHF."
        ),
        "pdf_url": "https://arxiv.org/pdf/2305.18290",
        "difficulty_tier": "pro",
        "venue": "NeurIPS 2023",
    },
    {
        "id": uid("2312.00752"),
        "arxiv_id": "2312.00752",
        "title": "Mamba: Linear-Time Sequence Modeling with Selective State Spaces",
        "authors": ["Albert Gu", "Tri Dao"],
        "abstract": (
            "Mamba proposes selective state space models (SSMs) as a Transformer alternative "
            "with linear scaling in sequence length, matching Transformers on language tasks."
        ),
        "pdf_url": "https://arxiv.org/pdf/2312.00752",
        "difficulty_tier": "pro",
        "venue": "arXiv 2023",
    },
]

# arxiv_id → list of prerequisite arxiv_ids
PREREQUISITES = {
    # Intermediate papers
    "1810.04805": ["1706.03762"],           # BERT ← Attention
    "1907.11692": ["1810.04805"],           # RoBERTa ← BERT
    "1910.10683": ["1810.04805", "1706.03762"],  # T5 ← BERT + Attention
    "2010.11929": ["1706.03762", "1512.03385"],  # ViT ← Attention + ResNet
    "2005.14165": ["1706.03762"],           # GPT-3 ← Attention
    "2001.08361": ["1706.03762"],           # Scaling Laws ← Attention
    "2103.00020": ["2010.11929"],           # CLIP ← ViT
    "2106.09685": ["1810.04805", "2005.14165"],  # LoRA ← BERT + GPT-3
    "2112.10752": ["2006.11239"],           # LDM ← DDPM
    "2204.06125": ["2103.00020", "2006.11239"],  # DALL-E 2 ← CLIP + DDPM
    # Pro papers
    "2203.02155": ["2005.14165"],           # InstructGPT ← GPT-3
    "2201.11903": ["2005.14165"],           # CoT ← GPT-3
    "2203.15556": ["2001.08361"],           # Chinchilla ← Scaling Laws
    "2205.14135": ["1706.03762"],           # FlashAttention ← Attention
    "2302.13971": ["2005.14165", "2203.15556"],  # LLaMA ← GPT-3 + Chinchilla
    "2212.08073": ["2203.02155"],           # Constitutional AI ← InstructGPT
    "2305.18290": ["2203.02155"],           # DPO ← InstructGPT
    "2312.00752": ["1706.03762"],           # Mamba ← Attention
}

# Track assignments: arxiv_id → track name
TRACK_PAPERS = {
    "beginner": [
        "1301.3781", "1412.6980", "1502.03167",
        "1512.03385", "1406.2661", "1706.03762", "2006.11239",
    ],
    "intermediate": [
        "1810.04805", "1907.11692", "1910.10683", "2010.11929",
        "2005.14165", "2001.08361", "2103.00020", "2106.09685",
        "2112.10752", "2204.06125",
    ],
    "pro": [
        "2203.02155", "2201.11903", "2203.15556", "2205.14135",
        "2302.13971", "2212.08073", "2305.18290", "2312.00752",
    ],
}


def main():
    db = SessionLocal()
    try:
        # ── Tracks ───────────────────────────────────────────────────────────
        tracks = {}
        for name in ["beginner", "intermediate", "pro"]:
            existing = db.query(Track).filter_by(domain="ML/AI", name=name).first()
            if existing:
                tracks[name] = existing
                print(f"Track '{name}' already exists, skipping.")
            else:
                track = Track(
                    id=str(uuid.uuid5(uuid.NAMESPACE_URL, f"paperpath:track:ml-ai:{name}")),
                    domain="ML/AI",
                    name=name,
                )
                db.add(track)
                tracks[name] = track
                print(f"Created track: {name}")
        db.flush()

        # ── Papers ───────────────────────────────────────────────────────────
        paper_id_map = {}  # arxiv_id → db id
        for p in PAPERS:
            existing = db.query(Paper).filter_by(arxiv_id=p["arxiv_id"]).first()
            if existing:
                paper_id_map[p["arxiv_id"]] = existing.id
                print(f"Paper '{p['arxiv_id']}' already exists, skipping.")
                continue
            paper = Paper(
                id=p["id"],
                arxiv_id=p["arxiv_id"],
                title=p["title"],
                authors=p["authors"],
                abstract=p["abstract"],
                pdf_url=p["pdf_url"],
                difficulty_tier=p["difficulty_tier"],
                venue=p.get("venue"),
            )
            db.add(paper)
            paper_id_map[p["arxiv_id"]] = p["id"]
            print(f"Created paper: {p['arxiv_id']} — {p['title'][:50]}")
        db.flush()

        # ── Prerequisites ────────────────────────────────────────────────────
        for arxiv_id, prereq_ids in PREREQUISITES.items():
            paper_id = paper_id_map[arxiv_id]
            for prereq_arxiv_id in prereq_ids:
                prereq_id = paper_id_map[prereq_arxiv_id]
                existing = db.query(Prerequisite).filter_by(
                    paper_id=paper_id, prerequisite_paper_id=prereq_id
                ).first()
                if not existing:
                    db.add(Prerequisite(paper_id=paper_id, prerequisite_paper_id=prereq_id))
                    print(f"  Prerequisite: {arxiv_id} <- {prereq_arxiv_id}")
        db.flush()

        # ── TrackPapers ──────────────────────────────────────────────────────
        for track_name, arxiv_ids in TRACK_PAPERS.items():
            track = tracks[track_name]
            for order, arxiv_id in enumerate(arxiv_ids):
                paper_id = paper_id_map[arxiv_id]
                existing = db.query(TrackPaper).filter_by(
                    track_id=track.id, paper_id=paper_id
                ).first()
                if not existing:
                    db.add(TrackPaper(track_id=track.id, paper_id=paper_id, order_hint=order))
                    print(f"  TrackPaper: {track_name}[{order}] = {arxiv_id}")
        db.commit()
        print("\n✓ Seed complete.")

    except Exception as e:
        db.rollback()
        print(f"\n✗ Seed failed: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
