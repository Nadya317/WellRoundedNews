%pip install torch numpy transformers sentence_transformers detoxify
import torch
import numpy as np
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from sentence_transformers import SentenceTransformer, util
from detoxify import Detoxify
import json

class SentimentAnalyticLab:
    def __init__(self):
        #Inirializing filtering and semantic matching logic
        print("Initializing filtering and semantic matching logic")
        self.safety_model = Detoxify('original')
        #Turns sentences into vectors to calculate sentence similarity
        self.encoder = SentenceTransformer('all-MiniLM-L6-v2')
        
        # breaks text into tokens 
        self.model_name = "answerdotai/ModernBERT-base" 
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.classifier = AutoModelForSequenceClassification.from_pretrained(self.model_name, num_labels=3)
        
    # Filtering content logic
    def validate_content(self, text):
        """Ensures that the content being derived is filtered."""
        results = self.safety_model.predict(text)
        # do not include if toxic score is greater than 0.8
        is_safe = results['toxicity'] < 0.8 and results['insult'] < 0.7
        return is_safe, results

    # Semantic topic/relevance logic 
    def is_news_relevant(self, influencer_text, news_context_text):
        """Calculates relevance of text using cosine similarity."""
        embeddings = self.encoder.encode([influencer_text, news_context_text])
        similarity = util.cos_sim(embeddings[0], embeddings[1])
        #If similarity is greater than 0.60 we can consider this, if less we ignore it
        return similarity.item() > 0.60 

    # logic for sentiment and bias analysis
    def run_inference(self, text):
        """classifies sentiment and connects to an ideology category"""
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=512)
        
        with torch.no_grad():
            logits = self.classifier(**inputs).logits
            probs = torch.nn.functional.softmax(logits, dim=-1).numpy()[0]
        
        # map output to bias scale
        sentiment_idx = np.argmax(probs)
        sentiment_labels = ["Negative", "Neutral", "Positive"]
        
        # adding a more specific label of political ideology (center vs establishment)
        ideology_report = {
            "primary_label": "Center/Moderate",
            "sub_tag": "Establishment",
            "extremity_score": round(float(np.max(probs)), 2)
        }
        
        text_lower = text.lower()
        if any(word in text_lower for word in ["socialist", "redistribution", "equity"]):
            ideology_report.update({"primary_label": "Left", "sub_tag": "Socialist Democrat"})
        elif any(word in text_lower for word in ["corporate", "market", "incremental"]):
            ideology_report.update({"primary_label": "Lean-Left", "sub_tag": "Corporate Democrat"})
        elif any(word in text_lower for word in ["heritage", "traditional", "libertarian"]):
            ideology_report.update({"primary_label": "Right", "sub_tag": "Conservative"})
            
        return sentiment_labels[sentiment_idx], ideology_report

    # processing script logic
    def process_transcript(self, transcript, news_headline):
        # validating filtering logic
        safe, safety_data = self.validate_content(transcript)
        if not safe:
            return {"status": "REJECTED", "reason": "Toxicity/Slur Detected", "data": safety_data}
        
        # validating relevance logic
        if not self.is_news_relevant(transcript, news_headline):
            return {"status": "SKIPPED", "reason": "Transcript not relevant to current news topic"}
        
        # analyze sentiment and bias
        sentiment, ideology = self.run_inference(transcript)
        
        return {
            "status": "ANALYZED",
            "topic_match": news_headline,
            "results": {
                "sentiment": sentiment,
                "political_alignment": ideology
            }
        }


lab = SentimentAnalyticLab()

# test case
news_story = "New legislation proposed for universal healthcare funding and redistribution."
influencer_post = "The socialist wing is finally pushing for the redistribution of healthcare funds to ensure equity in this new legislation."

result = lab.process_transcript(influencer_post, news_story)
print(json.dumps(result, indent=4))
